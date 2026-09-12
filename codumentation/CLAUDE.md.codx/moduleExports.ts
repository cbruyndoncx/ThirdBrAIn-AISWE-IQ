import * as path from 'path';

// Define expected exports for each module
const expectedExports = {
  'dist/discovery.js': ['discoverCodxTargets', 'extractVariables'],
  'dist/loader.js': ['loadCodxModule', 'loadAllModules'],
  'dist/renderer.js': ['renderTemplate', 'generateDiff'],
  'dist/validator.js': ['validateTarget', 'buildTarget'],
  'dist/logger.js': ['logValidationFailure', 'clearLog', 'readLog']
};

export const content = `### Exported Functions

Each core module exports the following key functions:

- **discovery.ts**: \`discoverCodxTargets\`, \`extractVariables\`
- **loader.ts**: \`loadCodxModule\`, \`loadAllModules\`
- **renderer.ts**: \`renderTemplate\`, \`generateDiff\`
- **validator.ts**: \`validateTarget\`, \`buildTarget\`
- **logger.ts**: \`logValidationFailure\`, \`clearLog\`, \`readLog\`
`;

export const validate = async () => {
  // Import each module and verify exports exist
  for (const [modulePath, expectedFunctions] of Object.entries(expectedExports)) {
    const fullPath = path.join(__dirname, '..', modulePath);

    try {
      // Clear require cache to ensure fresh load
      delete require.cache[require.resolve(fullPath)];

      // Load the module
      const module = require(fullPath);

      // Check each expected function
      for (const funcName of expectedFunctions) {
        if (!(funcName in module)) {
          throw new Error(
            `Module ${modulePath} is missing expected export: ${funcName}`
          );
        }

        if (typeof module[funcName] !== 'function') {
          throw new Error(
            `Module ${modulePath} export '${funcName}' is not a function (got ${typeof module[funcName]})`
          );
        }
      }
    } catch (error) {
      if ((error as any).code === 'MODULE_NOT_FOUND') {
        throw new Error(`Module not found: ${modulePath}`);
      }
      throw error;
    }
  }
};

export const errorContent = `
[Validation Failed] Documented function exports don't match actual module exports.

This means one of the following:
1. A documented function doesn't exist in the module
2. A function exists but isn't exported
3. An exported name is misspelled or has changed

Action required:
- If the code changed, update the documentation in CLAUDE.md.codx/moduleExports.ts
- If the documentation is wrong, fix the function names to match the actual exports
`;
