import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import type { SeverityLevel } from '@sentry/types';

interface SentryConfig {
  dsn: string;
  environment: string;
  tracesSampleRate: number;
  maxBreadcrumbs: number;
  attachStacktrace: boolean;
  normalizeDepth: number;
}

interface User {
  id: string;
  email?: string;
  username?: string;
  ip_address?: string;
}

interface ErrorContext {
  [key: string]: unknown;
}

const defaultConfig: SentryConfig = {
  dsn: process.env.SENTRY_DSN || '',
  environment: process.env.NODE_ENV || 'development',
  tracesSampleRate: 1.0,
  maxBreadcrumbs: 100,
  attachStacktrace: true,
  normalizeDepth: 3,
};

export const initializeSentry = (config: Partial<SentryConfig> = {}) => {
  if (process.env.NODE_ENV === 'production') {
    const finalConfig = { ...defaultConfig, ...config };
    
    Sentry.init({
      dsn: finalConfig.dsn,
      integrations: [new BrowserTracing()],
      tracesSampleRate: finalConfig.tracesSampleRate,
      environment: finalConfig.environment,
      maxBreadcrumbs: finalConfig.maxBreadcrumbs,
      attachStacktrace: finalConfig.attachStacktrace,
      normalizeDepth: finalConfig.normalizeDepth,
      beforeSend(event) {
        // Don't send events in development
        if (process.env.NODE_ENV === 'development') {
          return null;
        }

        // Filter out sensitive data
        if (event.request?.cookies) {
          delete event.request.cookies;
        }

        return event;
      },
    });
  }
};

export const captureException = (error: Error, context?: ErrorContext) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.withScope((scope) => {
      if (context) {
        Object.entries(context).forEach(([key, value]) => {
          scope.setExtra(key, value);
        });
      }

      // Add error metadata
      scope.setTag('error_type', error.name);
      scope.setLevel('error');

      Sentry.captureException(error);
    });
  } else {
    // Log to console in development
    console.error('Error:', error);
    if (context) {
      console.error('Context:', context);
    }
  }
};

export const captureMessage = (message: string, level: SeverityLevel = 'info') => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.withScope((scope) => {
      scope.setLevel(level);
      Sentry.captureMessage(message);
    });
  } else {
    // Log to console in development
    console[level === 'error' ? 'error' : 'log'](message);
  }
};

export const setUser = (user: User) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser(user);
  }
};

export const clearUser = () => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser(null);
  }
};

export const addBreadcrumb = (message: string, category?: string, level: SeverityLevel = 'info') => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.addBreadcrumb({
      message,
      category,
      level,
      timestamp: Date.now() / 1000,
    });
  }
}; 