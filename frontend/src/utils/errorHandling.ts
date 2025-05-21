interface ErrorContext {
  chainId?: string;
  action?: string;
  nodeCount?: number;
  edgeCount?: number;
  [key: string]: any;
}

interface ErrorWithContext extends Error {
  context?: ErrorContext;
}

export const handleError = (error: unknown, context?: ErrorContext): { message: string } => {
  const errorWithContext = error as ErrorWithContext;
  
  if (context) {
    errorWithContext.context = {
      ...errorWithContext.context,
      ...context
    };
  }

  let message = 'An unexpected error occurred';
  
  if (errorWithContext instanceof Error) {
    message = errorWithContext.message;
  } else if (typeof errorWithContext === 'string') {
    message = errorWithContext;
  }

  return { message };
};

export const isErrorWithContext = (error: unknown): error is ErrorWithContext => {
  return error instanceof Error && 'context' in error;
};

export const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
}; 