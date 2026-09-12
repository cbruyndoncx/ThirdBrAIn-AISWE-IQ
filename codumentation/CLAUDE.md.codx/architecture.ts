import * as fs from 'fs';
import * as path from 'path';

export const content = `
### Core Components

1. **Discovery** (\`src/discovery.ts\`): Finds all .codx directories and parses templates
2. **Loader** (\`src/loader.ts\`): Compiles and loads TypeScript modules at runtime using ts-node
3. **Renderer** (\`src/renderer.ts\`): Template engine for variable substitution
4. **Validator** (\`src/validator.ts\`): Orchestrates validation and build processes
5. **Logger** (\`src/logger.ts\`): Logs validation failures to .codumentation.log
6. **CLI** (\`src/cli.ts\`): Command-line interface

### Module Interface

Each .codx module must export:
- \`content\`: string - The content to inject
- \`validate\`: async function - Throws if validation fails
- \`errorContent\`: string - Human-readable error explanation
`;

export const validate = async () => {
  // Verify all core files exist
  const coreFiles = [
    'src/discovery.ts',
    'src/loader.ts',
    'src/renderer.ts',
    'src/validator.ts',
    'src/logger.ts',
    'src/cli.ts'
  ];

  for (const file of coreFiles) {
    const filePath = path.join(__dirname, '..', file);
    if (!fs.existsSync(filePath)) {
      throw new Error('Core file missing: ' + file);
    }
  }

  // Verify types file exports CodxModule interface
  const typesPath = path.join(__dirname, '..', 'src', 'types.ts');
  const typesContent = fs.readFileSync(typesPath, 'utf-8');
  if (!typesContent.includes('interface CodxModule')) {
    throw new Error('types.ts missing CodxModule interface');
  }
};

export const errorContent = `
[Validation Failed] Architecture section describes files that don't exist or are missing required exports.
Ensure all core files exist and types are properly defined.
`;
