import { useState, useCallback } from 'react';

export interface Job {
  id: string;
  type: 'build' | 'launch' | 'create' | 'package';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress?: number;
  projectName?: string;
  startTime?: Date;
  endTime?: Date;
  error?: string;
  logs?: string[];
}

interface UseJobResult {
  job: Job | null;
  loading: boolean;
  error: string | null;
  startJob: (type: Job['type'], projectName: string, projectPath?: string) => Promise<string | null>;
  cancelJob: (jobId: string) => Promise<boolean>;
  stopProject: (projectName: string) => Promise<boolean>;
  refetch: (jobId: string) => void;
}

/**
 * useJob
 *
 * Custom hook for managing long-running jobs (build, launch, create).
 * Handles job status tracking and provides control actions.
 */
export const useJob = (): UseJobResult => {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Start a new job
   */
  const startJob = useCallback(async (type: Job['type'], projectName: string, projectPath?: string): Promise<string | null> => {
    try {
      setLoading(true);
      setError(null);

      // Create initial job state
      const jobId = `job_${Date.now()}`;
      const newJob: Job = {
        id: jobId,
        type,
        status: 'pending',
        projectName,
        startTime: new Date(),
      };

      setJob(newJob);

      // Call the appropriate backend API
      if (type === 'build') {
        // Calculate project path from project name
        const calculatedProjectPath = projectPath || `source/apps/${projectName}`;

        console.log(`[useJob] Starting build for project: ${projectName} at ${calculatedProjectPath}`);

        // Start the build via backend API
        const response = await fetch('/api/projects/build', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            projectPath: calculatedProjectPath,
            projectName: projectName,
          }),
        });

        if (!response.ok) {
          throw new Error(`Build failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Build started:', data);

        // Update job status
        setJob({
          ...newJob,
          status: 'running',
          id: data.job_id || jobId,
        });

        return data.job_id || jobId;
      } else if (type === 'launch') {
        const calculatedProjectPath = projectPath || `source/apps/${projectName}`;
        console.log(`[useJob] Starting launch for project: ${projectName} at ${calculatedProjectPath}`);

        const response = await fetch('/api/projects/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            projectPath: calculatedProjectPath,
            projectName: projectName,
            useXpra: null,  // null = auto-detect based on environment
          }),
        });

        if (!response.ok) {
          throw new Error(`Launch failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Launch started:', data);

        setJob({
          ...newJob,
          status: 'running',
          id: data.job_id || jobId,
        });

        return data.job_id || jobId;
      } else if (type === 'package') {
        const calculatedProjectPath = projectPath || `source/apps/${projectName}`;
        console.log(`[useJob] Starting package for project: ${projectName} at ${calculatedProjectPath}`);

        const response = await fetch('/api/projects/package', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            projectPath: calculatedProjectPath,
            projectName: projectName,
          }),
        });

        if (!response.ok) {
          throw new Error(`Package failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Package started:', data);

        setJob({
          ...newJob,
          status: 'running',
          id: data.job_id || jobId,
        });

        return data.job_id || jobId;
      } else {
        // For 'create' type, job is handled by the project creation flow
        return jobId;
      }
    } catch (err) {
      console.error('Failed to start job:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to start job';
      setError(errorMessage);

      // Update job to failed status
      if (job) {
        setJob({
          ...job,
          status: 'failed',
          error: errorMessage,
          endTime: new Date(),
        });
      }

      return null;
    } finally {
      setLoading(false);
    }
  }, [job]);

  /**
   * Cancel a running job
   */
  const cancelJob = useCallback(async (jobId: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      if (!job) {
        console.warn('[useJob] No job to cancel');
        return false;
      }

      console.log(`[useJob] Canceling job ${jobId} for project ${job.projectName}`);

      // Call backend API to terminate the process
      const response = await fetch('/api/projects/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jobId,
          projectName: job.projectName,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to cancel job: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[useJob] Cancel response:', data);

      // Update local job state
      if (job && job.id === jobId) {
        setJob({
          ...job,
          status: 'cancelled',
          endTime: new Date(),
        });
      }

      return data.success;
    } catch (err) {
      console.error('Failed to cancel job:', err);
      setError(err instanceof Error ? err.message : 'Failed to cancel job');
      return false;
    } finally {
      setLoading(false);
    }
  }, [job]);

  /**
   * Stop a running project (separate from cancel)
   * This calls the backend to stop a project by name
   */
  const stopProject = useCallback(async (projectName: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);

      console.log(`[useJob] Stopping project: ${projectName}`);

      // Call backend API to stop the project
      const response = await fetch('/api/projects/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectName,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to stop project: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[useJob] Stop response:', data);

      return data.success;
    } catch (err) {
      console.error('Failed to stop project:', err);
      setError(err instanceof Error ? err.message : 'Failed to stop project');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch job status
   */
  const refetch = useCallback(async (jobId: string) => {
    try {
      setLoading(true);
      setError(null);

      // TODO: Replace with actual API call when endpoint is available
      // const response = await apiService.getJob(jobId);
      // setJob(response.job);

      // For now, no-op as we don't have the API yet
      console.log('Fetching job:', jobId);
    } catch (err) {
      console.error('Failed to fetch job:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch job');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    job,
    loading,
    error,
    startJob,
    cancelJob,
    stopProject,
    refetch,
  };
};
