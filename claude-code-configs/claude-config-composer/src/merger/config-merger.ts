import type { ConfigMetadata } from '../registry/config-registry';
import type { PackageDependencies } from '../types/config';
import { ConfigurationError, ErrorHandler, ValidationError } from '../utils/error-handler';

interface Section {
  title: string;
  content: string;
  level: number;
  source: string;
  priority: number;
  mergeable?: boolean;
}

export class ConfigMerger {
  private sections: Map<string, Section[]> = new Map();

  parseMarkdown(content: string, source: string, metadata?: ConfigMetadata): Section[] {
    try {
      if (!content || typeof content !== 'string') {
        throw new ConfigurationError(`Invalid content provided for parsing from source: ${source}`);
      }

      if (!source || typeof source !== 'string') {
        throw new ValidationError('Source identifier is required for markdown parsing');
      }

      const sections: Section[] = [];
      const lines = content.split('\n');

      let currentSection: Section | null = null;
      let contentBuffer: string[] = [];

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const headerMatch = line.match(/^(#{1,6})\s+(.+)$/);

        if (headerMatch) {
          if (currentSection) {
            currentSection.content = contentBuffer.join('\n').trim();
            // Include section even if it has no content (title-only sections)
            sections.push(currentSection);
          }

          const level = headerMatch[1].length;
          const title = headerMatch[2].trim();

          // Validate section title
          if (!title) {
            ErrorHandler.warn(
              new ConfigurationError(`Empty section title found at line ${i + 1} in ${source}`),
              'parse-markdown'
            );
            continue;
          }

          const sectionMetadata = metadata?.sections?.find(
            s => s.title.toLowerCase() === title.toLowerCase()
          );

          currentSection = {
            title,
            content: '',
            level: Math.min(level, 6), // Ensure level doesn't exceed 6
            source,
            priority: sectionMetadata?.priority ?? 0,
            mergeable: sectionMetadata?.mergeable ?? true,
          };
          contentBuffer = [];
        } else {
          contentBuffer.push(line);
        }
      }

      if (currentSection) {
        currentSection.content = contentBuffer.join('\n').trim();
        // Include section even if it has no content (title-only sections)
        sections.push(currentSection);
      }

      return sections;
    } catch (error) {
      if (error instanceof ConfigurationError || error instanceof ValidationError) {
        throw error;
      }
      throw new ConfigurationError(
        `Failed to parse markdown from ${source}: ${error instanceof Error ? error.message : String(error)}`,
        error as Error
      );
    }
  }

  addConfig(content: string, metadata: ConfigMetadata): void {
    try {
      if (!metadata) {
        throw new ValidationError('Configuration metadata is required');
      }

      if (!metadata.name) {
        throw new ValidationError('Configuration metadata must have a name');
      }

      const sections = this.parseMarkdown(content, metadata.name, metadata);

      for (const section of sections) {
        try {
          // Use normalized title for grouping similar sections
          const key = this.normalizeTitle(section.title);

          if (!this.sections.has(key)) {
            this.sections.set(key, []);
          }

          this.sections.get(key)?.push(section);
        } catch (error) {
          ErrorHandler.warn(
            new ConfigurationError(
              `Failed to process section "${section.title}" from ${metadata.name}: ${error instanceof Error ? error.message : String(error)}`,
              error as Error
            ),
            'add-config-section'
          );
        }
      }
    } catch (error) {
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ConfigurationError(
        `Failed to add configuration: ${error instanceof Error ? error.message : String(error)}`,
        error as Error
      );
    }
  }

  private normalizeTitle(title: string): string {
    // Special normalization for "Development Assistant" titles to group them together
    if (title.toLowerCase().includes('development assistant')) {
      return 'development assistant';
    }

    // Special normalization for similar section types
    const normalizations: Record<string, string> = {
      'breaking changes': 'breaking changes',
      'file conventions': 'file conventions',
      'project structure': 'project structure',
      'common commands': 'common commands',
      'available commands': 'available commands',
      'security best practices': 'security best practices',
      'performance optimization': 'performance optimization',
      testing: 'testing',
      deployment: 'deployment',
    };

    const titleLower = title.toLowerCase();
    for (const [pattern, normalized] of Object.entries(normalizations)) {
      if (titleLower.includes(pattern)) {
        return normalized;
      }
    }

    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  merge(
    configs: Array<{
      content: string;
      metadata: ConfigMetadata;
      dependencies?: PackageDependencies;
    }>
  ): string {
    return ErrorHandler.wrapSync(() => {
      // Validate inputs
      if (!configs || !Array.isArray(configs)) {
        throw new ValidationError('Configurations must be provided as an array');
      }

      // Handle empty configuration list with default output
      if (configs.length === 0) {
        return this.createEmptyConfiguration();
      }

      // Validate each config
      for (let i = 0; i < configs.length; i++) {
        const config = configs[i];
        if (!config || typeof config !== 'object') {
          throw new ValidationError(`Invalid configuration at index ${i}`);
        }
        if (!config.content || typeof config.content !== 'string') {
          throw new ValidationError(`Configuration at index ${i} has invalid content`);
        }
        if (!config.metadata) {
          throw new ValidationError(`Configuration at index ${i} is missing metadata`);
        }
      }

      this.sections.clear();

      // Add all configurations
      for (const { content, metadata } of configs) {
        try {
          this.addConfig(content, metadata);
        } catch (error) {
          ErrorHandler.warn(
            new ConfigurationError(
              `Failed to add configuration ${metadata.name}: ${error instanceof Error ? error.message : String(error)}`,
              error as Error
            ),
            'merge-add-config'
          );
        }
      }

      // Check if we have any sections to merge
      if (this.sections.size === 0) {
        throw new ConfigurationError(
          'No valid sections found to merge from provided configurations'
        );
      }

      const output: string[] = [];
      const processedSections = new Set<string>();

      // Generate header
      try {
        output.push(`# Composed Claude Code Configuration`);
        output.push('');
        output.push(`This configuration combines: ${configs.map(c => c.metadata.name).join(', ')}`);
        output.push('');
        output.push('---');
        output.push('');
      } catch (error) {
        ErrorHandler.warn(
          new ConfigurationError(
            `Failed to generate header: ${error instanceof Error ? error.message : String(error)}`,
            error as Error
          ),
          'merge-header'
        );
      }

      try {
        const prioritizedSections = this.getPrioritizedSections();

        for (const [key, sections] of prioritizedSections) {
          if (processedSections.has(key)) continue;

          try {
            const bestSection = this.selectBestSection(sections);

            // Skip sections with no content
            const hasContent = sections.some(s => s.content && s.content.trim() !== '');
            if (!hasContent) {
              processedSections.add(key);
              continue;
            }

            if (this.shouldMergeSections(sections)) {
              const merged = this.mergeSimilarSections(sections);
              // Only add if merged content is not empty
              if (merged?.trim()) {
                output.push(`${'#'.repeat(Math.min(bestSection.level, 2))} ${bestSection.title}`);
                output.push('');
                output.push(merged);
                output.push('');
              }
            } else {
              // Only add if content is not empty
              if (bestSection.content?.trim()) {
                output.push(`${'#'.repeat(Math.min(bestSection.level, 2))} ${bestSection.title}`);
                output.push('');
                output.push(bestSection.content);
                output.push('');
              }
            }

            processedSections.add(key);
          } catch (error) {
            ErrorHandler.warn(
              new ConfigurationError(
                `Failed to process section group "${key}": ${error instanceof Error ? error.message : String(error)}`,
                error as Error
              ),
              'merge-section'
            );
          }
        }
      } catch (error) {
        throw new ConfigurationError(
          `Failed to process sections: ${error instanceof Error ? error.message : String(error)}`,
          error as Error
        );
      }

      try {
        this.addMetadata(output, configs);
      } catch (error) {
        ErrorHandler.warn(
          new ConfigurationError(
            `Failed to add metadata: ${error instanceof Error ? error.message : String(error)}`,
            error as Error
          ),
          'merge-metadata'
        );
      }

      const result = output.join('\n');
      if (!result.trim()) {
        throw new ConfigurationError('Merge resulted in empty configuration');
      }

      return result;
    }, 'merge-configurations');
  }

  private getPrioritizedSections(): Array<[string, Section[]]> {
    const entries = Array.from(this.sections.entries());

    return entries.sort(([keyA, sectionsA], [keyB, sectionsB]) => {
      const maxPriorityA = Math.max(...sectionsA.map(s => s.priority));
      const maxPriorityB = Math.max(...sectionsB.map(s => s.priority));

      if (maxPriorityA !== maxPriorityB) {
        return maxPriorityB - maxPriorityA;
      }

      const orderMap: Record<string, number> = {
        'project context': 100,
        critical: 90,
        'core principles': 85,
        'technology stack': 80,
        'breaking changes': 75,
        'file conventions': 70,
        patterns: 65,
        'common commands': 60,
        security: 55,
        performance: 50,
        testing: 45,
        deployment: 40,
        debugging: 35,
        resources: 30,
      };

      for (const [pattern, _order] of Object.entries(orderMap)) {
        const aMatches = keyA.includes(pattern);
        const bMatches = keyB.includes(pattern);
        if (aMatches && !bMatches) return -1;
        if (!aMatches && bMatches) return 1;
        if (aMatches && bMatches) return 0;
      }

      return 0;
    });
  }

  private selectBestSection(sections: Section[]): Section {
    return sections.reduce((best, current) => {
      if (current.priority > best.priority) return current;
      if (current.priority === best.priority && current.content.length > best.content.length) {
        return current;
      }
      return best;
    });
  }

  private shouldMergeSections(sections: Section[]): boolean {
    if (sections.length <= 1) return false;

    // Check if any section is marked as non-mergeable
    if (sections.some(s => s.mergeable === false)) {
      return false;
    }

    const titles = sections.map(s => this.normalizeTitle(s.title));
    const uniqueTitles = new Set(titles);

    if (uniqueTitles.size > 1) return false;

    const mergeableKeywords = [
      'commands',
      'common commands',
      'development',
      'testing',
      'security',
      'performance',
      'project context',
      'technology stack',
      'dependencies',
      'scripts',
    ];

    const title = titles[0];
    return mergeableKeywords.some(keyword => title.includes(keyword));
  }

  private mergeSimilarSections(sections: Section[]): string {
    const mergedContent: string[] = [];
    const sources = [...new Set(sections.map(s => s.source))];

    // Only add "Combined from" if there are multiple unique sources
    if (sources.length > 1) {
      mergedContent.push(`*Combined from: ${sources.join(', ')}*`);
      mergedContent.push('');
    }

    // Special handling for sections with numbered lists (like Security Best Practices)
    const isNumberedListSection = sections.some(
      s => s.content.match(/^\d+\.\s+/m) || s.content.includes('1. ')
    );

    if (isNumberedListSection) {
      return this.mergeNumberedLists(sections, sources);
    }

    // Special handling for project context sections
    if (sections[0].title.toLowerCase().includes('project context')) {
      return this.mergeProjectContexts(sections, sources);
    }

    // For other sections, use improved content merging
    const contentMap = new Map<string, string[]>();
    const processedContent = new Set<string>();

    for (const section of sections) {
      if (!section.content || section.content.trim() === '') continue;

      const lines = section.content.split('\n');
      let currentSubsection = 'main';

      for (const line of lines) {
        // Track subsections
        if (line.match(/^#{3,}\s+/)) {
          currentSubsection = line;
        }

        if (!contentMap.has(currentSubsection)) {
          contentMap.set(currentSubsection, []);
        }

        const normalizedLine = line.trim();
        const contentKey = normalizedLine.toLowerCase().replace(/[^a-z0-9]/g, '');

        // Skip empty lines and duplicates
        if (
          normalizedLine &&
          !normalizedLine.startsWith('*Combined from:') &&
          !processedContent.has(contentKey)
        ) {
          contentMap.get(currentSubsection)?.push(line);
          if (contentKey) processedContent.add(contentKey);
        }
      }
    }

    // Rebuild content with proper structure
    for (const [subsection, lines] of contentMap) {
      if (lines.length === 0) continue; // Skip empty subsections

      if (subsection !== 'main') {
        mergedContent.push(subsection);
      }
      mergedContent.push(...lines);
    }

    return mergedContent.join('\n').trim();
  }

  private mergeNumberedLists(sections: Section[], sources: string[]): string {
    const mergedContent: string[] = [];

    if (sources.length > 1) {
      mergedContent.push(`*Combined from: ${sources.join(', ')}*`);
      mergedContent.push('');
    }

    const allItems = new Map<string, { content: string; source: string }>();
    let itemNumber = 1;

    for (const section of sections) {
      if (!section.content || section.content.trim() === '') continue;

      const lines = section.content.split('\n');
      let currentItem: string[] = [];
      let isInItem = false;

      for (const line of lines) {
        // Check if this is a numbered item (at any level)
        if (line.match(/^\d+\.\s+/)) {
          // Save previous item if exists
          if (currentItem.length > 0) {
            const itemText = currentItem.join('\n');
            const itemKey = itemText
              .toLowerCase()
              .replace(/^\d+\.\s+/, '')
              .trim();

            if (!allItems.has(itemKey)) {
              allItems.set(itemKey, { content: itemText, source: section.source });
            }
          }

          currentItem = [line];
          isInItem = true;
        } else if (isInItem && line.match(/^\s+/)) {
          // Continuation of current item (indented)
          currentItem.push(line);
        } else if (line.trim() === '') {
          // Empty line might end an item
          if (currentItem.length > 0) {
            const itemText = currentItem.join('\n');
            const itemKey = itemText
              .toLowerCase()
              .replace(/^\d+\.\s+/, '')
              .trim();

            if (!allItems.has(itemKey)) {
              allItems.set(itemKey, { content: itemText, source: section.source });
            }
            currentItem = [];
            isInItem = false;
          }
        } else if (!line.startsWith('*Combined from:')) {
          // Other content
          if (currentItem.length > 0) {
            const itemText = currentItem.join('\n');
            const itemKey = itemText
              .toLowerCase()
              .replace(/^\d+\.\s+/, '')
              .trim();

            if (!allItems.has(itemKey)) {
              allItems.set(itemKey, { content: itemText, source: section.source });
            }
            currentItem = [];
            isInItem = false;
          }
          mergedContent.push(line);
        }
      }

      // Don't forget the last item
      if (currentItem.length > 0) {
        const itemText = currentItem.join('\n');
        const itemKey = itemText
          .toLowerCase()
          .replace(/^\d+\.\s+/, '')
          .trim();

        if (!allItems.has(itemKey)) {
          allItems.set(itemKey, { content: itemText, source: section.source });
        }
      }
    }

    // Renumber and add all unique items
    for (const { content } of allItems.values()) {
      const renumbered = content.replace(/^\d+\.\s+/, `${itemNumber}. `);
      mergedContent.push(renumbered);
      itemNumber++;
    }

    return mergedContent.join('\n').trim();
  }

  private mergeProjectContexts(sections: Section[], sources: string[]): string {
    const mergedContent: string[] = [];

    if (sources.length > 1) {
      mergedContent.push(`*Combined from: ${sources.join(', ')}*`);
      mergedContent.push('');
    }

    // Collect unique project descriptions
    const projectDescriptions = new Map<string, string>();

    for (const section of sections) {
      if (!section.content || section.content.trim() === '') continue;

      // Extract project description paragraphs
      const lines = section.content.split('\n');
      const descriptionLines: string[] = [];

      for (const line of lines) {
        if (!line.startsWith('*Combined from:')) {
          descriptionLines.push(line);
        }
      }

      if (descriptionLines.length > 0) {
        const description = descriptionLines.join('\n').trim();
        if (description && !projectDescriptions.has(section.source)) {
          projectDescriptions.set(section.source, description);
        }
      }
    }

    // Combine project descriptions intelligently
    const descriptions = Array.from(projectDescriptions.values());
    if (descriptions.length === 1) {
      mergedContent.push(descriptions[0]);
    } else {
      // For multiple descriptions, present them as a unified context
      mergedContent.push('This is a comprehensive project that combines multiple technologies:');
      mergedContent.push('');

      for (const desc of descriptions) {
        // Add each description as a paragraph
        mergedContent.push(desc);
        mergedContent.push('');
      }
    }

    return mergedContent.join('\n').trim();
  }

  private createEmptyConfiguration(): string {
    const output: string[] = [];
    output.push('# Composed Claude Code Configuration');
    output.push('');
    output.push('This configuration combines: (no configurations provided)');
    output.push('');
    output.push('---');
    output.push('');
    output.push('## No Configurations Available');
    output.push('');
    output.push(
      'No configurations were provided for merging. Please specify at least one configuration.'
    );
    output.push('');
    output.push('---');
    output.push('');
    output.push('## Configuration Metadata');
    output.push('');
    output.push('### Generation Details');
    output.push('');
    output.push(`- Generated: ${new Date().toISOString()}`);
    output.push(`- Generator: Claude Config Composer v1.0.0`);
    output.push('');
    return output.join('\n');
  }

  private addMetadata(
    output: string[],
    configs: Array<{ metadata: ConfigMetadata; dependencies?: PackageDependencies }>
  ) {
    output.push('');
    output.push('---');
    output.push('');
    output.push('## Configuration Metadata');
    output.push('');
    output.push('### Included Configurations');
    output.push('');

    for (const { metadata } of configs) {
      output.push(`- **${metadata.name}** v${metadata.version}: ${metadata.description}`);
    }

    // Add dependency information if available
    const configsWithDeps = configs.filter(c => c.dependencies);
    if (configsWithDeps.length > 0) {
      output.push('');
      output.push('### Dependencies');
      output.push('');

      // Collect all unique dependencies
      const allPeerDeps = new Map<string, Set<string>>();
      const allEngines = new Map<string, Set<string>>();

      for (const { dependencies } of configsWithDeps) {
        if (dependencies?.peerDependencies) {
          for (const [pkg, version] of Object.entries(dependencies.peerDependencies)) {
            if (!allPeerDeps.has(pkg)) allPeerDeps.set(pkg, new Set());
            allPeerDeps.get(pkg)?.add(version as string);
          }
        }
        if (dependencies?.engines) {
          for (const [engine, version] of Object.entries(dependencies.engines)) {
            if (!allEngines.has(engine)) allEngines.set(engine, new Set());
            allEngines.get(engine)?.add(version as string);
          }
        }
      }

      if (allEngines.size > 0) {
        output.push('#### Required Engines');
        output.push('');
        for (const [engine, versions] of allEngines) {
          const versionList = Array.from(versions).join(', ');
          output.push(`- **${engine}**: ${versionList}`);
        }
        output.push('');
      }

      if (allPeerDeps.size > 0) {
        output.push('#### Peer Dependencies');
        output.push('');
        output.push('These packages should be installed in your project:');
        output.push('');
        for (const [pkg, versions] of allPeerDeps) {
          const versionList = Array.from(versions).join(' or ');
          output.push(`- **${pkg}**: ${versionList}`);
        }
        output.push('');
      }
    }

    output.push('');
    output.push('### Generation Details');
    output.push('');
    output.push(`- Generated: ${new Date().toISOString()}`);
    output.push(`- Generator: Claude Config Composer v1.0.0`);
    output.push('');
    output.push('### Compatibility Notes');
    output.push('');
    output.push(
      'This is a composed configuration. Some features may require additional setup or conflict resolution.'
    );
    output.push(
      'Review the combined configuration carefully and adjust as needed for your specific project.'
    );
  }
}
