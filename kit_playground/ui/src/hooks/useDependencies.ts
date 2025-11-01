/**
 * Custom hook for dependency preparation and status checking.
 */

import { useState, useEffect, useCallback } from 'react';

export interface DependencyStatus {
  cached: boolean;
  size: string;
  size_bytes: number;
  count: number;
  path: string;
  threshold: number;
  exists: boolean;
}

export interface DependencyEstimate {
  estimated_size: string;
  estimated_size_bytes: number;
  estimated_time: string;
  estimated_seconds: number;
  extension_count: number;
  bandwidth_mbps: number;
}

export interface PreparationProgress {
  type: 'status' | 'progress' | 'extension' | 'complete' | 'error' | 'warning';
  message: string;
  progress?: number;
  count?: number;
  time?: number;
  size?: string;
  exitCode?: number;
}

export const useDependencies = () => {
  const [status, setStatus] = useState<DependencyStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [estimateCache, setEstimateCache] = useState<DependencyEstimate | null>(null);

  /**
   * Check the current status of extension cache.
   */
  const checkStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/dependencies/status');
      const data = await response.json();

      if (data.success) {
        setStatus(data);

        // Update localStorage cache for first-launch detection
        const cacheInfo = {
          cached: data.cached,
          count: data.count,
          timestamp: Date.now(),
        };
        localStorage.setItem('kit_deps_cache_status', JSON.stringify(cacheInfo));
      } else {
        setError(data.error || 'Failed to check dependency status');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Get download size and time estimate.
   */
  const getEstimate = useCallback(async (bandwidthMbps: number = 50): Promise<DependencyEstimate | null> => {
    try {
      const response = await fetch(`/api/dependencies/estimate?bandwidth=${bandwidthMbps}`);
      const data = await response.json();

      if (data.success) {
        setEstimateCache(data);
        return data;
      } else {
        console.error('Failed to get estimate:', data.error);
        return null;
      }
    } catch (err) {
      console.error('Error getting estimate:', err);
      return null;
    }
  }, []);

  /**
   * Start preparation (pre-fetching) with progress tracking.
   */
  const startPreparation = useCallback((
    config: string = 'release',
    onProgress: (event: PreparationProgress) => void,
    onComplete: () => void,
    onError: (error: string) => void
  ) => {
    const eventSource = new EventSource(`/api/dependencies/prepare`, {
      // Note: EventSource doesn't support POST, so we need to use query params or create a session
    });

    // Since EventSource only supports GET, we'll use fetch with streaming
    fetch('/api/dependencies/prepare', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ config }),
    })
      .then(response => {
        if (!response.body) {
          throw new Error('No response body');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        const readStream = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              return;
            }

            // Decode the chunk
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.substring(6));
                  onProgress(data);

                  if (data.type === 'complete') {
                    onComplete();
                  } else if (data.type === 'error') {
                    onError(data.message);
                  }
                } catch (err) {
                  console.error('Error parsing SSE data:', err);
                }
              }
            }

            // Continue reading
            readStream();
          }).catch(err => {
            onError(err.message);
          });
        };

        readStream();
      })
      .catch(err => {
        onError(err.message);
      });
  }, []);

  /**
   * Check if this is the first launch (no cached extensions).
   */
  const isFirstLaunch = useCallback((): boolean => {
    const cached = localStorage.getItem('kit_deps_cache_status');
    if (!cached) {
      return true;
    }

    try {
      const data = JSON.parse(cached);
      // Consider first launch if count < threshold and less than 1 day old
      const ageHours = (Date.now() - data.timestamp) / (1000 * 60 * 60);
      return !data.cached || (data.count < 50 && ageHours < 24);
    } catch {
      return true;
    }
  }, []);

  /**
   * Auto-check status on mount.
   */
  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  return {
    status,
    loading,
    error,
    estimateCache,
    checkStatus,
    getEstimate,
    startPreparation,
    isFirstLaunch,
  };
};
