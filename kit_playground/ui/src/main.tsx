import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { ErrorBoundary } from './components/common';

// Version stamp for debugging
const UI_VERSION = 'v2.0-redesign-' + new Date().toISOString();
console.log('🎨 Kit Playground UI Loading...');
console.log('📦 Version:', UI_VERSION);
console.log('🔧 Mode:', import.meta.env.MODE);
console.log('🌐 Base URL:', import.meta.env.VITE_API_BASE_URL);

// Expose version globally for debugging
(window as any).KIT_PLAYGROUND_VERSION = UI_VERSION;
(window as any).KIT_PLAYGROUND_DEBUG = {
  version: UI_VERSION,
  mode: import.meta.env.MODE,
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
  wsBaseUrl: import.meta.env.VITE_WS_BASE_URL,
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);

console.log('✅ Kit Playground UI Mounted');
