# Add Resource to MCP Server

Adds a new resource endpoint to your MCP server with proper URI handling.

## Usage

```
/add-resource <name> <description> [uri-pattern] [mime-type]
```

## Examples

```
/add-resource config "Server configuration" config://settings application/json
/add-resource users "User database" data://users/{id} application/json
/add-resource files "File system access" file:///{path} text/plain
```

## Implementation

```typescript
import * as fs from 'fs/promises';
import * as path from 'path';

async function addResource(
  name: string,
  description: string,
  uriPattern?: string,
  mimeType: string = 'application/json'
) {
  // Generate URI pattern if not provided
  const uri = uriPattern || `${name}://default`;
  
  // Generate resource file
  const resourceContent = generateResourceFile(name, description, uri, mimeType);
  
  // Write resource file
  const resourcePath = path.join('src/resources', `${name}.ts`);
  await fs.writeFile(resourcePath, resourceContent);
  
  // Update resource index
  await updateResourceIndex(name);
  
  // Generate test file
  const testContent = generateResourceTest(name, uri);
  const testPath = path.join('tests/unit/resources', `${name}.test.ts`);
  await fs.writeFile(testPath, testContent);
  
  console.log(`✅ Resource "${name}" added successfully!`);
  console.log(`  - Implementation: ${resourcePath}`);
  console.log(`  - Test file: ${testPath}`);
  console.log(`  - URI pattern: ${uri}`);
  console.log(`  - MIME type: ${mimeType}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Implement the resource provider in ${resourcePath}`);
  console.log(`  2. Test with MCP Inspector`);
}

function generateResourceFile(
  name: string,
  description: string,
  uri: string,
  mimeType: string
): string {
  const hasDynamicParams = uri.includes('{');
  
  return `
import type { Resource, ResourceContent } from '../types/resources.js';

export const ${name}Resource: Resource = {
  uri: '${uri}',
  name: '${name}',
  description: '${description}',
  mimeType: '${mimeType}',
};

export async function read${capitalize(name)}Resource(
  uri: string
): Promise<ResourceContent[]> {
  ${hasDynamicParams ? generateDynamicResourceHandler(uri) : generateStaticResourceHandler()}
  
  return [
    {
      uri,
      mimeType: '${mimeType}',
      text: ${mimeType === 'application/json' ? 'JSON.stringify(data, null, 2)' : 'data'},
    },
  ];
}

${generateResourceDataFunction(name, mimeType)}
`;
}

function generateDynamicResourceHandler(uriPattern: string): string {
  return `
  // Parse dynamic parameters from URI
  const params = parseUriParams('${uriPattern}', uri);
  
  // Fetch data based on parameters
  const data = await fetch${capitalize(name)}Data(params);
  
  if (!data) {
    throw new Error(\`Resource not found: \${uri}\`);
  }
`;
}

function generateStaticResourceHandler(): string {
  return `
  // Fetch static resource data
  const data = await fetch${capitalize(name)}Data();
`;
}

function generateResourceDataFunction(name: string, mimeType: string): string {
  if (mimeType === 'application/json') {
    return `
async function fetch${capitalize(name)}Data(params?: Record<string, string>) {
  // TODO: Implement data fetching logic
  // This is a placeholder implementation
  
  if (params?.id) {
    // Return specific item
    return {
      id: params.id,
      name: 'Example Item',
      timestamp: new Date().toISOString(),
    };
  }
  
  // Return collection
  return {
    items: [
      { id: '1', name: 'Item 1' },
      { id: '2', name: 'Item 2' },
    ],
    total: 2,
  };
}

function parseUriParams(pattern: string, uri: string): Record<string, string> {
  // Convert pattern to regex
  const regexPattern = pattern
    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    .replace(/\{(\w+)\}/g, '(?<$1>[^/]+)');
  
  const regex = new RegExp(\`^\${regexPattern}$\`);
  const match = uri.match(regex);
  
  return match?.groups || {};
}
`;
  } else {
    return `
async function fetch${capitalize(name)}Data(params?: Record<string, string>) {
  // TODO: Implement data fetching logic
  // This is a placeholder implementation
  
  return 'Resource content as ${mimeType}';
}
`;
  }
}

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateResourceTest(name: string, uri: string): string {
  return `
import { describe, it, expect } from 'vitest';
import { ${name}Resource, read${capitalize(name)}Resource } from '../../src/resources/${name}.js';

describe('${name} resource', () => {
  it('should have correct metadata', () => {
    expect(${name}Resource.name).toBe('${name}');
    expect(${name}Resource.uri).toBe('${uri}');
    expect(${name}Resource.description).toBeDefined();
    expect(${name}Resource.mimeType).toBeDefined();
  });
  
  it('should read resource content', async () => {
    const content = await read${capitalize(name)}Resource('${uri.replace('{id}', 'test-id')}');
    
    expect(content).toBeInstanceOf(Array);
    expect(content[0]).toHaveProperty('uri');
    expect(content[0]).toHaveProperty('mimeType');
    expect(content[0]).toHaveProperty('text');
  });
  
  it('should handle missing resources', async () => {
    // TODO: Add tests for missing resources
  });
  
  it('should validate URI format', () => {
    // TODO: Add URI validation tests
  });
});
`;
}

async function updateResourceIndex(name: string) {
  const indexPath = 'src/resources/index.ts';
  
  try {
    let content = await fs.readFile(indexPath, 'utf-8');
    
    // Add import
    const importLine = `import { ${name}Resource, read${capitalize(name)}Resource } from './${name}.js';`;
    if (!content.includes(importLine)) {
      const lastImport = content.lastIndexOf('import');
      const endOfLastImport = content.indexOf('\n', lastImport);
      content = content.slice(0, endOfLastImport + 1) + importLine + '\n' + content.slice(endOfLastImport + 1);
    }
    
    // Add to exports
    const exportPattern = /export const resources = \[([^\]]*)]\;/;
    const match = content.match(exportPattern);
    if (match) {
      const currentExports = match[1].trim();
      const newExports = currentExports ? `${currentExports},\n  ${name}Resource` : `\n  ${name}Resource\n`;
      content = content.replace(exportPattern, `export const resources = [${newExports}];`);
    }
    
    await fs.writeFile(indexPath, content);
  } catch (error) {
    // Create index file if it doesn't exist
    const newIndex = `
import { ${name}Resource, read${capitalize(name)}Resource } from './${name}.js';

export const resources = [
  ${name}Resource,
];

export const resourceReaders = {
  '${name}': read${capitalize(name)}Resource,
};
`;
    await fs.writeFile(indexPath, newIndex);
  }
}
```