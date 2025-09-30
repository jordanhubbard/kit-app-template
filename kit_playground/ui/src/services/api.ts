/**
 * API Service Layer
 * Handles all communication with the backend
 */

import axios, { AxiosInstance } from 'axios';

let apiClient: AxiosInstance;

export const initializeAPI = async (baseURL: string) => {
  apiClient = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Add response interceptor for error handling
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error('API Error:', error);
      return Promise.reject(error);
    }
  );
};

export const getAPI = () => {
  if (!apiClient) {
    throw new Error('API not initialized. Call initializeAPI() first.');
  }
  return apiClient;
};

// Template APIs
export const templateAPI = {
  getAll: async () => {
    const response = await getAPI().get('/templates');
    return response.data;
  },

  getCode: async (templateId: string) => {
    const response = await getAPI().get(`/templates/${templateId}/code`);
    return response.data;
  },

  updateCode: async (templateId: string, code: string) => {
    const response = await getAPI().post(`/templates/${templateId}/update`, { code });
    return response.data;
  },

  build: async (templateId: string, config?: any) => {
    const response = await getAPI().post(`/templates/${templateId}/build`, config);
    return response.data;
  },

  run: async (templateId: string) => {
    const response = await getAPI().post(`/templates/${templateId}/run`);
    return response.data;
  },

  stop: async (templateId: string) => {
    const response = await getAPI().post(`/templates/${templateId}/stop`);
    return response.data;
  },

  deploy: async (templateId: string, options: any) => {
    const response = await getAPI().post(`/templates/${templateId}/deploy`, options);
    return response.data;
  },
};

// Project APIs
export const projectAPI = {
  create: async (name: string, outputPath: string) => {
    const response = await getAPI().post('/projects', { name, outputPath });
    return response.data;
  },

  load: async (projectPath: string) => {
    const response = await getAPI().post('/projects/load', { path: projectPath });
    return response.data;
  },

  save: async (project: any) => {
    const response = await getAPI().post('/projects/save', project);
    return response.data;
  },

  build: async (projectId: string) => {
    const response = await getAPI().post(`/projects/${projectId}/build`);
    return response.data;
  },

  run: async (projectId: string) => {
    const response = await getAPI().post(`/projects/${projectId}/run`);
    return response.data;
  },

  stop: async (projectId: string) => {
    const response = await getAPI().post(`/projects/${projectId}/stop`);
    return response.data;
  },
};

// Filesystem APIs
export const filesystemAPI = {
  list: async (path: string) => {
    const response = await getAPI().get(`/filesystem/list?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  createDirectory: async (path: string) => {
    const response = await getAPI().post('/filesystem/mkdir', { path });
    return response.data;
  },

  readFile: async (path: string) => {
    const response = await getAPI().get(`/filesystem/read?path=${encodeURIComponent(path)}`);
    return response.data;
  },

  writeFile: async (path: string, content: string) => {
    const response = await getAPI().post('/filesystem/write', { path, content });
    return response.data;
  },
};