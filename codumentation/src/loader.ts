import { register } from 'ts-node';
import * as path from 'path';
import { CodxModule } from './types';

// Register ts-node for runtime TypeScript compilation
let tsNodeRegistered = false;

function ensureTsNodeRegistered() {
  if (!tsNodeRegistered) {
    register({
      transpileOnly: true,
      // Don't load project tsconfig - use our own settings
      skipProject: true,
      compilerOptions: {
        module: 'commonjs',
        moduleResolution: 'node',
        target: 'es2020',
        esModuleInterop: true,
        skipLibCheck: true,
        allowSyntheticDefaultImports: true,
        resolveJsonModule: true,
        lib: ['es2020']
      }
    });
    tsNodeRegistered = true;
  }
}

/**
 * Loads a TypeScript module and validates it implements the CodxModule interface
 * @param modulePath Absolute path to the TypeScript module
 * @returns The loaded CodxModule
 * @throws Error if the module doesn't implement the required interface
 */
export async function loadCodxModule(modulePath: string): Promise<CodxModule> {
  ensureTsNodeRegistered();

  // Clear require cache to ensure fresh load
  delete require.cache[require.resolve(modulePath)];

  // Load the module
  const module = require(modulePath);

  // Validate the module exports
  validateCodxModule(module, modulePath);

  return module as CodxModule;
}

/**
 * Validates that a loaded module implements the CodxModule interface
 * @param module The loaded module object
 * @param modulePath Path to the module (for error messages)
 * @throws Error if validation fails
 */
function validateCodxModule(module: any, modulePath: string): void {
  const moduleName = path.basename(modulePath, '.ts');

  // Check for 'content' export
  if (!('content' in module)) {
    throw new Error(
      `Module ${moduleName} must export 'content' (string)\n` +
      `File: ${modulePath}`
    );
  }

  if (typeof module.content !== 'string') {
    throw new Error(
      `Module ${moduleName} 'content' must be a string, got ${typeof module.content}\n` +
      `File: ${modulePath}`
    );
  }

  // Check for 'validate' export
  if (!('validate' in module)) {
    throw new Error(
      `Module ${moduleName} must export 'validate' (function)\n` +
      `File: ${modulePath}`
    );
  }

  if (typeof module.validate !== 'function') {
    throw new Error(
      `Module ${moduleName} 'validate' must be a function, got ${typeof module.validate}\n` +
      `File: ${modulePath}`
    );
  }

  // Check for 'errorContent' export
  if (!('errorContent' in module)) {
    throw new Error(
      `Module ${moduleName} must export 'errorContent' (string)\n` +
      `File: ${modulePath}`
    );
  }

  if (typeof module.errorContent !== 'string') {
    throw new Error(
      `Module ${moduleName} 'errorContent' must be a string, got ${typeof module.errorContent}\n` +
      `File: ${modulePath}`
    );
  }
}

/**
 * Loads all modules for a given target
 * @param modules Map of variable names to module paths
 * @returns Map of variable names to loaded CodxModule objects
 */
export async function loadAllModules(
  modules: Map<string, string>
): Promise<Map<string, CodxModule>> {
  const loadedModules = new Map<string, CodxModule>();

  for (const [varName, modulePath] of modules.entries()) {
    const module = await loadCodxModule(modulePath);
    loadedModules.set(varName, module);
  }

  return loadedModules;
}
