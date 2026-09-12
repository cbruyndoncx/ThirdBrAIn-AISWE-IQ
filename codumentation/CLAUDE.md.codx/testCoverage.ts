import * as path from 'path';
import * as fs from 'fs';

const expectedTestFiles = [
  'tests/discovery.test.ts',
  'tests/renderer.test.ts',
  'tests/integration.test.ts'
];

const testFileContent: Record<string, string[]> = {
  'tests/discovery.test.ts': ['extractVariables'],
  'tests/renderer.test.ts': ['renderTemplate', 'generateDiff'],
  'tests/integration.test.ts': ['discoverCodxTargets', 'validateTarget', 'buildTarget']
};

export const content = `### Test Coverage

The project maintains comprehensive test coverage with the following test files:

- **tests/discovery.test.ts** - Tests for extractVariables
- **tests/renderer.test.ts** - Tests for renderTemplate and generateDiff
- **tests/integration.test.ts** - End-to-end integration tests using discoverCodxTargets, validateTarget, and buildTarget

All tests use Vitest and can be run with \`npm test\`.
`;

export const validate = async () => {
  // Verify tests directory exists
  const testsDir = path.join(__dirname, '..', 'tests');
  if (!fs.existsSync(testsDir)) {
    throw new Error('tests/ directory not found');
  }

  // Verify each test file exists
  for (const testFile of expectedTestFiles) {
    const testPath = path.join(__dirname, '..', testFile);

    if (!fs.existsSync(testPath)) {
      throw new Error(`Test file not found: ${testFile}`);
    }
  }

  // Verify test files actually test what they claim to test
  for (const [testFile, expectedTests] of Object.entries(testFileContent)) {
    const testPath = path.join(__dirname, '..', testFile);
    const content = fs.readFileSync(testPath, 'utf-8');

    // Check for Vitest imports
    if (!content.includes("from 'vitest'")) {
      throw new Error(`${testFile} doesn't import from vitest`);
    }

    // Check that it references the functions it claims to test
    for (const funcName of expectedTests) {
      if (!content.includes(funcName)) {
        throw new Error(
          `${testFile} doesn't appear to test '${funcName}' (no reference found)`
        );
      }
    }

    // Verify it has actual test cases
    if (!content.includes('describe(') && !content.includes('test(') && !content.includes('it(')) {
      throw new Error(`${testFile} doesn't contain any test cases`);
    }
  }

  // Verify package.json has test script
  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  if (!pkg.scripts?.test) {
    throw new Error('package.json missing "test" script');
  }

  // Verify vitest is in devDependencies
  if (!pkg.devDependencies?.vitest) {
    throw new Error('vitest not found in devDependencies');
  }
};

export const errorContent = `
[Validation Failed] Test coverage documentation doesn't match actual test files.

This could indicate:
1. A documented test file doesn't exist
2. A test file exists but doesn't test what it claims to test
3. Test files aren't using Vitest properly
4. package.json is missing test scripts or Vitest dependency

Action required:
- Verify all test files exist in tests/ directory
- Ensure each test file imports and tests the documented functions
- Check that package.json has test script and vitest as a devDependency
- If test structure changed, update documentation to match
`;
