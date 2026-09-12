/**
 * The interface that each TypeScript module in a .codx folder must export
 */
export interface CodxModule {
  /**
   * The string to inject into the markdown template.
   * Can be static or dynamically generated.
   */
  content: string;

  /**
   * An asynchronous function that asserts the truth of the content.
   * @throws Error if validation fails
   */
  validate: () => Promise<void>;

  /**
   * A human/AI-readable explanation of what went wrong and how to fix it.
   * Displayed in logs when validate() throws or content mismatches.
   */
  errorContent: string;
}

/**
 * Represents a discovered .codx directory and its target markdown file
 */
export interface CodxTarget {
  /** The target markdown file (e.g., "README.md") */
  targetFile: string;
  /** The .codx directory path (e.g., "README.md.codx") */
  codxDir: string;
  /** The index.md template file path */
  templateFile: string;
  /** Map of variable names to their module file paths */
  modules: Map<string, string>;
}

/**
 * Result of validating a single module
 */
export interface ValidationResult {
  /** Name of the variable/module */
  moduleName: string;
  /** Whether validation passed */
  success: boolean;
  /** Error message if validation failed */
  error?: string;
  /** The errorContent from the module */
  errorContent?: string;
}

/**
 * Result of building/validating a documentation file
 */
export interface BuildResult {
  /** The target markdown file */
  targetFile: string;
  /** Whether the build/validation succeeded */
  success: boolean;
  /** Individual module validation results */
  validationResults: ValidationResult[];
  /** Rendered markdown content */
  renderedContent?: string;
  /** Existing content from disk */
  diskContent?: string;
  /** Whether rendered content matches disk content */
  contentMatches?: boolean;
  /** Error message if build failed */
  error?: string;
}

/**
 * Log entry for validation failures
 */
export interface LogEntry {
  timestamp: Date;
  targetFile: string;
  moduleName: string;
  errorContent: string;
  error: string;
  diff?: string;
}

/**
 * Concise failure summary for analytics
 */
export interface FailureSummary {
  timestamp: Date;
  moduleName: string;
  targetFile: string;
}

/**
 * Statistics about validation failures
 */
export interface FailureStats {
  totalFailures: number;
  byModule: Record<string, number>;
  byTarget: Record<string, number>;
  timeRange: {
    start: Date;
    end: Date;
  };
}
