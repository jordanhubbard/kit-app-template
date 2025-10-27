import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // host: true allows binding to 0.0.0.0
    host: '0.0.0.0',
    // In Vite 7, explicitly disable host checking for remote development
    allowedHosts: true,
    strictPort: false,
    // Force browsers to not cache in dev mode
    headers: {
      'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Forward the original host header to the backend
            // This is crucial for the backend to construct URLs with the correct hostname
            const originalHost = req.headers.host;
            if (originalHost) {
              proxyReq.setHeader('X-Forwarded-Host', originalHost);
            }
          });
        },
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Forward the original host header for WebSocket connections too
            const originalHost = req.headers.host;
            if (originalHost) {
              proxyReq.setHeader('X-Forwarded-Host', originalHost);
            }
          });
        },
      },
    },
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: true,
    strictPort: false,
  },
  build: {
    // Generate hashed filenames for cache busting in production
    rollupOptions: {
      output: {
        // Use content hash for cache busting
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
})
