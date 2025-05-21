import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configure testing-library
configure({
  testIdAttribute: 'data-testid',
});

// Mock fetch globally
global.fetch = jest.fn();

// Mock Sentry
jest.mock('@sentry/react', () => ({
  captureException: jest.fn(),
  captureMessage: jest.fn(),
}));

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
}); 