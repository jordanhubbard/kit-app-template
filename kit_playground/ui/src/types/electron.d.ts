/**
 * Type definitions for Electron IPC API
 */

export interface ElectronAPI {
  // File operations
  openFileDialog: (options: any) => Promise<any>;
  saveFileDialog: (options: any) => Promise<any>;

  // Store operations
  storeGet: (key: string) => Promise<any>;
  storeSet: (key: string, value: any) => Promise<void>;
  storeDelete: (key: string) => Promise<void>;

  // API configuration
  getAPIConfig: () => Promise<{ host: string; port: number; url: string }>;

  // Shell operations
  openExternal: (url: string) => Promise<void>;
  showItemInFolder: (path: string) => Promise<void>;

  // Filesystem operations
  fsReadDir: (dirPath: string) => Promise<Array<{ name: string; path: string; isDirectory: boolean }>>;
  readDirectory: (dirPath: string) => Promise<Array<{ name: string; path: string; isDirectory: boolean }>>;
  fsCreateDir: (dirPath: string) => Promise<{ success: boolean }>;
  createDirectory: (dirPath: string) => Promise<{ success: boolean }>;
  fsGetHome: () => Promise<string>;
  getHomePath: () => Promise<string>;
  fsReadFile: (filePath: string) => Promise<string>;
  fsWriteFile: (filePath: string, content: string) => Promise<{ success: boolean }>;

  // Menu event listeners
  onMenuAction: (callback: (action: string) => void) => void;
  removeMenuListeners: () => void;
  onMenuNewProject: (callback: () => void) => void;
  onMenuOpenProject: (callback: () => void) => void;
  onMenuSaveProject: (callback: () => void) => void;
  onMenuImportTemplate: (callback: () => void) => void;
  onMenuExportProject: (callback: () => void) => void;
  onMenuViewGallery: (callback: () => void) => void;
  onMenuViewConnections: (callback: () => void) => void;
  onMenuViewCode: (callback: () => void) => void;
  onMenuViewConsole: (callback: () => void) => void;
  onMenuBuildProject: (callback: () => void) => void;
  onMenuRunProject: (callback: () => void) => void;
  onMenuStopProject: (callback: () => void) => void;
  onMenuCleanBuild: (callback: () => void) => void;
  onMenuPackageProject: (callback: () => void) => void;
  onMenuPreferences: (callback: () => void) => void;
  onMenuShowGuide: (callback: () => void) => void;
  onMenuViewLogs: (callback: () => void) => void;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
