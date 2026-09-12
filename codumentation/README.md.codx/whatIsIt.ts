import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';

export const content = `## What is Codumentation?

**Codumentation** turns documentation into executable specifications. Instead of hoping your docs stay up-to-date, you write validation code that *proves* they're accurate.

When your code changes but your docs don't, CI fails. When you run \`codumentation validate\`, it:

1. **Loads** each documentation module from \`.codx\` folders
2. **Executes** validation functions that check claims against reality
3. **Compares** rendered output with existing markdown
4. **Fails fast** if anything is out of sync

### The Problem

Traditional documentation rots:
- README says "run \`npm start\`" but that script was removed
- CLAUDE.md claims "strict TypeScript" but \`tsconfig.json\` has \`strict: false\`
- Architecture docs describe folders that no longer exist

### The Solution

Codumentation makes documentation claims *testable*:

\`\`\`typescript
// README.md.codx/techStack.ts
export const validate = async () => {
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
  if (!pkg.dependencies?.typescript) {
    throw new Error('README claims TypeScript but it\\'s not installed');
  }
};
\`\`\``;

export const validate = async () => {
  // Validate that this project actually uses .codx folders (eat our own dog food)
  const codxDirs = glob.sync('**/*.codx', {
    cwd: path.join(__dirname, '..'),
    ignore: ['node_modules/**', 'dist/**']
  });

  if (codxDirs.length < 2) {
    throw new Error(
      `README claims codumentation uses .codx folders, but found only ${codxDirs.length}. ` +
      `We should have at least README.md.codx and CLAUDE.md.codx`
    );
  }

  // Verify the example code in content is syntactically plausible
  // (checking that we're showing a real pattern)
  const examplePattern = /export const validate = async \(\)/;
  if (!examplePattern.test(content)) {
    throw new Error('The example code should show the validate function pattern');
  }
};

export const errorContent = `
[What Is It Section Validation Failed]

This section explains codumentation but the claims don't match reality.

Ensure:
- The project has at least 2 .codx directories (self-hosting)
- Example code patterns are accurate
`;
