/**
 * Type guards and utilities for error handling
 */

export interface NodeError extends Error {
  code?: string;
  path?: string;
  errno?: number;
  syscall?: string;
}

export function isNodeError(error: unknown): error is NodeError {
  return error instanceof Error && 'code' in error;
}

export function hasErrorCode(error: unknown, code: string): boolean {
  return isNodeError(error) && error.code === code;
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function isFileNotFoundError(error: unknown): boolean {
  return hasErrorCode(error, 'ENOENT');
}

export function isPermissionError(error: unknown): boolean {
  return hasErrorCode(error, 'EACCES') || hasErrorCode(error, 'EPERM');
}

export function isDirectoryNotEmptyError(error: unknown): boolean {
  return hasErrorCode(error, 'ENOTEMPTY');
}
