---
description: Close out the day and create carryover for tomorrow
---

# End of Day - Close Today

Update today's daily plan with end-of-day summary and create carryover for tomorrow.

## What this does

1. Updates today's daily plan with:
   - Completed tasks (mark checkboxes)
   - Notes from the day
   - Decisions and insights
   - Blockers encountered
2. Creates `state/carryover.yaml` with tasks for tomorrow
3. Commits and pushes changes (optional)

## Instructions

1. **Update today's daily plan:**
   ```bash
   # Open today's plan
   TODAY=$(date +%Y-%m-%d)
   vi reports/daily/$TODAY.md
   ```

   Fill in:
   - Mark completed tasks: `- [X] Completed`
   - Add notes in ## Notes section
   - Fill ## End of Day Summary:
     - **Сделано:** List completed tasks
     - **Решения/инсайты:** Key decisions made
     - **Перенос на завтра:** Tasks to carry over

2. **Create carryover file:**
   ```bash
   # Edit carryover.yaml
   vi state/carryover.yaml
   ```

   Format:
   ```yaml
   date: "YYYY-MM-DD"
   generated_at: "YYYY-MM-DDT23:59:00"
   carryover:
     - uid: "project#TXXX"
       project: "project-name"
       organization: "org-name"
       file: "path/to/tasks.md"
       id: "TXXX"
       title: "Task description"
       priority: "P1"
       status: "open"
       scope:
         section: "Section"
         subsection: "Subsection"
       notes: "Any notes"

   notes: |
     Summary of what happened today
   ```

3. **Commit changes:**
   ```bash
   git add reports/daily/$TODAY.md state/carryover.yaml
   git commit -m "eod: close $TODAY with summary and carryover"
   git push
   ```

## Example

See the completed `reports/daily/2025-10-22.md` for a real example.

## Tips

- Be honest about what was completed
- Document decisions for future reference
- Carry over incomplete tasks, not new ones
- Add context to carryover notes
