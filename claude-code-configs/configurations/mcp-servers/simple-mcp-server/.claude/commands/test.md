# Test MCP Server

Runs comprehensive tests for your MCP server including unit tests, integration tests, and protocol compliance validation.

## Usage

```
/test [type] [options]
```

## Options

- `type` - Test type: `unit`, `integration`, `all` (default: `all`)
- `--coverage` - Generate coverage report
- `--watch` - Run tests in watch mode
- `--inspector` - Launch MCP Inspector for manual testing

## Implementation

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';

const execAsync = promisify(exec);

async function runTests(
  type: 'unit' | 'integration' | 'all' = 'all',
  options: {
    coverage?: boolean;
    watch?: boolean;
    inspector?: boolean;
  } = {}
) {
  console.log('🧪 Running MCP Server Tests...');
  
  // Run linting first
  console.log('\n🔍 Running linter...');
  try {
    await execAsync('npm run lint');
    console.log('✅ Linting passed');
  } catch (error) {
    console.error('❌ Linting failed:', error.message);
    return;
  }
  
  // Run type checking
  console.log('\n📝 Type checking...');
  try {
    await execAsync('npm run typecheck');
    console.log('✅ Type checking passed');
  } catch (error) {
    console.error('❌ Type checking failed:', error.message);
    return;
  }
  
  // Run tests
  console.log(`\n🧪 Running ${type} tests...`);
  
  let testCommand = 'npx vitest';
  
  if (type === 'unit') {
    testCommand += ' tests/unit';
  } else if (type === 'integration') {
    testCommand += ' tests/integration';
  }
  
  if (options.coverage) {
    testCommand += ' --coverage';
  }
  
  if (options.watch) {
    testCommand += ' --watch';
  } else {
    testCommand += ' --run';
  }
  
  try {
    const { stdout } = await execAsync(testCommand);
    console.log(stdout);
    
    // Run protocol compliance check
    if (type === 'all' || type === 'integration') {
      console.log('\n🔌 Checking MCP protocol compliance...');
      await checkProtocolCompliance();
    }
    
    // Generate test report
    if (options.coverage) {
      console.log('\n📊 Coverage report generated:');
      console.log('  - HTML: coverage/index.html');
      console.log('  - JSON: coverage/coverage-final.json');
    }
    
    console.log('\n✅ All tests passed!');
    
    // Launch inspector if requested
    if (options.inspector) {
      console.log('\n🔍 Launching MCP Inspector...');
      await launchInspector();
    }
  } catch (error) {
    console.error('\n❌ Tests failed:', error.message);
    process.exit(1);
  }
}

async function checkProtocolCompliance() {
  const tests = [
    checkInitialization,
    checkToolsCapability,
    checkResourcesCapability,
    checkPromptsCapability,
    checkErrorHandling,
  ];
  
  for (const test of tests) {
    try {
      await test();
      console.log(`  ✅ ${test.name.replace('check', '')} compliance`);
    } catch (error) {
      console.log(`  ❌ ${test.name.replace('check', '')} compliance: ${error.message}`);
      throw error;
    }
  }
}

async function checkInitialization() {
  // Test that server properly handles initialization
  const { Server } = await import('@modelcontextprotocol/sdk/server/index.js');
  const { TestTransport } = await import('../tests/utils/test-transport.js');
  
  const server = new Server({
    name: 'test-server',
    version: '1.0.0',
  }, {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  });
  
  const transport = new TestTransport();
  await server.connect(transport);
  
  const response = await transport.request({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'test-client',
        version: '1.0.0',
      },
    },
  });
  
  if (!response.protocolVersion) {
    throw new Error('Server did not return protocol version');
  }
  
  await server.close();
}

async function checkToolsCapability() {
  // Verify tools capability is properly implemented
  const toolsExist = await fs.access('src/tools')
    .then(() => true)
    .catch(() => false);
  
  if (!toolsExist) {
    console.log('    (No tools implemented yet)');
    return;
  }
  
  // Check that tools are properly exported
  const { tools } = await import('../src/tools/index.js');
  if (!Array.isArray(tools)) {
    throw new Error('Tools must be exported as an array');
  }
}

async function checkResourcesCapability() {
  // Verify resources capability is properly implemented
  const resourcesExist = await fs.access('src/resources')
    .then(() => true)
    .catch(() => false);
  
  if (!resourcesExist) {
    console.log('    (No resources implemented yet)');
    return;
  }
  
  // Check that resources are properly exported
  const { resources } = await import('../src/resources/index.js');
  if (!Array.isArray(resources)) {
    throw new Error('Resources must be exported as an array');
  }
}

async function checkPromptsCapability() {
  // Verify prompts capability is properly implemented
  const promptsExist = await fs.access('src/prompts')
    .then(() => true)
    .catch(() => false);
  
  if (!promptsExist) {
    console.log('    (No prompts implemented yet)');
    return;
  }
  
  // Check that prompts are properly exported
  const { prompts } = await import('../src/prompts/index.js');
  if (!Array.isArray(prompts)) {
    throw new Error('Prompts must be exported as an array');
  }
}

async function checkErrorHandling() {
  // Test that server properly handles errors
  const { handleError } = await import('../src/utils/error-handler.js');
  
  // Test known error
  const knownError = new Error('Test error');
  knownError.code = 'TEST_ERROR';
  const response1 = handleError(knownError);
  if (!response1.error || response1.error.code !== 'TEST_ERROR') {
    throw new Error('Error handler does not preserve error codes');
  }
  
  // Test unknown error
  const unknownError = new Error('Unknown error');
  const response2 = handleError(unknownError);
  if (!response2.error || response2.error.code !== 'INTERNAL_ERROR') {
    throw new Error('Error handler does not handle unknown errors');
  }
}

async function launchInspector() {
  console.log('Starting MCP Inspector...');
  console.log('This will open an interactive testing UI in your browser.');
  console.log('Press Ctrl+C to stop the inspector.\n');
  
  const inspector = exec('npx @modelcontextprotocol/inspector');
  
  inspector.stdout.on('data', (data) => {
    console.log(data.toString());
  });
  
  inspector.stderr.on('data', (data) => {
    console.error(data.toString());
  });
  
  inspector.on('close', (code) => {
    console.log(`Inspector exited with code ${code}`);
  });
}
```