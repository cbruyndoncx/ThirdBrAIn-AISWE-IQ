# Project Scaffold Wizard

You are setting up a new Claude Code project. Follow this interactive process:

## Step 1: Gather Information

Ask the user for:
1. **Project name** (will be used for folder name)
2. **Project type** (React, Python API, Full Stack, or Other)
3. **Brief description** of what the project does
4. **Target directory** (default: current directory)

## Step 2: Analyze Existing Code (if applicable)

If scaffolding in an existing project:
1. Read package.json, pyproject.toml, or similar config files
2. Examine the folder structure
3. Look for existing README.md
4. Check for existing linter/formatter configs

## Step 3: Generate CLAUDE.md

Based on the project type, use the appropriate template from `/templates/claude-md/`:
- React/TypeScript: `react-typescript.md`
- Python API: `python-api.md`  
- Full Stack: `fullstack.md`
- Other: `minimal.md`

Customize the template by:
1. Replacing all `{{PLACEHOLDER}}` values
2. Adjusting commands to match actual project setup
3. Adding project-specific file boundaries
4. Including any detected patterns or conventions

## Step 4: Create Project Structure

Create the following structure:
```
<project>/
├── CLAUDE.md                 # Generated from template
├── .claude/
│   └── commands/             # Custom slash commands
│       └── review.md         # Code review command
└── docs/                     # Optional documentation folder
```

## Step 5: Suggest Additional Setup

Recommend to the user:
1. **MCP servers** that might be useful (GitHub, Puppeteer, etc.)
2. **Custom slash commands** for their workflow
3. **Skills** they might want to create
4. **Git hooks** for quality checks

## Step 6: Verify Setup

1. Run any available lint/test commands
2. Confirm CLAUDE.md is readable and well-formatted
3. Test that slash commands are recognized

## Output

After completing setup, provide a summary:
- Files created
- Next steps for the user
- How to customize further

---

$ARGUMENTS will contain any initial project details the user provided.
