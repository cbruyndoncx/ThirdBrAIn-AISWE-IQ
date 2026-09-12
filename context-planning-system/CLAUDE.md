# Context Planning System - Claude Code Instructions

**Project:** Context Planning (Project Memory System)
**Skills:** `/ctx.*` commands
**Mode:** Read from local `projects/<org>/<repo>` (no-clone mode)

## Commands

- `/ctx.scan` — Scan tasks from `projects/*/*/specs/**/tasks.md` and generate `state/backlog.yaml`
- `/ctx.daily` — Generate today's plan (considering carryover/WIP/priorities) → `reports/daily/YYYY-MM-DD.md`
- `/ctx.eod` — Close the day: mark completed tasks, generate carryover → `state/carryover.yaml`
- `/ctx.weekly` — Weekly review from daily logs and backlog → `reports/weekly/YYYY-WW.md`
- `/ctx.monthly` — Monthly overview draft (aggregates weekly reports + monthly goals)
- `/ctx.update` — Update `BaseContext.yaml` (goals/limits) with plan recalculation

## Skills

- `skills/ctx-collector/SKILL.md` — Parse Speckit tasks into YAML backlog
- `skills/ctx-planning/SKILL.md` — Generate daily/weekly reports with commit/push

## Configuration

Edit `BaseContext.yaml` to customize:
- WIP limits (daily tasks max, weekly projects max)
- Prioritization rules and tie-breakers
- Monthly goals
- Task scanning rules

## Task Format

Tasks follow Speckit checkbox format:

```markdown
## Feature Name

- [ ] T101 P1 Implement authentication
- [ ] T102 P2 Add user profile page
- [X] T103 P1 Fix login bug (completed)
```

**Patterns:**
- Task ID: `T\d+` (e.g., T101, T250)
- Priority: `P1`, `P2`, `P3` (can be in task line or heading)
- Status: `[ ]` = open, `[X]` or `[x]` = done

## Project Structure

The system supports flexible project organization:

```
projects/
├── my-project/
│   └── specs/
│       └── tasks.md
├── another-project/
│   └── specs/
│       └── tasks.md
└── (any structure you prefer)
```

**Note:** The scanner recursively finds `tasks.md` files at any depth.
See `projects/README.md` for structure options.

## Important Notes

- This context is **relevant** when working with task planning and context management
- Skills use local files only (no network access except git push)
- Generated files (`state/`, `reports/`) are gitignored by default
- The system is designed for personal productivity and multi-project tracking
