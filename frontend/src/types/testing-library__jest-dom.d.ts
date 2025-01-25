/// <reference types="jest" />

declare namespace jest {
  interface Matchers<R> {
    toBeInTheDocument(): R;
    toHaveClass(className: string): R;
    toBeVisible(): R;
    toHaveTextContent(text: string | RegExp): R;
    toHaveAttribute(attr: string, value?: string): R;
    toBeDisabled(): R;
    toBeEnabled(): R;
    toHaveStyle(style: Record<string, any>): R;
    toHaveValue(value: string | string[] | number): R;
  }
}
