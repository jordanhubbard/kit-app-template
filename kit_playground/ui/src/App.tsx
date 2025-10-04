/**
 * Kit Playground - Main React Application
 */

import React, { useEffect, useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import { BrowserRouter as Router } from 'react-router-dom';
import { store } from './store/store';
import MainLayoutWorkflow from './components/layout/MainLayoutWorkflow';
import { initializeAPI } from './services/api';
import { useAppDispatch } from './hooks/redux';
import { loadTemplates } from './store/slices/templatesSlice';
import './App.css';

// Create dark theme (similar to VS Code)
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#76b900', // NVIDIA Green
    },
    secondary: {
      main: '#00a86b',
    },
    background: {
      default: '#1e1e1e',
      paper: '#252526',
    },
    text: {
      primary: '#cccccc',
      secondary: '#969696',
    },
  },
  typography: {
    fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Fira Code", monospace',
    fontSize: 13,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: '#6b6b6b #2b2b2b',
          '&::-webkit-scrollbar, & *::-webkit-scrollbar': {
            width: 14,
            height: 14,
          },
          '&::-webkit-scrollbar-track, & *::-webkit-scrollbar-track': {
            background: '#2b2b2b',
          },
          '&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb': {
            background: '#6b6b6b',
            borderRadius: 0,
            border: '3px solid #2b2b2b',
          },
          '&::-webkit-scrollbar-thumb:hover, & *::-webkit-scrollbar-thumb:hover': {
            background: '#8b8b8b',
          },
        },
      },
    },
  },
});

function AppContent() {
  const dispatch = useAppDispatch();
  const [apiReady, setApiReady] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    // Initialize API connection
    const initAPI = async () => {
      try {
        // Use relative API URL (works with Flask serving static files)
        await initializeAPI('/api');
        setApiReady(true);

        // Load initial data
        dispatch(loadTemplates());
      } catch (error) {
        console.error('Failed to initialize API:', error);
        setApiError('Failed to connect to backend server. Is the server running?');
      }
    };

    initAPI();
  }, [dispatch]);

  if (apiError) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '20px'
      }}>
        <h2>Connection Error</h2>
        <p>{apiError}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!apiReady) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh'
      }}>
        <div>Connecting to backend...</div>
      </div>
    );
  }

  return <MainLayoutWorkflow />;
}

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Router>
          <AppContent />
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;