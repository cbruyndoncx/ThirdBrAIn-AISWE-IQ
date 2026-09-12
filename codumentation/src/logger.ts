import * as fs from 'fs';
import * as path from 'path';
import { LogEntry, FailureSummary, FailureStats } from './types';

const LOG_FILE = '.codumentation.log';
const SUMMARY_LOG_FILE = '.codumentation-summary.log';

/**
 * Logs a validation failure to the log file
 * @param entry The log entry to record
 * @param rootDir The root directory where the log file should be written
 */
export function logValidationFailure(entry: LogEntry, rootDir: string = process.cwd()): void {
  const logPath = path.join(rootDir, LOG_FILE);

  const logLine = formatLogEntry(entry);

  // Append to log file
  fs.appendFileSync(logPath, logLine + '\n\n', 'utf-8');
}

/**
 * Formats a log entry as a human-readable string
 * @param entry The log entry to format
 * @returns Formatted log string
 */
function formatLogEntry(entry: LogEntry): string {
  const lines = [
    `[${entry.timestamp.toISOString()}]`,
    `Target: ${entry.targetFile}`,
    `Module: ${entry.moduleName}`,
    `Error: ${entry.error}`,
    '',
    'Error Content:',
    entry.errorContent
  ];

  if (entry.diff) {
    lines.push('', 'Diff:', entry.diff);
  }

  lines.push('---');

  return lines.join('\n');
}

/**
 * Clears the log file
 * @param rootDir The root directory where the log file is located
 */
export function clearLog(rootDir: string = process.cwd()): void {
  const logPath = path.join(rootDir, LOG_FILE);
  if (fs.existsSync(logPath)) {
    fs.unlinkSync(logPath);
  }
}

/**
 * Reads and parses the log file
 * @param rootDir The root directory where the log file is located
 * @returns Array of log entries
 */
export function readLog(rootDir: string = process.cwd()): string {
  const logPath = path.join(rootDir, LOG_FILE);
  if (!fs.existsSync(logPath)) {
    return 'No log file found';
  }
  return fs.readFileSync(logPath, 'utf-8');
}

/**
 * Logs a concise failure summary for analytics
 * @param moduleName Name of the module that failed
 * @param targetFile Target file being validated
 * @param rootDir The root directory where the log file should be written
 */
export function logFailureSummary(
  moduleName: string,
  targetFile: string,
  rootDir: string = process.cwd()
): void {
  const logPath = path.join(rootDir, SUMMARY_LOG_FILE);

  const summary: FailureSummary = {
    timestamp: new Date(),
    moduleName,
    targetFile
  };

  const logLine = JSON.stringify(summary);
  fs.appendFileSync(logPath, logLine + '\n', 'utf-8');
}

/**
 * Gets failure statistics from the summary log
 * @param days Number of days to look back (default: all time)
 * @param rootDir The root directory where the log file is located
 * @returns Failure statistics
 */
export function getFailureStats(
  days?: number,
  rootDir: string = process.cwd()
): FailureStats {
  const logPath = path.join(rootDir, SUMMARY_LOG_FILE);

  if (!fs.existsSync(logPath)) {
    return {
      totalFailures: 0,
      byModule: {},
      byTarget: {},
      timeRange: { start: new Date(), end: new Date() }
    };
  }

  const content = fs.readFileSync(logPath, 'utf-8');
  const lines = content.trim().split('\n').filter(line => line.length > 0);

  const summaries: FailureSummary[] = lines.map(line => {
    const parsed = JSON.parse(line);
    return {
      ...parsed,
      timestamp: new Date(parsed.timestamp)
    };
  });

  // Filter by date range if specified
  let filtered = summaries;
  if (days) {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    filtered = summaries.filter(s => s.timestamp >= cutoff);
  }

  if (filtered.length === 0) {
    return {
      totalFailures: 0,
      byModule: {},
      byTarget: {},
      timeRange: { start: new Date(), end: new Date() }
    };
  }

  // Calculate statistics
  const byModule: Record<string, number> = {};
  const byTarget: Record<string, number> = {};

  for (const summary of filtered) {
    byModule[summary.moduleName] = (byModule[summary.moduleName] || 0) + 1;
    byTarget[summary.targetFile] = (byTarget[summary.targetFile] || 0) + 1;
  }

  const timestamps = filtered.map(s => s.timestamp);

  return {
    totalFailures: filtered.length,
    byModule,
    byTarget,
    timeRange: {
      start: new Date(Math.min(...timestamps.map(t => t.getTime()))),
      end: new Date(Math.max(...timestamps.map(t => t.getTime())))
    }
  };
}

/**
 * Rotates the summary log to keep only recent entries
 * @param maxEntries Maximum number of entries to keep (default: 1000)
 * @param rootDir The root directory where the log file is located
 */
export function rotateSummaryLog(
  maxEntries: number = 1000,
  rootDir: string = process.cwd()
): void {
  const logPath = path.join(rootDir, SUMMARY_LOG_FILE);

  if (!fs.existsSync(logPath)) {
    return;
  }

  const content = fs.readFileSync(logPath, 'utf-8');
  const lines = content.trim().split('\n').filter(line => line.length > 0);

  if (lines.length > maxEntries) {
    // Keep only the most recent entries
    const recentLines = lines.slice(-maxEntries);
    fs.writeFileSync(logPath, recentLines.join('\n') + '\n', 'utf-8');
  }
}
