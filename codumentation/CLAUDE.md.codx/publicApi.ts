import * as path from 'path';
import * as fs from 'fs';

const expectedTypeExports = [
  'CodxModule',
  'CodxTarget',
  'BuildResult',
  'ValidationResult',
  'LogEntry'
];

const expectedFunctionExports = [
  'discoverCodxTargets',
  'extractVariables',
  'loadCodxModule',
  'loadAllModules',
  'renderTemplate',
  'generateDiff',
  'validateTarget',
  'buildTarget',
  'logValidationFailure',
  'clearLog',
  'readLog'
];

export const content = `### Public API

The package exports all core functionality from \`src/index.ts\`:

- Types: \`CodxModule\`, \`CodxTarget\`, \`BuildResult\`, \`ValidationResult\`, \`LogEntry\`
- Discovery: \`discoverCodxTargets\`, \`extractVariables\`
- Loader: \`loadCodxModule\`, \`loadAllModules\`
- Renderer: \`renderTemplate\`, \`generateDiff\`
- Validator: \`validateTarget\`, \`buildTarget\`
- Logger: \`logValidationFailure\`, \`clearLog\`, \`readLog\`
`;

export const validate = async () => {
  const indexPath = path.join(__dirname, '..', 'dist', 'index.js');

  // Clear require cache to ensure fresh load
  delete require.cache[require.resolve(indexPath)];

  // Load the public API
  const publicApi = require(indexPath);

  // Validate function exports (types only exist at compile-time, not runtime)
  for (const funcName of expectedFunctionExports) {
    if (!(funcName in publicApi)) {
      throw new Error(
        `Public API (src/index.ts) is missing function export: ${funcName}`
      );
    }

    if (typeof publicApi[funcName] !== 'function') {
      throw new Error(
        `Public API export '${funcName}' is not a function (got ${typeof publicApi[funcName]})`
      );
    }
  }

  // Verify src/index.ts contains proper re-exports (including types)
  const indexSourcePath = path.join(__dirname, '..', 'src', 'index.ts');
  const indexContent = fs.readFileSync(indexSourcePath, 'utf-8');

  const requiredReExports = [
    "export * from './types'",
    "export * from './discovery'",
    "export * from './loader'",
    "export * from './renderer'",
    "export * from './validator'",
    "export * from './logger'"
  ];

  for (const reExport of requiredReExports) {
    if (!indexContent.includes(reExport)) {
      throw new Error(
        `src/index.ts is missing re-export: ${reExport}`
      );
    }
  }

  // Verify types are exported from types.ts (source-level check)
  const typesSourcePath = path.join(__dirname, '..', 'src', 'types.ts');
  const typesContent = fs.readFileSync(typesSourcePath, 'utf-8');

  for (const typeName of expectedTypeExports) {
    const exportPattern = new RegExp(`export (interface|type)\\s+${typeName}\\b`);
    if (!exportPattern.test(typesContent)) {
      throw new Error(
        `src/types.ts is missing type export: ${typeName}`
      );
    }
  }
};

export const errorContent = `
[Validation Failed] The public API documentation doesn't match actual exports from src/index.ts.

This is a critical issue because external consumers depend on these exports.

Action required:
1. Check if src/index.ts has all the documented re-exports
2. Ensure each re-exported module actually exports the claimed functions
3. If the API changed, update the documentation to match
4. Consider if this is a breaking change that requires a version bump
`;
