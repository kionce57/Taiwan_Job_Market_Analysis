import { ReactNode } from 'react';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

interface BaseChartProps {
  loading?: boolean;
  error?: string | null;
  children: ReactNode;
}

/**
 * Chart Skeleton Loading State
 */
function ChartSkeleton() {
  return (
    <div className="w-full h-full flex flex-col gap-3 p-2">
      <div className="skeleton h-4 w-1/3 rounded" />
      <div className="flex-1 skeleton rounded-lg" />
      <div className="flex gap-2">
        <div className="skeleton h-3 w-16 rounded" />
        <div className="skeleton h-3 w-16 rounded" />
        <div className="skeleton h-3 w-16 rounded" />
      </div>
    </div>
  );
}

/**
 * Chart Error State
 */
function ChartError({ message }: { message: string }) {
  return (
    <div className="w-full h-full flex items-center justify-center text-slate-500">
      <p className="text-sm">{message}</p>
    </div>
  );
}

/**
 * Base Chart Wrapper
 * Handles loading, error states, and wraps with ErrorBoundary
 */
export function BaseChart({ loading, error, children }: BaseChartProps) {
  if (loading) {
    return <ChartSkeleton />;
  }

  if (error) {
    return <ChartError message={error} />;
  }

  return (
    <ErrorBoundary>
      <div className="w-full h-full">
        {children}
      </div>
    </ErrorBoundary>
  );
}
