# Codumentation

Auto-verifiable Markdown for documentation that cannot rot

[![npm version](https://img.shields.io/npm/v/codumentation.svg)](https://www.npmjs.com/package/codumentation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)

> **This README is self-documenting.** Every claim is validated by code. If you see this, it passed.

## What is Codumentation?

**Codumentation** turns documentation into executable specifications. Instead of hoping your docs stay up-to-date, you write validation code that *proves* they're accurate.

When your code changes but your docs don't, CI fails. When you run `codumentation validate`, it:

1. **Loads** each documentation module from `.codx` folders
2. **Executes** validation functions that check claims against reality
3. **Compares** rendered output with existing markdown
4. **Fails fast** if anything is out of sync

### The Problem

Traditional documentation rots:
- README says "run `npm start`" but that script was removed
- CLAUDE.md claims "strict TypeScript" but `tsconfig.json` has `strict: false`
- Architecture docs describe folders that no longer exist

### The Solution

Codumentation makes documentation claims *testable*:

```typescript
// README.md.codx/techStack.ts
export const validate = async () => {
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
  if (!pkg.dependencies?.typescript) {
    throw new Error('README claims TypeScript but it\'s not installed');
  }
};
```

## Quick Start

### 1. Install

```bash
npm install codumentation --save-dev
```

### 2. Initialize for a markdown file

```bash
npx codumentation init README.md
```

This creates:
- `README.md.codx/` - folder with your documentation modules
- `README.md.codx/index.md` - template with double-brace placeholders
- `README.md.codx/*.ts` - one module per section, each with `validate()`
- `.codumentation-guide.md` - examples and patterns

### 3. Add validations

Open each `.ts` module and replace the TODO stubs with real validations:

```typescript
// README.md.codx/installation.ts
import { assertDependency, assertScript } from 'codumentation/helpers';

export const content = `Run \`npm install\` to install dependencies.`;

export const validate = async () => {
  // Verify the install command actually works
  assertScript('install', process.cwd()); // Not needed, npm has it built-in

  // Or verify specific dependencies exist
  assertDependency('typescript');
};

export const errorContent = `Installation instructions are outdated.`;
```

### 4. Validate

```bash
npx codumentation validate
```

If all validations pass and rendered content matches your markdown, you're done!

### 5. Add to CI

```yaml
# .github/workflows/docs.yml
- name: Validate Documentation
  run: npx codumentation validate
```

## How It Works

### File Structure

For each markdown file (e.g., `README.md`), create a `.codx` folder:

```
README.md           # The generated output
README.md.codx/     # The source of truth
  index.md          # Template with placeholders (double braces around names)
  intro.ts          # Module for intro section
  features.ts       # Module for features section
  _meta.ts          # Meta-validator (checks adoption)
```

### Module Interface

Each `.ts` module exports three things:

```typescript
// content: The text to inject into the template
export const content = \`## Features
- Fast validation
- TypeScript support\`;

// validate: Async function that throws if claims are false
export const validate = async () => {
  if (!fs.existsSync('src/validator.ts')) {
    throw new Error('Claims validation but validator.ts missing');
  }
};

// errorContent: Human-readable explanation when validation fails
export const errorContent = \`
Features section claims validation support but validator is missing.
Run: touch src/validator.ts
\`;
```

### Template Rendering

The `index.md` template uses double-brace placeholders like `{​{ name }​}` (where `name` maps to `name.ts`):

```markdown
# My Project

{​{ intro }​}

{​{ features }​}

{​{ license }​}
```

Each placeholder maps to a `.ts` module with the same name.

## CLI Reference

### `codumentation init <file>`

Initialize codumentation for a markdown file.

```bash
npx codumentation init README.md
npx codumentation init CLAUDE.md
npx codumentation init docs/API.md
```

**Options:**
- `-f, --force` - Overwrite existing .codx directory

### `codumentation validate`

Validate all documentation against the codebase. Use in CI.

```bash
npx codumentation validate
```

Exit codes:
- `0` - All validations pass
- `1` - Validation failed or content mismatch

### `codumentation build`

Regenerate markdown files from .codx sources.

```bash
npx codumentation build
```

Only writes files if all validations pass.

### `codumentation stats`

View validation failure statistics to identify problematic modules.

```bash
npx codumentation stats
npx codumentation stats --days 7
```

Shows which modules fail most often, helping you improve documentation.

## Helper Functions

Codumentation provides helper functions for common validation patterns.

```typescript
import {
  assertFileExists,
  assertDependency,
  assertNoCodePattern
} from 'codumentation/helpers';
```

### File System Helpers

| Function | Description |
|----------|-------------|
| `assertFileExists(path)` | Throws if file doesn't exist |
| `assertFilesExist(paths[])` | Throws if any file is missing |
| `assertDirectoryExists(path)` | Throws if directory doesn't exist |
| `assertNotExists(path)` | Throws if path exists (for cleanup checks) |

### Glob Pattern Helpers

| Function | Description |
|----------|-------------|
| `assertGlobMatches(pattern)` | Throws if no files match; returns matches |
| `assertNoGlobMatches(pattern)` | Throws if files DO match (forbidden patterns) |
| `assertGlobCount(pattern, n)` | Throws if match count != n |
| `assertGlobMinCount(pattern, n)` | Throws if match count < n |

### Package.json Helpers

| Function | Description |
|----------|-------------|
| `assertDependency(name)` | Throws if package not in deps/devDeps |
| `assertProdDependency(name)` | Throws if not in production deps |
| `assertDevDependency(name)` | Throws if not in devDependencies |
| `assertScript(name)` | Throws if npm script doesn't exist |
| `assertBin(name)` | Throws if bin entry doesn't exist |

### Content Helpers

| Function | Description |
|----------|-------------|
| `assertFileContains(path, str)` | Throws if file doesn't contain string |
| `assertFileNotContains(path, str)` | Throws if file contains string |
| `assertFileMatches(path, regex)` | Throws if file doesn't match pattern |
| `assertNoCodePattern(glob, regex)` | Throws if pattern found in any file |
| `assertCodePattern(glob, regex)` | Throws if pattern NOT found in files |

### TypeScript Helpers

| Function | Description |
|----------|-------------|
| `assertStrictMode()` | Throws if TypeScript strict mode disabled |
| `assertTsConfigOption(opt, val)` | Throws if tsconfig option != value |

### Structure Helpers

| Function | Description |
|----------|-------------|
| `assertFolderStructure(spec)` | Validates directory structure matches spec |
| `assertSingleDirectory(name)` | Throws if multiple directories with name exist |

### Example Usage

```typescript
export const validate = async () => {
  // Verify all mentioned files exist
  assertFilesExist(['src/index.ts', 'src/cli.ts', 'package.json']);

  // Verify no console.log in production code
  assertNoCodePattern('src/**/*.ts', /console\.log/, 'Remove console.log from production');

  // Verify TypeScript strict mode
  assertStrictMode();

  // Verify folder structure
  assertFolderStructure({
    'src': { 'index.ts': 'file', 'types.ts': 'file' },
    'tests': 'dir',
    'package.json': 'file'
  });
};
```

## Innovative Examples

Codumentation shines when you use it to encode *tribal knowledge* that would otherwise be forgotten.

### Validate No `any` Types

```typescript
// CLAUDE.md.codx/codeQuality.ts
export const validate = async () => {
  assertNoCodePattern(
    'src/**/*.ts',
    /:\s*any\b|as\s+any\b/,
    'TypeScript any types are forbidden'
  );
};
```

### Validate API Routes Have Zod Validation

```typescript
export const validate = async () => {
  const routes = assertGlobMatches('src/api/**/*.ts');
  for (const route of routes) {
    assertFileContains(route, 'z.object', `${route} missing Zod validation`);
  }
};
```

### Validate Single Source of Truth

```typescript
// Ensure there's only one components folder
export const validate = async () => {
  assertSingleDirectory('components');
};
```

### Validate Environment Variables Are Documented

```typescript
export const validate = async () => {
  // Find all process.env usages
  const srcFiles = assertGlobMatches('src/**/*.ts');
  const usedEnvVars = new Set<string>();

  for (const file of srcFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const matches = content.matchAll(/process\.env\.(\w+)/g);
    for (const match of matches) {
      usedEnvVars.add(match[1]);
    }
  }

  // Verify all are in .env.example
  const envExample = fs.readFileSync('.env.example', 'utf-8');
  for (const envVar of usedEnvVars) {
    if (!envExample.includes(envVar)) {
      throw new Error(`${envVar} used in code but not in .env.example`);
    }
  }
};
```

### Validate Architecture Rules

```typescript
// No direct database imports outside db/ folder
export const validate = async () => {
  assertNoCodePattern(
    'src/!(db)/**/*.ts',
    /from ['"].*prisma|from ['"].*drizzle/,
    'Database imports only allowed in src/db/'
  );
};
```

### Validate This README Is Self-Documenting

This README itself uses codumentation! Every section you're reading is:
1. Generated from `README.md.codx/` modules
2. Validated against the actual codebase
3. Rebuilt when you run `codumentation build`

If any claim in this README is false, `codumentation validate` fails.

## Optimizing AI Context Files

One of codumentation's most powerful features is using validation logs to **continuously improve AI context files** like CLAUDE.md.

### The Feedback Loop

When you use Claude Code (or similar AI agents) with a codumented CLAUDE.md:

1. **AI makes changes** based on your documented rules
2. **Validation runs** (manually or via hooks/CI)
3. **Failures are logged** to `.codumentation-summary.log`
4. **Stats reveal patterns** about which sections fail most
5. **You improve those sections** with better guidance
6. **Repeat** until documentation is bulletproof

```bash
# After a long coding session with AI agents
npx codumentation stats --days 7
```

Output might show:
```
Validation Failure Statistics (Last 7 days)
==================================================

Total Failures: 23

Failures by Module:
  codeStyle: 12 failures ← Improve guidance!
  architecture: 7 failures ← Consider improving
  testing: 4 failures
```

This tells you: **your code style documentation isn't clear enough** for the AI to follow consistently.

### Minimizing AI Context Files

Large CLAUDE.md files waste tokens and can confuse AI agents. Use the feedback loop to find the **minimal effective documentation**:

1. **Start with comprehensive rules**
2. **Track which validations never fail** - those rules are well understood
3. **Track which fail repeatedly** - those need better explanations
4. **Trim rules that never fail** - they might be obvious to the AI
5. **Expand rules that fail often** - add examples, clarify edge cases

### The `errorContent` Teaching Mechanism

When validation fails, the AI sees your `errorContent`. Write it as **teaching material**:

```typescript
export const errorContent = `
[Code Style Violation]

You used a class component, but this project uses functional components only.

WRONG:
  class MyComponent extends React.Component { ... }

RIGHT:
  function MyComponent() { ... }
  // or
  const MyComponent: React.FC = () => { ... }

Why: Functional components are smaller, easier to test, and support hooks.

See: src/components/Button.tsx for an example
`;
```

Now when the AI breaks this rule:
1. Validation fails immediately (not after human review)
2. AI receives specific guidance on what went wrong
3. AI learns the pattern for next time

### Practical Workflow

```bash
# 1. After AI coding session, check what broke
npx codumentation stats

# 2. Identify problematic modules
#    Example: "architecture" fails 40% of the time

# 3. Improve that module's documentation
#    - Add more examples to content
#    - Make errorContent more instructive
#    - Add edge cases the AI missed

# 4. Re-run to verify fix
npx codumentation validate

# 5. Over time, your CLAUDE.md becomes:
#    - Smaller (remove obvious rules)
#    - More precise (clarify confusing rules)
#    - Self-correcting (errorContent teaches)
```

### Why This Matters

Traditional AI context files are **write-once, pray-it-works**. Codumentation makes them **measurable and improvable**:

| Traditional CLAUDE.md | Codumented CLAUDE.md |
|----------------------|---------------------|
| No feedback on effectiveness | Stats show what works |
| Grows forever | Can be minimized |
| AI silently ignores unclear rules | Failures catch violations |
| Human reviews catch issues | Automated validation catches issues |
| "IMPORTANT: Never do X" | Validation prevents X |

## CI/CD Integration

### GitHub Actions

```yaml
name: Documentation
on: [push, pull_request]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npx codumentation validate
```

### GitLab CI

```yaml
validate-docs:
  image: node:18
  script:
    - npm ci
    - npx codumentation validate
  rules:
    - changes:
        - "*.md"
        - "*.codx/**/*"
        - "src/**/*"
```

### Pre-commit Hook (Husky)

```bash
npx husky add .husky/pre-commit "npx codumentation validate"
```

### Package.json Scripts

```json
{
  "scripts": {
    "docs:validate": "codumentation validate",
    "docs:build": "codumentation build",
    "test": "vitest && codumentation validate"
  }
}
```

This ensures documentation is validated alongside your test suite.

## Bundler Configuration

Codumentation is typically used as a dev-only validation tool. If your bundler tries to resolve its dependencies during production builds, you may need to exclude it.

### TypeScript

You'll likely want to exclude `.codx` folders from compilation since they contain validation modules:

```json
// tsconfig.json
{
  "exclude": ["**/*.codx/**"]
}
```

### Vite

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      external: ['codumentation', 'codumentation/helpers']
    }
  }
});
```

### Webpack

```javascript
// webpack.config.js
module.exports = {
  externals: {
    'codumentation': 'codumentation',
    'codumentation/helpers': 'codumentation/helpers'
  }
};
```

### esbuild

```bash
esbuild --external:codumentation --external:codumentation/helpers
```

### Note on Glob Dependency

The `glob` package is an optional peer dependency. It's only needed if you use glob-based helpers like `assertGlobMatches()`, `assertNoGlobMatches()`, etc. If you don't use these helpers, you don't need to install glob.

If you do use glob-based helpers, install it alongside codumentation:

```bash
npm install codumentation glob --save-dev
```

## Philosophy

### "Validate First, Generate Second"

Codumentation inverts the traditional docs workflow:

| Traditional | Codumentation |
|------------|---------------|
| Write docs | Write validation code |
| Hope they stay current | CI ensures they're current |
| Manual review | Automated enforcement |
| Docs as afterthought | Docs as code |

### Why Validation Matters

**For Humans:**
- README instructions that work on the first try
- Architecture docs that reflect actual structure
- No more "this doc is outdated" discoveries

**For AI Agents:**
- CLAUDE.md with rules that are *enforced*, not just stated
- AI context files that stay synchronized with codebase
- Validation failures teach the AI what went wrong via `errorContent`

### The `errorContent` Advantage

When validation fails, `errorContent` provides actionable guidance:

```typescript
export const errorContent = `
[Feature Flag Validation Failed]

You added a feature flag but didn't document it.

To fix:
1. Add the flag to docs/feature-flags.md
2. Update the FeatureFlags type in src/types.ts
3. Run \`codumentation validate\` again

See: https://wiki.example.com/feature-flags
`;
```

This transforms validation errors into learning opportunities.

## License

MIT - see [LICENSE](./LICENSE) for details.

---

**Ready to make your documentation unbreakable?**

```bash
npm install codumentation --save-dev
npx codumentation init README.md
```

Happy documenting!
