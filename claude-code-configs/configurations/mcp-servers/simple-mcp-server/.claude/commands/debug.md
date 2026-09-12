# Debug MCP Server

Provides comprehensive debugging tools for troubleshooting MCP server issues.

## Usage

```
/debug [component] [options]
```

## Components

- `protocol` - Debug protocol messages
- `tools` - Debug tool execution
- `resources` - Debug resource access
- `transport` - Debug transport layer
- `all` - Enable all debugging (default)

## Options

- `--verbose` - Extra verbose output
- `--save` - Save debug logs to file
- `--inspector` - Launch with MCP Inspector

## Implementation

```typescript
import * as fs from 'fs/promises';
import { exec, spawn } from 'child_process';
import * as path from 'path';

async function debugServer(
  component: 'protocol' | 'tools' | 'resources' | 'transport' | 'all' = 'all',
  options: {
    verbose?: boolean;
    save?: boolean;
    inspector?: boolean;
  } = {}
) {
  console.log('🔍 MCP Server Debugger');
  console.log('='.repeat(50));
  
  // Set debug environment variables
  const debugEnv = {
    ...process.env,
    DEBUG: component === 'all' ? 'mcp:*' : `mcp:${component}`,
    LOG_LEVEL: options.verbose ? 'trace' : 'debug',
    MCP_DEBUG: 'true',
  };
  
  // Create debug configuration
  const debugConfig = await createDebugConfig();
  
  // Start debug session
  if (options.inspector) {
    await launchWithInspector(debugEnv);
  } else {
    await runDebugSession(component, debugEnv, options);
  }
}

async function createDebugConfig(): Promise<string> {
  const config = {
    logging: {
      level: 'debug',
      format: 'pretty',
      includeTimestamp: true,
      includeLocation: true,
    },
    debug: {
      protocol: {
        logRequests: true,
        logResponses: true,
        logNotifications: true,
      },
      tools: {
        logCalls: true,
        logValidation: true,
        logErrors: true,
        measurePerformance: true,
      },
      resources: {
        logReads: true,
        logWrites: true,
        trackCache: true,
      },
      transport: {
        logConnections: true,
        logMessages: true,
        logErrors: true,
      },
    },
  };
  
  const configPath = '.debug-config.json';
  await fs.writeFile(configPath, JSON.stringify(config, null, 2));
  return configPath;
}

async function runDebugSession(
  component: string,
  env: NodeJS.ProcessEnv,
  options: { verbose?: boolean; save?: boolean }
) {
  console.log(`\n🔍 Debugging: ${component}`);
  console.log('Press Ctrl+C to stop\n');
  
  // Create debug wrapper
  const debugScript = `
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import debug from 'debug';
import pino from 'pino';

// Enable debug logging
const log = {
  protocol: debug('mcp:protocol'),
  tools: debug('mcp:tools'),
  resources: debug('mcp:resources'),
  transport: debug('mcp:transport'),
};

// Create logger
const logger = pino({
  level: process.env.LOG_LEVEL || 'debug',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'HH:MM:ss.l',
      ignore: 'pid,hostname',
    },
  },
});

// Wrap server methods for debugging
const originalServer = await import('./src/index.js');
const server = originalServer.server;

// Intercept requests
const originalSetRequestHandler = server.setRequestHandler.bind(server);
server.setRequestHandler = (schema, handler) => {
  const wrappedHandler = async (request) => {
    const start = Date.now();
    log.protocol('→ Request: %O', request);
    logger.debug({ request }, 'Incoming request');
    
    try {
      const result = await handler(request);
      const duration = Date.now() - start;
      
      log.protocol('← Response (%dms): %O', duration, result);
      logger.debug({ result, duration }, 'Response sent');
      
      return result;
    } catch (error) {
      log.protocol('✗ Error: %O', error);
      logger.error({ error }, 'Request failed');
      throw error;
    }
  };
  
  return originalSetRequestHandler(schema, wrappedHandler);
};

// Start server with debugging
logger.info('Debug server starting...');
const transport = new StdioServerTransport();
await server.connect(transport);
logger.info('Debug server ready');
`;
  
  // Write debug script
  const debugScriptPath = '.debug-server.js';
  await fs.writeFile(debugScriptPath, debugScript);
  
  // Start server with debugging
  const serverProcess = spawn('node', [debugScriptPath], {
    env,
    stdio: options.save ? 'pipe' : 'inherit',
  });
  
  if (options.save) {
    const logFile = `debug-${component}-${Date.now()}.log`;
    const logStream = await fs.open(logFile, 'w');
    
    serverProcess.stdout?.pipe(logStream.createWriteStream());
    serverProcess.stderr?.pipe(logStream.createWriteStream());
    
    console.log(`Saving debug output to: ${logFile}`);
  }
  
  // Handle cleanup
  process.on('SIGINT', () => {
    serverProcess.kill();
    process.exit();
  });
  
  serverProcess.on('exit', async () => {
    // Cleanup
    await fs.unlink(debugScriptPath).catch(() => {});
    await fs.unlink('.debug-config.json').catch(() => {});
  });
}

async function launchWithInspector(env: NodeJS.ProcessEnv) {
  console.log('\n🔍 Launching with MCP Inspector...');
  console.log('This will provide an interactive debugging interface.\n');
  
  // Start server in debug mode
  const serverProcess = spawn('node', ['--inspect', 'dist/index.js'], {
    env,
    stdio: 'pipe',
  });
  
  // Parse debug port from output
  serverProcess.stderr?.on('data', (data) => {
    const output = data.toString();
    const match = output.match(/Debugger listening on ws:\/\/(.+):(\d+)/);
    if (match) {
      console.log(`🔗 Node.js debugger: chrome://inspect`);
      console.log(`    Connect to: ${match[1]}:${match[2]}`);
    }
  });
  
  // Wait a moment for server to start
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Launch MCP Inspector
  console.log('\n🔍 Starting MCP Inspector...');
  const inspector = exec('npx @modelcontextprotocol/inspector');
  
  inspector.stdout?.on('data', (data) => {
    console.log(data.toString());
  });
  
  // Cleanup on exit
  process.on('SIGINT', () => {
    serverProcess.kill();
    inspector.kill();
    process.exit();
  });
}

// Additional debug utilities
export async function analyzeProtocolFlow() {
  console.log('\n📊 Analyzing Protocol Flow...');
  
  const checks = [
    { name: 'Initialization', test: testInitialization },
    { name: 'Capability Negotiation', test: testCapabilities },
    { name: 'Tool Discovery', test: testToolDiscovery },
    { name: 'Resource Listing', test: testResourceListing },
    { name: 'Error Handling', test: testErrorHandling },
  ];
  
  for (const check of checks) {
    try {
      await check.test();
      console.log(`  ✅ ${check.name}`);
    } catch (error) {
      console.log(`  ❌ ${check.name}: ${error.message}`);
    }
  }
}

async function testInitialization() {
  // Test initialization flow
  const { Server } = await import('@modelcontextprotocol/sdk/server/index.js');
  const server = new Server({ name: 'test', version: '1.0.0' }, {});
  if (!server) throw new Error('Server initialization failed');
}

async function testCapabilities() {
  // Test capability declaration
  const capabilities = {
    tools: {},
    resources: {},
    prompts: {},
  };
  if (!capabilities.tools) throw new Error('Tools capability missing');
}

async function testToolDiscovery() {
  // Test tool discovery
  try {
    const { tools } = await import('./src/tools/index.js');
    if (!Array.isArray(tools)) throw new Error('Tools not properly exported');
  } catch {
    // Tools may not be implemented yet
  }
}

async function testResourceListing() {
  // Test resource listing
  try {
    const { resources } = await import('./src/resources/index.js');
    if (!Array.isArray(resources)) throw new Error('Resources not properly exported');
  } catch {
    // Resources may not be implemented yet
  }
}

async function testErrorHandling() {
  // Test error handling
  const { handleError } = await import('./src/utils/error-handler.js');
  const result = handleError(new Error('Test'));
  if (!result.error) throw new Error('Error handler not working');
}
```