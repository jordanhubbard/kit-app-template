/**
 * UI Redux Slice
 * Manages UI state (sidebar, theme, active views)
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  sidebarVisible: boolean;
  theme: 'dark' | 'light';
  activeView: 'gallery' | 'editor' | 'connections';
  consoleHeight: number;
  splitPaneSize: number;
}

const initialState: UIState = {
  sidebarVisible: true,
  theme: 'dark',
  activeView: 'gallery',
  consoleHeight: 200,
  splitPaneSize: 50,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarVisible = !state.sidebarVisible;
    },
    setSidebarVisible: (state, action: PayloadAction<boolean>) => {
      state.sidebarVisible = action.payload;
    },
    setTheme: (state, action: PayloadAction<'dark' | 'light'>) => {
      state.theme = action.payload;
    },
    setActiveView: (state, action: PayloadAction<'gallery' | 'editor' | 'connections'>) => {
      state.activeView = action.payload;
    },
    setConsoleHeight: (state, action: PayloadAction<number>) => {
      state.consoleHeight = action.payload;
    },
    setSplitPaneSize: (state, action: PayloadAction<number>) => {
      state.splitPaneSize = action.payload;
    },
  },
});

export const {
  toggleSidebar,
  setSidebarVisible,
  setTheme,
  setActiveView,
  setConsoleHeight,
  setSplitPaneSize,
} = uiSlice.actions;

export default uiSlice.reducer;