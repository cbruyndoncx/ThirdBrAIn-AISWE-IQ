# Session Sync Hook Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically capture git changes at session end and route them to relevant agent state files so the Chief of Staff starts each day with current context.

**Architecture:** A pure-bash Stop hook (`session-sync.sh`) that collects git changes across three layers (commits, staged, unstaged/untracked), routes them to domain-specific state files based on file path patterns, and appends timestamped sync blocks. The Chief of Staff agent cleans up raw sync blocks on next startup.

**Tech Stack:** Bash, git, Claude Code hooks system

---

### Task 1: Create the session-sync.sh script

**Files:**
- Create: `scripts/session-sync.sh`

**Step 1: Write the script**

```bash
#!/bin/bash
# Session Sync Hook - Captures git changes and appends to agent state files
# Registered as a Claude Code Stop hook
# No LLM calls - pure bash/git

set -euo pipefail

# --- Configuration ---

# Domain routing: map file patterns to agent state file names
# Format: "pattern:agent" (checked in order, first match wins per file)
DOMAIN_ROUTES=(
  "tests/:qa"
  "__tests__/:qa"
  "*.test.*:qa"
  "*.spec.*:qa"
  ".github/workflows/:devops"
  "Dockerfile:devops"
  "docker-compose*:devops"
  "infrastructure/:devops"
  "deploy/:devops"
  "ci/:devops"
  "*.yml:devops"
  "*.yaml:devops"
  "docs/:content"
  "public/:design"
  "assets/:design"
  "*.css:design"
  "*.scss:design"
  "src/:eng"
  "lib/:eng"
  "packages/:eng"
  "*.ts:eng"
  "*.tsx:eng"
  "*.js:eng"
  "*.jsx:eng"
  "*.py:eng"
  "*.go:eng"
  "*.rs:eng"
  "*.rb:eng"
)

MAX_FILES_PER_LAYER=50

# --- Guard clauses ---

# Must be in a git repo
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

# Must have a HEAD (not an empty repo)
git rev-parse HEAD > /dev/null 2>&1 || exit 0

# Must have a .claude/state/ directory (project initialized)
STATE_DIR=".claude/state"
[ -d "$STATE_DIR" ] || exit 0

MARKER_FILE="$STATE_DIR/.last-sync-sha"
CURRENT_SHA=$(git rev-parse HEAD)

# --- Collect changes ---

COMMITS=""
STAGED=""
UNSTAGED=""
UNTRACKED=""

# Layer 1: Commits since last sync
if [ -f "$MARKER_FILE" ]; then
  LAST_SHA=$(cat "$MARKER_FILE")
  # Verify the SHA still exists (could be gone after rebase)
  if git cat-file -t "$LAST_SHA" > /dev/null 2>&1; then
    if [ "$LAST_SHA" != "$CURRENT_SHA" ]; then
      COMMITS=$(git log --oneline "$LAST_SHA".."$CURRENT_SHA" 2>/dev/null | head -n $MAX_FILES_PER_LAYER)
      COMMIT_COUNT=$(git log --oneline "$LAST_SHA".."$CURRENT_SHA" 2>/dev/null | wc -l | tr -d ' ')
    fi
  else
    # SHA gone (rebase, etc.) - just note current HEAD
    COMMITS="(baseline SHA no longer exists - reset to current HEAD)"
  fi
else
  # First run - no baseline
  COMMITS="(initial sync - no prior baseline)"
fi

# Layer 2: Staged but uncommitted
STAGED=$(git diff --cached --stat 2>/dev/null | head -n $MAX_FILES_PER_LAYER)

# Layer 3: Unstaged modifications
UNSTAGED=$(git diff --stat 2>/dev/null | head -n $MAX_FILES_PER_LAYER)

# Layer 3b: Untracked files
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | head -n $MAX_FILES_PER_LAYER)
UNTRACKED_COUNT=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')

# If nothing changed, just update marker and exit
if [ -z "$COMMITS" ] && [ -z "$STAGED" ] && [ -z "$UNSTAGED" ] && [ -z "$UNTRACKED" ]; then
  echo "$CURRENT_SHA" > "$MARKER_FILE"
  exit 0
fi

# --- Build sync block ---

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")

build_sync_block() {
  local domain_label="$1"
  local block=""

  block="<!-- SESSION SYNC -->"$'\n'
  block+="## Session Changes ($TIMESTAMP)"$'\n'$'\n'

  if [ -n "$domain_label" ]; then
    block+="**Domain:** $domain_label"$'\n'$'\n'
  fi

  if [ -n "$COMMITS" ]; then
    block+="### Commits"$'\n'
    block+="$COMMITS"$'\n'
    if [ -n "${COMMIT_COUNT:-}" ] && [ "$COMMIT_COUNT" -gt "$MAX_FILES_PER_LAYER" ]; then
      block+="... and $((COMMIT_COUNT - MAX_FILES_PER_LAYER)) more commits"$'\n'
    fi
    block+=$'\n'
  fi

  if [ -n "$STAGED" ]; then
    block+="### Staged (uncommitted)"$'\n'
    block+="$STAGED"$'\n'$'\n'
  fi

  if [ -n "$UNSTAGED" ]; then
    block+="### Working Directory (modified)"$'\n'
    block+="$UNSTAGED"$'\n'$'\n'
  fi

  if [ -n "$UNTRACKED" ]; then
    block+="### Untracked (new files)"$'\n'
    block+="$UNTRACKED"$'\n'
    if [ "$UNTRACKED_COUNT" -gt "$MAX_FILES_PER_LAYER" ]; then
      block+="... and $((UNTRACKED_COUNT - MAX_FILES_PER_LAYER)) more files"$'\n'
    fi
    block+=$'\n'
  fi

  block+="<!-- /SESSION SYNC -->"

  echo "$block"
}

# --- Route changes to domain state files ---

# Collect all changed file paths across all layers
ALL_FILES=""

if [ -f "$MARKER_FILE" ] && [ -n "$COMMITS" ] && [ "$COMMITS" != "(initial sync - no prior baseline)" ] && [ "$COMMITS" != "(baseline SHA no longer exists - reset to current HEAD)" ]; then
  LAST_SHA=$(cat "$MARKER_FILE")
  if git cat-file -t "$LAST_SHA" > /dev/null 2>&1; then
    COMMIT_FILES=$(git diff --name-only "$LAST_SHA".."$CURRENT_SHA" 2>/dev/null)
    ALL_FILES+="$COMMIT_FILES"$'\n'
  fi
fi

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)
UNSTAGED_FILES=$(git diff --name-only 2>/dev/null)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null)

ALL_FILES+="$STAGED_FILES"$'\n'
ALL_FILES+="$UNSTAGED_FILES"$'\n'
ALL_FILES+="$UNTRACKED_FILES"

# Determine which domains are affected
declare -A AFFECTED_DOMAINS

while IFS= read -r file; do
  [ -z "$file" ] && continue

  matched=false
  for route in "${DOMAIN_ROUTES[@]}"; do
    pattern="${route%%:*}"
    agent="${route##*:}"

    # Check if file path matches pattern
    case "$file" in
      $pattern*|*/$pattern*|*$pattern)
        AFFECTED_DOMAINS["$agent"]=1
        matched=true
        ;;
    esac
  done
done <<< "$ALL_FILES"

# --- Append sync blocks ---

# Always append to chief-of-staff
if [ -f "$STATE_DIR/chief-of-staff.md" ]; then
  echo "" >> "$STATE_DIR/chief-of-staff.md"
  build_sync_block "all" >> "$STATE_DIR/chief-of-staff.md"
fi

# Append to affected domain state files
for agent in "${!AFFECTED_DOMAINS[@]}"; do
  state_file="$STATE_DIR/$agent.md"
  if [ -f "$state_file" ]; then
    echo "" >> "$state_file"
    build_sync_block "$agent" >> "$state_file"
  fi
done

# --- Update marker ---

echo "$CURRENT_SHA" > "$MARKER_FILE"
```

**Step 2: Make executable**

Run: `chmod +x scripts/session-sync.sh`

**Step 3: Commit**

```bash
git add scripts/session-sync.sh
git commit -m "feat: add session-sync hook script for automatic state updates"
```

---

### Task 2: Register the Stop hook in user settings

**Files:**
- Modify: `~/.claude/settings.json`

**Step 1: Add hooks configuration**

Add a `hooks` key to the existing settings.json:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/plugins/solo-founder-fleet/scripts/session-sync.sh"
          }
        ]
      }
    ]
  }
}
```

This merges with the existing `enabledPlugins` and other keys already present.

**Step 2: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))"`
Expected: No output (valid JSON)

---

### Task 3: Add cleanup instructions to Chief of Staff agent

**Files:**
- Modify: `agents/chief-of-staff.md`

**Step 1: Add SESSION SYNC cleanup section**

Insert after the existing STATE MANAGEMENT section (after line ~96), a new section:

```markdown
### Session Sync Cleanup

When reading state files at session start, look for `<!-- SESSION SYNC -->` blocks.
These are raw change summaries appended automatically by the session-sync hook.

For EACH sync block found:
1. Read the changes listed (commits, staged, unstaged, untracked files)
2. Update the relevant sections of the state file:
   - Add/update entries in the **Active Work** table
   - Update **Current Focus** if the changes suggest a shift
   - Add relevant items to **Context for Next Session**
3. Remove the raw `<!-- SESSION SYNC -->` ... `<!-- /SESSION SYNC -->` block after processing

Do this for your own state file AND for any subagent state files you read that contain
unprocessed sync blocks. Process oldest blocks first (by timestamp).

If a sync block mentions uncommitted or untracked files, note these prominently -
they represent in-progress work the previous session didn't finish.
```

**Step 2: Commit**

```bash
git add agents/chief-of-staff.md
git commit -m "feat: add session sync cleanup instructions to chief of staff"
```

---

### Task 4: Add .last-sync-sha to .gitignore

**Files:**
- Modify or create: `.gitignore` (in projects using the fleet, not in the plugin itself)
- Modify: `scripts/init-project-state.sh`

**Step 1: Update init-project-state.sh to create .gitignore entry**

Add to the end of `init-project-state.sh`, after the state files are created:

```bash
# Ensure .last-sync-sha is gitignored
GITIGNORE="$PROJECT_DIR/.gitignore"
if [ -f "$GITIGNORE" ]; then
  if ! grep -q ".claude/state/.last-sync-sha" "$GITIGNORE"; then
    echo "" >> "$GITIGNORE"
    echo "# Session sync marker (auto-generated)" >> "$GITIGNORE"
    echo ".claude/state/.last-sync-sha" >> "$GITIGNORE"
  fi
fi
```

**Step 2: Commit**

```bash
git add scripts/init-project-state.sh
git commit -m "feat: init script adds .last-sync-sha to .gitignore"
```

---

### Task 5: Update permissions in plugin settings

**Files:**
- Modify: `.claude/settings.local.json`

**Step 1: Add session-sync.sh permission**

Add to the `allow` array:

```json
"Bash(~/.claude/plugins/solo-founder-fleet/scripts/session-sync.sh:*)"
```

**Step 2: Commit**

```bash
git add .claude/settings.local.json
git commit -m "feat: add session-sync.sh to allowed bash commands"
```

---

### Task 6: Update documentation

**Files:**
- Modify: `docs/STATE_MANAGEMENT.md`

**Step 1: Add Session Sync section to STATE_MANAGEMENT.md**

Append a new section documenting the hook system, how sync blocks work, and what the cleanup process does.

**Step 2: Commit**

```bash
git add docs/STATE_MANAGEMENT.md
git commit -m "docs: add session sync hook documentation"
```

---

### Task 7: Sync updated agent to deployed location

**Step 1: Copy updated chief-of-staff.md**

Run: `~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh push`

**Step 2: Verify sync**

Run: `~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh status`
Expected: chief-of-staff shows IN SYNC
