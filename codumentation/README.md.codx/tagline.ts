import * as fs from 'fs';
import * as path from 'path';

export const content = 'Auto-verifiable Markdown for documentation that cannot rot';

export const validate = async () => {
  // Verify this matches the package.json description
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  if (pkg.description !== content) {
    throw new Error(`Tagline mismatch: package.json says "${pkg.description}"`);
  }
};

export const errorContent = `
[Validation Failed] The tagline in README.md does not match package.json description.
Please ensure package.json description matches the README tagline.
`;
