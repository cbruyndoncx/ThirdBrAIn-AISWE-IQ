#!/opt/homebrew/bin/bash
# Session Sync Hook - Captures git changes and appends to agent state files
# Registered as a Claude Code Stop hook
# No LLM calls - pure bash/git

set -euo pipefail

# --- Configuration ---

# Domain routing: map file path patterns to agent state file names
DOMAIN_ROUTES=(
  "tests/:qa"
  "__tests__/:qa"
  ".test.:qa"
  ".spec.:qa"
  ".github/workflows/:devops"
  "Dockerfile:devops"
  "docker-compose:devops"
  "infrastructure/:devops"
  "deploy/:devops"
  "ci/:devops"
  "docs/:content"
  "public/:design"
  "assets/:design"
  ".css:design"
  ".scss:design"
  "src/:eng"
  "lib/:eng"
  "packages/:eng"
  ".ts:eng"
  ".tsx:eng"
  ".js:eng"
  ".jsx:eng"
  ".py:eng"
  ".go:eng"
  ".rs:eng"
  ".rb:eng"
)

MAX_FILES_PER_LAYER=50
MAX_SYNC_BLOCKS=10          # Keep only the last N sync blocks per state file
MAX_STATE_FILE_KB=50        # Hard limit: prune if state file exceeds this size (KB)

# --- Guard clauses ---

# Must be in a git repo
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

# Must have a HEAD (not an empty repo)
git rev-parse HEAD > /dev/null 2>&1 || exit 0

# Must have a .claude/state/ directory (project initialized)
STATE_DIR=".claude/state"
[ -d "$STATE_DIR" ] || exit 0

MARKER_FILE="$STATE_DIR/.last-sync-sha"
FINGERPRINT_FILE="$STATE_DIR/.last-sync-fingerprint"
CURRENT_SHA=$(git rev-parse HEAD)

# --- Collect changes ---

COMMITS=""
COMMIT_COUNT=0
STAGED=""
UNSTAGED=""
UNTRACKED=""
UNTRACKED_COUNT=0

# Layer 1: Commits since last sync
if [ -f "$MARKER_FILE" ]; then
  LAST_SHA=$(cat "$MARKER_FILE")
  # Verify the SHA still exists (could be gone after rebase)
  if git cat-file -t "$LAST_SHA" > /dev/null 2>&1; then
    if [ "$LAST_SHA" != "$CURRENT_SHA" ]; then
      COMMITS=$(git log --oneline "$LAST_SHA".."$CURRENT_SHA" 2>/dev/null | head -n "$MAX_FILES_PER_LAYER")
      COMMIT_COUNT=$(git log --oneline "$LAST_SHA".."$CURRENT_SHA" 2>/dev/null | wc -l | tr -d ' ')
    fi
  else
    # SHA gone (rebase, etc.) - just note current HEAD
    COMMITS="(baseline SHA no longer exists - reset to current HEAD)"
  fi
else
  # First run - no baseline, just record marker
  COMMITS="(initial sync - no prior baseline)"
fi

# Layer 2: Staged but uncommitted
STAGED=$(git diff --cached --stat 2>/dev/null | head -n "$MAX_FILES_PER_LAYER")

# Layer 3: Unstaged modifications
UNSTAGED=$(git diff --stat 2>/dev/null | head -n "$MAX_FILES_PER_LAYER")

# Layer 3b: Untracked files (exclude sync marker files)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | grep -v '^\.claude/state/\.last-sync-' | head -n "$MAX_FILES_PER_LAYER")
UNTRACKED_COUNT=$(git ls-files --others --exclude-standard 2>/dev/null | grep -v '^\.claude/state/\.last-sync-' | wc -l | tr -d ' ')

# If nothing changed, just update marker and exit
if [ -z "$COMMITS" ] && [ -z "$STAGED" ] && [ -z "$UNSTAGED" ] && [ -z "$UNTRACKED" ]; then
  echo "$CURRENT_SHA" > "$MARKER_FILE"
  exit 0
fi

# --- Dedup check ---
# Fingerprint uses stable content: commit log, file names (not stats which change as
# state files are appended to), and the current HEAD SHA to detect new commits.
STAGED_NAMES=$(git diff --cached --name-only 2>/dev/null || true)
UNSTAGED_NAMES=$(git diff --name-only 2>/dev/null || true)
CONTENT_FINGERPRINT=$(printf '%s\n%s\n%s\n%s\n%s' "$CURRENT_SHA" "$COMMITS" "$STAGED_NAMES" "$UNSTAGED_NAMES" "$UNTRACKED" | shasum -a 256 | cut -d' ' -f1)

if [ -f "$FINGERPRINT_FILE" ]; then
  LAST_FINGERPRINT=$(cat "$FINGERPRINT_FILE")
  if [ "$CONTENT_FINGERPRINT" = "$LAST_FINGERPRINT" ]; then
    # Identical changes already recorded - just update marker and exit
    echo "$CURRENT_SHA" > "$MARKER_FILE"
    exit 0
  fi
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
    block+="\`\`\`"$'\n'
    block+="$COMMITS"$'\n'
    block+="\`\`\`"$'\n'
    if [ "$COMMIT_COUNT" -gt "$MAX_FILES_PER_LAYER" ]; then
      block+="... and $((COMMIT_COUNT - MAX_FILES_PER_LAYER)) more commits"$'\n'
    fi
    block+=$'\n'
  fi

  if [ -n "$STAGED" ]; then
    block+="### Staged (uncommitted)"$'\n'
    block+="\`\`\`"$'\n'
    block+="$STAGED"$'\n'
    block+="\`\`\`"$'\n'$'\n'
  fi

  if [ -n "$UNSTAGED" ]; then
    block+="### Working Directory (modified)"$'\n'
    block+="\`\`\`"$'\n'
    block+="$UNSTAGED"$'\n'
    block+="\`\`\`"$'\n'$'\n'
  fi

  if [ -n "$UNTRACKED" ]; then
    block+="### Untracked (new files)"$'\n'
    block+="\`\`\`"$'\n'
    block+="$UNTRACKED"$'\n'
    block+="\`\`\`"$'\n'
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

if [ -f "$MARKER_FILE" ]; then
  LAST_SHA=$(cat "$MARKER_FILE")
  if git cat-file -t "$LAST_SHA" > /dev/null 2>&1 && [ "$LAST_SHA" != "$CURRENT_SHA" ]; then
    COMMIT_FILES=$(git diff --name-only "$LAST_SHA".."$CURRENT_SHA" 2>/dev/null || true)
    ALL_FILES+="${COMMIT_FILES}"$'\n'
  fi
fi

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || true)
UNSTAGED_FILES=$(git diff --name-only 2>/dev/null || true)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null | grep -v '^\.claude/state/\.last-sync-' || true)

ALL_FILES+="${STAGED_FILES}"$'\n'
ALL_FILES+="${UNSTAGED_FILES}"$'\n'
ALL_FILES+="${UNTRACKED_FILES}"

# Determine which domains are affected
declare -A AFFECTED_DOMAINS

while IFS= read -r file; do
  [ -z "$file" ] && continue

  for route in "${DOMAIN_ROUTES[@]}"; do
    pattern="${route%%:*}"
    agent="${route##*:}"

    case "$file" in
      *"$pattern"*)
        AFFECTED_DOMAINS["$agent"]=1
        ;;
    esac
  done
done <<< "$ALL_FILES"

# --- Prune old sync blocks from a state file ---
# Keeps only the last MAX_SYNC_BLOCKS blocks.
# If the file still exceeds MAX_STATE_FILE_KB after pruning by count,
# aggressively remove blocks until under the size limit.

prune_sync_blocks() {
  local file="$1"
  [ -f "$file" ] || return 0

  local file_size_kb
  file_size_kb=$(( $(wc -c < "$file" | tr -d ' ') / 1024 ))

  # Only prune if we have blocks to prune
  local block_count
  block_count=$(grep -c '<!-- SESSION SYNC -->' "$file" 2>/dev/null) || block_count=0

  if [ "$block_count" -le "$MAX_SYNC_BLOCKS" ] && [ "$file_size_kb" -le "$MAX_STATE_FILE_KB" ]; then
    return 0  # Within limits, nothing to do
  fi

  # Split file into: content before first sync block, and all sync blocks
  local base_content
  local first_block_line
  first_block_line=$(grep -n '<!-- SESSION SYNC -->' "$file" 2>/dev/null | head -1 | cut -d: -f1)

  if [ -z "$first_block_line" ]; then
    return 0  # No sync blocks found
  fi

  # Everything before the first sync block is the base state
  base_content=$(head -n "$((first_block_line - 1))" "$file")

  # Extract each sync block (from <!-- SESSION SYNC --> to <!-- /SESSION SYNC -->)
  local blocks=()
  local in_block=false
  local current_block=""

  while IFS= read -r line; do
    if [[ "$line" == *"<!-- SESSION SYNC -->"* ]]; then
      in_block=true
      current_block="$line"$'\n'
    elif [[ "$line" == *"<!-- /SESSION SYNC -->"* ]] && $in_block; then
      current_block+="$line"
      blocks+=("$current_block")
      current_block=""
      in_block=false
    elif $in_block; then
      current_block+="$line"$'\n'
    fi
  done < "$file"

  local total_blocks=${#blocks[@]}

  # Step 1: Keep only the last MAX_SYNC_BLOCKS
  local keep_from=0
  if [ "$total_blocks" -gt "$MAX_SYNC_BLOCKS" ]; then
    keep_from=$((total_blocks - MAX_SYNC_BLOCKS))
  fi

  # Step 2: If still over size, keep fewer blocks
  while [ "$keep_from" -lt "$total_blocks" ]; do
    local rebuilt="$base_content"
    for (( i=keep_from; i<total_blocks; i++ )); do
      rebuilt+=$'\n\n'"${blocks[$i]}"
    done
    local rebuilt_size=$(( ${#rebuilt} / 1024 ))
    if [ "$rebuilt_size" -le "$MAX_STATE_FILE_KB" ]; then
      break
    fi
    keep_from=$((keep_from + 1))
  done

  # Rebuild the file
  {
    echo "$base_content"
    for (( i=keep_from; i<total_blocks; i++ )); do
      echo ""
      echo "${blocks[$i]}"
    done
  } > "$file"

  local pruned=$((total_blocks - (total_blocks - keep_from)))
  if [ "$pruned" -gt 0 ]; then
    echo "session-sync: pruned $pruned old sync block(s) from $(basename "$file")" >&2
  fi
}

# --- Append sync blocks ---

# Always append to chief-of-staff
if [ -f "$STATE_DIR/chief-of-staff.md" ]; then
  prune_sync_blocks "$STATE_DIR/chief-of-staff.md"
  echo "" >> "$STATE_DIR/chief-of-staff.md"
  build_sync_block "all" >> "$STATE_DIR/chief-of-staff.md"
fi

# Append to affected domain state files
for agent in "${!AFFECTED_DOMAINS[@]}"; do
  state_file="$STATE_DIR/$agent.md"
  if [ -f "$state_file" ]; then
    prune_sync_blocks "$state_file"
    echo "" >> "$state_file"
    build_sync_block "$agent" >> "$state_file"
  fi
done

# --- Update marker and fingerprint ---

echo "$CURRENT_SHA" > "$MARKER_FILE"
echo "$CONTENT_FINGERPRINT" > "$FINGERPRINT_FILE"
