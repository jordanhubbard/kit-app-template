import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export interface Project {
  id: string;
  name: string;
  displayName: string;
  type: 'application' | 'extension' | 'microservice';
  path: string;
  lastModified: string;
  createdAt: string;
  kitFile?: string;
  isTest?: boolean;
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
 * Custom hook to fetch user-created projects from the backend.
 * Scans source/apps directory for user-created projects.
 */
export const useProjects = (): UseProjectsResult => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.listProjects();
      
      if (response.success) {
        setProjects(response.projects);
      } else {
        setError('Failed to load projects');
        setProjects([]);
      }
      
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      setError(err instanceof Error ? err.message : 'Failed to load projects');
      setProjects([]);
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

