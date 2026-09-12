# Generate CLAUDE.md for Existing Project

Analyze an existing codebase and generate an optimized CLAUDE.md file.

## Arguments

$ARGUMENTS can optionally specify a target directory. Default: current directory.

## Analysis Process

### Step 1: Detect Project Type

Look for these indicators:
- `package.json` → Node.js/JavaScript/TypeScript
- `pyproject.toml` / `requirements.txt` / `setup.py` → Python
- `Cargo.toml` → Rust
- `go.mod` → Go
- `pom.xml` / `build.gradle` → Java
- `Gemfile` → Ruby

### Step 2: Analyze Configuration Files

Read and extract:
- **Scripts/Commands**: From package.json scripts, Makefile, etc.
- **Dependencies**: Key frameworks and libraries
- **Tool Configs**: ESLint, Prettier, Ruff, MyPy, etc.

### Step 3: Examine Project Structure

Map the directory structure and identify:
- Source code directories
- Test directories  
- Configuration directories
- Build output directories (to exclude)

### Step 4: Look for Existing Documentation

Read if present:
- `README.md` - Project description and setup
- `CONTRIBUTING.md` - Contribution guidelines
- Existing `CLAUDE.md` - To preserve custom instructions

### Step 5: Generate CLAUDE.md

Create a CLAUDE.md following the WHAT/WHY/HOW framework:

```markdown
# Project Name

> Brief description from README or package description

## Tech Stack

- List detected technologies
- Key frameworks and libraries

## Project Structure

- Map key directories
- Note important files

## Commands

```bash
# List detected commands from package.json/Makefile/etc.
```

## Verification

- List available lint commands
- List available test commands
- List type check commands

## File Boundaries

- Safe to edit: source directories
- Read-only: config, generated files
- Never touch: node_modules, venv, build outputs
```

### Step 6: Apply Best Practices

Ensure the generated CLAUDE.md:
1. Is **concise** (under 200 lines ideally)
2. Contains only **universally applicable** instructions
3. References **specific commands** the user can run
4. Defines clear **file boundaries**
5. Does NOT include style guidelines (use linters instead)

### Step 7: Suggest Enhancements

After generating, recommend:
1. Custom slash commands for common workflows
2. MCP servers that could be useful
3. Skills that could help with specialized tasks

## Output

Write the CLAUDE.md file and provide a summary of what was detected and any recommendations.
