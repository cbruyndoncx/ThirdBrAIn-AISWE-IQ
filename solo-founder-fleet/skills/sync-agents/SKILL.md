---
name: sync-agents
description: "Check for drift between source repo and deployed agents, view diffs, and pull/push changes. Use when you need to sync agent definitions after making improvements. Triggers on: sync agents, check agent drift, pull agent changes, push agents."
---

# Agent Sync

Synchronize agent definitions between the source repository and deployed location.

---

## The Job

1. Check sync status between source and deployed agents
2. Show diffs for any changed files
3. Offer to pull changes from deployed back to source
4. Optionally commit the changes to git

**Paths:**
- Source: `~/.claude/plugins/solo-founder-fleet/agents/`
- Deployed: `~/.claude/agents/`

---

## Step 1: Check Status

Run the sync status check:

```bash
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh status
```

This shows:
- **IN SYNC** - Agent is identical in both locations
- **SOURCE NEWER** - Source repo has newer changes (push needed)
- **DEPLOYED NEWER** - Deployed location has newer changes (pull needed)
- **NOT DEPLOYED** - Agent exists in source but not deployed
- **DEPLOYED ONLY** - Agent exists in deployed but not source

---

## Step 2: Show Diffs

If there are differences, show the diffs:

```bash
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh diff
```

Or for a specific agent:

```bash
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh diff chief-of-staff.md
```

Present the diffs to the user in a readable format.

---

## Step 3: Pull Changes

If deployed agents have improvements to preserve:

```bash
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh pull
```

This will prompt for each changed file. Use `-f` to force without prompts.

---

## Step 4: Commit to Git (Optional)

After pulling, offer to commit the changes:

```bash
cd ~/.claude/plugins/solo-founder-fleet
git add agents/
git commit -m "Sync agent improvements from deployed"
```

---

## Common Workflows

### Weekly Sync Check
```
/sync-agents
```
Check status, review diffs, pull any improvements made while working in projects.

### After Editing Deployed Agent
If you made improvements to an agent in `~/.claude/agents/`:
1. Run `/sync-agents`
2. Review the diff
3. Pull the changes
4. Commit to preserve them

### After Updating Source Repo
If you updated agents in the plugin repo:
```bash
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh push
```
Then restart Claude Code.

---

## Output Format

Present results clearly:

```
Agent Sync Status

| Agent | Status |
|-------|--------|
| chief-of-staff.md | IN SYNC |
| engineering.md | DEPLOYED NEWER |
| content.md | IN SYNC |
...

engineering.md has changes in deployed. Would you like to:
1. View the diff
2. Pull the changes to source
3. Skip
```

---

## Checklist

Before finishing:

- [ ] Showed current sync status
- [ ] Displayed diffs for any changed files
- [ ] Offered to pull changes if deployed is newer
- [ ] Offered to commit if changes were pulled
