import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { renderTemplate, generateDiff } from '../src/renderer';
import { CodxModule } from '../src/types';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

describe('renderTemplate', () => {
  let tempDir: string;
  let templatePath: string;

  beforeEach(() => {
    // Create a temporary directory for test files
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'codx-test-'));
    templatePath = path.join(tempDir, 'index.md');
  });

  afterEach(() => {
    // Clean up
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  it('should render a simple template', () => {
    const template = 'Hello {{ name }}!';
    fs.writeFileSync(templatePath, template);

    const modules = new Map<string, CodxModule>([
      [
        'name',
        {
          content: 'World',
          validate: async () => {},
          errorContent: ''
        }
      ]
    ]);

    const result = renderTemplate(templatePath, modules);
    expect(result).toBe('Hello World!');
  });

  it('should render multiple variables', () => {
    const template = '{{ greeting }} {{ name }}!';
    fs.writeFileSync(templatePath, template);

    const modules = new Map<string, CodxModule>([
      ['greeting', { content: 'Hello', validate: async () => {}, errorContent: '' }],
      ['name', { content: 'World', validate: async () => {}, errorContent: '' }]
    ]);

    const result = renderTemplate(templatePath, modules);
    expect(result).toBe('Hello World!');
  });

  it('should handle multiline content', () => {
    const template = '# Title\n\n{{ content }}';
    fs.writeFileSync(templatePath, template);

    const modules = new Map<string, CodxModule>([
      [
        'content',
        {
          content: 'Line 1\nLine 2\nLine 3',
          validate: async () => {},
          errorContent: ''
        }
      ]
    ]);

    const result = renderTemplate(templatePath, modules);
    expect(result).toBe('# Title\n\nLine 1\nLine 2\nLine 3');
  });

  it('should throw error for unreplaced variables', () => {
    const template = 'Hello {{ name }} and {{ missing }}!';
    fs.writeFileSync(templatePath, template);

    const modules = new Map<string, CodxModule>([
      ['name', { content: 'World', validate: async () => {}, errorContent: '' }]
    ]);

    expect(() => renderTemplate(templatePath, modules)).toThrow(/missing/);
  });
});

describe('generateDiff', () => {
  it('should return no differences for identical strings', () => {
    const result = generateDiff('hello', 'hello');
    expect(result).toBe('No differences');
  });

  it('should identify first differing line', () => {
    const expected = 'Line 1\nLine 2\nLine 3';
    const actual = 'Line 1\nDifferent Line\nLine 3';
    const result = generateDiff(expected, actual);
    expect(result).toContain('line 2');
    expect(result).toContain('Line 2');
    expect(result).toContain('Different Line');
  });

  it('should handle missing lines', () => {
    const expected = 'Line 1\nLine 2';
    const actual = 'Line 1';
    const result = generateDiff(expected, actual);
    expect(result).toContain('line 2');
    expect(result).toContain('Line 2');
    expect(result).toContain('(missing)');
  });

  it('should handle extra lines', () => {
    const expected = 'Line 1';
    const actual = 'Line 1\nExtra Line';
    const result = generateDiff(expected, actual);
    expect(result).toContain('line 2');
    expect(result).toContain('Extra Line');
  });
});
