import * as fs from 'fs';
import * as path from 'path';
import { CodxTarget } from './types';

/**
 * Directories to ignore when searching for .codx folders
 */
const IGNORED_DIRS = new Set(['node_modules', 'dist', '.git']);

/**
 * Checks if a path should be ignored based on its components
 */
function shouldIgnore(relativePath: string): boolean {
  const parts = relativePath.split(path.sep);
  return parts.some(part => IGNORED_DIRS.has(part));
}

/**
 * Discovers all .codx directories in the given root directory
 * Uses native fs.readdir with recursive option (Node 18+) instead of glob
 * @param rootDir The root directory to search (defaults to current working directory)
 * @returns Array of CodxTarget objects
 */
export async function discoverCodxTargets(rootDir: string = process.cwd()): Promise<CodxTarget[]> {
  // Find all directories ending with .codx using native fs.readdir
  const entries = await fs.promises.readdir(rootDir, { recursive: true, withFileTypes: true });

  const codxDirs = entries
    .filter(entry => entry.isDirectory() && entry.name.endsWith('.codx'))
    .map(entry => {
      // entry.parentPath is available in Node 20.1+, entry.path in Node 18.17-20.0
      // These contain the directory path (absolute if rootDir was absolute)
      const parentPath = (entry as any).parentPath ?? (entry as any).path ?? rootDir;
      return path.join(parentPath, entry.name);
    })
    .filter(fullPath => !shouldIgnore(path.relative(rootDir, fullPath)));

  const targets: CodxTarget[] = [];

  for (const codxDir of codxDirs) {

    // The target file is the .codx directory name without the .codx extension
    // e.g., "README.md.codx" -> "README.md"
    const targetFile = codxDir.replace(/\.codx$/, '');

    // Check if index.md exists
    const templateFile = path.join(codxDir, 'index.md');
    if (!fs.existsSync(templateFile)) {
      console.warn(`Warning: ${codxDir} is missing index.md, skipping...`);
      continue;
    }

    // Read the template to find variable references
    const templateContent = fs.readFileSync(templateFile, 'utf-8');
    const variables = extractVariables(templateContent);

    // Map variables to their TypeScript module files
    const modules = new Map<string, string>();
    for (const varName of variables) {
      const modulePath = path.join(codxDir, `${varName}.ts`);
      if (fs.existsSync(modulePath)) {
        modules.set(varName, modulePath);
      } else {
        throw new Error(
          `Template references variable '${varName}' but ${varName}.ts not found in ${codxDir}`
        );
      }
    }

    targets.push({
      targetFile,
      codxDir,
      templateFile,
      modules
    });
  }

  return targets;
}

/**
 * Extracts variable references from a template string
 * Variables are in the format {{ variableName }}
 * @param template The template string
 * @returns Array of unique variable names
 */
export function extractVariables(template: string): string[] {
  const regex = /\{\{\s*(\w+)\s*\}\}/g;
  const variables = new Set<string>();
  let match;

  while ((match = regex.exec(template)) !== null) {
    variables.add(match[1]);
  }

  return Array.from(variables);
}
