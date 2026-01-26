import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 8010,
    host: true,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:9010',
        changeOrigin: true
      }
    }
  }
});
