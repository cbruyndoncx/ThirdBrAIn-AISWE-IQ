---
description: Generate today's daily plan with WIP limits
---

# Generate Daily Plan

Create a daily plan for today by selecting tasks from the backlog based on priorities, WIP limits, and carryover from yesterday.

## What this does

1. Loads configuration from `BaseContext.yaml`
2. Loads tasks from `state/backlog.yaml`
3. Loads carryover from `state/carryover.yaml`
4. Selects tasks based on:
   - Priority (P1 > P2 > P3)
   - WIP limits (daily_tasks_max, weekly_projects_max)
   - Tie-breaker rules (unblocker_first, short_first)
5. Generates `reports/daily/YYYY-MM-DD.md`

## Instructions

Since we don't have a Python script for this yet, manually create today's plan:

1. **Read carryover:**
   ```bash
   cat state/carryover.yaml
   ```

2. **Read backlog (filter P1 tasks):**
   ```bash
   grep -A 10 "priority: \"P1\"" state/backlog.yaml | head -50
   ```

3. **Check BaseContext limits:**
   ```bash
   cat BaseContext.yaml | grep -A 5 wip_limits
   ```

4. **Create daily plan:**
   - Use template: `templates/daily-with-context.md`
   - Include carryover tasks first
   - Add P1 tasks from backlog
   - Respect WIP limits (5 tasks max, 3 projects max)
   - Add project context links for each task
   - Save to: `reports/daily/$(date +%Y-%m-%d).md`

5. **Enhance with project context:**
   - For each task, read `reports/projects/<project>.md`
   - Add project overview, risks, TODOs
   - Link to project context report

## Manual Template

```markdown
# Daily Plan - YYYY-MM-DD

**Configuration:**
- Max tasks: 5
- Max projects: 3
- Tasks selected: X
- Projects involved: Y

## Monthly Goals

(from BaseContext.yaml)

## Today's Tasks

### 1. [P1] T### - project-name

**Task:** Task description

**Project Context:** [project-name analysis](../projects/project-name.md)

**File:** `path/to/tasks.md`

**Scope:** Section → Subsection

- [ ] Completed

(repeat for each task)

## Notes

## End of Day Summary
```

## Example

See `examples/daily-plan-example.md` for a complete example with project context integration.
