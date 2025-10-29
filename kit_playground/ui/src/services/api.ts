import axios, { type AxiosInstance, AxiosError } from 'axios';
import type {
  TemplateListResponse,
  TemplateDetailResponse,
  CreateProjectRequest,
  CreateProjectResponse,
  JobListResponse,
  JobDetailResponse,
  JobStatsResponse,
  JobStatus,
  JobType,
} from './types';

// API Base URL - use relative path to leverage Vite proxy in development
// In production, this can be overridden with VITE_API_BASE_URL env var
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class APIService {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // ===== Template Management =====

  async listTemplates(): Promise<TemplateListResponse> {
    const response = await this.client.get<TemplateListResponse>('/templates/list');
    return response.data;
  }

  async listLayers(): Promise<{
    layers: any[];
    categorized: Record<string, any[]>;
    count: number;
  }> {
    const response = await this.client.get('/templates/layers');
    return response.data;
  }

  async getTemplate(name: string): Promise<TemplateDetailResponse> {
    const response = await this.client.get<TemplateDetailResponse>(`/templates/get/${name}`);
    return response.data;
  }

  async createProject(request: CreateProjectRequest): Promise<CreateProjectResponse> {
    const response = await this.client.post<CreateProjectResponse>('/templates/create', request);
    return response.data;
  }

  // ===== Job Management =====

  async listJobs(filters?: { status?: JobStatus; type?: JobType }): Promise<JobListResponse> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.type) params.append('type', filters.type);

    const response = await this.client.get<JobListResponse>('/jobs', { params });
    return response.data;
  }

  async getJob(jobId: string): Promise<JobDetailResponse> {
    const response = await this.client.get<JobDetailResponse>(`/jobs/${jobId}`);
    return response.data;
  }

  async cancelJob(jobId: string): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post(`/jobs/${jobId}/cancel`);
    return response.data;
  }

  async deleteJob(jobId: string): Promise<{ success: boolean; message: string }> {
    const response = await this.client.delete(`/jobs/${jobId}`);
    return response.data;
  }

  async getJobStats(): Promise<JobStatsResponse> {
    const response = await this.client.get<JobStatsResponse>('/jobs/stats');
    return response.data;
  }

  // ===== Filesystem Operations =====

  async readFile(filePath: string): Promise<string> {
    const response = await this.client.get<string>('/filesystem/read', {
      params: { path: filePath },
    });
    return response.data;
  }

  async saveFile(filePath: string, content: string): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post('/filesystem/write', {
      path: filePath,
      content,
    });
    return response.data;
  }

  // ===== Project Management =====

  async listProjects(): Promise<{ success: boolean; projects: any[]; count: number }> {
    const response = await this.client.get('/projects/list');
    return response.data;
  }

  async cleanProjects(includeTest: boolean = false): Promise<{
    success: boolean;
    deleted: { projects: string[]; extensions: string[] };
    counts: { projects: number; extensions: number; total: number };
    errors?: any[];
    warning?: string;
  }> {
    const response = await this.client.post('/projects/clean', null, {
      params: { include_test: includeTest }
    });
    return response.data;
  }

  // ===== Health Check =====

  async healthCheck(): Promise<boolean> {
    try {
      await this.client.get('/templates/list');
      return true;
    } catch {
      return false;
    }
  }
}

// Export a singleton instance
export const apiService = new APIService();

// Export the class for testing
export { APIService };
