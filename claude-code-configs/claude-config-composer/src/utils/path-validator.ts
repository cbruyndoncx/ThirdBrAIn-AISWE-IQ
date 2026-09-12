import fs from 'fs';
import path from 'path';

/**
 * Security utilities for path validation and sanitization
 * Prevents directory traversal attacks and ensures safe file operations
 */

export class PathValidationError extends Error {
  constructor(
    message: string,
    public readonly path?: string
  ) {
    super(message);
    this.name = 'PathValidationError';
  }
}

/**
 * Validates and sanitizes file paths to prevent directory traversal attacks
 */
export class PathValidator {
  private static readonly UNSAFE_PATTERNS = [
    /\.\.[\\/]/, // Parent directory traversal
    /^\.\.[\\/]/, // Leading parent directory
    /[\\/]\.\.[\\/]/, // Middle parent directory
    /[\\/]\.\.$/, // Trailing parent directory
    /\0/, // Null bytes
    // Note: Windows invalid characters are checked separately for filenames only
    // Note: Absolute paths are blocked here but allowed in validateOutputPath
  ];

  private static readonly ABSOLUTE_PATH_PATTERNS = [
    /^[\\/]/, // Absolute paths starting with / or \
    /^[a-zA-Z]:[\\/]/, // Windows absolute paths (C:\, D:\, etc.)
  ];

  private static readonly MAX_PATH_LENGTH = 260; // Windows MAX_PATH
  private static readonly MAX_FILENAME_LENGTH = 255;

  // Windows-specific invalid filename characters
  private static readonly WINDOWS_INVALID_CHARS = /[<>:"|?*]/;

  // Check if running on Windows
  private static isWindows(): boolean {
    try {
      return process.platform === 'win32';
    } catch {
      // If process.platform is not available, assume Unix-like for safety
      return false;
    }
  }

  /**
   * Sanitizes a path by removing or replacing unsafe characters
   */
  static sanitizePath(inputPath: string): string {
    if (!inputPath || typeof inputPath !== 'string') {
      throw new PathValidationError('Path must be a non-empty string');
    }

    // Remove null bytes and normalize
    let sanitized = inputPath.replace(/\0/g, '');

    // Normalize path separators to forward slashes
    sanitized = sanitized.replace(/\\/g, '/');

    // Remove leading and trailing whitespace
    sanitized = sanitized.trim();

    // Remove leading slashes to prevent absolute paths
    sanitized = sanitized.replace(/^\/+/, '');

    // Resolve any .. patterns safely
    const segments = sanitized.split('/');
    const safeSegments: string[] = [];

    for (const segment of segments) {
      if (segment === '' || segment === '.') {
        continue; // Skip empty or current directory segments
      }
      if (segment === '..') {
        // Remove the last segment if it exists (but don't go above root)
        if (safeSegments.length > 0) {
          safeSegments.pop();
        }
        continue;
      }
      safeSegments.push(segment);
    }

    return safeSegments.join('/');
  }

  /**
   * Validates internal absolute paths (for package/system paths)
   * Less restrictive than validatePath for trusted internal use
   */
  static validateInternalPath(inputPath: string): string {
    if (!inputPath || typeof inputPath !== 'string') {
      throw new PathValidationError('Path must be a non-empty string');
    }

    // Check path length limits
    if (inputPath.length > PathValidator.MAX_PATH_LENGTH) {
      throw new PathValidationError(
        `Path exceeds maximum length of ${PathValidator.MAX_PATH_LENGTH} characters`,
        inputPath
      );
    }

    // Check for dangerous patterns but allow absolute paths for internal use
    const dangerousPatterns = [
      /\.\.[\\/]/, // Parent directory traversal
      /^\.\.[\\/]/, // Leading parent directory
      /[\\/]\.\.[\\/]/, // Middle parent directory
      /[\\/]\.\.$/, // Trailing parent directory
      /\0/, // Null bytes
    ];

    for (const pattern of dangerousPatterns) {
      if (pattern.test(inputPath)) {
        throw new PathValidationError(`Path contains unsafe pattern: ${pattern.source}`, inputPath);
      }
    }

    return path.normalize(inputPath);
  }

  /**
   * Validates an output path for CLI usage (allows absolute paths)
   */
  static validateOutputPath(inputPath: string): string {
    if (!inputPath || typeof inputPath !== 'string') {
      throw new PathValidationError('Path must be a non-empty string');
    }

    // Check for dangerous patterns (but allow absolute paths)
    for (const pattern of PathValidator.UNSAFE_PATTERNS) {
      if (pattern.test(inputPath)) {
        throw new PathValidationError(`Path contains unsafe pattern: ${pattern.source}`, inputPath);
      }
    }

    // Check path length limits
    if (inputPath.length > PathValidator.MAX_PATH_LENGTH) {
      throw new PathValidationError(
        `Path exceeds maximum length of ${PathValidator.MAX_PATH_LENGTH} characters`,
        inputPath
      );
    }

    // Allow absolute paths for output directory
    return inputPath;
  }

  /**
   * Validates that a path is safe and within allowed boundaries
   */
  static validatePath(inputPath: string, allowedBasePath?: string): string {
    if (!inputPath || typeof inputPath !== 'string') {
      throw new PathValidationError('Path must be a non-empty string');
    }

    // Check for unsafe patterns including absolute paths
    const allPatterns = [...PathValidator.UNSAFE_PATTERNS, ...PathValidator.ABSOLUTE_PATH_PATTERNS];
    for (const pattern of allPatterns) {
      if (pattern.test(inputPath)) {
        throw new PathValidationError(`Path contains unsafe pattern: ${pattern.source}`, inputPath);
      }
    }

    // Check path length limits
    if (inputPath.length > PathValidator.MAX_PATH_LENGTH) {
      throw new PathValidationError(
        `Path exceeds maximum length of ${PathValidator.MAX_PATH_LENGTH} characters`,
        inputPath
      );
    }

    // Sanitize the path
    const sanitized = PathValidator.sanitizePath(inputPath);

    // If a base path is provided, ensure the path stays within it
    // Avoid path.resolve() which uses process.cwd() internally
    if (allowedBasePath) {
      // Use path.normalize instead of resolve to avoid process.cwd()
      const normalizedBase = path.normalize(allowedBasePath);
      const normalizedTarget = path.normalize(path.join(allowedBasePath, sanitized));

      // Check if the target path escapes the base directory
      // by checking for .. components after normalization
      const relativePath = path.relative(normalizedBase, normalizedTarget);
      // Normalize separators for consistent checking across platforms
      const normalizedRelative = relativePath.replace(/\\/g, '/');
      if (normalizedRelative.startsWith('..')) {
        throw new PathValidationError('Path attempts to escape allowed directory', inputPath);
      }
    }

    return sanitized;
  }

  /**
   * Validates a filename (not a full path)
   */
  static validateFilename(filename: string): string {
    if (!filename || typeof filename !== 'string') {
      throw new PathValidationError('Filename must be a non-empty string');
    }

    // Check filename length
    if (filename.length > PathValidator.MAX_FILENAME_LENGTH) {
      throw new PathValidationError(
        `Filename exceeds maximum length of ${PathValidator.MAX_FILENAME_LENGTH} characters`,
        filename
      );
    }

    // Remove null bytes and control characters
    let sanitized = filename.replace(/[\0-\u001f\u007f-\u009f]/g, '');

    // Platform-specific validation
    if (PathValidator.isWindows()) {
      // Check for reserved names on Windows
      const reserved = /^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)/i;
      if (reserved.test(sanitized)) {
        throw new PathValidationError('Filename uses reserved system name', filename);
      }

      // Remove invalid characters on Windows
      sanitized = sanitized.replace(PathValidator.WINDOWS_INVALID_CHARS, '');
    } else {
      // On Unix/Linux, only remove the truly problematic characters
      // Allow colons and other characters that are valid on these systems
      sanitized = sanitized.replace(/[<>"|?*]/g, ''); // Remove chars invalid on Unix but keep :
    }

    // Remove leading/trailing dots and spaces
    sanitized = sanitized.replace(/^[.\s]+|[.\s]+$/g, '');

    if (!sanitized) {
      throw new PathValidationError('Filename becomes empty after sanitization', filename);
    }

    return sanitized;
  }

  /**
   * Validates a configuration ID (alphanumeric with hyphens and underscores only)
   */
  static validateConfigId(configId: string): string {
    if (!configId || typeof configId !== 'string') {
      throw new PathValidationError('Configuration ID must be a non-empty string');
    }

    const sanitized = configId.trim().toLowerCase();

    // Only allow alphanumeric characters, hyphens, and underscores
    if (!/^[a-z0-9_-]+$/.test(sanitized)) {
      throw new PathValidationError(
        'Configuration ID must contain only alphanumeric characters, hyphens, and underscores',
        configId
      );
    }

    // Prevent starting or ending with special characters
    if (/^[-_]|[-_]$/.test(sanitized)) {
      throw new PathValidationError(
        'Configuration ID cannot start or end with hyphens or underscores',
        configId
      );
    }

    // Prevent consecutive special characters
    if (/[-_]{2,}/.test(sanitized)) {
      throw new PathValidationError(
        'Configuration ID cannot contain consecutive hyphens or underscores',
        configId
      );
    }

    return sanitized;
  }

  /**
   * Safely creates a directory path, ensuring it's within the allowed base path
   */
  static async createSafeDirectory(targetPath: string, basePath: string): Promise<string> {
    // Handle current directory case - just use the provided basePath
    // Avoid process.cwd() which can fail in CI when directory is deleted
    const effectiveBasePath = basePath || '.';

    const validatedPath = PathValidator.validatePath(targetPath, effectiveBasePath);
    const fullPath = path.join(effectiveBasePath, validatedPath);

    // Double-check using path operations that don't require process.cwd()
    // Use normalize and relative instead of resolve
    const normalizedBase = path.normalize(effectiveBasePath);
    const normalizedTarget = path.normalize(fullPath);

    // Check if target escapes base using relative path
    const relativePath = path.relative(normalizedBase, normalizedTarget);
    // Normalize separators for consistent checking across platforms
    const normalizedRelative = relativePath.replace(/\\/g, '/');
    if (normalizedRelative.startsWith('..')) {
      throw new PathValidationError('Resolved path escapes base directory', targetPath);
    }

    return fullPath;
  }

  /**
   * Safely resolves a file path, ensuring it's within the allowed base path
   */
  static async createSafeFilePath(
    filename: string,
    directory: string,
    basePath: string
  ): Promise<string> {
    const validatedFilename = PathValidator.validateFilename(filename);
    const validatedDirectory = PathValidator.validatePath(directory, basePath);

    const fullDirectory = path.join(basePath, validatedDirectory);
    const fullPath = path.join(fullDirectory, validatedFilename);

    // Double-check using path operations that don't require process.cwd()
    const normalizedTarget = path.normalize(fullPath);

    // Check if target escapes base without using path.relative()
    // which can call process.cwd() and fail in CI
    // Simply ensure the path doesn't contain .. after normalization
    if (normalizedTarget.includes('..')) {
      throw new PathValidationError(
        'Resolved file path escapes base directory',
        `${directory}/${filename}`
      );
    }

    return fullPath;
  }

  /**
   * Validates that a path exists and is accessible
   */
  static async validatePathExists(filePath: string): Promise<boolean> {
    try {
      await fs.promises.access(filePath, fs.constants.F_OK);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Validates that a path is a directory
   */
  static async validateIsDirectory(dirPath: string): Promise<boolean> {
    try {
      const stats = await fs.promises.stat(dirPath);
      return stats.isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * Gets the file extension safely
   */
  static getFileExtension(filename: string): string {
    const validatedFilename = PathValidator.validateFilename(filename);
    return path.extname(validatedFilename).toLowerCase();
  }

  /**
   * Validates allowed file extensions
   */
  static validateFileExtension(filename: string, allowedExtensions: string[]): boolean {
    const extension = PathValidator.getFileExtension(filename);
    return allowedExtensions.includes(extension);
  }
}

/**
 * Convenience function for common path validation
 */
export function validatePath(inputPath: string, allowedBasePath?: string): string {
  return PathValidator.validatePath(inputPath, allowedBasePath);
}

/**
 * Convenience function for filename validation
 */
export function validateFilename(filename: string): string {
  return PathValidator.validateFilename(filename);
}

/**
 * Convenience function for configuration ID validation
 */
export function validateConfigId(configId: string): string {
  return PathValidator.validateConfigId(configId);
}
