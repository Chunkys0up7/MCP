import * as Sentry from '@sentry/react';

export const captureException = (error: unknown): void => {
  if (error instanceof Error) {
    Sentry.captureException(error);
  } else if (typeof error === 'string') {
    Sentry.captureMessage(error);
  } else {
    Sentry.captureMessage('An unexpected error occurred');
  }
};

export const captureMessage = (message: string, level: Sentry.SeverityLevel = 'info'): void => {
  Sentry.captureMessage(message, level);
};

export const setUser = (user: { id: string; email?: string; username?: string } | null): void => {
  Sentry.setUser(user);
};

export const setTag = (key: string, value: string): void => {
  Sentry.setTag(key, value);
};

export const setExtra = (key: string, value: any): void => {
  Sentry.setExtra(key, value);
}; 