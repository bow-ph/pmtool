import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'docuplan-debug-app-tunnel-y818htsi.devinapps.com'
    ],
    historyApiFallback: true,
  },
});
