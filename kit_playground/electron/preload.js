/**
 * Preload script for secure IPC between renderer and main process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  openFileDialog: (options) => ipcRenderer.invoke('open-file-dialog', options),
  saveFileDialog: (options) => ipcRenderer.invoke('save-file-dialog', options),

  // Store operations
  store: {
    get: (key) => ipcRenderer.invoke('store-get', key),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value),
    delete: (key) => ipcRenderer.invoke('store-delete', key)
  },

  // API configuration
  getAPIConfig: () => ipcRenderer.invoke('get-api-config'),

  // Shell operations
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  showItemInFolder: (path) => ipcRenderer.invoke('show-item-in-folder', path),

  // Menu events
  onMenuAction: (callback) => {
    const events = [
      'menu-new-project',
      'menu-open-project',
      'menu-save-project',
      'menu-import-template',
      'menu-export-project',
      'menu-view-gallery',
      'menu-view-connections',
      'menu-view-code',
      'menu-view-console',
      'menu-build-project',
      'menu-run-project',
      'menu-stop-project',
      'menu-clean-build',
      'menu-package-project',
      'menu-preferences',
      'menu-show-guide',
      'menu-view-logs'
    ];

    events.forEach(event => {
      ipcRenderer.on(event, (e, ...args) => callback(event, ...args));
    });
  },

  // Remove menu event listeners
  removeMenuListeners: () => {
    ipcRenderer.removeAllListeners();
  },

  // Filesystem operations
  readDirectory: (path) => ipcRenderer.invoke('fs-read-dir', path),
  createDirectory: (path) => ipcRenderer.invoke('fs-create-dir', path),
  getHomePath: () => ipcRenderer.invoke('fs-get-home'),
  readFile: (path) => ipcRenderer.invoke('fs-read-file', path),
  writeFile: (path, content) => ipcRenderer.invoke('fs-write-file', path, content)
});

// Platform information
contextBridge.exposeInMainWorld('platformAPI', {
  platform: process.platform,
  arch: process.arch,
  version: process.version,
  isDev: process.env.NODE_ENV === 'development'
});