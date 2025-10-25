import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Check if REMOTE mode is enabled (allows connections from any host)
const isRemote = process.env.REMOTE === '1'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    // REMOTE=1: Allow all hosts
    // REMOTE=0: Allow only specific hosts
    allowedHosts: isRemote ? 'all' : [
      'localhost',
      '.nvidia.com',
      '.hrd.nvidia.com',
      'jordanh-dev.hrd.nvidia.com',
    ],
  },
  preview: {
    port: 3000,
    host: true,
    allowedHosts: isRemote ? 'all' : [
      'localhost',
      '.nvidia.com',
      '.hrd.nvidia.com',
      'jordanh-dev.hrd.nvidia.com',
    ],
  },
})
