import * as fs from 'fs';
import * as path from 'path';

export const content = `## CI/CD Integration

### GitHub Actions

\`\`\`yaml
name: Documentation
on: [push, pull_request]

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npx codumentation validate
\`\`\`

### GitLab CI

\`\`\`yaml
validate-docs:
  image: node:18
  script:
    - npm ci
    - npx codumentation validate
  rules:
    - changes:
        - "*.md"
        - "*.codx/**/*"
        - "src/**/*"
\`\`\`

### Pre-commit Hook (Husky)

\`\`\`bash
npx husky add .husky/pre-commit "npx codumentation validate"
\`\`\`

### Package.json Scripts

\`\`\`json
{
  "scripts": {
    "docs:validate": "codumentation validate",
    "docs:build": "codumentation build",
    "test": "vitest && codumentation validate"
  }
}
\`\`\`

This ensures documentation is validated alongside your test suite.`;

export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Verify the package has codumentation scripts itself (eating our own dog food)
  const scripts = pkg.scripts || {};

  // Check for any codumentation-related scripts
  const hasValidateScript = Object.values(scripts).some(
    (script: any) => typeof script === 'string' && script.includes('codumentation validate')
  );
  const hasBuildScript = Object.values(scripts).some(
    (script: any) => typeof script === 'string' && script.includes('codumentation build')
  );

  if (!hasValidateScript) {
    throw new Error('CI section shows scripts but this project lacks a codumentation validate script');
  }

  if (!hasBuildScript) {
    throw new Error('CI section shows scripts but this project lacks a codumentation build script');
  }

  // Verify Node.js version mentioned matches what we require
  if (!pkg.engines?.node?.includes('18')) {
    throw new Error('CI examples use Node 18 but package.json engines does not require 18+');
  }
};

export const errorContent = `
[CI Integration Validation Failed]

The CI section shows example configurations but this project doesn't follow its own advice.

Ensure package.json has:
- A script that runs 'codumentation validate'
- A script that runs 'codumentation build'
- Node.js engine requirement >= 18
`;
