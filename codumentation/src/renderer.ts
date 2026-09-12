import * as fs from 'fs';
import { CodxModule } from './types';

/**
 * Renders a template by replacing variables with module content
 * @param templatePath Path to the index.md template file
 * @param modules Map of variable names to loaded CodxModule objects
 * @returns The rendered markdown content
 */
export function renderTemplate(
  templatePath: string,
  modules: Map<string, CodxModule>
): string {
  const template = fs.readFileSync(templatePath, 'utf-8');

  let rendered = template;

  // Replace each {{ variableName }} with the corresponding module.content
  for (const [varName, module] of modules.entries()) {
    const regex = new RegExp(`\\{\\{\\s*${varName}\\s*\\}\\}`, 'g');
    rendered = rendered.replace(regex, module.content);
  }

  // Check for any unreplaced variables
  const unreplacedVars = rendered.match(/\{\{\s*(\w+)\s*\}\}/g);
  if (unreplacedVars) {
    const varNames = unreplacedVars.map(v => v.replace(/\{\{\s*|\s*\}\}/g, ''));
    throw new Error(
      `Template contains variables without corresponding modules: ${varNames.join(', ')}\n` +
      `Template: ${templatePath}`
    );
  }

  return rendered;
}

/**
 * Compares two strings and returns a simple diff message
 * @param expected The expected content
 * @param actual The actual content
 * @returns A diff message showing the first difference
 */
export function generateDiff(expected: string, actual: string): string {
  if (expected === actual) {
    return 'No differences';
  }

  const expectedLines = expected.split('\n');
  const actualLines = actual.split('\n');

  // Find first differing line
  for (let i = 0; i < Math.max(expectedLines.length, actualLines.length); i++) {
    const expLine = expectedLines[i] ?? '(missing)';
    const actLine = actualLines[i] ?? '(missing)';

    if (expLine !== actLine) {
      return [
        `First difference at line ${i + 1}:`,
        `  Expected: ${expLine.substring(0, 100)}${expLine.length > 100 ? '...' : ''}`,
        `  Actual:   ${actLine.substring(0, 100)}${actLine.length > 100 ? '...' : ''}`,
        '',
        `Total lines - Expected: ${expectedLines.length}, Actual: ${actualLines.length}`
      ].join('\n');
    }
  }

  return 'Content differs but line-by-line comparison found no differences';
}
