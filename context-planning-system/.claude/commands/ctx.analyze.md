---
description: Analyze a specific project and generate context report
---

# Analyze Project Context

Analyze a specific project to extract tech stack, structure, dependencies, and generate comprehensive context reports.

## Usage

```
/ctx.analyze <org/project>
```

**Example:**
```
/ctx.analyze forgequant/nt-playground
```

## What this does

1. Analyzes project structure and files
2. Extracts:
   - Overview (from README/pyproject.toml)
   - Tech stack (languages, frameworks, dependencies)
   - Directory structure
   - Entry points and CLI commands
   - Spec files (Speckit + context-planning)
   - Test framework and coverage
   - Documentation files
3. Generates reports:
   - `reports/projects/<project>.md` (human-readable)
   - `reports/projects/<project>.json` (machine-readable)
4. Updates `reports/projects/INDEX.md`

## Instructions

Execute the project analyzer:

```bash
python3 skills/ctx-collector/scripts/analyze_project.py \
  projects/${1} \
  --output reports/projects/${2}.md
```

Where:
- `${1}` = full path (e.g., `forgequant/nt-playground`)
- `${2}` = project name only (e.g., `nt-playground`)

**Expected output:**
- Generated report with project overview, tech stack, structure
- Both MD and JSON files created
- INDEX.md updated

Show the user a summary of the project analysis.

## Auto-Update

This analysis is automatically run by git hooks when projects change.
See `docs/AUTO_UPDATE.md` for details.
