# Iteration Log

Track changes and learnings as the fleet evolves.

---

## 2026-01-26: Initial Implementation

### What was built
- 7 agents: chief-of-staff, engineering, product, design, marketing, sales, content
- State management system with per-project `.claude/state/` files
- Init script for bootstrapping new projects
- Documentation

### Key decisions
- **Chief of Staff uses Opus** - Needs highest reasoning for strategic synthesis
- **Specialists use Sonnet** - Good balance of capability and speed
- **State in markdown** - Human-readable, version-controllable
- **Per-project state** - Isolation between projects

### Learnings
1. Plugins in `~/.claude/plugins/` aren't auto-discovered - need registration
2. User-level agents in `~/.claude/agents/` ARE auto-discovered
3. `tools` field must be comma-separated string, not YAML array
4. Examples in description help Claude match tasks to agents

### Installation path that works
```
~/.claude/plugins/solo-founder-fleet/agents/*.md  (source)
        ↓ copy
~/.claude/agents/*.md  (active)
```

### Files created
```
~/.claude/plugins/solo-founder-fleet/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── chief-of-staff.md
│   ├── engineering.md
│   ├── product.md
│   ├── design.md
│   ├── marketing.md
│   ├── sales.md
│   └── content.md
├── scripts/
│   └── init-project-state.sh
├── docs/
│   ├── AGENT_FORMAT.md
│   ├── STATE_MANAGEMENT.md
│   └── ITERATION_LOG.md
└── README.md
```

---

## Future Ideas

### Enhancements to consider
- [ ] Add a `sync-agents.sh` script to copy agents to `~/.claude/agents/`
- [ ] Create slash commands for common workflows (`/standup`, `/review`)
- [ ] Add hooks for automatic state updates
- [ ] Portfolio-level agent for multi-product founders
- [ ] Integration with task management tools
- [ ] State file versioning/backup

### Agent improvements
- [ ] Refine trigger examples based on actual usage
- [ ] Adjust tool permissions per agent
- [ ] Add skill references for specialized tasks
- [ ] Consider adding `permissionMode` settings

### State improvements
- [ ] Auto-archive completed work periodically
- [ ] Add metrics/KPI tracking sections
- [ ] Cross-agent state awareness (design reads product state, etc.)

---

## How to iterate

1. Edit agent files in `~/.claude/plugins/solo-founder-fleet/agents/`
2. Test changes by copying to `~/.claude/agents/`
3. Restart Claude Code
4. Document learnings here

```bash
# Quick iteration cycle
cp ~/.claude/plugins/solo-founder-fleet/agents/*.md ~/.claude/agents/ && echo "Agents updated - restart Claude Code"
```
