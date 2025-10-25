import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Check if REMOTE mode is enabled (allows connections from any host)
// Also check if host is 0.0.0.0 (indicates remote mode from dev.sh)
const isRemote = process.env.REMOTE === '1' || process.env.VITE_HOST === '0.0.0.0'

// For development flexibility, especially in NVIDIA environments,
// we allow all hosts by default. This can be restricted by setting
// REMOTE=0 explicitly if needed.
// 
// Why 'all'? NVIDIA developers often work from various internal hosts
// (*.hrd.nvidia.com, *.nvidia.com, VPN IPs, etc.) and maintaining a
// whitelist is impractical and creates friction.
const allowedHosts = 'all'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    allowedHosts: allowedHosts,
  },
  preview: {
    port: 3000,
    host: true,
    allowedHosts: allowedHosts,
  },
})
