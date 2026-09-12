import crypto from 'crypto';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

/**
 * Caching utilities for improving performance of repeated operations
 *
 * This module provides file-based caching with automatic expiration,
 * cache invalidation, and memory management.
 */

/**
 * Cache entry metadata
 */
interface CacheEntry<T = unknown> {
  /** The cached data */
  data: T;
  /** Timestamp when the entry was created */
  timestamp: number;
  /** Expiration time in milliseconds */
  expiresAt: number;
  /** Version of the cached data */
  version: string;
  /** Hash of the original input that generated this cache */
  inputHash: string;
}

/**
 * Cache configuration options
 */
export interface CacheOptions {
  /** Cache directory (defaults to system temp + 'claude-config-composer') */
  cacheDir?: string;
  /** Default TTL in milliseconds (default: 1 hour) */
  defaultTTL?: number;
  /** Maximum cache size in MB (default: 100MB) */
  maxSizeBytes?: number;
  /** Whether to enable cache compression */
  compress?: boolean;
  /** Cache version for invalidation */
  version?: string;
}

/**
 * Default cache configuration
 */
const DEFAULT_CACHE_OPTIONS: Required<CacheOptions> = {
  cacheDir: path.join(os.tmpdir(), 'claude-config-composer'),
  defaultTTL: 60 * 60 * 1000, // 1 hour
  maxSizeBytes: 100 * 1024 * 1024, // 100MB
  compress: true,
  version: '1.0.0',
};

/**
 * Simple in-memory cache for frequently accessed data
 */
class MemoryCache<T = unknown> {
  private cache = new Map<string, CacheEntry<T>>();
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.maxSize = maxSize;
  }

  get(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  set(key: string, data: T, ttl?: number): void {
    // Remove oldest entries if cache is full
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }

    const now = Date.now();
    const expiresAt = now + (ttl || DEFAULT_CACHE_OPTIONS.defaultTTL);

    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt,
      version: DEFAULT_CACHE_OPTIONS.version,
      inputHash: '',
    });
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }

  keys(): string[] {
    return Array.from(this.cache.keys());
  }
}

/**
 * File-based cache manager with persistence and cleanup
 */
export class FileCache {
  private options: Required<CacheOptions>;
  private memoryCache: MemoryCache;

  constructor(options: CacheOptions = {}) {
    this.options = { ...DEFAULT_CACHE_OPTIONS, ...options };
    this.memoryCache = new MemoryCache(50); // Keep 50 items in memory
  }

  /**
   * Generate a cache key from input data
   *
   * @param input - Input data to hash
   * @returns Cache key string
   */
  private generateKey(input: string | Record<string, unknown>): string {
    const inputStr = typeof input === 'string' ? input : JSON.stringify(input);
    return crypto.createHash('md5').update(inputStr).digest('hex');
  }

  /**
   * Get cache file path for a given key
   *
   * @param key - Cache key
   * @returns Full path to cache file
   */
  private getCacheFilePath(key: string): string {
    return path.join(this.options.cacheDir, `${key}.json`);
  }

  /**
   * Ensure cache directory exists
   */
  private async ensureCacheDir(): Promise<void> {
    try {
      await fs.mkdir(this.options.cacheDir, { recursive: true });
    } catch (_error) {
      // Directory already exists or creation failed - non-fatal
    }
  }

  /**
   * Get data from cache
   *
   * @param key - Cache key or input to generate key from
   * @returns Cached data or null if not found/expired
   *
   * @example
   * ```typescript
   * const cache = new FileCache();
   * const result = await cache.get('my-computation-input');
   * if (result) {
   *   console.log('Cache hit:', result);
   * } else {
   *   console.log('Cache miss - need to compute');
   * }
   * ```
   */
  async get<T = unknown>(key: string | Record<string, unknown>): Promise<T | null> {
    const cacheKey = typeof key === 'string' ? key : this.generateKey(key);

    // Check memory cache first
    const memoryResult = this.memoryCache.get(cacheKey);
    if (memoryResult) {
      return memoryResult as T;
    }

    try {
      const filePath = this.getCacheFilePath(cacheKey);
      const content = await fs.readFile(filePath, 'utf-8');
      const entry: CacheEntry<T> = JSON.parse(content);

      // Check if expired
      if (Date.now() > entry.expiresAt) {
        await this.delete(cacheKey);
        return null;
      }

      // Check version compatibility
      if (entry.version !== this.options.version) {
        await this.delete(cacheKey);
        return null;
      }

      // Cache in memory for faster subsequent access
      this.memoryCache.set(cacheKey, entry.data);

      return entry.data;
    } catch {
      // File doesn't exist or is corrupted
      return null;
    }
  }

  /**
   * Store data in cache
   *
   * @param key - Cache key or input to generate key from
   * @param data - Data to cache
   * @param ttl - Time to live in milliseconds (optional)
   *
   * @example
   * ```typescript
   * const cache = new FileCache();
   * const result = await expensiveComputation();
   * await cache.set('my-computation-input', result, 30 * 60 * 1000); // Cache for 30 minutes
   * ```
   */
  async set<T = unknown>(
    key: string | Record<string, unknown>,
    data: T,
    ttl?: number
  ): Promise<void> {
    const cacheKey = typeof key === 'string' ? key : this.generateKey(key);
    const inputHash = typeof key === 'string' ? key : this.generateKey(key);

    await this.ensureCacheDir();

    const now = Date.now();
    const expiresAt = now + (ttl || this.options.defaultTTL);

    const entry: CacheEntry<T> = {
      data,
      timestamp: now,
      expiresAt,
      version: this.options.version,
      inputHash,
    };

    try {
      const filePath = this.getCacheFilePath(cacheKey);
      await fs.writeFile(filePath, JSON.stringify(entry), 'utf-8');

      // Also cache in memory
      this.memoryCache.set(cacheKey, data, ttl);
    } catch (error) {
      // Cache write failed - non-fatal, just log and continue
      console.warn('Failed to write cache file:', error);
    }

    // Clean up old cache files periodically
    if (Math.random() < 0.1) {
      // 10% chance to trigger cleanup
      setImmediate(() => this.cleanup());
    }
  }

  /**
   * Delete a cache entry
   *
   * @param key - Cache key or input to generate key from
   * @returns True if entry was deleted, false if not found
   */
  async delete(key: string | Record<string, unknown>): Promise<boolean> {
    const cacheKey = typeof key === 'string' ? key : this.generateKey(key);

    // Remove from memory cache
    this.memoryCache.delete(cacheKey);

    try {
      const filePath = this.getCacheFilePath(cacheKey);
      await fs.unlink(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Clear all cache entries
   */
  async clear(): Promise<void> {
    this.memoryCache.clear();

    try {
      const files = await fs.readdir(this.options.cacheDir);
      const deletePromises = files
        .filter(file => file.endsWith('.json'))
        .map(file => fs.unlink(path.join(this.options.cacheDir, file)));

      await Promise.all(deletePromises);
    } catch {
      // Directory doesn't exist or is empty
    }
  }

  /**
   * Clean up expired and oversized cache
   */
  async cleanup(): Promise<void> {
    try {
      await this.ensureCacheDir();
      const files = await fs.readdir(this.options.cacheDir);
      const now = Date.now();
      let totalSize = 0;
      const fileStats: Array<{ path: string; size: number; mtime: number }> = [];

      // Get file stats
      for (const file of files) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(this.options.cacheDir, file);
        try {
          const stats = await fs.stat(filePath);
          totalSize += stats.size;
          fileStats.push({
            path: filePath,
            size: stats.size,
            mtime: stats.mtime.getTime(),
          });

          // Check if file is expired
          try {
            const content = await fs.readFile(filePath, 'utf-8');
            const entry: CacheEntry = JSON.parse(content);

            if (now > entry.expiresAt || entry.version !== this.options.version) {
              await fs.unlink(filePath);
              totalSize -= stats.size;
            }
          } catch {
            // Corrupted file, delete it
            await fs.unlink(filePath);
            totalSize -= stats.size;
          }
        } catch {
          // File no longer exists
        }
      }

      // If total size exceeds limit, remove oldest files
      if (totalSize > this.options.maxSizeBytes) {
        const sortedFiles = fileStats
          .filter(file => file.path.endsWith('.json'))
          .sort((a, b) => a.mtime - b.mtime); // Oldest first

        for (const fileInfo of sortedFiles) {
          if (totalSize <= this.options.maxSizeBytes) break;

          try {
            await fs.unlink(fileInfo.path);
            totalSize -= fileInfo.size;
          } catch {
            // File already deleted
          }
        }
      }
    } catch (error) {
      console.warn('Cache cleanup failed:', error);
    }
  }

  /**
   * Get cache statistics
   *
   * @returns Cache usage statistics
   */
  async stats(): Promise<{
    totalFiles: number;
    totalSizeBytes: number;
    totalSizeMB: number;
    oldestEntry: number | null;
    newestEntry: number | null;
    memoryCache: {
      size: number;
      keys: string[];
    };
  }> {
    try {
      await this.ensureCacheDir();
      const files = await fs.readdir(this.options.cacheDir);
      let totalSize = 0;
      let oldestEntry: number | null = null;
      let newestEntry: number | null = null;
      let validFiles = 0;

      for (const file of files) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(this.options.cacheDir, file);
        try {
          const stats = await fs.stat(filePath);
          totalSize += stats.size;
          validFiles++;

          const mtime = stats.mtime.getTime();
          if (oldestEntry === null || mtime < oldestEntry) {
            oldestEntry = mtime;
          }
          if (newestEntry === null || mtime > newestEntry) {
            newestEntry = mtime;
          }
        } catch {
          // File no longer exists
        }
      }

      return {
        totalFiles: validFiles,
        totalSizeBytes: totalSize,
        totalSizeMB: Math.round((totalSize / 1024 / 1024) * 100) / 100,
        oldestEntry,
        newestEntry,
        memoryCache: {
          size: this.memoryCache.size(),
          keys: this.memoryCache.keys(),
        },
      };
    } catch {
      return {
        totalFiles: 0,
        totalSizeBytes: 0,
        totalSizeMB: 0,
        oldestEntry: null,
        newestEntry: null,
        memoryCache: {
          size: this.memoryCache.size(),
          keys: this.memoryCache.keys(),
        },
      };
    }
  }
}

/**
 * Singleton cache instance for global use
 */
let globalCache: FileCache | null = null;

/**
 * Get the global cache instance
 *
 * @param options - Cache options (only used on first call)
 * @returns Global cache instance
 */
export function getGlobalCache(options?: CacheOptions): FileCache {
  if (!globalCache) {
    globalCache = new FileCache(options);
  }
  return globalCache;
}

/**
 * Memoization decorator for caching function results
 *
 * @param fn - Function to memoize
 * @param options - Cache options
 * @returns Memoized function
 *
 * @example
 * ```typescript
 * const expensiveFunction = memoize(async (input: string) => {
 *   // Expensive computation
 *   await new Promise(resolve => setTimeout(resolve, 1000));
 *   return input.toUpperCase();
 * }, { defaultTTL: 5 * 60 * 1000 }); // Cache for 5 minutes
 *
 * // First call: computes result
 * const result1 = await expensiveFunction('hello');
 *
 * // Second call: returns cached result
 * const result2 = await expensiveFunction('hello');
 * ```
 */
export function memoize<TArgs extends unknown[], TReturn>(
  fn: (...args: TArgs) => Promise<TReturn>,
  options: CacheOptions = {}
): (...args: TArgs) => Promise<TReturn> {
  const cache = new FileCache(options);

  return async (...args: TArgs): Promise<TReturn> => {
    const key = { function: fn.name, args };

    // Try to get from cache
    const cached = await cache.get<TReturn>(key);
    if (cached !== null) {
      return cached;
    }

    // Compute result and cache it
    const result = await fn(...args);
    await cache.set(key, result);

    return result;
  };
}

/**
 * Cache key generation utilities
 */
export const CacheKey = {
  /**
   * Generate cache key for configuration parsing
   */
  configParse: (configPath: string, lastModified: number) =>
    `config-parse:${configPath}:${lastModified}`,

  /**
   * Generate cache key for configuration merging
   */
  configMerge: (configIds: string[], options: Record<string, unknown>) =>
    `config-merge:${configIds.sort().join(',')}:${JSON.stringify(options)}`,

  /**
   * Generate cache key for registry loading
   */
  registryLoad: (registryPath: string, lastModified: number) =>
    `registry-load:${registryPath}:${lastModified}`,

  /**
   * Generate cache key for validation
   */
  validation: (targetPath: string, lastModified: number) =>
    `validation:${targetPath}:${lastModified}`,
};
