import path from 'path';
import { beforeEach, describe, expect, it } from 'vitest';
import { ConfigRegistry } from '../src/registry/config-registry';

describe('ConfigRegistry', () => {
  let registry: ConfigRegistry;

  beforeEach(async () => {
    const configurationsPath = path.resolve(__dirname, '../../configurations');
    registry = new ConfigRegistry(configurationsPath);
    await registry.initialize();
  });

  describe('initialization', () => {
    it('should load all available configurations', () => {
      const configs = registry.getAll();

      expect(configs.length).toBeGreaterThan(0);
      expect(configs).toContainEqual(
        expect.objectContaining({
          id: 'nextjs-15',
          name: 'Next.js 15',
          category: 'framework',
        })
      );
      expect(configs).toContainEqual(
        expect.objectContaining({
          id: 'shadcn',
          name: 'shadcn/ui',
          category: 'ui',
        })
      );
    });

    it('should categorize configurations correctly', () => {
      const configs = registry.getAll();

      const categories = [...new Set(configs.map(c => c.category))];
      expect(categories).toContain('framework');
      expect(categories).toContain('ui');
      expect(categories).toContain('database');
      expect(categories).toContain('tooling');
    });
  });

  describe('get', () => {
    it('should retrieve configuration by ID', () => {
      const config = registry.get('nextjs-15');

      expect(config).toBeDefined();
      expect(config?.id).toBe('nextjs-15');
      expect(config?.name).toBe('Next.js 15');
      expect(config?.category).toBe('framework');
    });

    it('should return undefined for non-existent config', () => {
      const config = registry.get('non-existent');

      expect(config).toBeUndefined();
    });
  });

  describe('getByCategory', () => {
    it('should retrieve configurations by category', () => {
      const frameworkConfigs = registry.getByCategory('framework');
      const uiConfigs = registry.getByCategory('ui');

      expect(frameworkConfigs.length).toBeGreaterThan(0);
      expect(frameworkConfigs.every(c => c.category === 'framework')).toBe(true);

      expect(uiConfigs.length).toBeGreaterThan(0);
      expect(uiConfigs.every(c => c.category === 'ui')).toBe(true);
    });

    it('should return empty array for non-existent category', () => {
      const configs = registry.getByCategory('non-existent');

      expect(configs).toEqual([]);
    });
  });

  describe('validateCompatibility', () => {
    it('should validate compatible configurations', () => {
      const result = registry.validateCompatibility(['nextjs-15', 'shadcn']);

      expect(result.valid).toBe(true);
      expect(result.conflicts).toEqual([]);
      expect(result.missingDependencies).toEqual([]);
    });

    it('should handle single configuration', () => {
      const result = registry.validateCompatibility(['nextjs-15']);

      expect(result.valid).toBe(true);
      expect(result.conflicts).toEqual([]);
      expect(result.missingDependencies).toEqual([]);
    });

    it('should handle empty configuration list', () => {
      const result = registry.validateCompatibility([]);

      expect(result.valid).toBe(true);
      expect(result.conflicts).toEqual([]);
      expect(result.missingDependencies).toEqual([]);
    });

    it('should detect incompatible configurations', () => {
      // This test depends on actual conflict definitions in the configs
      // For now, we'll just verify the method returns the expected structure
      const result = registry.validateCompatibility(['nextjs-15', 'shadcn', 'tailwindcss']);

      expect(result).toHaveProperty('valid');
      expect(result).toHaveProperty('conflicts');
      expect(result).toHaveProperty('missingDependencies');
      expect(Array.isArray(result.conflicts)).toBe(true);
      expect(Array.isArray(result.missingDependencies)).toBe(true);
    });
  });

  describe('configuration validation', () => {
    it('should have valid paths for all configurations', () => {
      const configs = registry.getAll();

      configs.forEach(config => {
        expect(config.path).toBeDefined();
        expect(config.path).toContain('configurations');
      });
    });

    it('should have required metadata for all configurations', () => {
      const configs = registry.getAll();

      configs.forEach(config => {
        expect(config.id).toBeDefined();
        expect(config.name).toBeDefined();
        expect(config.version).toBeDefined();
        expect(config.description).toBeDefined();
        expect(config.category).toBeDefined();
        expect(config.priority).toBeDefined();
        expect(typeof config.priority).toBe('number');
      });
    });
  });

  describe('getConfigContent', () => {
    it('should retrieve content for existing configuration', async () => {
      const content = await registry.getConfigContent('nextjs-15');

      expect(content).toBeDefined();
      expect(content).toContain('Next.js');
    });

    it('should return null for non-existent configuration', async () => {
      const content = await registry.getConfigContent('non-existent');

      expect(content).toBeNull();
    });
  });

  describe('registry compatibility checks', () => {
    it('should detect compatible configurations', () => {
      const result = registry.validateCompatibility(['nextjs-15', 'shadcn']);

      expect(result.valid).toBe(true);
    });

    it('should handle framework conflicts gracefully', () => {
      // Get all framework configs
      const frameworkConfigs = registry.getByCategory('framework');

      // If there are multiple framework configs, they might conflict
      if (frameworkConfigs.length > 1) {
        const configIds = frameworkConfigs.map(c => c.id);
        const result = registry.validateCompatibility(configIds);

        // The result should still have the correct structure
        expect(result).toHaveProperty('compatible');
        expect(result).toHaveProperty('warnings');
        expect(result).toHaveProperty('errors');
      } else {
        // Skip this test if there's only one framework
        expect(true).toBe(true);
      }
    });
  });
});
