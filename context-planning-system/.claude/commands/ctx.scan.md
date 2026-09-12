---
description: Scan all projects and aggregate tasks into unified backlog
---

# Scan Tasks Across All Projects

Run the task scanner to collect all open and completed tasks from all projects into a unified backlog.

## What this does

1. Recursively scans `projects/` directory
2. Finds tasks in both `specs/tasks.md` and `.specify/` formats
3. Extracts task metadata (ID, priority, status, scope)
4. Generates `state/backlog.yaml` with all tasks

## Instructions

Execute the task scanner script:

```bash
python3 skills/ctx-collector/scripts/scan_tasks.py --verbose
```

**Expected output:**
- Summary: "Scanned X files, found Y tasks (Z open, W done)"
- Updated: `state/backlog.yaml`

Report the summary statistics to the user.

## Multi-format Support

The scanner supports:
- **Context-planning format:** `specs/tasks.md`
- **Speckit format:** `.specify/` directories
- **Priority formats:** `P1/P2/P3` and `[P]` (Speckit → P1)
- **Task IDs:** `T###` pattern or auto-generated hash

## After Scanning

The backlog is ready for planning commands:
- `/ctx.daily` - Generate today's plan
- `/ctx.weekly` - Generate weekly review
