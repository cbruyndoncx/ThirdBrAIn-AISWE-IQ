# Add Tool to MCP Server

Adds a new tool to your MCP server with proper schema validation and error handling.

## Usage

```
/add-tool <name> <description> [parameters]
```

## Examples

```
/add-tool calculate "Performs mathematical calculations"
/add-tool search "Search for information" query:string limit:number?
/add-tool process_data "Process data with options" input:string format:enum[json,csv,xml]
```

## Implementation

```typescript
import { z } from 'zod';
import * as fs from 'fs/promises';
import * as path from 'path';

async function addTool(name: string, description: string, parameters?: string[]) {
  // Parse parameters into schema
  const schema = parseParameterSchema(parameters || []);
  
  // Generate tool file
  const toolContent = generateToolFile(name, description, schema);
  
  // Write tool file
  const toolPath = path.join('src/tools', `${name}.ts`);
  await fs.writeFile(toolPath, toolContent);
  
  // Update tool index
  await updateToolIndex(name);
  
  // Generate test file
  const testContent = generateToolTest(name);
  const testPath = path.join('tests/unit/tools', `${name}.test.ts`);
  await fs.writeFile(testPath, testContent);
  
  console.log(`✅ Tool "${name}" added successfully!`);
  console.log(`  - Implementation: ${toolPath}`);
  console.log(`  - Test file: ${testPath}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Implement the tool logic in ${toolPath}`);
  console.log(`  2. Run tests with "npm test"`);
  console.log(`  3. Test with MCP Inspector`);
}

function parseParameterSchema(parameters: string[]): any {
  const properties: Record<string, any> = {};
  const required: string[] = [];
  
  for (const param of parameters) {
    const [nameType, ...rest] = param.split(':');
    const isOptional = nameType.endsWith('?');
    const name = isOptional ? nameType.slice(0, -1) : nameType;
    const type = rest.join(':') || 'string';
    
    if (!isOptional) {
      required.push(name);
    }
    
    properties[name] = parseType(type);
  }
  
  return {
    type: 'object',
    properties,
    required: required.length > 0 ? required : undefined,
  };
}

function parseType(type: string): any {
  if (type.startsWith('enum[')) {
    const values = type.slice(5, -1).split(',');
    return {
      type: 'string',
      enum: values,
    };
  }
  
  switch (type) {
    case 'number':
      return { type: 'number' };
    case 'boolean':
      return { type: 'boolean' };
    case 'array':
      return { type: 'array', items: { type: 'string' } };
    default:
      return { type: 'string' };
  }
}

function generateToolFile(name: string, description: string, schema: any): string {
  return `
import { z } from 'zod';
import type { ToolHandler } from '../types/tools.js';

// Define Zod schema for validation
const ${capitalize(name)}Schema = z.object({
${generateZodSchema(schema.properties, '  ')}
});

export type ${capitalize(name)}Args = z.infer<typeof ${capitalize(name)}Schema>;

export const ${name}Tool = {
  name: '${name}',
  description: '${description}',
  inputSchema: ${JSON.stringify(schema, null, 2)},
  handler: async (args: unknown): Promise<ToolHandler> => {
    // Validate input
    const validated = ${capitalize(name)}Schema.parse(args);
    
    // TODO: Implement your tool logic here
    const result = await process${capitalize(name)}(validated);
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result),
        },
      ],
    };
  },
};

async function process${capitalize(name)}(args: ${capitalize(name)}Args) {
  // TODO: Implement the actual processing logic
  return {
    success: true,
    message: 'Tool executed successfully',
    input: args,
  };
}
`;
}

function generateZodSchema(properties: Record<string, any>, indent: string): string {
  const lines: string[] = [];
  
  for (const [key, value] of Object.entries(properties)) {
    let zodType = 'z.string()';
    
    if (value.type === 'number') {
      zodType = 'z.number()';
    } else if (value.type === 'boolean') {
      zodType = 'z.boolean()';
    } else if (value.enum) {
      zodType = `z.enum([${value.enum.map((v: string) => `'${v}'`).join(', ')}])`;
    } else if (value.type === 'array') {
      zodType = 'z.array(z.string())';
    }
    
    lines.push(`${indent}${key}: ${zodType},`);
  }
  
  return lines.join('\n');
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateToolTest(name: string): string {
  return `
import { describe, it, expect, vi } from 'vitest';
import { ${name}Tool } from '../../src/tools/${name}.js';

describe('${name} tool', () => {
  it('should have correct metadata', () => {
    expect(${name}Tool.name).toBe('${name}');
    expect(${name}Tool.description).toBeDefined();
    expect(${name}Tool.inputSchema).toBeDefined();
  });
  
  it('should validate input parameters', async () => {
    const invalidInput = {};
    
    await expect(${name}Tool.handler(invalidInput))
      .rejects
      .toThrow();
  });
  
  it('should handle valid input', async () => {
    const validInput = {
      // TODO: Add valid test input
    };
    
    const result = await ${name}Tool.handler(validInput);
    
    expect(result).toHaveProperty('content');
    expect(result.content[0]).toHaveProperty('type', 'text');
  });
  
  it('should handle errors gracefully', async () => {
    // TODO: Add error handling tests
  });
});
`;
}
```