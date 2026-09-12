#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Configuration metadata mapping
const configMetadata = {
  'frameworks/nextjs-15': {
    name: 'Next.js 15',
    version: '1.0.0',
    category: 'framework'
  },
  'ui/shadcn': {
    name: 'shadcn/ui',
    version: '1.0.0',
    category: 'ui'
  },
  'ui/tailwindcss': {
    name: 'Tailwind CSS',
    version: '1.0.0',
    category: 'ui'
  },
  'databases/drizzle': {
    name: 'Drizzle ORM',
    version: '1.0.0',
    category: 'database'
  },
  'tooling/vercel-ai-sdk': {
    name: 'Vercel AI SDK',
    version: '1.0.0',
    category: 'tooling'
  },
  'mcp-servers/memory-mcp-server': {
    name: 'Memory MCP Server',
    version: '1.0.0',
    category: 'mcp-server'
  },
  'mcp-servers/token-gated-mcp-server': {
    name: 'Token-Gated MCP Server',
    version: '1.0.0',
    category: 'mcp-server'
  }
};

const configurationsDir = path.resolve(__dirname, '../../configurations');

Object.entries(configMetadata).forEach(([configPath, metadata]) => {
  const settingsPath = path.join(configurationsDir, configPath, '.claude', 'settings.json');
  
  if (fs.existsSync(settingsPath)) {
    try {
      const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'));
      
      // Add metadata if not present
      if (!settings._metadata) {
        settings._metadata = {
          name: metadata.name,
          version: metadata.version,
          category: metadata.category,
          generated: new Date().toISOString(),
          generator: 'manual',
          note: 'Official Claude Code configuration'
        };
        
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
        console.log(`✅ Added metadata to ${configPath}`);
      } else {
        console.log(`⏭️  Metadata already exists in ${configPath}`);
      }
    } catch (error) {
      console.error(`❌ Error processing ${configPath}: ${error.message}`);
    }
  } else {
    console.warn(`⚠️  Settings file not found: ${settingsPath}`);
  }
});

console.log('\n✅ Metadata update complete!');