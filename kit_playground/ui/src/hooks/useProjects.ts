import { useState, useEffect } from 'react';

export interface Project {
  id: string;
  name: string;
  displayName: string;
  type: 'application' | 'extension' | 'microservice';
  template: string;
  path: string;
  status: 'created' | 'built' | 'running' | 'failed';
  lastModified: Date;
  createdAt: Date;
  kitFile?: string;
}

interface UseProjectsResult {
  projects: Project[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * useProjects
 * 
 * Custom hook to fetch user-created projects.
 * 
 * TODO: Connect to actual API endpoint when available.
 * For now, returns empty list as no projects API exists yet.
 */
export const useProjects = (): UseProjectsResult => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // TODO: Replace with actual API call when endpoint is available
      // const response = await apiService.listProjects();
      // setProjects(response.projects);
      
      // For now, return empty array
      // In production, this would fetch from /api/projects/list
      setProjects([]);
      
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
  };
};

