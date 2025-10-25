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
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts: true,
    strictPort: false,
  },
})
