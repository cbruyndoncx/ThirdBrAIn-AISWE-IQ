import * as fs from 'fs';
import * as path from 'path';

// List of helper functions that should be documented and exported
const DOCUMENTED_HELPERS = [
  'assertFileExists',
  'assertFilesExist',
  'assertDirectoryExists',
  'assertGlobMatches',
  'assertNoGlobMatches',
  'assertDependency',
  'assertDevDependency',
  'assertScript',
  'assertFileContains',
  'assertNoCodePattern',
  'assertStrictMode',
  'assertFolderStructure'
];

export const content = `## Helper Functions

Codumentation provides helper functions for common validation patterns.

\`\`\`typescript
import {
  assertFileExists,
  assertDependency,
  assertNoCodePattern
} from 'codumentation/helpers';
\`\`\`

### File System Helpers

| Function | Description |
|----------|-------------|
| \`assertFileExists(path)\` | Throws if file doesn't exist |
| \`assertFilesExist(paths[])\` | Throws if any file is missing |
| \`assertDirectoryExists(path)\` | Throws if directory doesn't exist |
| \`assertNotExists(path)\` | Throws if path exists (for cleanup checks) |

### Glob Pattern Helpers

| Function | Description |
|----------|-------------|
| \`assertGlobMatches(pattern)\` | Throws if no files match; returns matches |
| \`assertNoGlobMatches(pattern)\` | Throws if files DO match (forbidden patterns) |
| \`assertGlobCount(pattern, n)\` | Throws if match count != n |
| \`assertGlobMinCount(pattern, n)\` | Throws if match count < n |

### Package.json Helpers

| Function | Description |
|----------|-------------|
| \`assertDependency(name)\` | Throws if package not in deps/devDeps |
| \`assertProdDependency(name)\` | Throws if not in production deps |
| \`assertDevDependency(name)\` | Throws if not in devDependencies |
| \`assertScript(name)\` | Throws if npm script doesn't exist |
| \`assertBin(name)\` | Throws if bin entry doesn't exist |

### Content Helpers

| Function | Description |
|----------|-------------|
| \`assertFileContains(path, str)\` | Throws if file doesn't contain string |
| \`assertFileNotContains(path, str)\` | Throws if file contains string |
| \`assertFileMatches(path, regex)\` | Throws if file doesn't match pattern |
| \`assertNoCodePattern(glob, regex)\` | Throws if pattern found in any file |
| \`assertCodePattern(glob, regex)\` | Throws if pattern NOT found in files |

### TypeScript Helpers

| Function | Description |
|----------|-------------|
| \`assertStrictMode()\` | Throws if TypeScript strict mode disabled |
| \`assertTsConfigOption(opt, val)\` | Throws if tsconfig option != value |

### Structure Helpers

| Function | Description |
|----------|-------------|
| \`assertFolderStructure(spec)\` | Validates directory structure matches spec |
| \`assertSingleDirectory(name)\` | Throws if multiple directories with name exist |

### Example Usage

\`\`\`typescript
export const validate = async () => {
  // Verify all mentioned files exist
  assertFilesExist(['src/index.ts', 'src/cli.ts', 'package.json']);

  // Verify no console.log in production code
  assertNoCodePattern('src/**/*.ts', /console\\.log/, 'Remove console.log from production');

  // Verify TypeScript strict mode
  assertStrictMode();

  // Verify folder structure
  assertFolderStructure({
    'src': { 'index.ts': 'file', 'types.ts': 'file' },
    'tests': 'dir',
    'package.json': 'file'
  });
};
\`\`\``;

export const validate = async () => {
  const helpersPath = path.join(__dirname, '..', 'src', 'helpers.ts');

  if (!fs.existsSync(helpersPath)) {
    throw new Error('helpers.ts file does not exist');
  }

  const helpersContent = fs.readFileSync(helpersPath, 'utf-8');

  // Verify all documented helpers are actually exported
  const missingExports: string[] = [];
  for (const helper of DOCUMENTED_HELPERS) {
    const exportPattern = new RegExp(`export\\s+function\\s+${helper}\\b`);
    if (!exportPattern.test(helpersContent)) {
      missingExports.push(helper);
    }
  }

  if (missingExports.length > 0) {
    throw new Error(
      `README documents helpers that aren't exported: ${missingExports.join(', ')}`
    );
  }

  // Verify package.json exports ./helpers path
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  if (!pkg.exports?.['./helpers']) {
    throw new Error('package.json must export ./helpers for import path to work');
  }
};

export const errorContent = `
[Helper Functions Validation Failed]

The README documents helper functions that aren't actually exported.

Ensure all documented helpers exist in src/helpers.ts with 'export function' declarations.
Also ensure package.json has exports["./helpers"] configured.
`;
