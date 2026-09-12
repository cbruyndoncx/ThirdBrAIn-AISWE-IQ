import fs from 'fs/promises';
import path from 'path';
import { z } from 'zod';
import { PathValidationError, PathValidator } from '../utils/path-validator';

// Legacy schema for backward compatibility - use SecureConfigMetadataSchema for new code
export const ConfigMetadataSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  version: z.string(),
  category: z.enum(['framework', 'ui', 'tooling', 'testing', 'database', 'api', 'mcp-server']),
  dependencies: z.array(z.string()).optional(),
  conflicts: z.array(z.string()).optional(),
  priority: z.number().default(0),
  path: z.string(),
  sections: z
    .array(
      z.object({
        title: z.string(),
        mergeable: z.boolean().default(true),
        priority: z.number().default(0),
      })
    )
    .optional(),
});

export type ConfigMetadata = z.infer<typeof ConfigMetadataSchema>;

export class ConfigRegistry {
  private configs: Map<string, ConfigMetadata> = new Map();
  private configsPath: string;

  constructor(configsPath?: string) {
    // Default to configurations directory relative to this module's location
    if (configsPath) {
      try {
        this.configsPath = PathValidator.validateInternalPath(configsPath);
      } catch (error) {
        throw new Error(
          `Invalid configurations path: ${error instanceof PathValidationError ? error.message : 'Unknown error'}`
        );
      }
    } else {
      // Find configurations directory
      // When installed via npm, configurations will be in the package
      // When running locally, they're in the parent directory
      const moduleDir = path.dirname(path.dirname(__dirname)); // Go up from dist/registry/ to project root

      // First, try to find configurations in the package (npm install case)
      // Use path.join instead of resolve to avoid process.cwd()
      const packageConfigs = path.join(moduleDir, 'configurations');
      // Second, try parent directory (local development case)
      const parentConfigs = path.join(moduleDir, '..', 'configurations');

      // Check which path exists and validate it
      if (require('fs').existsSync(packageConfigs)) {
        try {
          this.configsPath = PathValidator.validateInternalPath(packageConfigs);
        } catch (error) {
          throw new Error(
            `Invalid package configurations path: ${error instanceof PathValidationError ? error.message : 'Unknown error'}`
          );
        }
      } else if (require('fs').existsSync(parentConfigs)) {
        try {
          this.configsPath = PathValidator.validateInternalPath(parentConfigs);
        } catch (error) {
          throw new Error(
            `Invalid parent configurations path: ${error instanceof PathValidationError ? error.message : 'Unknown error'}`
          );
        }
      } else {
        throw new Error(
          'Could not locate configurations directory. Please ensure claude-config-composer is installed correctly.'
        );
      }
    }
  }

  async initialize() {
    const registry: ConfigMetadata[] = [
      {
        id: 'nextjs-15',
        name: 'Next.js 15',
        description: 'Next.js 15 with App Router, React 19, and Server Components',
        version: '15.0.0',
        category: 'framework',
        path: path.join(this.configsPath, 'frameworks', 'nextjs-15'),
        priority: 10,
        sections: [
          { title: 'Project Context', mergeable: true, priority: 10 },
          { title: 'Critical Next.js 15 Changes', mergeable: false, priority: 15 },
          { title: 'Core Principles', mergeable: true, priority: 8 },
          { title: 'Common Commands', mergeable: true, priority: 5 },
          { title: 'Security Best Practices', mergeable: true, priority: 7 },
          { title: 'Performance Optimization', mergeable: true, priority: 6 },
        ],
      },
      {
        id: 'shadcn',
        name: 'shadcn/ui',
        description: 'Beautiful, accessible components with Radix UI and Tailwind CSS',
        version: '0.8.0',
        category: 'ui',
        path: path.join(this.configsPath, 'ui', 'shadcn'),
        priority: 8,
        sections: [
          { title: 'Project Context', mergeable: true, priority: 10 },
          { title: 'Technology Stack', mergeable: true, priority: 9 },
          { title: 'Critical shadcn/ui Principles', mergeable: false, priority: 15 },
          { title: 'Component Development Patterns', mergeable: true, priority: 8 },
          { title: 'Theming System', mergeable: false, priority: 10 },
          { title: 'Common Commands', mergeable: true, priority: 5 },
        ],
      },
      {
        id: 'memory-mcp-server',
        name: 'Memory MCP Server',
        description: 'MCP server with memory persistence and vector search capabilities',
        version: '1.0.0',
        category: 'mcp-server',
        path: path.join(this.configsPath, 'mcp-servers', 'memory-mcp-server'),
        priority: 9,
      },
      {
        id: 'token-gated-mcp-server',
        name: 'Token-Gated MCP Server',
        description: 'Token-gated MCP server using the Radius MCP SDK',
        version: '1.0.0',
        category: 'mcp-server',
        path: path.join(this.configsPath, 'mcp-servers', 'token-gated-mcp-server'),
        priority: 8,
      },
      {
        id: 'vercel-ai-sdk',
        name: 'Vercel AI SDK',
        description: 'Streaming AI applications with function calling and multi-provider support',
        version: '1.0.0',
        category: 'tooling',
        path: path.join(this.configsPath, 'tooling', 'vercel-ai-sdk'),
        priority: 9,
        sections: [
          { title: 'Project Context', mergeable: true, priority: 10 },
          { title: 'Core AI SDK Principles', mergeable: false, priority: 15 },
          { title: 'Common Patterns', mergeable: true, priority: 8 },
          { title: 'Security Best Practices', mergeable: true, priority: 7 },
          { title: 'Performance Optimization', mergeable: true, priority: 6 },
        ],
      },
      {
        id: 'drizzle',
        name: 'Drizzle ORM',
        description: 'Type-safe database operations with schema management and migrations',
        version: '1.0.0',
        category: 'database',
        path: path.join(this.configsPath, 'databases', 'drizzle'),
        priority: 9,
        sections: [
          { title: 'Project Context', mergeable: true, priority: 10 },
          { title: 'Core Drizzle Principles', mergeable: false, priority: 15 },
          { title: 'Database Setup', mergeable: true, priority: 12 },
          { title: 'Schema Patterns', mergeable: true, priority: 8 },
          { title: 'Query Patterns', mergeable: true, priority: 8 },
          { title: 'Migration Management', mergeable: true, priority: 9 },
        ],
      },
      {
        id: 'tailwindcss',
        name: 'Tailwind CSS',
        description: 'Utility-first CSS framework for rapid UI development',
        version: '3.4.0',
        category: 'ui',
        path: path.join(this.configsPath, 'ui', 'tailwindcss'),
        priority: 7,
        sections: [
          { title: 'Project Context', mergeable: true, priority: 10 },
          { title: 'Core Tailwind Principles', mergeable: false, priority: 15 },
          { title: 'Configuration Patterns', mergeable: true, priority: 9 },
          { title: 'Component Patterns', mergeable: true, priority: 8 },
          { title: 'Responsive Design Patterns', mergeable: true, priority: 8 },
          { title: 'Dark Mode Implementation', mergeable: true, priority: 7 },
        ],
      },
    ];

    // Validate configs before registering
    const validatedConfigs = await this.validateConfigs(registry);
    for (const config of validatedConfigs) {
      this.configs.set(config.id, config);
    }
  }

  private async validateConfigs(configs: ConfigMetadata[]): Promise<ConfigMetadata[]> {
    const validConfigs: ConfigMetadata[] = [];
    const errors: string[] = [];

    for (const config of configs) {
      try {
        const validation = await this.validateConfig(config);
        if (validation.valid) {
          validConfigs.push(config);
        } else {
          errors.push(`Config '${config.id}': ${validation.errors.join(', ')}`);
        }
      } catch (error) {
        errors.push(`Config '${config.id}': ${error}`);
      }
    }

    if (errors.length > 0) {
      console.warn('⚠️  Configuration validation warnings:');
      errors.forEach(error => console.warn(`   ${error}`));
    }

    return validConfigs;
  }

  private async validateConfig(
    config: ConfigMetadata
  ): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];

    try {
      // Check if directory exists
      await fs.access(config.path);

      // Check if CLAUDE.md exists
      const claudeMdPath = path.join(config.path, 'CLAUDE.md');
      await fs.access(claudeMdPath);

      // Check if README.md exists
      const readmePath = path.join(config.path, 'README.md');
      try {
        await fs.access(readmePath);
      } catch {
        errors.push('README.md missing');
      }
    } catch {
      errors.push('directory or CLAUDE.md not found');
      return { valid: false, errors };
    }

    return { valid: errors.length === 0, errors };
  }

  getAll(): ConfigMetadata[] {
    return Array.from(this.configs.values());
  }

  getByCategory(category: string): ConfigMetadata[] {
    return this.getAll().filter(c => c.category === category);
  }

  get(id: string): ConfigMetadata | undefined {
    return this.configs.get(id);
  }

  validateCompatibility(selectedIds: string[]): {
    valid: boolean;
    conflicts: string[];
    missingDependencies: string[];
  } {
    const conflicts: string[] = [];
    const missingDependencies: string[] = [];

    for (const id of selectedIds) {
      const config = this.get(id);
      if (!config) continue;

      if (config.conflicts) {
        const foundConflicts = config.conflicts.filter(c => selectedIds.includes(c));
        conflicts.push(...foundConflicts.map(c => `${id} conflicts with ${c}`));
      }

      if (config.dependencies) {
        const missing = config.dependencies.filter(d => !selectedIds.includes(d));
        missingDependencies.push(...missing.map(d => `${id} requires ${d}`));
      }
    }

    return {
      valid: conflicts.length === 0 && missingDependencies.length === 0,
      conflicts,
      missingDependencies,
    };
  }

  async getConfigContent(id: string): Promise<string | null> {
    const config = this.get(id);
    if (!config) return null;

    const claudeMdPath = path.join(config.path, 'CLAUDE.md');
    try {
      return await fs.readFile(claudeMdPath, 'utf-8');
    } catch {
      return null;
    }
  }
}
