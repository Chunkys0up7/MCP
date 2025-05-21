import { captureException } from '../monitoring/error';
import axios from 'axios';

export interface ErrorWithContext {
  message: string;
  context?: Record<string, unknown>;
  originalError?: unknown;
}

export function handleError(error: unknown, context?: Record<string, unknown>): ErrorWithContext {
  let errorMessage = 'An unexpected error occurred';
  let errorContext = context || {};

  if (error instanceof Error) {
    errorMessage = error.message;
    errorContext = {
      ...errorContext,
      stack: error.stack,
      name: error.name,
    };
  } else if (axios.isAxiosError(error)) {
    errorMessage = error.response?.data?.message || error.message || 'Network error occurred';
    errorContext = {
      ...errorContext,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
    };
  }

  // Log to Sentry
  captureException(error);

  return {
    message: errorMessage,
    context: errorContext,
    originalError: error,
  };
}

export function isErrorWithContext(error: unknown): error is ErrorWithContext {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as ErrorWithContext).message === 'string'
  );
}

export function getErrorMessage(error: unknown): string {
  if (isErrorWithContext(error)) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
} 