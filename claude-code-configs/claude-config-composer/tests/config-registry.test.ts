import path from 'path';
import { beforeEach, describe, expect, it } from 'vitest';
import { ConfigRegistry } from '../src/registry/config-registry';

describe('ConfigRegistry', () => {
  let registry: ConfigRegistry;
  const testConfigsPath = path.resolve(__dirname, '..', '..', 'configurations');

  beforeEach(() => {
    registry = new ConfigRegistry(testConfigsPath);
  });

  describe('initialization', () => {
    it('should initialize without errors', async () => {
      await expect(registry.initialize()).resolves.not.toThrow();
    });

    it('should load all valid configurations', async () => {
      await registry.initialize();
      const configs = registry.getAll();

      expect(configs.length).toBeGreaterThan(0);
    });

    it('should include expected configurations', async () => {
      await registry.initialize();
      const configs = registry.getAll();
      const configIds = configs.map(c => c.id);

      const expectedConfigs = [
        'nextjs-15',
        'shadcn',
        'tailwindcss',
        'vercel-ai-sdk',
        'drizzle',
        'memory-mcp-server',
        'token-gated-mcp-server',
      ];

      expectedConfigs.forEach(expectedId => {
        expect(configIds).toContain(expectedId);
      });
    });
  });

  describe('configuration validation', () => {
    it('should validate that all configs have required metadata', async () => {
      await registry.initialize();
      const configs = registry.getAll();

      for (const config of configs) {
        // Check that config has required metadata
        expect(config.path).toBeDefined();
        expect(config.id).toBeDefined();
        expect(config.name).toBeDefined();
      }
    });

    it('should have proper metadata structure', async () => {
      await registry.initialize();
      const configs = registry.getAll();

      configs.forEach(config => {
        expect(config).toHaveProperty('id');
        expect(config).toHaveProperty('name');
        expect(config).toHaveProperty('description');
        expect(config).toHaveProperty('version');
        expect(config).toHaveProperty('category');
        expect(config).toHaveProperty('path');
        expect(config).toHaveProperty('priority');

        expect(typeof config.id).toBe('string');
        expect(typeof config.name).toBe('string');
        expect(typeof config.description).toBe('string');
        expect(typeof config.version).toBe('string');
        expect(typeof config.category).toBe('string');
        expect(typeof config.path).toBe('string');
        expect(typeof config.priority).toBe('number');

        expect(config.id).toBeTruthy();
        expect(config.name).toBeTruthy();
        expect(config.description).toBeTruthy();
        expect(config.version).toBeTruthy();
      });
    });

    it('should have valid categories', async () => {
      await registry.initialize();
      const configs = registry.getAll();
      const validCategories = [
        'framework',
        'ui',
        'tooling',
        'testing',
        'database',
        'api',
        'mcp-server',
      ];

      configs.forEach(config => {
        expect(validCategories).toContain(config.category);
      });
    });
  });

  describe('configuration retrieval', () => {
    beforeEach(async () => {
      await registry.initialize();
    });

    it('should retrieve configs by ID', () => {
      const nextjsConfig = registry.get('nextjs-15');

      expect(nextjsConfig).toBeDefined();
      expect(nextjsConfig?.id).toBe('nextjs-15');
      expect(nextjsConfig?.name).toBe('Next.js 15');
    });

    it('should return undefined for non-existent config', () => {
      const nonExistentConfig = registry.get('non-existent');
      expect(nonExistentConfig).toBeUndefined();
    });

    it('should retrieve configs by category', () => {
      const frameworkConfigs = registry.getByCategory('framework');
      const uiConfigs = registry.getByCategory('ui');
      const toolingConfigs = registry.getByCategory('tooling');
      const databaseConfigs = registry.getByCategory('database');

      expect(frameworkConfigs.length).toBeGreaterThan(0);
      expect(uiConfigs.length).toBeGreaterThan(0);
      expect(toolingConfigs.length).toBeGreaterThan(0);
      expect(databaseConfigs.length).toBeGreaterThan(0);

      frameworkConfigs.forEach(config => {
        expect(config.category).toBe('framework');
      });

      uiConfigs.forEach(config => {
        expect(config.category).toBe('ui');
      });
    });
  });

  describe('compatibility validation', () => {
    beforeEach(async () => {
      await registry.initialize();
    });

    it('should validate compatible configurations', () => {
      const result = registry.validateCompatibility(['nextjs-15', 'shadcn', 'tailwindcss']);

      expect(result.valid).toBe(true);
      expect(result.conflicts).toHaveLength(0);
      expect(result.missingDependencies).toHaveLength(0);
    });

    it('should handle single configuration', () => {
      const result = registry.validateCompatibility(['nextjs-15']);

      expect(result.valid).toBe(true);
      expect(result.conflicts).toHaveLength(0);
      expect(result.missingDependencies).toHaveLength(0);
    });

    it('should handle empty configuration list', () => {
      const result = registry.validateCompatibility([]);

      expect(result.valid).toBe(true);
      expect(result.conflicts).toHaveLength(0);
      expect(result.missingDependencies).toHaveLength(0);
    });

    it('should handle non-existent configurations gracefully', () => {
      const result = registry.validateCompatibility(['non-existent-config']);

      // Should not throw error, but config won't be found
      expect(result).toBeDefined();
      expect(typeof result.valid).toBe('boolean');
    });
  });

  describe('configuration content', () => {
    beforeEach(async () => {
      await registry.initialize();
    });

    it('should read configuration content', async () => {
      const content = await registry.getConfigContent('nextjs-15');

      expect(content).toBeDefined();
      expect(typeof content).toBe('string');
      expect(content?.length).toBeGreaterThan(0);
      expect(content).toContain('Next.js 15');
    });

    it('should return null for non-existent config content', async () => {
      const content = await registry.getConfigContent('non-existent');

      expect(content).toBeNull();
    });

    it('should read content for all registered configs', async () => {
      const configs = registry.getAll();

      for (const config of configs) {
        const content = await registry.getConfigContent(config.id);
        expect(content).toBeDefined();
        expect(typeof content).toBe('string');
        expect(content?.length).toBeGreaterThan(0);
      }
    });
  });

  describe('configuration priorities', () => {
    beforeEach(async () => {
      await registry.initialize();
    });

    it('should have reasonable priority values', () => {
      const configs = registry.getAll();

      configs.forEach(config => {
        expect(config.priority).toBeGreaterThanOrEqual(0);
        expect(config.priority).toBeLessThanOrEqual(20);
      });
    });

    it('should sort configs by priority when needed', () => {
      const configs = registry.getAll();
      const sortedByPriority = [...configs].sort((a, b) => b.priority - a.priority);

      expect(sortedByPriority[0].priority).toBeGreaterThanOrEqual(
        sortedByPriority[sortedByPriority.length - 1].priority
      );
    });
  });
});
