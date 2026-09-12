import * as path from 'path';
import * as fs from 'fs';

const expectedCommands = ['validate', 'build'];

export const content = `### CLI Commands

The CLI (src/cli.ts) provides two main commands:

1. **validate** - Validates all documentation against the codebase
2. **build** - Builds/regenerates all documentation files

Both commands are implemented using Commander.js and properly registered in the program.
`;

export const validate = async () => {
  const cliPath = path.join(__dirname, '..', 'src', 'cli.ts');

  if (!fs.existsSync(cliPath)) {
    throw new Error('CLI file not found: src/cli.ts');
  }

  // Read the CLI file to verify commands are registered
  const cliContent = fs.readFileSync(cliPath, 'utf-8');

  // Check for commander import
  if (!cliContent.includes("from 'commander'")) {
    throw new Error('CLI must import from commander');
  }

  // Check that each expected command is registered
  for (const cmd of expectedCommands) {
    const commandPattern = new RegExp(
      `\\.command\\s*\\(\\s*['"\`]${cmd}['"\`]\\s*\\)`,
      'm'
    );

    if (!commandPattern.test(cliContent)) {
      throw new Error(
        `CLI command '${cmd}' is not registered in src/cli.ts`
      );
    }
  }

  // Verify shebang for executable
  if (!cliContent.startsWith('#!/usr/bin/env node')) {
    throw new Error('CLI file must start with shebang: #!/usr/bin/env node');
  }

  // Verify the CLI calls the correct functions
  const requiredImports = [
    'discoverCodxTargets',
    'validateTarget',
    'buildTarget'
  ];

  for (const importName of requiredImports) {
    if (!cliContent.includes(importName)) {
      throw new Error(
        `CLI must import and use function: ${importName}`
      );
    }
  }

  // Verify bin entry in package.json matches
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  if (!pkg.bin?.codumentation) {
    throw new Error('package.json missing bin.codumentation entry');
  }

  // Check that bin points to compiled CLI
  if (!pkg.bin.codumentation.includes('cli.js')) {
    throw new Error(
      `bin.codumentation should point to cli.js, got: ${pkg.bin.codumentation}`
    );
  }
};

export const errorContent = `
[Validation Failed] CLI commands documentation doesn't match implementation in src/cli.ts.

This could mean:
1. A documented command isn't registered with Commander.js
2. The CLI is missing required imports from other modules
3. The shebang is missing or incorrect
4. package.json bin entry doesn't point to the CLI

Action required:
- Check that src/cli.ts registers all documented commands
- Ensure the CLI imports and uses validateTarget, buildTarget, etc.
- Verify package.json bin entry points to dist/cli.js
`;
