import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { discoverCodxTargets } from '../src/discovery';
import { validateTarget, buildTarget } from '../src/validator';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('Integration Tests', () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'codx-integration-'));
  });

  afterEach(() => {
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  it('should discover and build a simple .codx target', async () => {
    // Create TEST.md.codx directory
    const codxDir = path.join(tempDir, 'TEST.md.codx');
    fs.mkdirSync(codxDir);

    // Create index.md template
    const template = '# Test\n\n{{ content }}';
    fs.writeFileSync(path.join(codxDir, 'index.md'), template);

    // Create content.ts module
    const moduleContent = `
export const content = 'This is test content';

export const validate = async () => {
  // Always passes
};

export const errorContent = 'Test error content';
`;
    fs.writeFileSync(path.join(codxDir, 'content.ts'), moduleContent);

    // Discover targets
    const targets = await discoverCodxTargets(tempDir);
    expect(targets).toHaveLength(1);
    expect(targets[0].targetFile).toBe(path.join(tempDir, 'TEST.md'));

    // Build target
    const result = await buildTarget(targets[0], tempDir);
    expect(result.success).toBe(true);

    // Check that file was created
    const targetFile = path.join(tempDir, 'TEST.md');
    expect(fs.existsSync(targetFile)).toBe(true);

    const content = fs.readFileSync(targetFile, 'utf-8');
    expect(content).toBe('# Test\n\nThis is test content');
  });

  it('should fail validation when module validate() throws', async () => {
    const codxDir = path.join(tempDir, 'TEST.md.codx');
    fs.mkdirSync(codxDir);

    const template = '# Test\n\n{{ content }}';
    fs.writeFileSync(path.join(codxDir, 'index.md'), template);

    const moduleContent = `
export const content = 'Content';

export const validate = async () => {
  throw new Error('Validation failed!');
};

export const errorContent = 'This validation always fails for testing';
`;
    fs.writeFileSync(path.join(codxDir, 'content.ts'), moduleContent);

    const targets = await discoverCodxTargets(tempDir);
    const result = await buildTarget(targets[0], tempDir);

    expect(result.success).toBe(false);
    expect(result.validationResults[0].success).toBe(false);
    expect(result.validationResults[0].error).toContain('Validation failed');
  });

  it('should detect content mismatch during validation', async () => {
    const codxDir = path.join(tempDir, 'TEST.md.codx');
    fs.mkdirSync(codxDir);

    const template = '# Test\n\n{{ content }}';
    fs.writeFileSync(path.join(codxDir, 'index.md'), template);

    const moduleContent = `
export const content = 'Correct content';
export const validate = async () => {};
export const errorContent = 'Error';
`;
    fs.writeFileSync(path.join(codxDir, 'content.ts'), moduleContent);

    // Create TEST.md with WRONG content
    const targetFile = path.join(tempDir, 'TEST.md');
    fs.writeFileSync(targetFile, '# Test\n\nWrong content');

    const targets = await discoverCodxTargets(tempDir);
    const result = await validateTarget(targets[0], tempDir);

    expect(result.success).toBe(false);
    expect(result.contentMatches).toBe(false);
  });

  it('should pass validation when content matches', async () => {
    const codxDir = path.join(tempDir, 'TEST.md.codx');
    fs.mkdirSync(codxDir);

    const template = '# Test\n\n{{ content }}';
    fs.writeFileSync(path.join(codxDir, 'index.md'), template);

    const moduleContent = `
export const content = 'Correct content';
export const validate = async () => {};
export const errorContent = 'Error';
`;
    fs.writeFileSync(path.join(codxDir, 'content.ts'), moduleContent);

    // Create TEST.md with CORRECT content
    const targetFile = path.join(tempDir, 'TEST.md');
    fs.writeFileSync(targetFile, '# Test\n\nCorrect content');

    const targets = await discoverCodxTargets(tempDir);
    const result = await validateTarget(targets[0], tempDir);

    expect(result.success).toBe(true);
    expect(result.contentMatches).toBe(true);
  });

  it('should handle multiple variables', async () => {
    const codxDir = path.join(tempDir, 'TEST.md.codx');
    fs.mkdirSync(codxDir);

    const template = '# {{ title }}\n\n{{ content }}';
    fs.writeFileSync(path.join(codxDir, 'index.md'), template);

    const titleModule = `
export const content = 'My Title';
export const validate = async () => {};
export const errorContent = 'Error';
`;
    fs.writeFileSync(path.join(codxDir, 'title.ts'), titleModule);

    const contentModule = `
export const content = 'My Content';
export const validate = async () => {};
export const errorContent = 'Error';
`;
    fs.writeFileSync(path.join(codxDir, 'content.ts'), contentModule);

    const targets = await discoverCodxTargets(tempDir);
    const result = await buildTarget(targets[0], tempDir);

    expect(result.success).toBe(true);

    const targetFile = path.join(tempDir, 'TEST.md');
    const content = fs.readFileSync(targetFile, 'utf-8');
    expect(content).toBe('# My Title\n\nMy Content');
  });
});
