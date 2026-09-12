# Initialize MCP Server Project

Sets up a new MCP server project with the specified configuration level.

## Usage

```
/init [basic|standard|full]
```

## Options

- `basic` - Minimal server with one example tool
- `standard` - Server with tools and resources (default)
- `full` - Complete server with all capabilities

## Implementation

```typescript
async function initializeProject(level: 'basic' | 'standard' | 'full' = 'standard') {
  // Create project structure
  const dirs = [
    'src',
    'src/tools',
    'src/resources',
    'src/prompts',
    'src/utils',
    'src/types',
    'tests',
    'tests/unit',
    'tests/integration',
  ];
  
  for (const dir of dirs) {
    await fs.mkdir(dir, { recursive: true });
  }
  
  // Create package.json
  const packageJson = {
    name: 'mcp-server',
    version: '1.0.0',
    type: 'module',
    scripts: {
      'dev': 'tsx watch src/index.ts',
      'build': 'tsc',
      'start': 'node dist/index.js',
      'test': 'vitest',
      'lint': 'eslint src',
      'typecheck': 'tsc --noEmit',
    },
    dependencies: {
      '@modelcontextprotocol/sdk': '^1.0.0',
      'zod': '^3.22.0',
    },
    devDependencies: {
      '@types/node': '^20.0.0',
      'typescript': '^5.0.0',
      'tsx': '^4.0.0',
      'vitest': '^1.0.0',
      'eslint': '^8.0.0',
    },
  };
  
  await fs.writeFile('package.json', JSON.stringify(packageJson, null, 2));
  
  // Create tsconfig.json
  const tsConfig = {
    compilerOptions: {
      target: 'ES2022',
      module: 'NodeNext',
      moduleResolution: 'NodeNext',
      outDir: './dist',
      rootDir: './src',
      strict: true,
      esModuleInterop: true,
      skipLibCheck: true,
      forceConsistentCasingInFileNames: true,
    },
    include: ['src/**/*'],
    exclude: ['node_modules', 'dist'],
  };
  
  await fs.writeFile('tsconfig.json', JSON.stringify(tsConfig, null, 2));
  
  // Create main server file
  let serverContent = '';
  
  if (level === 'basic') {
    serverContent = generateBasicServer();
  } else if (level === 'standard') {
    serverContent = generateStandardServer();
  } else {
    serverContent = generateFullServer();
  }
  
  await fs.writeFile('src/index.ts', serverContent);
  
  // Install dependencies
  console.log('Installing dependencies...');
  await exec('npm install');
  
  console.log('✅ MCP server initialized successfully!');
  console.log('\nNext steps:');
  console.log('1. Run "npm run dev" to start development server');
  console.log('2. Use "/add-tool" to add custom tools');
  console.log('3. Test with MCP Inspector: npx @modelcontextprotocol/inspector');
}

function generateBasicServer(): string {
  return `
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

const server = new Server({
  name: 'my-mcp-server',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
  },
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'hello',
        description: 'Say hello to someone',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Name to greet',
            },
          },
          required: ['name'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === 'hello') {
    const validated = z.object({
      name: z.string(),
    }).parse(args);
    
    return {
      content: [
        {
          type: 'text',
          text: \`Hello, \${validated.name}!\`,
        },
      ],
    };
  }
  
  throw new Error(\`Unknown tool: \${name}\`);
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('MCP server running on stdio');
`;
}
```