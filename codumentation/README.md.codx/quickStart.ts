import * as fs from 'fs';
import * as path from 'path';

export const content = `## Quick Start

### 1. Install

\`\`\`bash
npm install codumentation --save-dev
\`\`\`

### 2. Initialize for a markdown file

\`\`\`bash
npx codumentation init README.md
\`\`\`

This creates:
- \`README.md.codx/\` - folder with your documentation modules
- \`README.md.codx/index.md\` - template with double-brace placeholders
- \`README.md.codx/*.ts\` - one module per section, each with \`validate()\`
- \`.codumentation-guide.md\` - examples and patterns

### 3. Add validations

Open each \`.ts\` module and replace the TODO stubs with real validations:

\`\`\`typescript
// README.md.codx/installation.ts
import { assertDependency, assertScript } from 'codumentation/helpers';

export const content = \`Run \\\`npm install\\\` to install dependencies.\`;

export const validate = async () => {
  // Verify the install command actually works
  assertScript('install', process.cwd()); // Not needed, npm has it built-in

  // Or verify specific dependencies exist
  assertDependency('typescript');
};

export const errorContent = \`Installation instructions are outdated.\`;
\`\`\`

### 4. Validate

\`\`\`bash
npx codumentation validate
\`\`\`

If all validations pass and rendered content matches your markdown, you're done!

### 5. Add to CI

\`\`\`yaml
# .github/workflows/docs.yml
- name: Validate Documentation
  run: npx codumentation validate
\`\`\``;

export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Verify the init command exists in CLI
  const cliPath = path.join(__dirname, '..', 'src', 'cli.ts');
  const cliContent = fs.readFileSync(cliPath, 'utf-8');

  if (!cliContent.includes("command('init")) {
    throw new Error('Quick start mentions init command but CLI does not have it');
  }

  // Verify the validate command exists
  if (!cliContent.includes("command('validate")) {
    throw new Error('Quick start mentions validate command but CLI does not have it');
  }

  // Verify helpers export path is correct
  if (!pkg.exports?.['./helpers']) {
    throw new Error('Quick start shows importing from codumentation/helpers but package.json exports are missing');
  }

  // Verify bin entry exists for npx usage
  if (!pkg.bin?.codumentation) {
    throw new Error('Quick start shows npx codumentation but bin entry is missing');
  }
};

export const errorContent = `
[Quick Start Validation Failed]

The quick start guide mentions commands or features that don't exist.

Check:
- CLI has 'init' command
- CLI has 'validate' command
- package.json has correct bin entry
- package.json exports ./helpers path
`;
