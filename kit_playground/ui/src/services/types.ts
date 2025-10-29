// API Types for Kit App Template

export interface Template {
  name: string;
  display_name: string;
  description: string;
  type: 'application' | 'extension' | 'microservice' | 'component';
  version?: string;
  metadata?: {
    category?: string;
    tags?: string[];
    requirements?: {
      min_kit_version?: string;
    };
  };
  documentation?: {
    overview?: string;
    getting_started?: string;
    key_features?: string[];
    use_cases?: string[];
  };
}

export interface TemplateListResponse {
  templates: Record<string, Template>;
}

export interface TemplateDetailResponse {
  template: Template;
}

export interface CreateProjectRequest {
  template: string;
  name: string;
  displayName?: string;
  version?: string;
  outputDir?: string;
  standalone?: boolean;
  perAppDeps?: boolean;
  enableStreaming?: boolean;
  layers?: string[];  // List of layer template names to apply
}

export interface CreateProjectResponse {
  success: boolean;
  projectInfo?: {
    projectName: string;
    displayName: string;
    outputDir?: string;
    kitFile: string;
  };
  job_id?: string;
  error?: string;
}

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type JobType = 'build' | 'launch' | 'template_create';

export interface Job {
  id: string;
  type: JobType;
  status: JobStatus;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  project_name?: string;
  logs?: string[];
  error?: string;
}

export interface JobListResponse {
  jobs: Job[];
  count: number;
}

export interface JobDetailResponse {
  job: Job;
}

export interface JobStatsResponse {
  total: number;
  by_status: Record<JobStatus, number>;
  by_type: Record<JobType, number>;
  recent_completed: number;
  recent_failed: number;
}

// WebSocket Event Types
export interface JobLogEvent {
  job_id: string;
  timestamp: string;
  message: string;
}

export interface JobProgressEvent {
  job_id: string;
  progress: number;
  total?: number;
}

export interface JobStatusEvent {
  job_id: string;
  status: JobStatus;
  timestamp: string;
}
