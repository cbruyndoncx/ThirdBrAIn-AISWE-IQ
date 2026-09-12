---
description: Generate weekly review and progress report
---

# Weekly Review

Generate a weekly review by aggregating daily reports and assessing progress toward monthly goals.

## What this does

1. Aggregates achievements from daily reports (Mon-Sun)
2. Calculates metrics (tasks completed, projects touched)
3. Assesses progress toward monthly goals
4. Identifies blockers and patterns
5. Generates `reports/weekly/YYYY-WW.md`

## Instructions

Since we don't have a Python script yet, manually create the weekly review:

1. **Find this week's daily reports:**
   ```bash
   WEEK=$(date +%Y-%W)
   ls -la reports/daily/ | grep $(date +%Y-%m) | tail -7
   ```

2. **Aggregate completed tasks:**
   - Read each daily report's "End of Day Summary"
   - Collect all completed tasks
   - Group by project

3. **Calculate metrics:**
   - Total tasks completed
   - Projects worked on
   - Completion rate vs planned

4. **Review monthly goals:**
   ```bash
   cat BaseContext.yaml | grep -A 10 "goals:"
   ```

5. **Create weekly report:**
   Save to: `reports/weekly/YYYY-WW.md`

## Template

```markdown
# Weekly Review - Week YYYY-WW

**Period:** YYYY-MM-DD to YYYY-MM-DD

## Summary

- **Tasks Completed:** X
- **Projects Involved:** Y
- **Days Worked:** Z

## Achievements

### Project A
- Task 1
- Task 2

### Project B
- Task 3

## Progress Toward Monthly Goals

### Goal 1: [Goal text]
**Status:** [On track / Behind / Ahead]
**Progress:** [Description]

## Blockers & Challenges

- Blocker 1
- Blocker 2

## Insights & Decisions

- Key insight 1
- Decision made

## Plan for Next Week

- Focus area 1
- Focus area 2
```

## Review Cadence

Run this every Monday morning to review the previous week.
