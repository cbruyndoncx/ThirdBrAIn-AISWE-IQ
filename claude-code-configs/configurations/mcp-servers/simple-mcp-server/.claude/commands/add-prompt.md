# Add Prompt Template to MCP Server

Adds a new prompt template to your MCP server for reusable conversation patterns.

## Usage

```
/add-prompt <name> <description> [arguments]
```

## Examples

```
/add-prompt code_review "Review code for improvements" language:string file:string?
/add-prompt analyze_data "Analyze data patterns" dataset:string metrics:array
/add-prompt generate_docs "Generate documentation" codebase:string style:enum[minimal,detailed]
```

## Implementation

```typescript
import * as fs from 'fs/promises';
import * as path from 'path';

async function addPrompt(
  name: string,
  description: string,
  argumentDefs?: string[]
) {
  // Parse arguments
  const args = parsePromptArguments(argumentDefs || []);
  
  // Generate prompt file
  const promptContent = generatePromptFile(name, description, args);
  
  // Write prompt file
  const promptPath = path.join('src/prompts', `${name}.ts`);
  await fs.writeFile(promptPath, promptContent);
  
  // Update prompt index
  await updatePromptIndex(name);
  
  // Generate test file
  const testContent = generatePromptTest(name);
  const testPath = path.join('tests/unit/prompts', `${name}.test.ts`);
  await fs.writeFile(testPath, testContent);
  
  console.log(`✅ Prompt "${name}" added successfully!`);
  console.log(`  - Implementation: ${promptPath}`);
  console.log(`  - Test file: ${testPath}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Define the prompt template in ${promptPath}`);
  console.log(`  2. Test with MCP Inspector`);
}

interface PromptArgument {
  name: string;
  description: string;
  required: boolean;
  type: string;
}

function parsePromptArguments(argumentDefs: string[]): PromptArgument[] {
  return argumentDefs.map(def => {
    const [nameWithType, description] = def.split('=');
    const [nameType] = nameWithType.split(':');
    const isOptional = nameType.endsWith('?');
    const name = isOptional ? nameType.slice(0, -1) : nameType;
    const type = nameWithType.split(':')[1] || 'string';
    
    return {
      name,
      description: description || `${name} parameter`,
      required: !isOptional,
      type: type.replace('?', ''),
    };
  });
}

function generatePromptFile(
  name: string,
  description: string,
  args: PromptArgument[]
): string {
  return `
import type { Prompt, PromptMessage } from '../types/prompts.js';

export const ${name}Prompt: Prompt = {
  name: '${name}',
  description: '${description}',
  arguments: [
${args.map(arg => `    {
      name: '${arg.name}',
      description: '${arg.description}',
      required: ${arg.required},
    },`).join('\n')}
  ],
};

export function get${capitalize(name)}Prompt(
  args: Record<string, unknown>
): PromptMessage[] {
  // Validate required arguments
${args.filter(a => a.required).map(arg => `  if (!args.${arg.name}) {
    throw new Error('Missing required argument: ${arg.name}');
  }`).join('\n')}
  
  // Build prompt messages
  const messages: PromptMessage[] = [];
  
  // System message (optional)
  messages.push({
    role: 'system',
    content: {
      type: 'text',
      text: buildSystemPrompt(args),
    },
  });
  
  // User message
  messages.push({
    role: 'user',
    content: {
      type: 'text',
      text: buildUserPrompt(args),
    },
  });
  
  return messages;
}

function buildSystemPrompt(args: Record<string, unknown>): string {
  // TODO: Define the system prompt template
  return \`You are an expert assistant helping with ${description.toLowerCase()}.\`;
}

function buildUserPrompt(args: Record<string, unknown>): string {
  // TODO: Define the user prompt template
  let prompt = '${description}\\n\\n';
  
${args.map(arg => `  if (args.${arg.name}) {
    prompt += \`${capitalize(arg.name)}: \${args.${arg.name}}\\n\`;
  }`).join('\n')}
  
  return prompt;
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
`;
}

function generatePromptTest(name: string): string {
  return `
import { describe, it, expect } from 'vitest';
import { ${name}Prompt, get${capitalize(name)}Prompt } from '../../src/prompts/${name}.js';

describe('${name} prompt', () => {
  it('should have correct metadata', () => {
    expect(${name}Prompt.name).toBe('${name}');
    expect(${name}Prompt.description).toBeDefined();
    expect(${name}Prompt.arguments).toBeDefined();
  });
  
  it('should generate prompt messages', () => {
    const args = {
      // TODO: Add test arguments
    };
    
    const messages = get${capitalize(name)}Prompt(args);
    
    expect(messages).toBeInstanceOf(Array);
    expect(messages.length).toBeGreaterThan(0);
    expect(messages[0]).toHaveProperty('role');
    expect(messages[0]).toHaveProperty('content');
  });
  
  it('should validate required arguments', () => {
    const invalidArgs = {};
    
    expect(() => get${capitalize(name)}Prompt(invalidArgs))
      .toThrow('Missing required argument');
  });
  
  it('should handle optional arguments', () => {
    const minimalArgs = {
      // Only required args
    };
    
    const messages = get${capitalize(name)}Prompt(minimalArgs);
    expect(messages).toBeDefined();
  });
});
`;
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

async function updatePromptIndex(name: string) {
  const indexPath = 'src/prompts/index.ts';
  
  try {
    let content = await fs.readFile(indexPath, 'utf-8');
    
    // Add import
    const importLine = `import { ${name}Prompt, get${capitalize(name)}Prompt } from './${name}.js';`;
    if (!content.includes(importLine)) {
      const lastImport = content.lastIndexOf('import');
      const endOfLastImport = content.indexOf('\n', lastImport);
      content = content.slice(0, endOfLastImport + 1) + importLine + '\n' + content.slice(endOfLastImport + 1);
    }
    
    // Add to exports
    const exportPattern = /export const prompts = \[([^\]]*)]\;/;
    const match = content.match(exportPattern);
    if (match) {
      const currentExports = match[1].trim();
      const newExports = currentExports ? `${currentExports},\n  ${name}Prompt` : `\n  ${name}Prompt\n`;
      content = content.replace(exportPattern, `export const prompts = [${newExports}];`);
    }
    
    await fs.writeFile(indexPath, content);
  } catch (error) {
    // Create index file if it doesn't exist
    const newIndex = `
import { ${name}Prompt, get${capitalize(name)}Prompt } from './${name}.js';

export const prompts = [
  ${name}Prompt,
];

export const promptHandlers = {
  '${name}': get${capitalize(name)}Prompt,
};
`;
    await fs.writeFile(indexPath, newIndex);
  }
}
```