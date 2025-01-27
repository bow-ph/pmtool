import '@testing-library/jest-dom';
import { jest } from '@jest/globals';

declare global {
  interface JestMatchers<R = void> {
    toBeInTheDocument(): R;
    toHaveClass(className: string): R;
    toBeVisible(): R;
    toBeDisabled(): R;
    toHaveAttribute(attr: string, value?: string): R;
    toHaveTextContent(text: string | RegExp): R;
  }
}

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock import.meta
// Mock global import.meta
const mockImportMeta = {
  env: {
    VITE_API_URL: 'http://localhost:8000',
    MODE: 'test'
  }
};

Object.defineProperty(global, 'import', {
  value: { meta: mockImportMeta },
  writable: true,
  configurable: true
});
