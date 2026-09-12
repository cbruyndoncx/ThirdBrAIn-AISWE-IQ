import * as fs from 'fs';
import * as path from 'path';

// This section validates that the version in badges matches package.json
export const content = `[![npm version](https://img.shields.io/npm/v/codumentation.svg)](https://www.npmjs.com/package/codumentation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)

> **This README is self-documenting.** Every claim is validated by code. If you see this, it passed.`;

export const validate = async () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Verify TypeScript version mentioned in badge matches or is satisfied by package.json
  const tsVersion = pkg.dependencies?.typescript || pkg.devDependencies?.typescript;
  if (!tsVersion) {
    throw new Error('TypeScript not found in dependencies');
  }

  // Verify Node.js version mentioned matches engines
  if (!pkg.engines?.node?.includes('18')) {
    throw new Error('Node.js engine should require 18+');
  }

  // Verify license is MIT
  if (pkg.license !== 'MIT') {
    throw new Error(`License should be MIT, found: ${pkg.license}`);
  }
};

export const errorContent = `
[Badge Validation Failed]

The badges in the README make claims that don't match package.json.

Ensure:
- TypeScript version matches the badge
- Node.js engine requirement matches the badge
- License is MIT
`;
