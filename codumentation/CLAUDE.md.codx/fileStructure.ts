import * as fs from 'fs';
import * as path from 'path';

export const content = `
\`\`\`
codumentation/
├── src/
│   ├── types.ts          # Type definitions
│   ├── discovery.ts      # Find .codx directories
│   ├── loader.ts         # Load and validate modules
│   ├── renderer.ts       # Template rendering
│   ├── validator.ts      # Validation orchestration
│   ├── logger.ts         # Logging system
│   ├── cli.ts           # CLI entry point
│   └── index.ts         # Public API exports
├── tests/
│   ├── discovery.test.ts
│   ├── renderer.test.ts
│   └── integration.test.ts
├── README.md.codx/      # Self-hosted README
├── CLAUDE.md.codx/      # Self-hosted AI context
└── package.json
\`\`\`
`;

export const validate = async () => {
  // Verify key directories exist
  const requiredDirs = ['src', 'tests', 'README.md.codx', 'CLAUDE.md.codx'];

  for (const dir of requiredDirs) {
    const dirPath = path.join(__dirname, '..', dir);
    if (!fs.existsSync(dirPath)) {
      throw new Error('Required directory missing: ' + dir);
    }
  }

  // Verify package.json exists
  const pkgPath = path.join(__dirname, '..', 'package.json');
  if (!fs.existsSync(pkgPath)) {
    throw new Error('package.json not found');
  }
};

export const errorContent = `
[Validation Failed] File structure documentation describes directories that don't exist.
Ensure the project structure matches the documented layout.
`;
