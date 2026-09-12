# Agent File Format Reference

Claude Code agents are Markdown files with YAML frontmatter.

## Required Structure

```markdown
---
name: agent-name
model: sonnet
color: blue
tools: Read, Write, Edit, Glob, Grep
description: |
  Description of when to use this agent.

  <example>
  Context: Situation description
  user: "User message"
  assistant: "How assistant responds"
  <commentary>
  Why this triggers the agent
  </commentary>
  </example>
---

# Agent instructions (system prompt)

Content here becomes the agent's instructions.
```

## Frontmatter Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Unique identifier (lowercase, hyphens) |
| `description` | Yes | string | When Claude should delegate to this agent |
| `tools` | No | comma-separated | Tools agent can use (inherits all if omitted) |
| `disallowedTools` | No | comma-separated | Tools to deny |
| `model` | No | string | `sonnet`, `opus`, `haiku`, or `inherit` |
| `color` | No | string | UI color: `red`, `yellow`, `green`, `blue`, `cyan`, `magenta` |
| `permissionMode` | No | string | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |

## Available Tools

Common tools to include:
- `Read` - Read files
- `Write` - Create/overwrite files
- `Edit` - Edit existing files
- `Glob` - Find files by pattern
- `Grep` - Search file contents
- `Bash` - Run shell commands
- `WebSearch` - Search the web
- `WebFetch` - Fetch URL content

## Examples in Description

The `<example>` blocks help Claude understand when to delegate:

```yaml
description: |
  Use this agent for [domain].

  <example>
  Context: [Situation]
  user: "[What user says]"
  assistant: "[How to respond]"
  <commentary>
  [Why this triggers the agent]
  </commentary>
  </example>
```

Include 2-4 examples covering different trigger scenarios.

## Body Content

Everything after the closing `---` becomes the agent's system prompt. Include:
- Core responsibilities
- Protocols and workflows
- Communication style guidelines
- State management instructions (for stateful agents)

## Common Mistakes

1. **YAML array for tools** - Use comma-separated string, not array
   ```yaml
   # Wrong
   tools:
     - Read
     - Write

   # Correct
   tools: Read, Write, Edit
   ```

2. **Missing pipe for multiline description** - Use `|` for multiline strings
   ```yaml
   # Wrong
   description: Use this agent for...

   # Correct
   description: |
     Use this agent for...
   ```

3. **Indentation in examples** - Keep consistent indentation within the `description: |` block
