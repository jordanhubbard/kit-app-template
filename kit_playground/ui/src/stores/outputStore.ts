import { create } from 'zustand';

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'error' | 'warning' | 'debug';
  source: string;
  message: string;
}

interface OutputState {
  logs: LogEntry[];
  isCollapsed: boolean;
  height: number;
  minHeight: number;
  maxHeight: number;
  autoScroll: boolean;
}

interface OutputActions {
  addLog: (level: LogEntry['level'], source: string, message: string) => void;
  clearLogs: () => void;
  toggleCollapsed: () => void;
  setCollapsed: (collapsed: boolean) => void;
  setHeight: (height: number) => void;
  setAutoScroll: (autoScroll: boolean) => void;
  expand: () => void;
}

export interface OutputStore extends OutputState, OutputActions {}

export const useOutputStore = create<OutputStore>((set, get) => ({
  // State
  logs: [],
  isCollapsed: true,
  height: 300,
  minHeight: 150,
  maxHeight: 600,
  autoScroll: true,

  // Actions
  addLog: (level, source, message) => {
    const log: LogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      level,
      source,
      message,
    };

    set((state) => ({
      logs: [...state.logs, log],
      // Auto-expand when new logs arrive
      isCollapsed: false,
    }));
  },

  clearLogs: () => {
    set({ logs: [] });
  },

  toggleCollapsed: () => {
    set((state) => ({ isCollapsed: !state.isCollapsed }));
  },

  setCollapsed: (collapsed) => {
    set({ isCollapsed: collapsed });
  },

  setHeight: (height) => {
    const { minHeight, maxHeight } = get();
    const clampedHeight = Math.max(minHeight, Math.min(maxHeight, height));
    set({ height: clampedHeight });
  },

  setAutoScroll: (autoScroll) => {
    set({ autoScroll });
  },

  expand: () => {
    set({ isCollapsed: false });
  },
}));
