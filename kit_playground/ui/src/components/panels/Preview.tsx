import React, { useState, useEffect } from 'react';
import { X, ExternalLink, AlertTriangle, RefreshCw, Monitor } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { useWebSocket } from '../../hooks/useWebSocket';

interface PreviewProps {
  projectName?: string;
  streamingUrl?: string;
  mode?: 'streaming' | 'xpra' | 'direct';
}

/**
 * Preview
 * 
 * Preview panel for viewing running applications (Panel 6/7).
 * Supports three display modes:
 * - Kit App Streaming (WebRTC): iframe with streaming URL
 * - Xpra Display Server: iframe to port 10000
 * - Direct Launch: informational panel (no preview)
 * 
 * Features:
 * - Embedded iframe preview
 * - External link option
 * - SSL certificate warning handling
 * - Connection status monitoring
 * - Refresh/reload capability
 */
export const Preview: React.FC<PreviewProps> = ({
  projectName,
  streamingUrl: initialStreamingUrl,
  mode = 'streaming',
}) => {
  const { closePanel, getPanelsByType } = usePanelStore();
  const [streamingUrl, setStreamingUrl] = useState<string | null>(initialStreamingUrl || null);
  const [isLoading, setIsLoading] = useState(!initialStreamingUrl);
  const [error, setError] = useState<string | null>(null);
  const [showCertWarning, setShowCertWarning] = useState(true);
  const [key, setKey] = useState(0); // For iframe refresh

  // Listen for streaming_ready event
  useWebSocket({
    onStreamingReady: (data) => {
      console.log('Streaming ready:', data);
      if (data.url) {
        setStreamingUrl(data.url);
        setIsLoading(false);
      }
    },
  });

  useEffect(() => {
    if (mode === 'streaming' && !streamingUrl) {
      // Wait for streaming URL from WebSocket
      const timeout = setTimeout(() => {
        if (!streamingUrl) {
          setError('Timeout waiting for streaming URL');
          setIsLoading(false);
        }
      }, 60000); // 60 second timeout

      return () => clearTimeout(timeout);
    } else if (mode === 'xpra') {
      // Xpra mode: construct URL to port 10000
      const hostname = window.location.hostname;
      setStreamingUrl(`http://${hostname}:10000`);
      setIsLoading(false);
    } else if (mode === 'direct') {
      // Direct mode: no preview available
      setIsLoading(false);
    }
  }, [mode, streamingUrl]);

  const handleClose = () => {
    const panels = getPanelsByType('preview');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
  };

  const handleRefresh = () => {
    setKey(prev => prev + 1);
    setShowCertWarning(true);
  };

  const handleOpenExternal = () => {
    if (streamingUrl) {
      window.open(streamingUrl, '_blank');
    }
  };

  const getTitle = () => {
    switch (mode) {
      case 'streaming':
        return 'Kit App Streaming Preview';
      case 'xpra':
        return 'Xpra Display Preview';
      case 'direct':
        return 'Direct Launch';
      default:
        return 'Preview';
    }
  };

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-3">
          <Monitor className="w-5 h-5 text-nvidia-green" />
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              {getTitle()}
            </h3>
            {projectName && (
              <p className="text-xs text-text-muted">
                {projectName}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {streamingUrl && (
            <>
              <button
                onClick={handleRefresh}
                className="
                  p-2 rounded
                  hover:bg-bg-card
                  text-text-secondary hover:text-text-primary
                  transition-colors
                "
                title="Refresh preview"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              
              <button
                onClick={handleOpenExternal}
                className="
                  p-2 rounded
                  hover:bg-bg-card
                  text-text-secondary hover:text-nvidia-green
                  transition-colors
                "
                title="Open in new window"
              >
                <ExternalLink className="w-4 h-4" />
              </button>
              
              <div className="w-px h-6 bg-border-subtle mx-1" />
            </>
          )}
          
          <button
            onClick={handleClose}
            className="
              p-2 rounded
              hover:bg-bg-card
              text-text-secondary hover:text-text-primary
              transition-colors
            "
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* SSL Certificate Warning (for Kit App Streaming) */}
      {mode === 'streaming' && streamingUrl && showCertWarning && (
        <div className="p-4 bg-status-warning/10 border-b border-status-warning/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-status-warning flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-status-warning mb-1">
                Self-Signed SSL Certificate
              </h4>
              <p className="text-xs text-text-secondary mb-2">
                Kit App Streaming uses a self-signed SSL certificate. Your browser may show a security warning.
                This is normal for development. Click "Advanced" and "Proceed" to continue.
              </p>
              <button
                onClick={() => setShowCertWarning(false)}
                className="
                  text-xs text-status-warning hover:text-status-warning/80
                  underline transition-colors
                "
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preview Content */}
      <div className="flex-1 overflow-hidden relative">
        {/* Loading State */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-bg-dark">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-nvidia-green border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-text-primary font-medium mb-2">
                {mode === 'streaming' && 'Waiting for streaming server...'}
                {mode === 'xpra' && 'Waiting for Xpra display...'}
                {mode === 'direct' && 'Launching application...'}
              </p>
              <p className="text-text-muted text-sm">
                This may take a moment
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-bg-dark">
            <div className="text-center px-4">
              <AlertTriangle className="w-12 h-12 text-status-error mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Preview Error
              </h3>
              <p className="text-text-secondary text-sm mb-4">
                {error}
              </p>
              <button
                onClick={handleClose}
                className="
                  px-4 py-2 rounded
                  bg-nvidia-green hover:bg-nvidia-green-dark
                  text-white text-sm font-medium
                  transition-colors
                "
              >
                Close Preview
              </button>
            </div>
          </div>
        )}

        {/* Direct Launch Mode (No Preview) */}
        {mode === 'direct' && !isLoading && !error && (
          <div className="absolute inset-0 flex items-center justify-center bg-bg-dark">
            <div className="text-center px-4 max-w-md">
              <Monitor className="w-16 h-16 text-nvidia-green mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Direct Launch Mode
              </h3>
              <p className="text-text-secondary text-sm mb-4">
                The application is running directly on this machine's display.
                Check your desktop environment to interact with it.
              </p>
              <p className="text-text-muted text-xs">
                Direct launch mode does not support in-browser preview.
                Use Kit App Streaming or Xpra for remote preview.
              </p>
            </div>
          </div>
        )}

        {/* Iframe Preview */}
        {streamingUrl && !isLoading && !error && mode !== 'direct' && (
          <iframe
            key={key}
            src={streamingUrl}
            className="w-full h-full border-0"
            title={`${projectName || 'Application'} Preview`}
            allow="camera; microphone; autoplay; encrypted-media"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-pointer-lock"
          />
        )}
      </div>

      {/* Footer */}
      {streamingUrl && !error && (
        <div className="p-3 border-t border-border-subtle bg-bg-dark">
          <div className="flex items-center justify-between text-xs">
            <span className="text-text-muted">
              {mode === 'streaming' && 'WebRTC Streaming'}
              {mode === 'xpra' && 'Xpra Display Server'}
            </span>
            <a
              href={streamingUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-nvidia-green hover:text-nvidia-green-light flex items-center gap-1"
            >
              {streamingUrl}
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

