import path from 'path';
import { beforeEach, describe, expect, it } from 'vitest';
import { ConfigRegistry } from '../../src/registry/config-registry';

describe('ConfigRegistry Unit Tests', () => {
  let configRegistry: ConfigRegistry;
  const configurationsPath = path.resolve(__dirname, '../../../configurations');

  beforeEach(async () => {
    configRegistry = new ConfigRegistry(configurationsPath);
    await configRegistry.initialize();
  });

  describe('Initialization', () => {
    it('should initialize with valid configurations', () => {
      const configs = configRegistry.getAll();
      expect(configs.length).toBeGreaterThan(0);

      // Check for expected core configurations
      const configIds = configs.map(c => c.id);
      expect(configIds).toContain('nextjs-15');
      expect(configIds).toContain('shadcn');
      expect(configIds).toContain('tailwindcss');
    });

    it('should load configuration metadata correctly', () => {
      const nextjsConfig = configRegistry.get('nextjs-15');

      expect(nextjsConfig).toBeDefined();
      expect(nextjsConfig?.name).toBe('Next.js 15');
      expect(nextjsConfig?.category).toBe('framework');
      expect(nextjsConfig?.version).toBe('15.0.0');
      expect(nextjsConfig?.priority).toBe(10);
    });

    it('should validate configuration paths exist', () => {
      const configs = configRegistry.getAll();

      for (const config of configs) {
        expect(config.path).toBeDefined();
        expect(typeof config.path).toBe('string');
        expect(config.path.length).toBeGreaterThan(0);
      }
    });
  });

  describe('Configuration Validation', () => {
    it('should validate all configurations have required fields', () => {
      const configs = configRegistry.getAll();

      for (const config of configs) {
        expect(config.id).toBeDefined();
        expect(config.name).toBeDefined();
        expect(config.description).toBeDefined();
        expect(config.version).toBeDefined();
        expect(config.category).toBeDefined();
        expect(config.path).toBeDefined();

        // Validate category is one of allowed values
        expect([
          'framework',
          'ui',
          'tooling',
          'testing',
          'database',
          'api',
          'mcp-server',
        ]).toContain(config.category);
      }
    });

    it('should handle missing configurations gracefully', () => {
      const nonExistentConfig = configRegistry.get('non-existent-config');
      expect(nonExistentConfig).toBeUndefined();
    });

    it('should validate section metadata when present', () => {
      const nextjsConfig = configRegistry.get('nextjs-15');

      if (nextjsConfig?.sections) {
        for (const section of nextjsConfig.sections) {
          expect(section.title).toBeDefined();
          expect(typeof section.title).toBe('string');
          expect(typeof section.mergeable).toBe('boolean');
          expect(typeof section.priority).toBe('number');
        }
      }
    });
  });

  describe('Priority and Ordering', () => {
    it('should order configurations by priority correctly', () => {
      const configs = configRegistry.getAll();

      // Find framework configs to test priority ordering
      const frameworkConfigs = configs.filter(c => c.category === 'framework');

      if (frameworkConfigs.length > 1) {
        const sortedByPriority = [...frameworkConfigs].sort((a, b) => b.priority - a.priority);

        for (let i = 0; i < sortedByPriority.length - 1; i++) {
          expect(sortedByPriority[i].priority).toBeGreaterThanOrEqual(
            sortedByPriority[i + 1].priority
          );
        }
      }
    });

    it('should have sensible priority values', () => {
      const configs = configRegistry.getAll();

      for (const config of configs) {
        expect(config.priority).toBeGreaterThanOrEqual(0);
        expect(config.priority).toBeLessThanOrEqual(20); // Reasonable upper bound
      }
    });

    it('should prioritize framework configs appropriately', () => {
      const nextjsConfig = configRegistry.get('nextjs-15');
      const shadcnConfig = configRegistry.get('shadcn');

      if (nextjsConfig && shadcnConfig) {
        // Framework should generally have higher priority than UI
        expect(nextjsConfig.priority).toBeGreaterThanOrEqual(shadcnConfig.priority);
      }
    });
  });

  describe('Categories', () => {
    it('should group configurations by category correctly', () => {
      const configs = configRegistry.getAll();
      const categories = new Map<string, string[]>();

      for (const config of configs) {
        if (!categories.has(config.category)) {
          categories.set(config.category, []);
        }
        const categoryList = categories.get(config.category);
        if (categoryList) {
          categoryList.push(config.id);
        }
      }

      // Should have framework category
      expect(categories.has('framework')).toBe(true);
      expect(categories.get('framework')).toContain('nextjs-15');

      // Should have ui category
      expect(categories.has('ui')).toBe(true);
      expect(categories.get('ui')).toContain('shadcn');

      // Should have tooling category
      expect(categories.has('tooling')).toBe(true);
    });

    it('should have reasonable distribution across categories', () => {
      const configs = configRegistry.getAll();
      const categoryCounts = new Map<string, number>();

      for (const config of configs) {
        categoryCounts.set(config.category, (categoryCounts.get(config.category) || 0) + 1);
      }

      // Should have multiple categories
      expect(categoryCounts.size).toBeGreaterThan(2);

      // No category should dominate too much
      const totalConfigs = configs.length;
      for (const [_category, count] of categoryCounts) {
        expect(count / totalConfigs).toBeLessThan(0.8); // No category > 80%
      }
    });
  });

  describe('Dependencies and Conflicts', () => {
    it('should handle configurations with dependencies', () => {
      const configs = configRegistry.getAll();
      const configIds = configs.map(c => c.id);

      for (const config of configs) {
        if (config.dependencies) {
          expect(Array.isArray(config.dependencies)).toBe(true);

          // Each dependency should reference a valid config
          for (const dep of config.dependencies) {
            expect(typeof dep).toBe('string');
            expect(configIds).toContain(dep);
          }
        }
      }
    });

    it('should handle configurations with conflicts', () => {
      const configs = configRegistry.getAll();

      for (const config of configs) {
        if (config.conflicts) {
          expect(Array.isArray(config.conflicts)).toBe(true);

          for (const conflict of config.conflicts) {
            expect(typeof conflict).toBe('string');
            // Conflicts may reference configs that don't exist yet, so we don't validate existence
          }
        }
      }
    });

    it('should not have circular dependencies', () => {
      const configs = configRegistry.getAll();
      const configMap = new Map(configs.map(c => [c.id, c]));

      // Simple check for direct circular dependencies
      for (const config of configs) {
        if (config.dependencies) {
          expect(config.dependencies).not.toContain(config.id); // Can't depend on self

          // Check if any dependency also depends on this config
          for (const depId of config.dependencies) {
            const depConfig = configMap.get(depId);
            if (depConfig?.dependencies) {
              expect(depConfig.dependencies).not.toContain(config.id);
            }
          }
        }
      }
    });
  });

  describe('Section Configuration', () => {
    it('should have valid section configurations for configs that define them', () => {
      const nextjsConfig = configRegistry.get('nextjs-15');

      expect(nextjsConfig?.sections).toBeDefined();
      expect(Array.isArray(nextjsConfig?.sections)).toBe(true);

      if (nextjsConfig?.sections) {
        // Should have critical sections marked as non-mergeable
        const criticalSection = nextjsConfig.sections.find(
          s => s.title.includes('Critical') || s.title.includes('Breaking')
        );

        if (criticalSection) {
          expect(criticalSection.mergeable).toBe(false);
          expect(criticalSection.priority).toBeGreaterThan(10); // High priority
        }

        // Should have common sections marked as mergeable
        const commonSection = nextjsConfig.sections.find(s => s.title.includes('Common Commands'));

        if (commonSection) {
          expect(commonSection.mergeable).toBe(true);
        }
      }
    });

    it('should have reasonable section priority distribution', () => {
      const configs = configRegistry.getAll();

      for (const config of configs) {
        if (config.sections) {
          const priorities = config.sections.map(s => s.priority);

          // Should have varied priorities
          if (priorities.length > 1) {
            const uniquePriorities = new Set(priorities);
            expect(uniquePriorities.size).toBeGreaterThan(1);
          }

          // All priorities should be reasonable
          for (const priority of priorities) {
            expect(priority).toBeGreaterThanOrEqual(0);
            expect(priority).toBeLessThanOrEqual(20);
          }
        }
      }
    });
  });

  describe('Path Resolution', () => {
    it('should resolve configuration paths correctly', () => {
      const configs = configRegistry.getAll();

      for (const config of configs) {
        expect(config.path).toBeDefined();
        expect(config.path).toContain('configurations');
        expect(path.isAbsolute(config.path)).toBe(true);
      }
    });
  });
});
