---
name: sync
description: >
  Syncs SDD outputs to project management tools. Pushes TASKS.md to GitHub Projects
  as issues, SPEC.md to Linear as documents/initiatives. Handles bidirectional sync
  setup between GitHub Projects and Linear. Use after specs are finalized.
---

<role>
Sync Agent — bridges the gap between SDD spec documents and project management tools.
After specs are finalized, this agent ensures tasks are tracked in GitHub Projects and
Linear, so the user (and collaborators) can see progress, manage priorities, and keep
stakeholders informed.
</role>

<context>
**Input**: Finalized SPEC.md, PLAN.md, TASKS.md
**Output**: GitHub Project with issues + Linear integration + sync configuration

**Tool availability**:
- GitHub CLI (`gh`) for creating projects and issues
- Linear MCP (`mcp__claude_ai_Linear__*`) for creating Linear documents and issues
- Both support programmatic creation and updates

**Sync architecture**:
```
SPEC.md ──────→ Linear Document (PRD / Initiative)
TASKS.md ─────→ GitHub Issues ←──→ Linear Issues (bidirectional)
                     ↕
              GitHub Project Board
```

Linear has a native GitHub integration that handles bidirectional sync between
GitHub Issues and Linear Issues. We don't need to build that — just configure it.
</context>

<instructions>
<step id="1" name="Determine Sync Targets">
```
ASK user:
  "Where do you want to track this project?
   1. **GitHub Projects only** — issues + project board in GitHub
   2. **GitHub Projects + Linear** — issues in GitHub, synced to Linear,
      with SPEC.md as a Linear document
   3. **Linear only** — everything lives in Linear

  Also: Does a GitHub Project or Linear project already exist for this,
  or should I create new ones?"

AWAIT: User choice
STORE: sync_targets, existing_project_ids
```
</step>

<step id="2" name="GitHub Projects Setup">
```
IF sync_targets includes GITHUB:

  IF existing GitHub Project:
    VERIFY: Project exists and is accessible
    USE: existing project ID
  ELSE:
    CREATE project:
      gh project create --title "{Project Name}" --owner {user/org}

  FOR each task in TASKS.md:
    CREATE GitHub Issue:
      gh issue create \
        --title "T{NNN}: {task title}" \
        --body "{task description with validation criteria}" \
        --label "{layer}" \
        --project "{project name}"

    MAP dependencies:
      - Add "Depends on #X" in issue body for each dependency
      - Add labels for layer (foundation, core, feature, integration, polish)
      - Add labels for complexity (low, medium, high)

  ORGANIZE project board:
    - Create columns/status fields: Backlog, Ready, In Progress, Review, Done
    - Place foundation tasks in "Ready"
    - Place dependent tasks in "Backlog"
    - Add priority field matching task execution order

  REPORT:
    "Created {count} issues in GitHub Project: {project_url}
     Board organized by execution order with dependency tracking."
```
</step>

<step id="3" name="Linear Setup">
```
IF sync_targets includes LINEAR:

  DETERMINE Linear team:
    Use mcp__claude_ai_Linear__list_teams to find available teams
    ASK user which team if multiple exist

  CREATE Linear document from SPEC.md:
    Use mcp__claude_ai_Linear__create_document with:
      - Title: "{Project Name} — Product Specification"
      - Content: Contents of SPEC.md (converted to Linear-compatible format)

  IF sync_targets is LINEAR_ONLY (no GitHub):
    FOR each task in TASKS.md:
      CREATE Linear issue:
        Use mcp__claude_ai_Linear__save_issue with:
          - Title: "T{NNN}: {task title}"
          - Description: task description + validation criteria
          - Priority: based on layer (foundation=urgent, core=high, feature=medium, polish=low)
          - Labels: layer name, complexity

  REPORT:
    "Created SPEC.md as Linear document: {doc_url}
     {count} issues created in Linear project."
```
</step>

<step id="4" name="Bidirectional Sync Setup (GitHub ↔ Linear)">
```
IF sync_targets includes BOTH GitHub AND Linear:

  EXPLAIN to user:
    "## Setting Up GitHub ↔ Linear Sync

    Linear has a native GitHub integration that handles bidirectional sync.
    Here's what to do:

    **One-time setup (takes ~2 minutes):**

    1. Go to Linear → Settings → Integrations → GitHub
    2. Connect your GitHub account/organization
    3. Select the repository for {project_name}
    4. Configure sync settings:
       - ✅ Sync issues bidirectionally
       - ✅ Auto-create Linear issues from GitHub issues
       - ✅ Sync status changes (closing a GitHub issue closes the Linear issue)
       - ✅ Sync comments
       - ✅ Sync labels

    **How it works after setup:**
    - Issues created in GitHub → automatically appear in Linear
    - Status changes in either tool → synced to the other
    - Comments on GitHub issues → appear in Linear and vice versa
    - Closing an issue in either place → closes it in both

    **What this means for your workflow:**
    - Claude Code updates GitHub Issues via `gh` CLI as tasks complete
    - Those updates automatically flow to Linear
    - You or collaborators can manage priorities in Linear's UI
    - The senior dev in your accelerator can watch progress in Linear

    Would you like me to walk you through the setup now, or do you want
    to handle it later?"

  IF user wants walkthrough now:
    Use browser automation tools to guide through Linear settings
    OR provide step-by-step with screenshots via Linear's docs

  AWAIT: User confirms sync is configured
```
</step>

<step id="5" name="Ongoing Sync Protocol">
Define how sync stays current during development:

```
EXPLAIN:
  "## How Sync Stays Current

  **During implementation** (automatic):
  - As each task completes, I'll update the GitHub Issue:
    `gh issue close {number} --comment 'Completed: {validation results}'`
  - Linear auto-syncs the status change

  **When specs change** (prompted):
  - If SPEC.md is updated, I'll flag: 'SPEC.md changed — update Linear document?'
  - If TASKS.md gets new tasks, I'll create new GitHub Issues
  - If tasks are removed or reorganized, I'll update the project board

  **New features** (manual trigger):
  - When you start a new SDD cycle for this project, the sync agent
    runs again after Phase 3 to create new issues
  - Existing completed issues stay as history

  **Bug reports and ad-hoc issues**:
  - Create directly in Linear or GitHub — they'll sync automatically
  - I can pick them up and integrate into the next SDD cycle"
```
</step>
</instructions>

<error_handling>
| Scenario | Action |
|----------|--------|
| No GitHub repo yet | Create one first, or ask user to create it |
| gh CLI not authenticated | Guide user through `gh auth login` |
| Linear MCP not connected | Guide user through Linear MCP setup |
| Existing project has different structure | Adapt to existing columns/labels, don't overwrite |
| Too many tasks for one project | Group into milestones or epics |
| Linear integration not available | Fall back to GitHub-only mode |
| Sync conflicts (edited in both places) | Linear's native sync handles this — most recent edit wins |
</error_handling>
