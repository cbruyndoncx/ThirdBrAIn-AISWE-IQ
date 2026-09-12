# Context Planning System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-purple)](https://claude.com/claude-code)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)

Personal context management system with task aggregation and daily/weekly planning workflows powered by Claude Code skills.

## Overview

This system helps manage multiple projects through:
- **Task Aggregation**: Scan Speckit-format tasks across repositories
- **Daily Planning**: Generate focused daily plans with WIP limits
- **Weekly Reviews**: Track progress toward monthly goals
- **Automated Workflows**: Git integration for seamless tracking

## Features

### Task Management
✅ **Multi-format support**: `.specify/` (Speckit) and `specs/` directories
✅ **Priority detection**: `P1/P2/P3` and `[P]` (Speckit) formats
✅ **Recursive scanning**: Finds tasks at any depth
✅ **Robust error handling** and logging
✅ **CLI with verbose mode**

### Project Context
✅ **Automatic analysis**: Extracts tech stack, structure, dependencies
✅ **Auto-update on changes**: Git hooks for continuous sync
✅ **Multi-language support**: Python, JavaScript/TypeScript, Rust
✅ **Comprehensive reports**: Markdown + JSON output

### Planning
✅ **Configurable WIP limits**
✅ **Priority-based task selection**
✅ **Multi-project balancing**
✅ **Git automation**
✅ **Template-driven reports**

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Real-AI-Engineering/context-planning-system.git
cd context-planning-system
```

### 2. Configure Your Planning

Edit `BaseContext.yaml`:

```yaml
wip_limits:
  daily_tasks_max: 5
  weekly_projects_max: 3

goals:
  month:
    - "Your monthly goal 1"
    - "Your monthly goal 2"
```

### 3. Set Up Projects

Create your project structure (flexible - choose what works for you):

```bash
# Option 1: Simple structure
projects/
├── my-app/
│   └── specs/tasks.md
└── website/
    └── specs/tasks.md

# Option 2: With organization (for multiple clients/orgs)
projects/
├── client-a/
│   └── project-x/
│       └── specs/tasks.md
└── personal/
    └── hobby-project/
        └── specs/tasks.md
```

See `projects/README.md` for more examples and best practices.

### 4. Install Auto-Update Hooks

```bash
# Enable automatic project context updates
bash scripts/install_hooks.sh
```

This installs git hooks that automatically update project contexts when you commit, pull, or switch branches.

### 5. Use the Skills

```bash
# Scan tasks across projects
/ctx.scan

# Analyze project structure and dependencies
/ctx.analyze my-org/my-project

# Generate daily plan
/ctx.daily

# End of day update
/ctx.eod

# Weekly review
/ctx.weekly
```

## Project Structure

```
context-planning-system/
├── skills/              # Claude Code skills
│   ├── ctx-collector/   # Task scanning and aggregation
│   └── ctx-planning/    # Daily/weekly planning
├── state/               # Generated state files (gitignored)
│   ├── backlog.yaml     # Aggregated tasks
│   └── carryover.yaml   # Carryover tasks
├── reports/             # Generated reports (gitignored)
│   ├── daily/           # Daily plans
│   └── weekly/          # Weekly reviews
├── templates/           # Report templates
├── scripts/             # Automation scripts
├── projects/            # Your projects - flexible structure!
│   ├── README.md        # Structure examples and best practices
│   └── (your projects)  # Add any structure you want
└── BaseContext.yaml     # Configuration
```

**Your Projects:** The `projects/` directory is flexible - organize however you like!
See `projects/README.md` for structure options and examples.

## Skills

### ctx-collector

Scans Speckit task files across projects and generates unified backlog.

**Features:**
- Recursive task file discovery
- Priority and ID extraction (`P1`, `P2`, `P3`, `T###`)
- Robust error handling
- CLI with verbose mode

**Usage:**
```bash
# Via Claude Code
/ctx.scan

# Direct script execution
python3 .claude/skills/ctx-collector/scripts/scan_tasks.py --verbose
```

**Task Format:**
```markdown
## Feature Name

- [ ] T101 P1 Implement authentication
- [ ] T102 P2 Add user profile page
- [X] T103 P1 Fix login bug
```

### ctx-planning

Generates daily and weekly planning reports with WIP limits and priority rules.

**Features:**
- Daily plan generation with WIP limits
- End-of-day progress tracking
- Weekly reviews with goal alignment
- Monthly retrospectives
- Configurable priorities and tie-breakers

**Workflows:**
- `/ctx.daily` - Generate today's plan
- `/ctx.eod` - Close out the day
- `/ctx.weekly` - Weekly review
- `/ctx.monthly` - Monthly retrospective
- `/ctx.update` - Update configuration

## Configuration

### BaseContext.yaml

Complete configuration reference:

```yaml
version: 0.2
timezone: "UTC"

cadence:
  weekly_review_day: "Monday"
  monthly_cycle: "next-30-days"

wip_limits:
  daily_tasks_max: 5            # Max tasks per day
  weekly_projects_max: 3        # Max concurrent projects

prioritization:
  order: ["P1", "P2", "P3"]     # High to low priority
  tie_breakers:
    - "unblocker_first"         # Tasks that unblock others
    - "short_first"             # Quick wins

goals:
  month:
    - "Launch MVP for project X"
    - "Complete security audit"
    - "Implement CI/CD pipeline"

rules:
  include_open_tasks_from:
    - "tasks.md"
    - "checklists/*.md"
  task_id_pattern: "T\\d+"
  priority_patterns: ["P1", "P2", "P3"]
```

See `.claude/skills/ctx-planning/references/configuration.md` for detailed documentation.

## Installation Options

### Option 1: Use from Repository (Recommended)

Skills and slash commands are already in the repository:

```bash
cd context-planning-system

# Skills are available when working in this directory
/ctx.scan
/ctx.daily
```

**Note:** Slash commands (`.claude/commands/*.md`) work automatically when in the repository directory.

### Option 2: Install Globally

Copy skills to your global Claude directory to use from anywhere:

```bash
# Copy skills
cp -r .claude/skills/ctx-collector ~/.claude/skills/
cp -r .claude/skills/ctx-planning ~/.claude/skills/

# Copy slash commands (optional)
mkdir -p ~/.claude/commands
cp .claude/commands/ctx.*.md ~/.claude/commands/
```

**Benefits:**
- ✅ Use `/ctx.*` commands from any directory
- ✅ Skills available in all Claude Code sessions
- ✅ No need to cd into repository

**Note:** After copying, update skills manually when repository changes, or use symlinks:

```bash
# Alternative: symlinks (auto-updates with repository)
ln -s $(pwd)/.claude/skills/ctx-collector ~/.claude/.claude/skills/ctx-collector
ln -s $(pwd)/.claude/skills/ctx-planning ~/.claude/.claude/skills/ctx-planning
```

## Documentation

### Core Documentation
- **[SKILLS_IMPROVEMENTS.md](SKILLS_IMPROVEMENTS.md)**: Complete improvement summary
- **[.claude/skills/ctx-collector/SKILL.md](.claude/skills/ctx-collector/SKILL.md)**: Task collector documentation
- **[.claude/skills/ctx-planning/SKILL.md](.claude/skills/ctx-planning/SKILL.md)**: Planning skill documentation
- **[.claude/skills/ctx-planning/references/workflows.md](.claude/skills/ctx-planning/references/workflows.md)**: Detailed algorithms
- **[.claude/skills/ctx-planning/references/configuration.md](.claude/skills/ctx-planning/references/configuration.md)**: Configuration reference

### Advanced Features
- **[docs/AUTO_UPDATE.md](docs/AUTO_UPDATE.md)**: Automatic project context updates with git hooks
- **[docs/PROJECT_CONTEXT_INTEGRATION.md](docs/PROJECT_CONTEXT_INTEGRATION.md)**: Integrating project context into daily planning

### Templates & Examples
- **[templates/daily-with-context.md](templates/daily-with-context.md)**: Enhanced daily plan template with project context
- **[examples/daily-plan-example.md](examples/daily-plan-example.md)**: Example daily plan with full project integration

## Workflows

### Daily Planning Flow
1. Load configuration from `BaseContext.yaml`
2. Load backlog and carryover state
3. Select tasks by priority with WIP limits
4. Generate `reports/daily/YYYY-MM-DD.md`
5. Commit and push changes (optional)

### End-of-Day Flow
1. Update daily report with progress
2. Document decisions and insights
3. Generate carryover for tomorrow
4. Commit and push changes (optional)

### Weekly Review Flow
1. Aggregate achievements from daily reports
2. Assess progress toward monthly goals
3. Generate `reports/weekly/YYYY-WW.md`
4. Commit and push changes (optional)

## Task Format Reference

### Checkbox Syntax

```markdown
- [ ] T101 P1 Task description (open task)
- [X] T102 P2 Completed task (done)
```

### Priority Levels

- **P1**: High priority (critical, blockers, urgent)
- **P2**: Medium priority (normal development)
- **P3**: Low priority (nice-to-have, tech debt)

### Task IDs

- Pattern: `T` followed by digits (e.g., `T1`, `T100`, `T999`)
- Optional but recommended for tracking
- Auto-generated hash if not provided

## Requirements

- Python 3.7+
- Claude Code
- Git (optional, for automation)
- PyYAML (optional, JSON fallback available)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `/ctx.scan` and `/ctx.daily`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Inspired by personal productivity systems and GTD methodology
- Designed for Speckit-format task management

## Support

- **Issues**: [GitHub Issues](https://github.com/Real-AI-Engineering/context-planning-system/issues)
- **Documentation**: See `skills/*/SKILL.md` files
- **Examples**: Check `templates/` directory

---

**Status:** Active Development
**Version:** 0.2
**Last Updated:** 2025-10-22
