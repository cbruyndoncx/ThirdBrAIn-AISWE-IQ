# Build MCP Server for Production

Builds and prepares your MCP server for production deployment.

## Usage

```
/build [target] [options]
```

## Targets

- `node` - Build for Node.js (default)
- `docker` - Build Docker image
- `npm` - Prepare for npm publishing

## Options

- `--minify` - Minify output
- `--sourcemap` - Include source maps
- `--analyze` - Analyze bundle size

## Implementation

```typescript
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);

async function buildServer(
  target: 'node' | 'docker' | 'npm' = 'node',
  options: {
    minify?: boolean;
    sourcemap?: boolean;
    analyze?: boolean;
  } = {}
) {
  console.log('🔨 Building MCP Server for Production');
  console.log('='.repeat(50));
  
  // Pre-build checks
  await runPreBuildChecks();
  
  // Build based on target
  switch (target) {
    case 'node':
      await buildForNode(options);
      break;
    case 'docker':
      await buildForDocker(options);
      break;
    case 'npm':
      await buildForNpm(options);
      break;
  }
  
  // Post-build validation
  await validateBuild(target);
  
  console.log('\n✅ Build completed successfully!');
}

async function runPreBuildChecks() {
  console.log('\n🔍 Running pre-build checks...');
  
  // Check for uncommitted changes
  try {
    const { stdout: gitStatus } = await execAsync('git status --porcelain');
    if (gitStatus.trim()) {
      console.warn('⚠️  Warning: You have uncommitted changes');
    }
  } catch {
    // Git not available or not a git repo
  }
  
  // Run tests
  console.log('  Running tests...');
  try {
    await execAsync('npm test');
    console.log('  ✅ Tests passed');
  } catch (error) {
    console.error('  ❌ Tests failed');
    throw new Error('Build aborted: tests must pass');
  }
  
  // Check dependencies
  console.log('  Checking dependencies...');
  try {
    await execAsync('npm audit --production');
    console.log('  ✅ No vulnerabilities found');
  } catch (error) {
    console.warn('  ⚠️  Security vulnerabilities detected');
    console.log('  Run "npm audit fix" to resolve');
  }
}

async function buildForNode(options: any) {
  console.log('\n📦 Building for Node.js...');
  
  // Clean previous build
  await fs.rm('dist', { recursive: true, force: true });
  
  // Update tsconfig for production
  const tsConfig = JSON.parse(await fs.readFile('tsconfig.json', 'utf-8'));
  const prodConfig = {
    ...tsConfig,
    compilerOptions: {
      ...tsConfig.compilerOptions,
      sourceMap: options.sourcemap || false,
      inlineSources: false,
      removeComments: true,
    },
  };
  
  await fs.writeFile('tsconfig.prod.json', JSON.stringify(prodConfig, null, 2));
  
  // Build with TypeScript
  console.log('  Compiling TypeScript...');
  await execAsync('npx tsc -p tsconfig.prod.json');
  
  // Minify if requested
  if (options.minify) {
    console.log('  Minifying code...');
    await minifyCode();
  }
  
  // Copy package files
  console.log('  Copying package files...');
  await fs.copyFile('package.json', 'dist/package.json');
  await fs.copyFile('README.md', 'dist/README.md').catch(() => {});
  await fs.copyFile('LICENSE', 'dist/LICENSE').catch(() => {});
  
  // Create production package.json
  const pkg = JSON.parse(await fs.readFile('package.json', 'utf-8'));
  const prodPkg = {
    ...pkg,
    scripts: {
      start: 'node index.js',
    },
    devDependencies: undefined,
  };
  await fs.writeFile('dist/package.json', JSON.stringify(prodPkg, null, 2));
  
  // Analyze bundle if requested
  if (options.analyze) {
    await analyzeBundleSize();
  }
  
  console.log('  ✅ Node.js build complete');
  console.log('  Output: ./dist');
}

async function buildForDocker(options: any) {
  console.log('\n🐋 Building Docker image...');
  
  // Build Node.js first
  await buildForNode(options);
  
  // Create Dockerfile if it doesn't exist
  const dockerfilePath = 'Dockerfile';
  if (!await fs.access(dockerfilePath).then(() => true).catch(() => false)) {
    await createDockerfile();
  }
  
  // Build Docker image
  console.log('  Building Docker image...');
  const imageName = 'mcp-server';
  const version = JSON.parse(await fs.readFile('package.json', 'utf-8')).version;
  
  await execAsync(`docker build -t ${imageName}:${version} -t ${imageName}:latest .`);
  
  // Test the image
  console.log('  Testing Docker image...');
  const { stdout } = await execAsync(`docker run --rm ${imageName}:latest node index.js --version`);
  console.log(`  Version: ${stdout.trim()}`);
  
  console.log('  ✅ Docker build complete');
  console.log(`  Image: ${imageName}:${version}`);
  console.log('  Run: docker run -it ' + imageName + ':latest');
}

async function buildForNpm(options: any) {
  console.log('\n📦 Preparing for npm publishing...');
  
  // Build Node.js first
  await buildForNode(options);
  
  // Validate package.json
  const pkg = JSON.parse(await fs.readFile('package.json', 'utf-8'));
  
  if (!pkg.name) {
    throw new Error('package.json must have a name field');
  }
  
  if (!pkg.version) {
    throw new Error('package.json must have a version field');
  }
  
  if (!pkg.description) {
    console.warn('⚠️  Warning: package.json should have a description');
  }
  
  // Create .npmignore if needed
  const npmignorePath = '.npmignore';
  if (!await fs.access(npmignorePath).then(() => true).catch(() => false)) {
    await createNpmIgnore();
  }
  
  // Run npm pack to test
  console.log('  Creating package tarball...');
  const { stdout } = await execAsync('npm pack --dry-run');
  
  // Parse package contents
  const files = stdout.split('\n').filter(line => line.includes('npm notice'));
  console.log(`  Package will include ${files.length} files`);
  
  // Check package size
  const sizeMatch = stdout.match(/npm notice ([\d.]+[kMG]B)/);
  if (sizeMatch) {
    console.log(`  Package size: ${sizeMatch[1]}`);
    
    // Warn if package is large
    if (sizeMatch[1].includes('M') && parseFloat(sizeMatch[1]) > 10) {
      console.warn('⚠️  Warning: Package is larger than 10MB');
    }
  }
  
  console.log('  ✅ npm package ready');
  console.log('  Publish with: npm publish');
}

async function createDockerfile() {
  const dockerfile = `
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app

# Install dumb-init for signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nodejs -u 1001

# Copy built application
COPY --from=builder /app/dist ./
COPY --from=builder /app/node_modules ./node_modules

# Change ownership
RUN chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3000

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "index.js"]
`;
  
  await fs.writeFile('Dockerfile', dockerfile);
  console.log('  Created Dockerfile');
}

async function createNpmIgnore() {
  const npmignore = `
# Source files
src/
tests/

# Config files
.eslintrc*
.prettierrc*
tsconfig*.json
vitest.config.ts

# Development files
*.log
.env
.env.*
!.env.example

# Build artifacts
*.tsbuildinfo
coverage/
.nyc_output/

# Docker
Dockerfile
docker-compose.yml

# Git
.git/
.gitignore

# CI/CD
.github/
.gitlab-ci.yml

# IDE
.vscode/
.idea/

# Misc
.DS_Store
Thumbs.db
`;
  
  await fs.writeFile('.npmignore', npmignore);
  console.log('  Created .npmignore');
}

async function minifyCode() {
  // Use esbuild or terser to minify
  try {
    await execAsync('npx esbuild dist/**/*.js --minify --outdir=dist --allow-overwrite');
  } catch {
    console.warn('  Minification skipped (esbuild not available)');
  }
}

async function analyzeBundleSize() {
  console.log('\n📊 Analyzing bundle size...');
  
  const files = await fs.readdir('dist', { recursive: true });
  let totalSize = 0;
  const fileSizes: Array<{ name: string; size: number }> = [];
  
  for (const file of files) {
    const filePath = path.join('dist', file as string);
    const stat = await fs.stat(filePath);
    
    if (stat.isFile()) {
      totalSize += stat.size;
      fileSizes.push({ name: file as string, size: stat.size });
    }
  }
  
  // Sort by size
  fileSizes.sort((a, b) => b.size - a.size);
  
  console.log('  Largest files:');
  fileSizes.slice(0, 5).forEach(file => {
    console.log(`    ${file.name}: ${(file.size / 1024).toFixed(2)}KB`);
  });
  
  console.log(`  Total size: ${(totalSize / 1024).toFixed(2)}KB`);
}

async function validateBuild(target: string) {
  console.log('\n🔍 Validating build...');
  
  // Check that main file exists
  const mainFile = 'dist/index.js';
  if (!await fs.access(mainFile).then(() => true).catch(() => false)) {
    throw new Error('Build validation failed: main file not found');
  }
  
  // Try to load the server
  try {
    await import(path.resolve(mainFile));
    console.log('  ✅ Server module loads successfully');
  } catch (error) {
    throw new Error(`Build validation failed: ${error.message}`);
  }
}
```