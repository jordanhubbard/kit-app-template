/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // NVIDIA Green (Primary)
        'nvidia-green': '#76B900',
        'nvidia-green-dark': '#5A9100',
        'nvidia-green-light': '#8FD400',
        'nvidia-green-hover': '#5E9400',
        'nvidia-green-active': '#4A7600',
        
        // Backgrounds
        'bg-dark': '#0F0F0F',
        'bg-panel': '#1A1A1A',
        'bg-card': '#252525',
        'bg-card-hover': '#2D2D2D',
        
        // Borders
        'border-subtle': 'rgba(255, 255, 255, 0.1)',
        'border-panel': 'rgba(255, 255, 255, 0.15)',
        'border-active': '#76B900',
        
        // Text
        'text-primary': '#FFFFFF',
        'text-secondary': '#B3B3B3',
        'text-muted': '#808080',
        
        // Status Colors
        'status-success': '#76B900',
        'status-warning': '#FFB700',
        'status-error': '#FF5252',
        'status-info': '#00B8D4',
        
        // Legacy (keep for backwards compatibility)
        'dark-bg': '#1E1E1E',
        'dark-card': '#2D2D2D',
        'dark-hover': '#3D3D3D',
      },
    },
  },
  plugins: [],
}
