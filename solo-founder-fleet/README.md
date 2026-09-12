# Solo Founder Fleet

An executive agent fleet for solo founders with persistent state management across sessions and projects.

## Quick Install

```bash
# Clone and install agents
git clone https://github.com/justuseapen/solo-founder-fleet ~/.claude/plugins/solo-founder-fleet
cp ~/.claude/plugins/solo-founder-fleet/agents/*.md ~/.claude/agents/

# Verify installation (should show 10 agents)
ls ~/.claude/agents/*.md | wc -l
```

## Architecture

```
                    ┌─────────────────────┐
                    │  Chief of Staff     │
                    │  (opus, cyan)       │
                    │  Orchestration      │
                    └─────────┬───────────┘
                              │
    ┌─────────┬───────┬───────┼───────┬─────────┬─────────┐
    ▼         ▼       ▼       ▼       ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌─────────┐ ┌───────┐
│ Eng   │ │Product│ │Design │ │Market │ │ Sales   │ │Content│
│ blue  │ │ green │ │magenta│ │yellow │ │ yellow  │ │ green │
└───────┘ └───────┘ └───────┘ └───────┘ └─────────┘ └───────┘
```

## Agents

| Agent | Model | Color | Purpose |
|-------|-------|-------|---------|
| **chief-of-staff** | opus | cyan | Daily planning, cross-domain coordination, priority management, delegation |
| **engineering** | sonnet | blue | Architecture, debugging, tech debt, code quality, implementation |
| **product** | sonnet | green | Feature prioritization, user research, specs, roadmap |
| **design** | sonnet | magenta | UX/UI, design systems, accessibility, wireframes |
| **marketing** | sonnet | yellow | Positioning, channels, campaigns, growth experiments |
| **sales** | sonnet | yellow | Pipeline, lead qualification, outreach, deal strategy |
| **content** | sonnet | green | Blog posts, social media, email sequences, documentation |
| **custdev** | sonnet | magenta | Persona research, prospect finding, daily outreach, customer interviews |
| **qa** | sonnet | red | Testing, bug tracking, test automation, release validation |
| **devops** | sonnet | blue | Infrastructure, deployments, CI/CD, monitoring, incident response |

## Installation

Agents are installed to `~/.claude/agents/` for user-level availability across all projects.

```bash
# Copy agents to user directory (already done)
cp ~/.claude/plugins/solo-founder-fleet/agents/*.md ~/.claude/agents/
```

## Project State Setup

Initialize state files for a new project:

```bash
~/.claude/plugins/solo-founder-fleet/scripts/init-project-state.sh /path/to/project
```

This creates `.claude/state/` directory with state files for each agent:
- `chief-of-staff.md`
- `eng.md`
- `product.md`
- `design.md`
- `marketing.md`
- `sales.md`
- `content.md`
- `custdev.md`
- `qa.md`
- `devops.md`

## Usage

### Invoke agents naturally:

```
What should I focus on today?          → Chief of Staff
Fix the login bug                      → Engineering
Prioritize features for next release   → Product
Design the checkout flow               → Design
Position us against competitors        → Marketing
Help me qualify this lead              → Sales
Write a blog post about our launch     → Content
Find customers to interview            → CustDev
Do my daily customer outreach          → CustDev
Test the new checkout flow             → QA
Deploy to production                   → DevOps
```

### Or explicitly:

```
Use the chief-of-staff agent to do a weekly review
Use the engineering agent to continue the API refactor
```

## State Management

Each agent reads/writes to its state file at:
- **Session start**: Reads state, understands context, checks "Context for Next Session"
- **Session end**: Updates state with accomplishments, blockers, context for next session

### State File Structure

```markdown
# [Agent Name] State - [Project Name]

## Last Updated
YYYY-MM-DD HH:MM UTC

## Current Focus
[Primary objective]

## Active Work
| Task | Status | Notes |
|------|--------|-------|

## Blockers
- [ ] Blocker items

## Recent Decisions
- Date: Decision

## Context for Next Session
[Critical context for continuity]
```

See `examples/state/` for sample state files showing what populated state looks like.

## Multi-Project Support

For managing multiple products, create a portfolio state file:

**Location:** `~/business/.claude/state/portfolio.md`

The Chief of Staff agent can read this for cross-project awareness.

## File Locations

| Type | Location |
|------|----------|
| Agent definitions | `~/.claude/agents/*.md` |
| Plugin source | `~/.claude/plugins/solo-founder-fleet/` |
| Project state | `[project]/.claude/state/*.md` |
| Portfolio state | `~/business/.claude/state/portfolio.md` |
| Init script | `~/.claude/plugins/solo-founder-fleet/scripts/init-project-state.sh` |

## Syncing Agent Changes

Agents are deployed from the plugin repo to `~/.claude/agents/`. When you improve agents while working, those changes live in the deployed location. Use the sync tools to pull changes back to source.

### Quick Commands

```bash
# Check sync status
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh status

# View diffs
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh diff

# Pull deployed changes to source
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh pull

# Push source changes to deployed
~/.claude/plugins/solo-founder-fleet/scripts/sync-agents.sh push
```

### Using the Skill

```
/sync-agents
```

This runs an interactive sync check that:
1. Shows status of all agents
2. Displays diffs for changed files
3. Offers to pull changes back to source
4. Helps commit changes to git

### Weekly Sync Workflow

1. Run `/sync-agents` or `sync-agents.sh status`
2. Review any diffs (deployed changes are improvements made while working)
3. Pull changes you want to preserve
4. Commit to the plugin repo
5. Push source changes if needed

### Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| IN SYNC | Files identical | None needed |
| SOURCE NEWER | Repo has newer changes | `push` to deploy |
| DEPLOYED NEWER | Working copy has changes | `pull` to preserve |
| NOT DEPLOYED | Only in source | `push` to deploy |
| DEPLOYED ONLY | Only in ~/.claude/agents | `pull` to add to repo |

## Iteration Notes

To modify agents:
1. Edit files in `~/.claude/plugins/solo-founder-fleet/agents/`
2. Run `sync-agents.sh push` to deploy
3. Restart Claude Code

Or use the quick deploy:
```bash
cp ~/.claude/plugins/solo-founder-fleet/agents/*.md ~/.claude/agents/
```

## Troubleshooting

**Agents not appearing?**
- Ensure files are in `~/.claude/agents/` (not just the plugin directory)
- Restart Claude Code after copying agents
- Verify with `ls ~/.claude/agents/*.md | wc -l` (should show 10)

**State not persisting?**
- Run the init script for your project: `~/.claude/plugins/solo-founder-fleet/scripts/init-project-state.sh /path/to/project`
- Check that `.claude/state/` exists in your project directory

**Agent using wrong model?**
- Edit the agent file in `~/.claude/plugins/solo-founder-fleet/agents/`
- Re-copy to `~/.claude/agents/`
- Restart Claude Code

## Key Learnings

1. **Plugin discovery**: Claude Code doesn't auto-discover plugins in `~/.claude/plugins/` unless registered
2. **User-level agents**: `~/.claude/agents/` is automatically scanned for agent definitions
3. **Frontmatter format**: `tools` must be comma-separated string, not YAML array
4. **State persistence**: Markdown files in `.claude/state/` provide cross-session memory

## Contributing

To add or modify agents:
1. Fork this repo
2. Edit agent files in `agents/`
3. Test by copying to `~/.claude/agents/` and restarting Claude Code
4. Submit a PR with your changes

See `docs/AGENT_FORMAT.md` for the agent file specification.

## License

MIT
