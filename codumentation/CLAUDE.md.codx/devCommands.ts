import * as fs from 'fs';
import * as path from 'path';

const commands = {
  build: 'npm run build',
  test: 'npm test',
  validateDocs: 'npm run codumentation:validate',
  buildDocs: 'npm run codumentation:build'
};

const importantNote = `**IMPORTANT**: After making any changes to the codebase, always run \`${commands.validateDocs}\` to ensure the documentation remains valid and in sync with the code. This is a core principle of the "Validate First, Generate Second" philosophy - if validation fails, the documentation needs to be updated before proceeding.`;

export const content = `
- **Build**: \`${commands.build}\` - Compile TypeScript to dist/
- **Test**: \`${commands.test}\` - Run test suite with Vitest
- **Validate Docs**: \`${commands.validateDocs}\` - Check docs are up-to-date
- **Build Docs**: \`${commands.buildDocs}\` - Regenerate documentation files

${importantNote}
`;

export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Verify build script
  if (!pkg.scripts?.build) {
    throw new Error('Missing "build" script in package.json');
  }

  // Verify test script
  if (!pkg.scripts?.test) {
    throw new Error('Missing "test" script in package.json');
  }

  // Verify codumentation:validate script
  if (!pkg.scripts?.['codumentation:validate']) {
    throw new Error('Missing "codumentation:validate" script in package.json');
  }

  // Verify codumentation:build script
  if (!pkg.scripts?.['codumentation:build']) {
    throw new Error('Missing "codumentation:build" script in package.json');
  }

  // Verify the scripts use the codumentation command
  const validateScript = pkg.scripts['codumentation:validate'];
  const buildScript = pkg.scripts['codumentation:build'];

  if (!validateScript.includes('codumentation validate')) {
    throw new Error('The "codumentation:validate" script should run "codumentation validate"');
  }

  if (!buildScript.includes('codumentation build')) {
    throw new Error('The "codumentation:build" script should run "codumentation build"');
  }

  // Verify bin entry for codumentation
  if (!pkg.bin?.codumentation) {
    throw new Error('Missing "codumentation" bin entry in package.json');
  }

  // Verify the IMPORTANT note is in the generated content
  if (!content.includes('IMPORTANT')) {
    throw new Error('Missing IMPORTANT note about running validation after changes');
  }

  if (!content.includes('npm run codumentation:validate')) {
    throw new Error('IMPORTANT note should reference the npm run codumentation:validate command');
  }
};

export const errorContent = `
[Validation Failed] Development commands reference scripts that don't exist in package.json or the validation reminder is missing.
Update package.json scripts (codumentation:validate, codumentation:build) to match documented commands and ensure the IMPORTANT note is present.
`;
