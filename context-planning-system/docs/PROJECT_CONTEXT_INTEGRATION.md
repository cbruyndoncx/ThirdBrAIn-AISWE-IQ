# Project Context Integration

How to integrate project context analysis into your daily planning workflow.

## Overview

The context planning system can automatically analyze your projects and integrate that knowledge into daily plans, making planning decisions more informed by understanding:

- **Tech stack and dependencies** - Know what tools and libraries are involved
- **Project structure** - Understand complexity and organization
- **Entry points and CLI commands** - Quick reference for how to work with the project
- **Current state** - Open tasks, test coverage, documentation status
- **Risks** - Missing tests, complex dependencies, external requirements

## Benefits

### For AI Assistants (ChatGPT, Claude, etc.)

When an AI reads your daily plan with project context:
- ✅ **Better task prioritization** - Understands project complexity and dependencies
- ✅ **Risk awareness** - Knows about missing tests, external dependencies
- ✅ **Faster onboarding** - No need to explore codebase from scratch
- ✅ **Informed decisions** - Can suggest time estimates based on tech stack
- ✅ **Architecture awareness** - Understands how pieces fit together

### For You

- ✅ **Quick project refresh** - See overview without diving into code
- ✅ **Risk visibility** - Surface issues before starting work
- ✅ **Better planning** - Account for complexity and dependencies
- ✅ **Documentation** - Always have up-to-date project summaries

## How It Works

### 1. Project Analysis

When you commit changes, git hooks automatically run `analyze_project.py`:

```bash
# Triggered automatically by git hooks
# Or run manually:
python3 .claude/skills/ctx-collector/scripts/analyze_project.py \
  projects/my-org/my-project \
  --output reports/projects/my-project.md
```

This generates:
- `reports/projects/my-project.md` - Human-readable report
- `reports/projects/my-project.json` - Machine-readable data
- `reports/projects/INDEX.md` - Catalog of all projects

### 2. Daily Plan Generation

When generating daily plans with `/ctx.daily`, you can enhance task descriptions:

**Basic task (without context):**
```markdown
### 1. [P1] T042 - my-project

**Task:** Implement feature X
**File:** projects/my-project/specs/tasks.md
- [ ] Completed
```

**Enhanced task (with context):**
```markdown
### 1. [P1] T042 - my-project

**Task:** Implement feature X

**Project Context:** [my-project analysis](../projects/my-project.md)

**File:** projects/my-project/specs/tasks.md

**Project Overview:**
- **Type:** REST API service
- **Tech Stack:** Python 3.11+, FastAPI, PostgreSQL, Redis
- **Key Features:** Authentication, rate limiting, caching
- **CLI Commands:** `/api.start`, `/api.test`, `/api.deploy`
- **Current State:** 12 open tasks, 85% test coverage

**Risks & Considerations:**
- Database migration required (check schema compatibility)
- Redis dependency (ensure running locally)
- Authentication changes may affect existing clients

**TODO Before Starting:**
- [ ] Review existing authentication implementation
- [ ] Check database schema in migrations/
- [ ] Verify Redis is running (docker-compose up redis)
- [ ] Read API documentation in docs/api.md

- [ ] Completed
```

### 3. Manual Enhancement

For tasks not yet in specs (like new initiatives), manually add context:

```markdown
### 1. [P1] NEW - my-project

**Task:** Create new feature (not in spec yet)

**Project Context:** [my-project analysis](../projects/my-project.md)

**File:** projects/my-project/specs/*/tasks.md (to be created)

**Project Overview:**
- **Type:** [Brief description]
- **Tech Stack:** [Languages, frameworks]
- **Key Features:** [Main capabilities]
- **Current State:** [Open tasks, test coverage, etc.]

**Risks & Considerations:**
- [Risk 1]
- [Risk 2]

**TODO Before Starting:**
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

- [ ] Completed
```

## Template Usage

### Using `daily-with-context.md` Template

The enhanced template at `templates/daily-with-context.md` includes placeholders for:

```handlebars
**Project Context:** [{{project}} analysis](../projects/{{project}}.md)

{{#if project_overview}}
**Project Overview:**
- **Type:** {{project_overview.type}}
- **Tech Stack:** {{project_overview.stack}}
...
{{/if}}
```

### Populating from JSON Reports

You can programmatically populate these fields from `reports/projects/*.json`:

```python
import json
from pathlib import Path

def load_project_context(project_name):
    """Load project context from JSON report."""
    json_path = Path(f"reports/projects/{project_name}.json")
    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    return None

# Usage in daily plan generation
context = load_project_context("my-project")
if context:
    overview = {
        "type": context["overview"]["description"],
        "stack": ", ".join(context["stack"]["languages"] + context["stack"]["frameworks"]),
        "state": f"{context['specs']['open_tasks_count']} open tasks"
    }
```

## Best Practices

### 1. Keep Project READMEs Updated

The analyzer extracts overview from `README.md` and `pyproject.toml`:

```markdown
# My Project

Brief description of what this project does.

## Features
- Feature 1
- Feature 2

## Quick Start
...
```

Better READMEs = Better context extraction

### 2. Link Tasks to Context

Always link daily plan tasks to project reports:

```markdown
**Project Context:** [project-name analysis](../projects/project-name.md)
```

This allows AI assistants to follow the link and get full context.

### 3. Surface Risks Early

Add a "Risks & Considerations" section for complex tasks:

```markdown
**Risks & Considerations:**
- No test coverage - add tests before implementation
- External API dependency - check rate limits
- Database migration - backup before running
```

### 4. Create TODOs for Unknowns

If you need to investigate before starting:

```markdown
**TODO Before Starting:**
- [ ] Review existing implementation in src/
- [ ] Check for similar patterns in codebase
- [ ] Verify dependencies are installed
```

### 5. Update Context After Major Changes

After significant project changes, manually trigger analysis:

```bash
bash scripts/update_project_contexts.sh manual
```

Or commit changes (git hooks will run automatically).

## Example Workflow

### Morning Planning

1. Run `/ctx.daily` to generate today's plan
2. For each task, check project context link
3. Review risks and TODOs
4. Make informed decisions about:
   - Task ordering (do simple tasks first? or unblock others?)
   - Time allocation (complex projects need more time)
   - Prerequisites (install deps, start services, etc.)

### During Work

1. Click project context link when starting a task
2. Review tech stack, structure, entry points
3. Check current state (open tasks, test coverage)
4. Use CLI commands from context for quick actions

### End of Day

1. Run `/ctx.eod` to close out the day
2. Update task completion status
3. Document any new risks discovered
4. Add notes for tomorrow

## Integration with AI Assistants

### ChatGPT Example

```markdown
User: "What should I work on today?"

ChatGPT reads:
- reports/daily/2025-10-22.md (daily plan)
- reports/projects/my-project.md (project context)
- BaseContext.yaml (goals, WIP limits)

ChatGPT responds:
"I recommend starting with task #2 (implement caching) because:
- It's P1 priority
- Project has Redis already set up (no new dependencies)
- 85% test coverage means you can add tests easily
- It unblocks task #3 (API optimization)

Before starting:
1. Check Redis is running: docker ps
2. Review existing cache implementation in src/cache/
3. Consider adding integration tests for cache invalidation"
```

### Claude Code Example

When working in Claude Code with project context:

```bash
# Claude can read project context automatically
/ctx.analyze my-project

# Then work with full context
"I see this is a FastAPI project with PostgreSQL. Let me check
the current database schema before implementing this feature..."
```

## Troubleshooting

### Context Not Updating

```bash
# Check git hooks are installed
ls -la .git/hooks/post-*

# Reinstall if needed
bash scripts/install_hooks.sh

# Manual update
bash scripts/update_project_contexts.sh manual
```

### Missing Project Context

```bash
# Analyze specific project
python3 .claude/skills/ctx-collector/scripts/analyze_project.py \
  projects/my-org/my-project \
  --output reports/projects/my-project.md
```

### Links Broken in Daily Plans

Check relative path is correct:
```markdown
# From: reports/daily/2025-10-22.md
# To:   reports/projects/my-project.md
# Link: ../projects/my-project.md ✅
```

## Further Reading

- [AUTO_UPDATE.md](AUTO_UPDATE.md) - Automatic project context updates
- [.claude/skills/ctx-collector/SKILL.md](../.claude/skills/ctx-collector/SKILL.md) - Task and project scanning
- [.claude/skills/ctx-planning/SKILL.md](../.claude/skills/ctx-planning/SKILL.md) - Planning workflows
- [README.md](../README.md) - System overview

---

**Pro Tip:** The better your project context, the better AI assistants can help you plan and work. Keep READMEs updated and specs organized!
