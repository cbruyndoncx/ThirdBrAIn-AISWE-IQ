/**
 * Codumentation Helpers - Reusable validation functions for .codx modules
 *
 * These helpers wrap common validation patterns to make writing validate() functions
 * easier and more consistent. Import them in your .codx modules:
 *
 * ```typescript
 * import { assertFileExists, assertDependency } from 'codumentation/helpers';
 * ```
 */

import * as fs from 'fs';
import * as path from 'path';

// Lazy-loaded glob module for optional dependency
let globModule: typeof import('glob') | null = null;

/**
 * Lazily loads the glob module. Throws a helpful error if glob is not installed.
 * This allows codumentation to work without glob for users who don't use glob-based helpers.
 */
function getGlob(): typeof import('glob') {
  if (globModule) {
    return globModule;
  }

  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const loaded = require('glob') as typeof import('glob');
    globModule = loaded;
    return loaded;
  } catch {
    throw new Error(
      'The "glob" package is required for glob-based helpers.\n' +
      'Install it with: npm install glob\n\n' +
      'Note: If you don\'t use glob-based helpers (assertGlobMatches, assertNoGlobMatches, etc.), you don\'t need it.'
    );
  }
}

// ============================================================================
// File System Helpers
// ============================================================================

/**
 * Asserts that a file exists at the given path
 * @param filePath - Path to the file (relative to cwd or absolute)
 * @param message - Optional custom error message
 * @throws Error if file doesn't exist
 */
export function assertFileExists(filePath: string, message?: string): void {
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(message || `File not found: ${filePath}`);
  }
}

/**
 * Asserts that all files in the array exist
 * @param filePaths - Array of file paths to check
 * @param message - Optional custom error message prefix
 * @throws Error if any file doesn't exist
 */
export function assertFilesExist(filePaths: string[], message?: string): void {
  const missing: string[] = [];
  for (const filePath of filePaths) {
    const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
    if (!fs.existsSync(absolutePath)) {
      missing.push(filePath);
    }
  }
  if (missing.length > 0) {
    throw new Error(
      (message || 'Files not found') + `: ${missing.join(', ')}`
    );
  }
}

/**
 * Asserts that a directory exists at the given path
 * @param dirPath - Path to the directory
 * @param message - Optional custom error message
 * @throws Error if directory doesn't exist or is not a directory
 */
export function assertDirectoryExists(dirPath: string, message?: string): void {
  const absolutePath = path.isAbsolute(dirPath) ? dirPath : path.resolve(dirPath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(message || `Directory not found: ${dirPath}`);
  }
  const stats = fs.statSync(absolutePath);
  if (!stats.isDirectory()) {
    throw new Error(message || `Not a directory: ${dirPath}`);
  }
}

/**
 * Asserts that a path does NOT exist (useful for ensuring cleanup)
 * @param targetPath - Path that should not exist
 * @param message - Optional custom error message
 * @throws Error if path exists
 */
export function assertNotExists(targetPath: string, message?: string): void {
  const absolutePath = path.isAbsolute(targetPath) ? targetPath : path.resolve(targetPath);
  if (fs.existsSync(absolutePath)) {
    throw new Error(message || `Path should not exist: ${targetPath}`);
  }
}

// ============================================================================
// Glob Pattern Helpers
// ============================================================================

/**
 * Options for glob-based assertions
 */
export interface GlobOptions {
  cwd?: string;
  ignore?: string[];
}

/**
 * Asserts that a glob pattern matches at least one file
 * @param pattern - Glob pattern to match
 * @param options - Optional glob options
 * @returns Array of matching file paths
 * @throws Error if no files match
 */
export function assertGlobMatches(
  pattern: string,
  options: GlobOptions = {}
): string[] {
  const matches = getGlob().sync(pattern, {
    cwd: options.cwd || process.cwd(),
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  if (matches.length === 0) {
    throw new Error(`No files match pattern: ${pattern}`);
  }

  return matches;
}

/**
 * Asserts that a glob pattern matches NO files (useful for forbidden patterns)
 * @param pattern - Glob pattern that should not match anything
 * @param options - Optional glob options
 * @param message - Optional custom error message
 * @throws Error if any files match
 */
export function assertNoGlobMatches(
  pattern: string,
  options: GlobOptions = {},
  message?: string
): void {
  const matches = getGlob().sync(pattern, {
    cwd: options.cwd || process.cwd(),
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  if (matches.length > 0) {
    throw new Error(
      message || `Forbidden pattern found: ${pattern}\nMatching files: ${matches.slice(0, 5).join(', ')}${matches.length > 5 ? ` (+${matches.length - 5} more)` : ''}`
    );
  }
}

/**
 * Asserts that a glob pattern matches exactly N files
 * @param pattern - Glob pattern to match
 * @param expectedCount - Expected number of matches
 * @param options - Optional glob options
 * @throws Error if count doesn't match
 */
export function assertGlobCount(
  pattern: string,
  expectedCount: number,
  options: GlobOptions = {}
): string[] {
  const matches = getGlob().sync(pattern, {
    cwd: options.cwd || process.cwd(),
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  if (matches.length !== expectedCount) {
    throw new Error(
      `Expected ${expectedCount} files matching "${pattern}", found ${matches.length}` +
      (matches.length > 0 ? `\nMatches: ${matches.join(', ')}` : '')
    );
  }

  return matches;
}

/**
 * Asserts that a glob pattern matches at least N files
 * @param pattern - Glob pattern to match
 * @param minCount - Minimum number of matches
 * @param options - Optional glob options
 * @throws Error if count is less than minimum
 */
export function assertGlobMinCount(
  pattern: string,
  minCount: number,
  options: GlobOptions = {}
): string[] {
  const matches = getGlob().sync(pattern, {
    cwd: options.cwd || process.cwd(),
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  if (matches.length < minCount) {
    throw new Error(
      `Expected at least ${minCount} files matching "${pattern}", found ${matches.length}`
    );
  }

  return matches;
}

// ============================================================================
// Package.json Helpers
// ============================================================================

/**
 * Reads and parses package.json from a directory
 * @param dir - Directory containing package.json (defaults to cwd)
 * @returns Parsed package.json object
 * @throws Error if package.json not found or invalid
 */
export function readPackageJson(dir: string = process.cwd()): Record<string, any> {
  const pkgPath = path.join(dir, 'package.json');
  if (!fs.existsSync(pkgPath)) {
    throw new Error(`package.json not found in ${dir}`);
  }
  return JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
}

/**
 * Asserts that a dependency exists in package.json (either deps or devDeps)
 * @param name - Package name to check
 * @param dir - Directory containing package.json
 * @throws Error if dependency not found
 */
export function assertDependency(name: string, dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);
  const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };

  if (!allDeps[name]) {
    throw new Error(`Dependency "${name}" not found in package.json`);
  }
}

/**
 * Asserts that a dependency exists specifically in dependencies (not devDeps)
 * @param name - Package name to check
 * @param dir - Directory containing package.json
 * @throws Error if not in production dependencies
 */
export function assertProdDependency(name: string, dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);

  if (!pkg.dependencies?.[name]) {
    throw new Error(`"${name}" not found in production dependencies`);
  }
}

/**
 * Asserts that a dependency exists specifically in devDependencies
 * @param name - Package name to check
 * @param dir - Directory containing package.json
 * @throws Error if not in dev dependencies
 */
export function assertDevDependency(name: string, dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);

  if (!pkg.devDependencies?.[name]) {
    throw new Error(`"${name}" not found in devDependencies`);
  }
}

/**
 * Asserts that multiple dependencies exist
 * @param names - Array of package names to check
 * @param dir - Directory containing package.json
 * @throws Error if any dependency not found
 */
export function assertDependencies(names: string[], dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);
  const allDeps = { ...pkg.dependencies, ...pkg.devDependencies };

  const missing = names.filter(name => !allDeps[name]);
  if (missing.length > 0) {
    throw new Error(`Dependencies not found: ${missing.join(', ')}`);
  }
}

/**
 * Asserts that an npm script exists in package.json
 * @param name - Script name to check
 * @param dir - Directory containing package.json
 * @throws Error if script not found
 */
export function assertScript(name: string, dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);

  if (!pkg.scripts?.[name]) {
    throw new Error(`Script "${name}" not found in package.json`);
  }
}

/**
 * Asserts that multiple npm scripts exist
 * @param names - Array of script names to check
 * @param dir - Directory containing package.json
 * @throws Error if any script not found
 */
export function assertScripts(names: string[], dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);
  const missing = names.filter(name => !pkg.scripts?.[name]);

  if (missing.length > 0) {
    throw new Error(`Scripts not found: ${missing.join(', ')}`);
  }
}

/**
 * Asserts that a bin entry exists in package.json
 * @param name - Bin name to check
 * @param dir - Directory containing package.json
 * @throws Error if bin entry not found
 */
export function assertBin(name: string, dir: string = process.cwd()): void {
  const pkg = readPackageJson(dir);

  if (!pkg.bin?.[name]) {
    throw new Error(`Bin "${name}" not found in package.json`);
  }
}

/**
 * Gets the package version from package.json
 * @param dir - Directory containing package.json
 * @returns The version string
 */
export function getPackageVersion(dir: string = process.cwd()): string {
  const pkg = readPackageJson(dir);
  return pkg.version || '0.0.0';
}

/**
 * Gets the package name from package.json
 * @param dir - Directory containing package.json
 * @returns The package name
 */
export function getPackageName(dir: string = process.cwd()): string {
  const pkg = readPackageJson(dir);
  return pkg.name || '';
}

// ============================================================================
// File Content Helpers
// ============================================================================

/**
 * Asserts that a file contains a specific string
 * @param filePath - Path to the file
 * @param searchString - String that should be in the file
 * @param message - Optional custom error message
 * @throws Error if string not found in file
 */
export function assertFileContains(
  filePath: string,
  searchString: string,
  message?: string
): void {
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const content = fs.readFileSync(absolutePath, 'utf-8');
  if (!content.includes(searchString)) {
    throw new Error(
      message || `File "${filePath}" does not contain expected string: "${searchString.substring(0, 50)}${searchString.length > 50 ? '...' : ''}"`
    );
  }
}

/**
 * Asserts that a file does NOT contain a specific string (for forbidden patterns)
 * @param filePath - Path to the file
 * @param searchString - String that should NOT be in the file
 * @param message - Optional custom error message
 * @throws Error if string IS found in file
 */
export function assertFileNotContains(
  filePath: string,
  searchString: string,
  message?: string
): void {
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    return; // File doesn't exist, so it doesn't contain the string
  }

  const content = fs.readFileSync(absolutePath, 'utf-8');
  if (content.includes(searchString)) {
    throw new Error(
      message || `File "${filePath}" contains forbidden string: "${searchString.substring(0, 50)}${searchString.length > 50 ? '...' : ''}"`
    );
  }
}

/**
 * Asserts that a file content matches a regex pattern
 * @param filePath - Path to the file
 * @param pattern - Regex pattern to match
 * @param message - Optional custom error message
 * @throws Error if pattern not found
 */
export function assertFileMatches(
  filePath: string,
  pattern: RegExp,
  message?: string
): RegExpMatchArray {
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const content = fs.readFileSync(absolutePath, 'utf-8');
  const match = content.match(pattern);

  if (!match) {
    throw new Error(
      message || `File "${filePath}" does not match pattern: ${pattern}`
    );
  }

  return match;
}

/**
 * Asserts that a file does NOT match a regex pattern (for forbidden patterns)
 * @param filePath - Path to the file
 * @param pattern - Regex pattern that should NOT match
 * @param message - Optional custom error message
 * @throws Error if pattern IS found
 */
export function assertFileNotMatches(
  filePath: string,
  pattern: RegExp,
  message?: string
): void {
  const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    return; // File doesn't exist, so it doesn't match
  }

  const content = fs.readFileSync(absolutePath, 'utf-8');
  const match = content.match(pattern);

  if (match) {
    throw new Error(
      message || `File "${filePath}" matches forbidden pattern: ${pattern}\nMatch: "${match[0].substring(0, 100)}${match[0].length > 100 ? '...' : ''}"`
    );
  }
}

// ============================================================================
// Code Quality Helpers
// ============================================================================

/**
 * Asserts that NO file matching glob contains the regex pattern (forbidden code patterns)
 * @param globPattern - Glob pattern to find files
 * @param regex - Regex pattern that should NOT be found
 * @param message - Optional custom error message
 * @param options - Optional glob options
 * @throws Error if pattern found in any file
 */
export function assertNoCodePattern(
  globPattern: string,
  regex: RegExp,
  message?: string,
  options: GlobOptions = {}
): void {
  const files = getGlob().sync(globPattern, {
    cwd: options.cwd || process.cwd(),
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  const violations: Array<{ file: string; match: string; line: number }> = [];

  for (const file of files) {
    const absolutePath = path.isAbsolute(file) ? file : path.resolve(options.cwd || process.cwd(), file);
    const content = fs.readFileSync(absolutePath, 'utf-8');
    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const match = lines[i].match(regex);
      if (match) {
        violations.push({
          file,
          match: match[0],
          line: i + 1
        });
      }
    }
  }

  if (violations.length > 0) {
    const details = violations
      .slice(0, 5)
      .map(v => `  ${v.file}:${v.line} - "${v.match}"`)
      .join('\n');

    throw new Error(
      (message || `Forbidden pattern found`) +
      `\n${details}` +
      (violations.length > 5 ? `\n  (+${violations.length - 5} more violations)` : '')
    );
  }
}

/**
 * Asserts that ALL files matching glob contain the regex pattern
 * @param globPattern - Glob pattern to find files
 * @param regex - Regex pattern that SHOULD be found
 * @param message - Optional custom error message
 * @param options - Optional glob options
 * @throws Error if pattern not found in any file
 */
export function assertCodePattern(
  globPattern: string,
  regex: RegExp,
  message?: string,
  options: GlobOptions = {}
): void {
  const files = getGlob().sync(globPattern, {
    cwd: options.cwd || process.cwd(),
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  if (files.length === 0) {
    throw new Error(`No files match pattern: ${globPattern}`);
  }

  const missing: string[] = [];

  for (const file of files) {
    const absolutePath = path.isAbsolute(file) ? file : path.resolve(options.cwd || process.cwd(), file);
    const content = fs.readFileSync(absolutePath, 'utf-8');

    if (!regex.test(content)) {
      missing.push(file);
    }
  }

  if (missing.length > 0) {
    throw new Error(
      (message || `Required pattern not found in files`) +
      `\nMissing in: ${missing.slice(0, 5).join(', ')}` +
      (missing.length > 5 ? ` (+${missing.length - 5} more)` : '')
    );
  }
}

// ============================================================================
// TypeScript Config Helpers
// ============================================================================

/**
 * Reads and parses tsconfig.json
 * @param dir - Directory containing tsconfig.json
 * @returns Parsed tsconfig object
 * @throws Error if tsconfig not found or invalid
 */
export function readTsConfig(dir: string = process.cwd()): Record<string, any> {
  const tsconfigPath = path.join(dir, 'tsconfig.json');
  if (!fs.existsSync(tsconfigPath)) {
    throw new Error(`tsconfig.json not found in ${dir}`);
  }

  // Read and strip comments (tsconfig allows comments)
  let content = fs.readFileSync(tsconfigPath, 'utf-8');
  // Remove single-line comments
  content = content.replace(/\/\/.*$/gm, '');
  // Remove multi-line comments
  content = content.replace(/\/\*[\s\S]*?\*\//g, '');

  return JSON.parse(content);
}

/**
 * Asserts that TypeScript strict mode is enabled
 * @param dir - Directory containing tsconfig.json
 * @throws Error if strict mode not enabled
 */
export function assertStrictMode(dir: string = process.cwd()): void {
  const tsconfig = readTsConfig(dir);

  if (!tsconfig.compilerOptions?.strict) {
    throw new Error('TypeScript strict mode is not enabled in tsconfig.json');
  }
}

/**
 * Asserts a specific tsconfig compiler option has expected value
 * @param option - Compiler option name (e.g., 'target', 'module')
 * @param expectedValue - Expected value
 * @param dir - Directory containing tsconfig.json
 * @throws Error if option doesn't match
 */
export function assertTsConfigOption(
  option: string,
  expectedValue: any,
  dir: string = process.cwd()
): void {
  const tsconfig = readTsConfig(dir);
  const actualValue = tsconfig.compilerOptions?.[option];

  if (actualValue !== expectedValue) {
    throw new Error(
      `tsconfig.json compilerOptions.${option} is "${actualValue}", expected "${expectedValue}"`
    );
  }
}

// ============================================================================
// Folder Structure Helpers
// ============================================================================

/**
 * Asserts that a directory structure matches expected layout
 * @param expectedStructure - Object describing expected structure
 * @param rootDir - Root directory to check
 * @throws Error if structure doesn't match
 *
 * @example
 * assertFolderStructure({
 *   'src': {
 *     'index.ts': 'file',
 *     'types': 'dir',
 *     'utils': 'dir'
 *   },
 *   'tests': 'dir',
 *   'package.json': 'file'
 * });
 */
export function assertFolderStructure(
  expectedStructure: Record<string, 'file' | 'dir' | Record<string, any>>,
  rootDir: string = process.cwd()
): void {
  const missing: string[] = [];
  const wrongType: string[] = [];

  function check(structure: Record<string, any>, currentPath: string) {
    for (const [name, expected] of Object.entries(structure)) {
      const fullPath = path.join(currentPath, name);
      const relativePath = path.relative(rootDir, fullPath);

      if (!fs.existsSync(fullPath)) {
        missing.push(relativePath);
        continue;
      }

      const stats = fs.statSync(fullPath);

      if (expected === 'file') {
        if (!stats.isFile()) {
          wrongType.push(`${relativePath} (expected file, got directory)`);
        }
      } else if (expected === 'dir') {
        if (!stats.isDirectory()) {
          wrongType.push(`${relativePath} (expected directory, got file)`);
        }
      } else if (typeof expected === 'object') {
        if (!stats.isDirectory()) {
          wrongType.push(`${relativePath} (expected directory, got file)`);
        } else {
          check(expected, fullPath);
        }
      }
    }
  }

  check(expectedStructure, rootDir);

  if (missing.length > 0 || wrongType.length > 0) {
    let message = 'Folder structure validation failed:\n';
    if (missing.length > 0) {
      message += `  Missing: ${missing.join(', ')}\n`;
    }
    if (wrongType.length > 0) {
      message += `  Wrong type: ${wrongType.join(', ')}`;
    }
    throw new Error(message);
  }
}

/**
 * Asserts that there's only one directory matching a pattern (e.g., single components folder)
 * @param pattern - Directory name or glob pattern
 * @param options - Optional glob options
 * @throws Error if multiple directories found
 */
export function assertSingleDirectory(
  pattern: string,
  options: GlobOptions = {}
): string {
  const cwd = options.cwd || process.cwd();
  const allMatches = getGlob().sync(`**/${pattern}`, {
    cwd,
    ignore: options.ignore || ['node_modules/**', 'dist/**', '.git/**']
  });

  // Filter to only directories
  const matches = allMatches.filter(match => {
    const fullPath = path.isAbsolute(match) ? match : path.join(cwd, match);
    try {
      return fs.statSync(fullPath).isDirectory();
    } catch {
      return false;
    }
  });

  if (matches.length === 0) {
    throw new Error(`No directory matching "${pattern}" found`);
  }

  if (matches.length > 1) {
    throw new Error(
      `Expected single "${pattern}" directory but found ${matches.length}: ${matches.join(', ')}`
    );
  }

  return matches[0];
}

// ============================================================================
// Export Validation Helpers
// ============================================================================

/**
 * Asserts that a module exports specific named exports
 * @param modulePath - Path to the module
 * @param expectedExports - Array of expected export names
 * @throws Error if exports don't match
 */
export function assertModuleExports(
  modulePath: string,
  expectedExports: string[]
): void {
  const absolutePath = path.isAbsolute(modulePath) ? modulePath : path.resolve(modulePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`Module not found: ${modulePath}`);
  }

  const content = fs.readFileSync(absolutePath, 'utf-8');
  const missing: string[] = [];

  for (const exp of expectedExports) {
    // Check for various export patterns
    const patterns = [
      new RegExp(`export\\s+(?:const|function|class|type|interface|enum)\\s+${exp}\\b`),
      new RegExp(`export\\s*\\{[^}]*\\b${exp}\\b[^}]*\\}`),
      new RegExp(`export\\s+\\*\\s+from`) // re-export all
    ];

    const found = patterns.some(p => p.test(content));
    if (!found) {
      missing.push(exp);
    }
  }

  if (missing.length > 0) {
    throw new Error(
      `Module "${modulePath}" missing expected exports: ${missing.join(', ')}`
    );
  }
}

// ============================================================================
// Composite Helpers
// ============================================================================

/**
 * Creates a validator function that checks multiple conditions
 * @param validators - Array of validation functions
 * @returns A combined validation function
 */
export function combineValidators(
  ...validators: Array<() => void | Promise<void>>
): () => Promise<void> {
  return async () => {
    for (const validator of validators) {
      await validator();
    }
  };
}
