/**
 * Templates Redux Slice
 * Manages template state (loading, selection, metadata)
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface Template {
  name: string;
  display_name: string;
  type: string;
  category: string;
  description: string;
  thumbnail?: string;
  connectors: any[];
}

interface TemplatesState {
  templates: Record<string, Template>;
  loading: boolean;
  error: string | null;
  selectedTemplate: string | null;
}

const initialState: TemplatesState = {
  templates: {},
  loading: false,
  error: null,
  selectedTemplate: null,
};

// Async thunk to load templates
export const loadTemplates = createAsyncThunk(
  'templates/load',
  async () => {
    const response = await fetch('/api/templates');
    if (!response.ok) throw new Error('Failed to load templates');
    return await response.json();
  }
);

const templatesSlice = createSlice({
  name: 'templates',
  initialState,
  reducers: {
    selectTemplate: (state, action: PayloadAction<string>) => {
      state.selectedTemplate = action.payload;
    },
    clearSelection: (state) => {
      state.selectedTemplate = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadTemplates.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadTemplates.fulfilled, (state, action) => {
        state.loading = false;
        state.templates = action.payload;
      })
      .addCase(loadTemplates.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to load templates';
      });
  },
});

export const { selectTemplate, clearSelection } = templatesSlice.actions;
export default templatesSlice.reducer;