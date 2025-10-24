/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'nvidia-green': '#76B900',
        'nvidia-green-hover': '#5E9400',
        'nvidia-green-active': '#4A7600',
        'dark-bg': '#1E1E1E',
        'dark-card': '#2D2D2D',
        'dark-hover': '#3D3D3D',
      },
    },
  },
  plugins: [],
}
