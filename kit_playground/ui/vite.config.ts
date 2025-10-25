import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    // Allow access from NVIDIA dev hosts
    allowedHosts: [
      'localhost',
      '.nvidia.com',
      '.hrd.nvidia.com',
      'jordanh-dev.hrd.nvidia.com',
    ],
  },
  preview: {
    port: 3000,
    host: true,
    allowedHosts: [
      'localhost',
      '.nvidia.com',
      '.hrd.nvidia.com',
      'jordanh-dev.hrd.nvidia.com',
    ],
  },
})
