import { createReadStream, createWriteStream } from 'fs';
import fs from 'fs/promises';
import { Transform } from 'stream';
import { pipeline } from 'stream/promises';

/**
 * Streaming utilities for handling large files efficiently
 *
 * These utilities provide memory-efficient file operations by processing
 * data in chunks rather than loading entire files into memory.
 */

/**
 * Maximum chunk size for streaming operations (1MB)
 */
const CHUNK_SIZE = 1024 * 1024;

/**
 * Memory threshold for switching to streaming (10MB)
 */
const STREAMING_THRESHOLD = 10 * 1024 * 1024;

/**
 * Interface for streaming progress callbacks
 */
export interface StreamingProgress {
  /** Total bytes to process */
  total: number;
  /** Bytes processed so far */
  processed: number;
  /** Progress percentage (0-100) */
  percentage: number;
}

/**
 * Options for streaming operations
 */
export interface StreamingOptions {
  /** Chunk size for reading/writing operations */
  chunkSize?: number;
  /** Progress callback function */
  onProgress?: (progress: StreamingProgress) => void;
  /** Whether to use streaming for small files */
  forceStreaming?: boolean;
}

/**
 * Check if a file should be processed using streaming based on size
 *
 * @param filePath - Path to the file to check
 * @returns Promise resolving to true if file should be streamed
 */
export async function shouldUseStreaming(filePath: string): Promise<boolean> {
  try {
    const stats = await fs.stat(filePath);
    return stats.size > STREAMING_THRESHOLD;
  } catch {
    // If we can't get stats, default to non-streaming
    return false;
  }
}

/**
 * Stream-based file copying with progress tracking
 *
 * @param sourcePath - Source file path
 * @param destinationPath - Destination file path
 * @param options - Streaming options
 * @returns Promise that resolves when copying is complete
 *
 * @example
 * ```typescript
 * await streamCopyFile('./large-file.md', './backup/large-file.md', {
 *   onProgress: (progress) => {
 *     console.log(`Copying: ${progress.percentage}%`);
 *   }
 * });
 * ```
 */
export async function streamCopyFile(
  sourcePath: string,
  destinationPath: string,
  options: StreamingOptions = {}
): Promise<void> {
  const { chunkSize = CHUNK_SIZE, onProgress } = options;

  const stats = await fs.stat(sourcePath);
  const totalSize = stats.size;
  let processedSize = 0;

  const progressTransform = new Transform({
    transform(chunk, _encoding, callback) {
      processedSize += chunk.length;

      if (onProgress) {
        onProgress({
          total: totalSize,
          processed: processedSize,
          percentage: Math.round((processedSize / totalSize) * 100),
        });
      }

      callback(null, chunk);
    },
  });

  const readStream = createReadStream(sourcePath, { highWaterMark: chunkSize });
  const writeStream = createWriteStream(destinationPath);

  await pipeline(readStream, progressTransform, writeStream);
}

/**
 * Stream-based file reading with processing
 *
 * @param filePath - Path to the file to read
 * @param processor - Function to process each chunk
 * @param options - Streaming options
 * @returns Promise that resolves when processing is complete
 *
 * @example
 * ```typescript
 * let lineCount = 0;
 * await streamProcessFile('./large-config.md', (chunk) => {
 *   lineCount += (chunk.toString().match(/\n/g) || []).length;
 * });
 * ```
 */
export async function streamProcessFile<T = void>(
  filePath: string,
  processor: (chunk: Buffer) => Promise<T> | T,
  options: StreamingOptions = {}
): Promise<void> {
  const { chunkSize = CHUNK_SIZE, onProgress } = options;

  const stats = await fs.stat(filePath);
  const totalSize = stats.size;
  let processedSize = 0;

  const readStream = createReadStream(filePath, { highWaterMark: chunkSize });

  for await (const chunk of readStream) {
    await processor(chunk);

    processedSize += chunk.length;

    if (onProgress) {
      onProgress({
        total: totalSize,
        processed: processedSize,
        percentage: Math.round((processedSize / totalSize) * 100),
      });
    }
  }
}

/**
 * Memory-efficient file reading that automatically chooses between
 * streaming and full-file reading based on file size
 *
 * @param filePath - Path to the file to read
 * @param options - Streaming options
 * @returns Promise resolving to file contents as string
 *
 * @example
 * ```typescript
 * const content = await smartReadFile('./config.md', {
 *   onProgress: (progress) => console.log(`Reading: ${progress.percentage}%`)
 * });
 * ```
 */
export async function smartReadFile(
  filePath: string,
  options: StreamingOptions = {}
): Promise<string> {
  const useStreaming = options.forceStreaming || (await shouldUseStreaming(filePath));

  if (!useStreaming) {
    // For small files, use regular file reading
    return fs.readFile(filePath, 'utf-8');
  }

  // For large files, use streaming
  const chunks: Buffer[] = [];

  await streamProcessFile(
    filePath,
    chunk => {
      chunks.push(chunk);
    },
    options
  );

  return Buffer.concat(chunks).toString('utf-8');
}

/**
 * Memory-efficient file writing that automatically chooses between
 * streaming and direct writing based on content size
 *
 * @param filePath - Path where to write the file
 * @param content - Content to write
 * @param options - Streaming options
 * @returns Promise that resolves when writing is complete
 *
 * @example
 * ```typescript
 * await smartWriteFile('./large-output.md', largeContent, {
 *   onProgress: (progress) => console.log(`Writing: ${progress.percentage}%`)
 * });
 * ```
 */
export async function smartWriteFile(
  filePath: string,
  content: string,
  options: StreamingOptions = {}
): Promise<void> {
  const contentSize = Buffer.byteLength(content, 'utf-8');
  const useStreaming = options.forceStreaming || contentSize > STREAMING_THRESHOLD;

  if (!useStreaming) {
    // For small content, use regular file writing
    return fs.writeFile(filePath, content, 'utf-8');
  }

  // For large content, use streaming
  const { chunkSize = CHUNK_SIZE, onProgress } = options;
  const writeStream = createWriteStream(filePath);

  let processedSize = 0;
  const totalSize = contentSize;

  const contentBuffer = Buffer.from(content, 'utf-8');

  return new Promise((resolve, reject) => {
    writeStream.on('error', reject);
    writeStream.on('finish', resolve);

    const writeChunk = () => {
      if (processedSize >= totalSize) {
        writeStream.end();
        return;
      }

      const remainingSize = totalSize - processedSize;
      const currentChunkSize = Math.min(chunkSize, remainingSize);
      const chunk = contentBuffer.subarray(processedSize, processedSize + currentChunkSize);

      processedSize += currentChunkSize;

      if (onProgress) {
        onProgress({
          total: totalSize,
          processed: processedSize,
          percentage: Math.round((processedSize / totalSize) * 100),
        });
      }

      const needsDrain = !writeStream.write(chunk);

      if (needsDrain) {
        writeStream.once('drain', writeChunk);
      } else {
        // Use setImmediate to prevent stack overflow on large files
        setImmediate(writeChunk);
      }
    };

    writeChunk();
  });
}

/**
 * Batch processor for handling multiple files efficiently
 *
 * @param filePaths - Array of file paths to process
 * @param processor - Function to process each file
 * @param options - Processing options
 * @returns Promise that resolves when all files are processed
 *
 * @example
 * ```typescript
 * await batchProcessFiles(
 *   ['./agent1.md', './agent2.md', './agent3.md'],
 *   async (filePath, content) => {
 *     const processed = await processAgentFile(content);
 *     await smartWriteFile(filePath.replace('.md', '.processed.md'), processed);
 *   },
 *   { concurrency: 3 }
 * );
 * ```
 */
export async function batchProcessFiles<T = void>(
  filePaths: string[],
  processor: (filePath: string, content: string) => Promise<T> | T,
  options: {
    concurrency?: number;
    onProgress?: (completed: number, total: number) => void;
  } = {}
): Promise<T[]> {
  const { concurrency = 5, onProgress } = options;
  const results: T[] = [];
  let completed = 0;

  // Process files in batches to control memory usage
  for (let i = 0; i < filePaths.length; i += concurrency) {
    const batch = filePaths.slice(i, i + concurrency);

    const batchPromises = batch.map(async filePath => {
      const content = await smartReadFile(filePath);
      const result = await processor(filePath, content);

      completed++;
      if (onProgress) {
        onProgress(completed, filePaths.length);
      }

      return result;
    });

    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }

  return results;
}

/**
 * Get memory usage information
 *
 * @returns Object with memory usage statistics
 */
export function getMemoryUsage() {
  const usage = process.memoryUsage();
  return {
    rss: Math.round(usage.rss / 1024 / 1024), // MB
    heapTotal: Math.round(usage.heapTotal / 1024 / 1024), // MB
    heapUsed: Math.round(usage.heapUsed / 1024 / 1024), // MB
    external: Math.round(usage.external / 1024 / 1024), // MB
    arrayBuffers: Math.round(usage.arrayBuffers / 1024 / 1024), // MB
  };
}

/**
 * Monitor memory usage and warn if it gets too high
 *
 * @param threshold - Memory threshold in MB (default: 500MB)
 * @param callback - Optional callback when threshold is exceeded
 */
export function monitorMemoryUsage(
  threshold: number = 500,
  callback?: (usage: ReturnType<typeof getMemoryUsage>) => void
): () => void {
  const interval = setInterval(() => {
    const usage = getMemoryUsage();

    if (usage.heapUsed > threshold) {
      if (callback) {
        callback(usage);
      } else {
        console.warn(
          `⚠️  High memory usage detected: ${usage.heapUsed}MB (threshold: ${threshold}MB)`
        );
      }
    }
  }, 5000); // Check every 5 seconds

  // Return cleanup function
  return () => clearInterval(interval);
}
