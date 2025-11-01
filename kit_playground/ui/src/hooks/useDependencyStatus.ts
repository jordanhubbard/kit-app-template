/**
 * useDependencyStatus Hook
 * 
 * Custom hook for managing Kit extension dependency status.
 * Handles API calls, localStorage caching, and automatic refresh.
 */

import { useState, useEffect, useCallback } from 'react';

interface DependencyStatus {
  cached: boolean;
  exists: boolean;
  size: string;
  size_bytes: number;
  count: number;
  path: string;
  threshold?: number;
  error?: string;
}

interface UseDependencyStatusReturn {
  status: DependencyStatus | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  needsPrepare: boolean;
}

const CACHE_KEY = 'kit_dependency_status';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export const useDependencyStatus = (): UseDependencyStatusReturn => {
  const [status, setStatus] = useState<DependencyStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const loadFromCache = (): DependencyStatus | null => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (!cached) return null;
      
      const { data, timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;
      
      // Return cached data if less than CACHE_DURATION old
      if (age < CACHE_DURATION) {
        return data;
      }
      
      // Clear stale cache
      localStorage.removeItem(CACHE_KEY);
      return null;
    } catch (e) {
      console.error('Error loading cache:', e);
      return null;
    }
  };
  
  const saveToCache = (data: DependencyStatus) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    } catch (e) {
      console.error('Error saving cache:', e);
    }
  };
  
  const fetchStatus = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:5000/api/dependencies/status');
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      const data: DependencyStatus = await response.json();
      setStatus(data);
      saveToCache(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dependency status';
      console.error('Error fetching dependency status:', err);
      setError(errorMessage);
      
      // Try to use cached data on error
      const cached = loadFromCache();
      if (cached) {
        setStatus(cached);
      }
    } finally {
      setLoading(false);
    }
  }, []);
  
  const refresh = useCallback(async () => {
    await fetchStatus();
  }, [fetchStatus]);
  
  useEffect(() => {
    // Try to load from cache first for instant UI
    const cached = loadFromCache();
    if (cached) {
      setStatus(cached);
      setLoading(false);
    }
    
    // Then fetch fresh data
    fetchStatus();
    
    // Set up periodic refresh (every 30 seconds while component mounted)
    const interval = setInterval(() => {
      fetchStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [fetchStatus]);
  
  // Determine if preparation is needed
  const needsPrepare = !status?.cached || status?.count < (status?.threshold || 50);
  
  return {
    status,
    loading,
    error,
    refresh,
    needsPrepare
  };
};

export default useDependencyStatus;

