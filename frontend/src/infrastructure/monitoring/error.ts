import * as Sentry from '@sentry/react';

export const captureException = (error: unknown) => {
  if (error instanceof Error) {
    Sentry.captureException(error);
  } else {
    Sentry.captureMessage(String(error));
  }
};

export const captureMessage = (message: string) => {
  Sentry.captureMessage(message);
};

export const setUser = (user: { id: string; email?: string; username?: string }) => {
  Sentry.setUser(user);
};

export const clearUser = () => {
  Sentry.setUser(null);
}; 