import * as fs from 'fs';
import * as path from 'path';

export const content = `## Innovative Examples

Codumentation shines when you use it to encode *tribal knowledge* that would otherwise be forgotten.

### Validate No \`any\` Types

\`\`\`typescript
// CLAUDE.md.codx/codeQuality.ts
export const validate = async () => {
  assertNoCodePattern(
    'src/**/*.ts',
    /:\\s*any\\b|as\\s+any\\b/,
    'TypeScript any types are forbidden'
  );
};
\`\`\`

### Validate API Routes Have Zod Validation

\`\`\`typescript
export const validate = async () => {
  const routes = assertGlobMatches('src/api/**/*.ts');
  for (const route of routes) {
    assertFileContains(route, 'z.object', \`\${route} missing Zod validation\`);
  }
};
\`\`\`

### Validate Single Source of Truth

\`\`\`typescript
// Ensure there's only one components folder
export const validate = async () => {
  assertSingleDirectory('components');
};
\`\`\`

### Validate Environment Variables Are Documented

\`\`\`typescript
export const validate = async () => {
  // Find all process.env usages
  const srcFiles = assertGlobMatches('src/**/*.ts');
  const usedEnvVars = new Set<string>();

  for (const file of srcFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const matches = content.matchAll(/process\\.env\\.(\\w+)/g);
    for (const match of matches) {
      usedEnvVars.add(match[1]);
    }
  }

  // Verify all are in .env.example
  const envExample = fs.readFileSync('.env.example', 'utf-8');
  for (const envVar of usedEnvVars) {
    if (!envExample.includes(envVar)) {
      throw new Error(\`\${envVar} used in code but not in .env.example\`);
    }
  }
};
\`\`\`

### Validate Architecture Rules

\`\`\`typescript
// No direct database imports outside db/ folder
export const validate = async () => {
  assertNoCodePattern(
    'src/!(db)/**/*.ts',
    /from ['"].*prisma|from ['"].*drizzle/,
    'Database imports only allowed in src/db/'
  );
};
\`\`\`

### Validate This README Is Self-Documenting

This README itself uses codumentation! Every section you're reading is:
1. Generated from \`README.md.codx/\` modules
2. Validated against the actual codebase
3. Rebuilt when you run \`codumentation build\`

If any claim in this README is false, \`codumentation validate\` fails.`;

export const validate = async () => {
  const srcDir = path.join(__dirname, '..');

  // Meta-validation: verify this README actually uses .codx
  const readmeCodxDir = path.join(srcDir, 'README.md.codx');
  if (!fs.existsSync(readmeCodxDir)) {
    throw new Error('README claims to be self-documenting but README.md.codx missing');
  }

  // Count modules to verify substantial self-documentation
  const modules = fs.readdirSync(readmeCodxDir).filter(f => f.endsWith('.ts'));
  if (modules.length < 5) {
    throw new Error(
      `README claims substantial self-documentation but only has ${modules.length} modules`
    );
  }

  // Verify we have innovative examples that use the helpers we document
  const helpersPath = path.join(srcDir, 'src', 'helpers.ts');
  if (!fs.existsSync(helpersPath)) {
    throw new Error('Examples reference helpers but helpers.ts does not exist');
  }
};

export const errorContent = `
[Innovative Examples Validation Failed]

This section shows innovative codumentation patterns but the claims aren't backed up.

Ensure:
- README.md.codx/ exists with substantial modules
- helpers.ts exists for the documented helper functions
- At least 5 modules demonstrate real self-documentation
`;
