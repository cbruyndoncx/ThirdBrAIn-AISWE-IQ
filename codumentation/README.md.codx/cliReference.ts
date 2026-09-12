import * as fs from 'fs';
import * as path from 'path';

export const content = `## CLI Reference

### \`codumentation init <file>\`

Initialize codumentation for a markdown file.

\`\`\`bash
npx codumentation init README.md
npx codumentation init CLAUDE.md
npx codumentation init docs/API.md
\`\`\`

**Options:**
- \`-f, --force\` - Overwrite existing .codx directory

### \`codumentation validate\`

Validate all documentation against the codebase. Use in CI.

\`\`\`bash
npx codumentation validate
\`\`\`

Exit codes:
- \`0\` - All validations pass
- \`1\` - Validation failed or content mismatch

### \`codumentation build\`

Regenerate markdown files from .codx sources.

\`\`\`bash
npx codumentation build
\`\`\`

Only writes files if all validations pass.

### \`codumentation stats\`

View validation failure statistics to identify problematic modules.

\`\`\`bash
npx codumentation stats
npx codumentation stats --days 7
\`\`\`

Shows which modules fail most often, helping you improve documentation.`;

export const validate = async () => {
  const cliPath = path.join(__dirname, '..', 'src', 'cli.ts');
  const cliContent = fs.readFileSync(cliPath, 'utf-8');

  // Verify all documented commands exist
  const commands = ['init', 'validate', 'build', 'stats'];
  const missingCommands: string[] = [];

  for (const cmd of commands) {
    if (!cliContent.includes(`command('${cmd}`)) {
      missingCommands.push(cmd);
    }
  }

  if (missingCommands.length > 0) {
    throw new Error(`CLI reference documents commands that don't exist: ${missingCommands.join(', ')}`);
  }

  // Verify init has --force option
  if (!cliContent.includes('--force') && !cliContent.includes('-f')) {
    throw new Error('CLI reference mentions --force option but it is not implemented');
  }

  // Verify stats has --days option
  if (!cliContent.includes('--days') && !cliContent.includes('-d')) {
    throw new Error('CLI reference mentions --days option but it is not implemented');
  }
};

export const errorContent = `
[CLI Reference Validation Failed]

The CLI reference documents commands or options that don't exist in src/cli.ts.

Ensure all documented commands are implemented:
- init (with --force option)
- validate
- build
- stats (with --days option)
`;
