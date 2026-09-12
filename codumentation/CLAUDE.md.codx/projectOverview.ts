import * as fs from 'fs';
import * as path from 'path';

const codxReminder = `

**Note for AI Assistants**: This repository uses codumentation for its documentation. All .md files with corresponding .codx folders (e.g., CLAUDE.md.codx/, README.md.codx/) are generated from TypeScript modules. When making documentation changes:
1. Edit the .codx modules, not the generated .md files directly
2. Each .codx module exports: \`content\` (text), \`validate\` (verification function), and \`errorContent\` (error message)
3. Run \`npm run codumentation:validate\` to verify changes before committing
`;

export const content = `
Codumentation is a documentation validation tool that treats documentation as code.
It enforces a strict validation layer between the codebase state and written documentation.

**Core Philosophy**: "Codify Your Documentation"

Turn documentation claims into provable assertions. Every statement in your docs can be backed by validation code - if reality changes, your documentation build fails instead of silently becoming outdated.
${codxReminder}
`;

export const validate = async () => {
  // Verify package.json exists and has basic fields
  const pkgPath = path.join(__dirname, '..', 'package.json');
  if (!fs.existsSync(pkgPath)) {
    throw new Error('package.json not found');
  }

  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
  if (!pkg.name || !pkg.version) {
    throw new Error('package.json missing required fields');
  }

  // Verify .codx folders exist (self-hosting validation)
  const claudeCodxPath = path.join(__dirname, '..', 'CLAUDE.md.codx');
  const readmeCodxPath = path.join(__dirname, '..', 'README.md.codx');

  if (!fs.existsSync(claudeCodxPath)) {
    throw new Error('CLAUDE.md.codx directory not found - documentation claims self-hosting but directory missing');
  }

  if (!fs.existsSync(readmeCodxPath)) {
    throw new Error('README.md.codx directory not found - documentation claims self-hosting but directory missing');
  }

  // Verify the reminder about .codx folders is in content
  if (!content.includes('.codx')) {
    throw new Error('Missing reminder about .codx folders in project overview');
  }

  if (!content.includes('Note for AI Assistants')) {
    throw new Error('Missing "Note for AI Assistants" section about .codx usage');
  }

  // Verify the core philosophy is present
  if (!content.includes('Codify Your Documentation')) {
    throw new Error('Missing "Codify Your Documentation" core philosophy');
  }

  if (!content.includes('provable assertions')) {
    throw new Error('Missing supporting text about provable assertions');
  }
};

export const errorContent = `
[Validation Failed] Project overview validation failed. Either package.json is invalid or .codx directories are missing.
Ensure package.json exists with required fields and that CLAUDE.md.codx/ and README.md.codx/ directories exist.
`;
