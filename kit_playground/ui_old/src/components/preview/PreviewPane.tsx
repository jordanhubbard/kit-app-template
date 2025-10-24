/**
 * Preview Pane Component
 * Displays running templates in an iframe with controls
 */

import React, { forwardRef, useImperativeHandle, useRef, useEffect, useState } from 'react';
import { Box, IconButton, LinearProgress, Tooltip, Paper } from '@mui/material';
import {
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  FitScreen as FitScreenIcon,
  PhoneIphone as PhoneIcon,
  Tablet as TabletIcon,
  DesktopWindows as DesktopIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

interface PreviewPaneProps {
  url: string;
  templateId: string | null;
  mode?: 'iframe' | 'xpra';
  onError?: (error: Error) => void;
}

interface PreviewPaneHandle {
  reload: () => void;
  fullscreen: () => void;
  openInBrowser: () => void;
  setZoom: (zoom: number) => void;
  setDevice: (device: DevicePreset) => void;
}

interface DevicePreset {
  name: string;
  width: number;
  height: number;
  scale?: number;
}

const devicePresets: DevicePreset[] = [
  { name: 'Desktop', width: 1920, height: 1080 },
  { name: 'Laptop', width: 1366, height: 768 },
  { name: 'Tablet', width: 768, height: 1024 },
  { name: 'Phone', width: 375, height: 812 },
  { name: 'TV/4K', width: 3840, height: 2160, scale: 0.5 },
];

const PreviewPane = forwardRef<PreviewPaneHandle, PreviewPaneProps>(
  ({ url, templateId, mode = 'iframe', onError }, ref) => {
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [zoom, setZoomState] = useState(100);
    const [selectedDevice, setSelectedDevice] = useState<DevicePreset | null>(null);
    const [iframeKey, setIframeKey] = useState(0);
    const [xpraInstalled, setXpraInstalled] = useState<boolean | null>(null);

    // Log when URL changes
    useEffect(() => {
      console.log('[PreviewPane] URL changed:', url);
      console.log('[PreviewPane] Mode:', mode);
    }, [url, mode]);

    // Check if Xpra is installed (for Xpra mode)
    useEffect(() => {
      if (mode === 'xpra') {
        fetch('/api/xpra/check')
          .then(res => res.json())
          .then(data => {
            setXpraInstalled(data.installed);
            if (!data.installed) {
              setError(`Xpra is not installed. Run: ${data.installCommand || 'make install-xpra'}`);
            }
          })
          .catch(err => {
            console.error('Failed to check Xpra:', err);
            setXpraInstalled(false);
          });
      }
    }, [mode]);

    // Expose methods via ref
    useImperativeHandle(ref, () => ({
      reload: () => {
        setIframeKey(k => k + 1);
        setLoading(true);
        setError(null);
      },
      fullscreen: () => {
        if (containerRef.current) {
          if (!document.fullscreenElement) {
            containerRef.current.requestFullscreen();
          } else {
            document.exitFullscreen();
          }
        }
      },
      openInBrowser: () => {
        window.open(url, '_blank');
      },
      setZoom: (newZoom: number) => {
        setZoomState(newZoom);
      },
      setDevice: (device: DevicePreset) => {
        setSelectedDevice(device);
      },
    }));

    // Handle fullscreen change
    useEffect(() => {
      const handleFullscreenChange = () => {
        setIsFullscreen(!!document.fullscreenElement);
      };

      document.addEventListener('fullscreenchange', handleFullscreenChange);
      return () => {
        document.removeEventListener('fullscreenchange', handleFullscreenChange);
      };
    }, []);

    // Handle iframe load
    const handleIframeLoad = () => {
      setLoading(false);
      setError(null);

      // Set up message communication with iframe
      if (iframeRef.current?.contentWindow) {
        // Send initial configuration
        iframeRef.current.contentWindow.postMessage({
          type: 'playground-init',
          templateId,
          config: {
            hotReload: true,
            debug: true,
          }
        }, '*');
      }
    };

    // Handle iframe error
    const handleIframeError = (e: any) => {
      setLoading(false);
      const errorMsg = `Failed to load preview from ${url}`;
      setError(errorMsg);
      console.error('[PreviewPane] Iframe error:', errorMsg, e);
      if (onError) {
        onError(new Error(errorMsg));
      }
    };

    // Handle messages from iframe
    useEffect(() => {
      const handleMessage = (event: MessageEvent) => {
        if (event.data.type === 'playground-error') {
          setError(event.data.message);
          if (onError) {
            onError(new Error(event.data.message));
          }
        } else if (event.data.type === 'playground-ready') {
          setLoading(false);
        } else if (event.data.type === 'playground-log') {
          // Forward logs to console component
          console.log('[Preview]', event.data.message);
        }
      };

      window.addEventListener('message', handleMessage);
      return () => {
        window.removeEventListener('message', handleMessage);
      };
    }, [onError]);

    // Calculate iframe dimensions based on device preset
    const getIframeStyle = () => {
      if (!selectedDevice) {
        return {
          width: '100%',
          height: '100%',
          transform: `scale(${zoom / 100})`,
          transformOrigin: 'top left',
        };
      }

      const containerWidth = containerRef.current?.clientWidth || 0;
      const containerHeight = containerRef.current?.clientHeight || 0;

      const scale = selectedDevice.scale || Math.min(
        containerWidth / selectedDevice.width,
        containerHeight / selectedDevice.height,
        1
      );

      return {
        width: `${selectedDevice.width}px`,
        height: `${selectedDevice.height}px`,
        transform: `scale(${scale * (zoom / 100)})`,
        transformOrigin: 'center',
        position: 'absolute' as const,
        top: '50%',
        left: '50%',
        marginTop: `-${selectedDevice.height / 2}px`,
        marginLeft: `-${selectedDevice.width / 2}px`,
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
        border: '1px solid #333',
        backgroundColor: '#000',
      };
    };

    return (
      <Box
        ref={containerRef}
        sx={{
          position: 'relative',
          width: '100%',
          height: '100%',
          backgroundColor: '#1a1a1a',
          overflow: 'hidden',
        }}
      >
        {/* Toolbar */}
        <Paper
          elevation={1}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            zIndex: 10,
            display: 'flex',
            gap: 0.5,
            p: 0.5,
            backgroundColor: 'rgba(30, 30, 30, 0.9)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {/* Zoom Controls */}
          <Tooltip title="Zoom Out">
            <IconButton
              size="small"
              onClick={() => setZoomState(Math.max(25, zoom - 25))}
            >
              <ZoomOutIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Box sx={{ display: 'flex', alignItems: 'center', px: 1 }}>
            {zoom}%
          </Box>

          <Tooltip title="Zoom In">
            <IconButton
              size="small"
              onClick={() => setZoomState(Math.min(200, zoom + 25))}
            >
              <ZoomInIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Fit to Screen">
            <IconButton
              size="small"
              onClick={() => {
                setZoomState(100);
                setSelectedDevice(null);
              }}
            >
              <FitScreenIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          {/* Device Presets */}
          <Box sx={{ borderLeft: 1, borderColor: 'divider', pl: 1, ml: 0.5 }}>
            <Tooltip title="Desktop">
              <IconButton
                size="small"
                onClick={() => setSelectedDevice(devicePresets[0])}
                color={selectedDevice?.name === 'Desktop' ? 'primary' : 'default'}
              >
                <DesktopIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title="Tablet">
              <IconButton
                size="small"
                onClick={() => setSelectedDevice(devicePresets[2])}
                color={selectedDevice?.name === 'Tablet' ? 'primary' : 'default'}
              >
                <TabletIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title="Phone">
              <IconButton
                size="small"
                onClick={() => setSelectedDevice(devicePresets[3])}
                color={selectedDevice?.name === 'Phone' ? 'primary' : 'default'}
              >
                <PhoneIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Actions */}
          <Box sx={{ borderLeft: 1, borderColor: 'divider', pl: 1, ml: 0.5 }}>
            <Tooltip title="Refresh">
              <IconButton
                size="small"
                onClick={() => {
                  setIframeKey(k => k + 1);
                  setLoading(true);
                }}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title="Open in Browser">
              <IconButton
                size="small"
                onClick={() => window.open(url, '_blank')}
              >
                <OpenInNewIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
              <IconButton
                size="small"
                onClick={() => {
                  if (!document.fullscreenElement) {
                    containerRef.current?.requestFullscreen();
                  } else {
                    document.exitFullscreen();
                  }
                }}
              >
                {isFullscreen ? (
                  <FullscreenExitIcon fontSize="small" />
                ) : (
                  <FullscreenIcon fontSize="small" />
                )}
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>

        {/* Loading indicator */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              zIndex: 5,
            }}
          >
            <LinearProgress />
          </Box>
        )}

        {/* Error display */}
        {error && (
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              color: 'error.main',
            }}
          >
            <WarningIcon sx={{ fontSize: 48, mb: 2 }} />
            <Box>{error}</Box>
            <Box sx={{ mt: 1, fontSize: 12, color: 'text.secondary' }}>
              Check the console for more details
            </Box>
          </Box>
        )}

        {/* Preview iframe */}
        {!error && (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <iframe
              key={iframeKey}
              ref={iframeRef}
              src={url}
              title={mode === 'xpra' ? "Xpra X11 Display" : "Template Preview"}
              style={getIframeStyle()}
              onLoad={handleIframeLoad}
              onError={handleIframeError}
              sandbox={mode === 'xpra' ? "allow-scripts allow-same-origin allow-forms allow-modals allow-popups allow-downloads" : "allow-scripts allow-same-origin allow-forms allow-modals allow-popups"}
              allow="accelerometer; camera; encrypted-media; geolocation; gyroscope; microphone; clipboard-read; clipboard-write"
            />
          </Box>
        )}

        {/* Device frame overlay */}
        {selectedDevice && (
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              left: 8,
              backgroundColor: 'rgba(0,0,0,0.7)',
              color: 'white',
              px: 1,
              py: 0.5,
              borderRadius: 1,
              fontSize: 12,
              zIndex: 5,
            }}
          >
            {selectedDevice.name} ({selectedDevice.width}×{selectedDevice.height})
          </Box>
        )}

        {/* Xpra mode indicator */}
        {mode === 'xpra' && xpraInstalled && (
          <Box
            sx={{
              position: 'absolute',
              bottom: 8,
              left: 8,
              backgroundColor: 'rgba(0,150,136,0.9)',
              color: 'white',
              px: 1,
              py: 0.5,
              borderRadius: 1,
              fontSize: 11,
              zIndex: 5,
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            <Box component="span" sx={{ fontSize: 16 }}>🖥️</Box>
            Xpra Remote Display
          </Box>
        )}
      </Box>
    );
  }
);

PreviewPane.displayName = 'PreviewPane';

export default PreviewPane;