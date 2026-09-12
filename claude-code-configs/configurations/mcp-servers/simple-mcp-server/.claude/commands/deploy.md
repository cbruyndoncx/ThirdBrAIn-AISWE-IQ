# Deploy MCP Server

Deploys your MCP server to various platforms and registries.

## Usage

```
/deploy [target] [options]
```

## Targets

- `npm` - Publish to npm registry
- `docker` - Push to Docker registry
- `claude` - Register with Claude Code
- `github` - Create GitHub release

## Options

- `--tag` - Version tag (default: from package.json)
- `--registry` - Custom registry URL
- `--dry-run` - Test deployment without publishing

## Implementation

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);

async function deployServer(
  target: 'npm' | 'docker' | 'claude' | 'github',
  options: {
    tag?: string;
    registry?: string;
    dryRun?: boolean;
  } = {}
) {
  console.log('🚀 Deploying MCP Server');
  console.log('='.repeat(50));
  
  // Get version info
  const pkg = JSON.parse(await fs.readFile('package.json', 'utf-8'));
  const version = options.tag || pkg.version;
  
  // Pre-deployment checks
  await runPreDeploymentChecks(version);
  
  // Deploy based on target
  switch (target) {
    case 'npm':
      await deployToNpm(pkg, version, options);
      break;
    case 'docker':
      await deployToDocker(pkg, version, options);
      break;
    case 'claude':
      await deployToClaude(pkg, version, options);
      break;
    case 'github':
      await deployToGitHub(pkg, version, options);
      break;
  }
  
  console.log('\n✅ Deployment completed successfully!');
}

async function runPreDeploymentChecks(version: string) {
  console.log('\n🔍 Running pre-deployment checks...');
  
  // Check git status
  try {
    const { stdout: status } = await execAsync('git status --porcelain');
    if (status.trim()) {
      throw new Error('Working directory has uncommitted changes');
    }
    console.log('  ✅ Working directory clean');
  } catch (error) {
    if (error.message.includes('uncommitted')) {
      throw error;
    }
    console.warn('  ⚠️  Git not available');
  }
  
  // Check if version tag exists
  try {
    await execAsync(`git rev-parse v${version}`);
    console.log(`  ✅ Version tag v${version} exists`);
  } catch {
    console.warn(`  ⚠️  Version tag v${version} not found`);
    console.log('  Create with: git tag v' + version);
  }
  
  // Verify build exists
  const buildExists = await fs.access('dist').then(() => true).catch(() => false);
  if (!buildExists) {
    throw new Error('Build not found. Run /build first');
  }
  console.log('  ✅ Build found');
  
  // Run tests
  console.log('  Running tests...');
  try {
    await execAsync('npm test');
    console.log('  ✅ Tests passed');
  } catch {
    throw new Error('Tests must pass before deployment');
  }
}

async function deployToNpm(pkg: any, version: string, options: any) {
  console.log(`\n📦 Deploying to npm (v${version})...`);
  
  // Check npm authentication
  try {
    await execAsync('npm whoami');
    console.log('  ✅ npm authenticated');
  } catch {
    throw new Error('Not authenticated with npm. Run: npm login');
  }
  
  // Check if version already published
  try {
    const { stdout } = await execAsync(`npm view ${pkg.name}@${version}`);
    if (stdout) {
      throw new Error(`Version ${version} already published`);
    }
  } catch (error) {
    if (error.message.includes('already published')) {
      throw error;
    }
    // Version not published yet (good)
  }
  
  // Update version if different
  if (pkg.version !== version) {
    console.log(`  Updating version to ${version}...`);
    await execAsync(`npm version ${version} --no-git-tag-version`);
  }
  
  // Publish package
  const publishCmd = options.dryRun
    ? 'npm publish --dry-run'
    : `npm publish ${options.registry ? `--registry ${options.registry}` : ''}`;
  
  console.log('  Publishing to npm...');
  const { stdout } = await execAsync(publishCmd);
  
  if (options.dryRun) {
    console.log('  🧪 Dry run complete (not published)');
  } else {
    console.log('  ✅ Published to npm');
    console.log(`  Install with: npm install ${pkg.name}`);
    console.log(`  View at: https://www.npmjs.com/package/${pkg.name}`);
  }
}

async function deployToDocker(pkg: any, version: string, options: any) {
  console.log(`\n🐋 Deploying to Docker registry (v${version})...`);
  
  const imageName = pkg.name.replace('@', '').replace('/', '-');
  const registry = options.registry || 'docker.io';
  const fullImageName = `${registry}/${imageName}`;
  
  // Check Docker authentication
  try {
    await execAsync(`docker pull ${registry}/hello-world`);
    console.log('  ✅ Docker authenticated');
  } catch {
    console.warn('  ⚠️  May not be authenticated with Docker registry');
  }
  
  // Build image if not exists
  try {
    await execAsync(`docker image inspect ${imageName}:${version}`);
    console.log('  ✅ Docker image exists');
  } catch {
    console.log('  Building Docker image...');
    await execAsync(`docker build -t ${imageName}:${version} -t ${imageName}:latest .`);
  }
  
  // Tag for registry
  console.log('  Tagging image...');
  await execAsync(`docker tag ${imageName}:${version} ${fullImageName}:${version}`);
  await execAsync(`docker tag ${imageName}:latest ${fullImageName}:latest`);
  
  // Push to registry
  if (!options.dryRun) {
    console.log('  Pushing to registry...');
    await execAsync(`docker push ${fullImageName}:${version}`);
    await execAsync(`docker push ${fullImageName}:latest`);
    console.log('  ✅ Pushed to Docker registry');
    console.log(`  Pull with: docker pull ${fullImageName}:${version}`);
  } else {
    console.log('  🧪 Dry run complete (not pushed)');
  }
}

async function deployToClaude(pkg: any, version: string, options: any) {
  console.log(`\n🤖 Registering with Claude Code...`);
  
  // Create Claude integration instructions
  const instructions = `
# Claude Code Integration

## Installation

### From npm
\`\`\`bash
claude mcp add ${pkg.name} -- npx ${pkg.name}
\`\`\`

### From local build
\`\`\`bash
claude mcp add ${pkg.name} -- node ${path.resolve('dist/index.js')}
\`\`\`

### With custom configuration
\`\`\`bash
claude mcp add ${pkg.name} \\
  --env LOG_LEVEL=info \\
  --env CUSTOM_CONFIG=/path/to/config \\
  -- npx ${pkg.name}
\`\`\`

## Available Capabilities

- Tools: ${await countTools()}
- Resources: ${await countResources()}
- Prompts: ${await countPrompts()}

## Version: ${version}
`;
  
  // Save integration instructions
  const instructionsPath = 'CLAUDE_INTEGRATION.md';
  await fs.writeFile(instructionsPath, instructions);
  
  console.log('  ✅ Integration instructions created');
  console.log(`  View: ${instructionsPath}`);
  
  // Test local integration
  if (!options.dryRun) {
    console.log('  Testing local integration...');
    try {
      const { stdout } = await execAsync('claude mcp list');
      if (stdout.includes(pkg.name)) {
        console.log('  ✅ Already registered with Claude Code');
      } else {
        console.log('  Register with:');
        console.log(`    claude mcp add ${pkg.name} -- node ${path.resolve('dist/index.js')}`);
      }
    } catch {
      console.log('  Claude Code CLI not available');
    }
  }
}

async function deployToGitHub(pkg: any, version: string, options: any) {
  console.log(`\n💙 Creating GitHub release (v${version})...`);
  
  // Check gh CLI
  try {
    await execAsync('gh --version');
  } catch {
    throw new Error('GitHub CLI not installed. Install from: https://cli.github.com');
  }
  
  // Check authentication
  try {
    await execAsync('gh auth status');
    console.log('  ✅ GitHub authenticated');
  } catch {
    throw new Error('Not authenticated with GitHub. Run: gh auth login');
  }
  
  // Create release notes
  const releaseNotes = await generateReleaseNotes(version);
  const notesPath = `.release-notes-${version}.md`;
  await fs.writeFile(notesPath, releaseNotes);
  
  // Create release
  if (!options.dryRun) {
    const releaseCmd = `gh release create v${version} \\
      --title "v${version}" \\
      --notes-file ${notesPath} \\
      --generate-notes`;
    
    try {
      await execAsync(releaseCmd);
      console.log('  ✅ GitHub release created');
      
      // Get release URL
      const { stdout } = await execAsync(`gh release view v${version} --json url`);
      const { url } = JSON.parse(stdout);
      console.log(`  View at: ${url}`);
    } catch (error) {
      if (error.message.includes('already exists')) {
        console.log('  ℹ️ Release already exists');
      } else {
        throw error;
      }
    }
  } else {
    console.log('  🧪 Dry run complete (release not created)');
    console.log(`  Release notes saved to: ${notesPath}`);
  }
  
  // Cleanup
  await fs.unlink(notesPath).catch(() => {});
}

async function generateReleaseNotes(version: string): Promise<string> {
  const pkg = JSON.parse(await fs.readFile('package.json', 'utf-8'));
  
  return `
# ${pkg.name} v${version}

## 🎆 What's New

- [Add your changes here]

## 📦 Installation

### npm
\`\`\`bash
npm install ${pkg.name}@${version}
\`\`\`

### Claude Code
\`\`\`bash
claude mcp add ${pkg.name} -- npx ${pkg.name}@${version}
\`\`\`

## 📄 Documentation

See [README.md](README.md) for usage instructions.

## 🔧 MCP Capabilities

- Tools: ${await countTools()}
- Resources: ${await countResources()}
- Prompts: ${await countPrompts()}
`;
}

async function countTools(): Promise<number> {
  try {
    const files = await fs.readdir('src/tools').catch(() => []);
    return files.filter(f => f.endsWith('.ts') && f !== 'index.ts').length;
  } catch {
    return 0;
  }
}

async function countResources(): Promise<number> {
  try {
    const files = await fs.readdir('src/resources').catch(() => []);
    return files.filter(f => f.endsWith('.ts') && f !== 'index.ts').length;
  } catch {
    return 0;
  }
}

async function countPrompts(): Promise<number> {
  try {
    const files = await fs.readdir('src/prompts').catch(() => []);
    return files.filter(f => f.endsWith('.ts') && f !== 'index.ts').length;
  } catch {
    return 0;
  }
}
```