import { Mock } from 'jest';

declare global {
  interface MediaQueryList {
    readonly matches: boolean;
    readonly media: string;
    onchange: ((this: MediaQueryList, ev: MediaQueryListEvent) => void) | null;
    addListener(callback: ((this: MediaQueryList, ev: MediaQueryListEvent) => void) | null): void;
    removeListener(callback: ((this: MediaQueryList, ev: MediaQueryListEvent) => void) | null): void;
  }

  interface Window {
    matchMedia: Mock<MediaQueryList>;
  }
}
