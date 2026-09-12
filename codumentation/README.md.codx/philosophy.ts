import * as fs from 'fs';
import * as path from 'path';

export const content = `## Philosophy

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
- Validation failures teach the AI what went wrong via \`errorContent\`

### The \`errorContent\` Advantage

When validation fails, \`errorContent\` provides actionable guidance:

\`\`\`typescript
export const errorContent = \`
[Feature Flag Validation Failed]

You added a feature flag but didn't document it.

To fix:
1. Add the flag to docs/feature-flags.md
2. Update the FeatureFlags type in src/types.ts
3. Run \\\`codumentation validate\\\` again

See: https://wiki.example.com/feature-flags
\`;
\`\`\`

This transforms validation errors into learning opportunities.`;

export const validate = async () => {
  const srcDir = path.join(__dirname, '..');

  // Verify we practice what we preach - check that our modules have good errorContent
  const codxDirs = ['README.md.codx', 'CLAUDE.md.codx'];

  for (const codxDir of codxDirs) {
    const fullDir = path.join(srcDir, codxDir);
    if (!fs.existsSync(fullDir)) continue;

    const modules = fs.readdirSync(fullDir).filter(f => f.endsWith('.ts'));

    for (const mod of modules) {
      const modPath = path.join(fullDir, mod);
      const content = fs.readFileSync(modPath, 'utf-8');

      // Verify each module has a non-trivial errorContent
      if (!content.includes('export const errorContent')) {
        throw new Error(`${codxDir}/${mod} missing errorContent export`);
      }

      // Check errorContent is not just empty
      const match = content.match(/export const errorContent\s*=\s*`([^`]*)`/s);
      if (match && match[1].trim().length < 50) {
        throw new Error(`${codxDir}/${mod} has trivial errorContent - should be descriptive`);
      }
    }
  }
};

export const errorContent = `
[Philosophy Section Validation Failed]

The philosophy section talks about good errorContent practices,
but this project's own .codx modules don't follow that advice.

Ensure every .ts module in README.md.codx and CLAUDE.md.codx has:
- An 'export const errorContent' declaration
- At least 50 characters of helpful guidance
`;
