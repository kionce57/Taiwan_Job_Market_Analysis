import { useState, useEffect, useCallback } from 'react';
import type { DashboardData } from '@/types/market';

interface UseDashboardDataResult {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refetch: (jobName?: string) => void;
}

/**
 * Custom hook for fetching dashboard data
 * Handles loading, error states, and refetch capability
 *
 * @param jobName - Optional job name filter for searching jobs
 */
export function useDashboardData(jobName?: string): UseDashboardDataResult {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (filterJobName?: string) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      const searchTerm = filterJobName ?? jobName;
      if (searchTerm) {
        params.set('job_name', searchTerm);
      }

      const url = params.toString()
        ? `/api/dashboard?${params.toString()}`
        : '/api/dashboard';

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json() as DashboardData;
      setData(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '載入數據失敗';
      setError(errorMessage);
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  }, [jobName]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
