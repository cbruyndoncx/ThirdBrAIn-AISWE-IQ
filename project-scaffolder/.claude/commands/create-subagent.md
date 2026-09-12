# Create a Custom Subagent

Create a specialized subagent for delegated tasks.

## Arguments

$ARGUMENTS should contain: `<subagent-name> [description]`

## What Are Subagents?

Subagents are specialized AI assistants that:
- Have their own context window (preserves main conversation)
- Can be configured with specific tools
- Have custom system prompts
- Are automatically invoked when matching tasks appear

## Subagent Creation Process

### Step 1: Gather Information

Ask the user:
1. **Name**: Short, descriptive (kebab-case, e.g., `test-runner`)
2. **Purpose**: What specific task does this subagent handle?
3. **Trigger**: When should Claude delegate to this subagent?
4. **Tools needed**: What tools does it need? (or inherit all)
5. **Model**: sonnet (default), opus, haiku, or inherit

### Step 2: Choose Scope

- **Project-level** (`.claude/agents/`): Available only in this project
- **User-level** (`~/.claude/agents/`): Available across all projects

Recommend project-level for project-specific workflows.

### Step 3: Generate Subagent File

Create the subagent with this structure:

```markdown
---
name: <name>
description: <description>. Use PROACTIVELY when <trigger condition>.
tools: <tool1>, <tool2>  # Or omit to inherit all tools
model: <model>           # Optional: sonnet/opus/haiku/inherit
---

<Detailed system prompt>

## When Invoked
1. First step
2. Second step
...

## Process
<Detailed instructions>

## Output Format
<Expected output structure>
```

### Step 4: Write an Effective Description

The description is CRITICAL for automatic invocation. Include:
- What the subagent does
- "Use PROACTIVELY" or "MUST BE USED" for automatic triggering
- Specific trigger conditions

**Good descriptions:**
- "Expert code reviewer. Use PROACTIVELY after writing or modifying code."
- "Test runner specialist. MUST BE USED when tests fail or new tests needed."

**Bad descriptions:**
- "Helps with code" (too vague)
- "Reviews things" (no trigger)

### Step 5: Configure Tools

Available tools:
- **Read**: Read file contents
- **Edit**: Modify files
- **Write**: Create new files
- **Bash**: Execute shell commands
- **Grep**: Search file contents
- **Glob**: Find files by pattern
- **MCP tools**: Any configured MCP server tools

Limit to only necessary tools for better focus and security.

### Step 6: Write the System Prompt

Include:
1. **Role definition**: Who is this subagent?
2. **When invoked**: Immediate first steps
3. **Process**: Detailed workflow
4. **Output format**: How to structure responses
5. **Tips**: Domain-specific guidance

### Step 7: Verify and Test

After creating:
1. Use `/agents` to see it listed
2. Test with an explicit invocation: "Use the <name> subagent to..."
3. Verify automatic delegation works
4. Iterate on the prompt based on results

## Example Subagents

### Test Runner
```markdown
---
name: test-runner
description: Test automation expert. Use PROACTIVELY when tests fail or after code changes.
tools: Read, Bash, Grep
model: inherit
---

You are a test automation expert...
```

### Security Auditor
```markdown
---
name: security-auditor
description: Security review specialist. Use PROACTIVELY before merging PRs or when handling auth/payment code.
tools: Read, Grep, Glob
model: sonnet
---

You are a security-focused code auditor...
```

## Output

Create the subagent file and provide:
- File location
- How to test it
- Suggestions for refinement
