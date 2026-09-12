# Quick React/TypeScript Project Scaffold

Quickly scaffold a new React + TypeScript project with Claude Code configuration.

## Arguments

$ARGUMENTS should contain: `<project-name> [target-directory]`

## Process

### 1. Create Project Structure

```bash
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME
```

### 2. Initialize Package.json (if not using a framework CLI)

If starting from scratch, create a basic Vite + React + TypeScript setup:

```bash
npm create vite@latest . -- --template react-ts
npm install
```

### 3. Generate CLAUDE.md

Use the `react-typescript.md` template from `/templates/claude-md/`. Fill in:
- Project name from arguments
- Detect actual commands from package.json
- Adjust structure based on what was created

### 4. Set Up Quality Tools

Ensure these are configured:
```bash
# Install dev dependencies if not present
npm install -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install -D prettier eslint-config-prettier
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

Add scripts to package.json if missing:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "typecheck": "tsc --noEmit",
    "lint": "eslint src --ext .ts,.tsx",
    "format": "prettier --write src"
  }
}
```

### 5. Create Slash Commands

Create `.claude/commands/` with useful React-specific commands:

**review.md** - Component review
**test-component.md** - Create tests for a component
**add-feature.md** - Add a new feature with proper structure

### 6. Verify

1. Run `npm run typecheck`
2. Run `npm run lint`
3. Ensure dev server starts: `npm run dev`

### Output

Summarize what was created and provide next steps.
