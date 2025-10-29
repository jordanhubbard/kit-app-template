import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export interface LayersData {
  layers: any[];
  categorized: Record<string, any[]>;
  count: number;
}

interface UseLayersResult {
  data: LayersData | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * useLayers
 *
 * Custom hook to fetch available application layers from the API.
 * Handles loading states, errors, and provides categorized layer data.
 */
export const useLayers = (): UseLayersResult => {
  const [data, setData] = useState<LayersData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLayers = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiService.listLayers();
      setData(response);
    } catch (err) {
      console.error('Failed to fetch layers:', err);
      setError(err instanceof Error ? err.message : 'Failed to load layers');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLayers();
  }, []);

  return {
    data,
    isLoading,
    error,
    refetch: fetchLayers,
  };
};

