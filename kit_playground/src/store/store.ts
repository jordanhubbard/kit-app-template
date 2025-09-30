/**
 * Redux Store Configuration
 */

import { configureStore } from '@reduxjs/toolkit';
import templatesReducer from './slices/templatesSlice';
import uiReducer from './slices/uiSlice';
import projectReducer from './slices/projectSlice';

export const store = configureStore({
  reducer: {
    templates: templatesReducer,
    ui: uiReducer,
    project: projectReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['project/loadProject'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;