import { Component, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary for isolated chart error handling
 * Each chart is wrapped to prevent cascade failures
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center h-full text-slate-500 p-4">
          <AlertTriangle className="w-12 h-12 mb-3 text-amber-500" />
          <p className="text-sm font-medium">載入失敗</p>
          <p className="text-xs text-slate-400 mt-1">請稍後再試</p>
        </div>
      );
    }

    return this.props.children;
  }
}
