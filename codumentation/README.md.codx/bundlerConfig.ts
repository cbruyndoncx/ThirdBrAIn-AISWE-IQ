import * as fs from 'fs';
import * as path from 'path';

export const content = `## Bundler Configuration

Codumentation is typically used as a dev-only validation tool. If your bundler tries to resolve its dependencies during production builds, you may need to exclude it.

### TypeScript

You'll likely want to exclude \`.codx\` folders from compilation since they contain validation modules:

\`\`\`json
// tsconfig.json
{
  "exclude": ["**/*.codx/**"]
}
\`\`\`

### Vite

\`\`\`typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      external: ['codumentation', 'codumentation/helpers']
    }
  }
});
\`\`\`

### Webpack

\`\`\`javascript
// webpack.config.js
module.exports = {
  externals: {
    'codumentation': 'codumentation',
    'codumentation/helpers': 'codumentation/helpers'
  }
};
\`\`\`

### esbuild

\`\`\`bash
esbuild --external:codumentation --external:codumentation/helpers
\`\`\`

### Note on Glob Dependency

The \`glob\` package is an optional peer dependency. It's only needed if you use glob-based helpers like \`assertGlobMatches()\`, \`assertNoGlobMatches()\`, etc. If you don't use these helpers, you don't need to install glob.

If you do use glob-based helpers, install it alongside codumentation:

\`\`\`bash
npm install codumentation glob --save-dev
\`\`\``;

export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Verify glob is an optional peer dependency as documented
  if (!pkg.peerDependencies?.glob) {
    throw new Error('Documentation says glob is an optional peer dependency, but it is not listed in peerDependencies');
  }

  if (!pkg.peerDependenciesMeta?.glob?.optional) {
    throw new Error('Documentation says glob is optional, but peerDependenciesMeta.glob.optional is not true');
  }

  // Verify glob is not in regular dependencies
  if (pkg.dependencies?.glob) {
    throw new Error('glob should be in peerDependencies (optional), not in dependencies');
  }

  // Since glob is optional, our examples should use helpers, not direct glob imports
  // This prevents users from copying examples that won't work without installing glob
  const directGlobImportPattern = /import \{ glob \} from ['"]glob['"]/;

  // Check the guide file
  const guidePath = path.join(__dirname, '..', '.codumentation-guide.md');
  if (fs.existsSync(guidePath)) {
    const guideContent = fs.readFileSync(guidePath, 'utf-8');
    if (directGlobImportPattern.test(guideContent)) {
      throw new Error(
        '.codumentation-guide.md contains direct glob imports, but glob is optional.\n' +
        'Examples should use codumentation/helpers (e.g., assertGlobMatches) instead.'
      );
    }
  }

  // Check init.ts which generates the guide for new users
  const initPath = path.join(__dirname, '..', 'src', 'init.ts');
  const initContent = fs.readFileSync(initPath, 'utf-8');
  if (directGlobImportPattern.test(initContent)) {
    throw new Error(
      'src/init.ts generates examples with direct glob imports, but glob is optional.\n' +
      'Generated examples should use codumentation/helpers instead.'
    );
  }

  // Verify that helpers mentioned in documentation are actually exported
  const helpersPath = path.join(__dirname, '..', 'src', 'helpers.ts');
  const helpersContent = fs.readFileSync(helpersPath, 'utf-8');

  // Extract helper names mentioned in the guide
  const helperImportPattern = /import \{ (\w+) \} from ['"]codumentation\/helpers['"]/g;
  const mentionedHelpers = new Set<string>();

  if (fs.existsSync(guidePath)) {
    const guideContent = fs.readFileSync(guidePath, 'utf-8');
    let match;
    while ((match = helperImportPattern.exec(guideContent)) !== null) {
      mentionedHelpers.add(match[1]);
    }
  }

  // Also check init.ts for helper mentions
  helperImportPattern.lastIndex = 0;
  let match;
  while ((match = helperImportPattern.exec(initContent)) !== null) {
    mentionedHelpers.add(match[1]);
  }

  // Verify each mentioned helper is exported
  for (const helper of mentionedHelpers) {
    const exportPattern = new RegExp(`export (async )?function ${helper}\\b|export const ${helper}\\b`);
    if (!exportPattern.test(helpersContent)) {
      throw new Error(
        `Documentation mentions helper '${helper}' but it's not exported from src/helpers.ts`
      );
    }
  }
};

export const errorContent = `
[Bundler Configuration Validation Failed]

This validation ensures consistency between our optional glob dependency and documentation.

Possible issues:

1. **package.json misconfigured:**
   - "peerDependencies": { "glob": ">=10.0.0" }
   - "peerDependenciesMeta": { "glob": { "optional": true } }
   - glob should NOT be in regular dependencies

2. **Examples use direct glob imports:**
   - .codumentation-guide.md or src/init.ts contains: import { glob } from 'glob'
   - Since glob is optional, examples should use codumentation/helpers instead
   - Replace with: import { assertGlobMatches } from 'codumentation/helpers'

3. **Documentation references non-existent helpers:**
   - A helper function mentioned in docs isn't exported from src/helpers.ts
   - Either add the export or fix the documentation
`;
