import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary
 * 
 * React error boundary component to catch and display errors gracefully.
 * Prevents the entire app from crashing when a component fails.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error Boundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="flex items-center justify-center min-h-screen bg-bg-dark p-4">
          <div className="max-w-2xl w-full">
            <div className="bg-bg-panel border border-status-error/30 rounded-lg p-6">
              <div className="flex items-start gap-4 mb-6">
                <div className="p-3 rounded-full bg-status-error/10">
                  <AlertTriangle className="w-8 h-8 text-status-error" />
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-text-primary mb-2">
                    Something went wrong
                  </h2>
                  <p className="text-text-secondary mb-4">
                    An unexpected error occurred. You can try reloading the page or contact support if the problem persists.
                  </p>
                </div>
              </div>

              {/* Error Details (collapsed by default in production) */}
              {this.state.error && import.meta.env.DEV && (
                <details className="mb-4">
                  <summary className="cursor-pointer text-sm font-medium text-text-primary hover:text-nvidia-green mb-2">
                    Technical Details
                  </summary>
                  <div className="bg-bg-dark rounded p-4 overflow-auto">
                    <p className="text-status-error text-sm font-mono mb-2">
                      {this.state.error.toString()}
                    </p>
                    {this.state.errorInfo && (
                      <pre className="text-text-muted text-xs font-mono whitespace-pre-wrap">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    )}
                  </div>
                </details>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={this.handleReset}
                  className="
                    flex items-center gap-2 px-4 py-2 rounded
                    bg-nvidia-green hover:bg-nvidia-green-dark
                    text-white font-medium text-sm
                    transition-colors
                  "
                >
                  <RefreshCw className="w-4 h-4" />
                  Try Again
                </button>
                
                <button
                  onClick={() => window.location.reload()}
                  className="
                    px-4 py-2 rounded
                    bg-bg-card hover:bg-bg-card-hover
                    border border-border-subtle
                    text-text-primary font-medium text-sm
                    transition-colors
                  "
                >
                  Reload Page
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

