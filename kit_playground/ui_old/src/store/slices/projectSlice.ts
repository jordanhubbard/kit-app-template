/**
 * Project Redux Slice
 * Manages current project state (templates, connections, build status)
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Project {
  id: string;
  name: string;
  templates: string[];
  connections: Array<{
    from: string;
    fromConnector: string;
    to: string;
    toConnector: string;
  }>;
  configuration: Record<string, any>;
  outputPath: string;
  hotReload?: boolean;
  runningTemplates?: string[];
}

interface ProjectState {
  currentProject: Project | null;
  isBuilding: boolean;
  isRunning: boolean;
  buildOutput: string[];
  error: string | null;
}

const initialState: ProjectState = {
  currentProject: null,
  isBuilding: false,
  isRunning: false,
  buildOutput: [],
  error: null,
};

const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    createProject: (state, action: PayloadAction<{ name: string; outputPath: string }>) => {
      state.currentProject = {
        id: `project_${Date.now()}`,
        name: action.payload.name,
        templates: [],
        connections: [],
        configuration: {},
        outputPath: action.payload.outputPath,
      };
    },
    loadProject: (state, action: PayloadAction<Project>) => {
      state.currentProject = action.payload;
    },
    addTemplate: (state, action: PayloadAction<string>) => {
      if (state.currentProject) {
        state.currentProject.templates.push(action.payload);
      }
    },
    removeTemplate: (state, action: PayloadAction<string>) => {
      if (state.currentProject) {
        state.currentProject.templates = state.currentProject.templates.filter(
          t => t !== action.payload
        );
      }
    },
    setOutputPath: (state, action: PayloadAction<string>) => {
      if (state.currentProject) {
        state.currentProject.outputPath = action.payload;
      }
    },
    setBuildStatus: (state, action: PayloadAction<boolean>) => {
      state.isBuilding = action.payload;
    },
    setRunStatus: (state, action: PayloadAction<boolean>) => {
      state.isRunning = action.payload;
    },
    addBuildOutput: (state, action: PayloadAction<string>) => {
      state.buildOutput.push(action.payload);
    },
    clearBuildOutput: (state) => {
      state.buildOutput = [];
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  createProject,
  loadProject,
  addTemplate,
  removeTemplate,
  setOutputPath,
  setBuildStatus,
  setRunStatus,
  addBuildOutput,
  clearBuildOutput,
  setError,
} = projectSlice.actions;

export default projectSlice.reducer;