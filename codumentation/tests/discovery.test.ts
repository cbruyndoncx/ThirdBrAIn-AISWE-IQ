import { describe, it, expect } from 'vitest';
import { extractVariables } from '../src/discovery';

describe('extractVariables', () => {
  it('should extract single variable', () => {
    const template = 'Hello {{ name }}!';
    const variables = extractVariables(template);
    expect(variables).toEqual(['name']);
  });

  it('should extract multiple variables', () => {
    const template = '{{ greeting }} {{ name }}, you have {{ count }} messages.';
    const variables = extractVariables(template);
    expect(variables).toEqual(['greeting', 'name', 'count']);
  });

  it('should handle variables with whitespace', () => {
    const template = '{{  name  }} and {{ title}}';
    const variables = extractVariables(template);
    expect(variables).toEqual(['name', 'title']);
  });

  it('should return unique variables', () => {
    const template = '{{ name }} appears {{ name }} twice';
    const variables = extractVariables(template);
    expect(variables).toEqual(['name']);
  });

  it('should return empty array for template without variables', () => {
    const template = 'No variables here!';
    const variables = extractVariables(template);
    expect(variables).toEqual([]);
  });

  it('should handle multiline templates', () => {
    const template = `
# Title

{{ section1 }}

## Subtitle

{{ section2 }}
    `;
    const variables = extractVariables(template);
    expect(variables).toEqual(['section1', 'section2']);
  });
});
