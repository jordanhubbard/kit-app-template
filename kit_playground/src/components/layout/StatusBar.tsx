/**
 * Status Bar Component
 * Bottom status bar showing project status, build info, and notifications
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Sync as SyncIcon,
  Cloud as CloudIcon,
  CloudDone as CloudDoneIcon,
  BugReport as BugIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';
import { useAppSelector } from '../../hooks/redux';

interface StatusBarProps {
  className?: string;
}

const StatusBar: React.FC<StatusBarProps> = ({ className }) => {
  const { currentProject, isBuilding, isRunning } = useAppSelector(
    state => state.project || { currentProject: null, isBuilding: false, isRunning: false }
  );

  const [cpuUsage, setCpuUsage] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);
  const [buildStatus, setBuildStatus] = useState<'idle' | 'building' | 'success' | 'error'>('idle');
  const [errorCount, setErrorCount] = useState(0);
  const [warningCount, setWarningCount] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected');

  // Monitor system resources (mock for now, would connect to backend)
  useEffect(() => {
    const interval = setInterval(() => {
      // In production, fetch from backend API
      setCpuUsage(Math.random() * 100);
      setMemoryUsage(Math.random() * 100);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Listen for build status updates
  useEffect(() => {
    const handleBuildStatus = (event: CustomEvent) => {
      setBuildStatus(event.detail.status);
      setErrorCount(event.detail.errors || 0);
      setWarningCount(event.detail.warnings || 0);
    };

    window.addEventListener('build-status' as any, handleBuildStatus);
    return () => {
      window.removeEventListener('build-status' as any, handleBuildStatus);
    };
  }, []);

  // Update build status based on project state
  useEffect(() => {
    if (isBuilding) {
      setBuildStatus('building');
    } else if (buildStatus === 'building') {
      // Assume success if building stopped without errors
      setBuildStatus(errorCount > 0 ? 'error' : 'success');
    }
  }, [isBuilding, errorCount, buildStatus]);

  // Get status icon
  const getStatusIcon = () => {
    switch (buildStatus) {
      case 'building':
        return <CircularProgress size={14} />;
      case 'success':
        return <SuccessIcon sx={{ fontSize: 14, color: '#76b900' }} />;
      case 'error':
        return <ErrorIcon sx={{ fontSize: 14, color: '#f44336' }} />;
      default:
        return <InfoIcon sx={{ fontSize: 14, color: 'text.secondary' }} />;
    }
  };

  // Get status text
  const getStatusText = () => {
    if (isRunning) return 'Running';
    if (isBuilding) return 'Building...';
    if (buildStatus === 'success') return 'Build Successful';
    if (buildStatus === 'error') return 'Build Failed';
    return 'Ready';
  };

  // Get connection icon
  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <CloudDoneIcon sx={{ fontSize: 14, color: '#76b900' }} />;
      case 'connecting':
        return <SyncIcon sx={{ fontSize: 14, color: '#ff9800' }} className="spin" />;
      case 'disconnected':
        return <CloudIcon sx={{ fontSize: 14, color: '#f44336' }} />;
    }
  };

  return (
    <Box
      className={className}
      sx={{
        display: 'flex',
        alignItems: 'center',
        height: 24,
        backgroundColor: '#007acc',
        color: 'white',
        px: 1,
        fontSize: 12,
        gap: 2,
        borderTop: 1,
        borderColor: 'divider',
      }}
    >
      {/* Project Name */}
      {currentProject && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
            {currentProject.name}
          </Typography>
        </Box>
      )}

      {/* Build Status */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {getStatusIcon()}
        <Typography variant="caption">{getStatusText()}</Typography>
      </Box>

      {/* Error/Warning Counts */}
      {(errorCount > 0 || warningCount > 0) && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {errorCount > 0 && (
            <Tooltip title="Errors">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <ErrorIcon sx={{ fontSize: 14, color: '#f44336' }} />
                <Typography variant="caption">{errorCount}</Typography>
              </Box>
            </Tooltip>
          )}
          {warningCount > 0 && (
            <Tooltip title="Warnings">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <WarningIcon sx={{ fontSize: 14, color: '#ff9800' }} />
                <Typography variant="caption">{warningCount}</Typography>
              </Box>
            </Tooltip>
          )}
        </Box>
      )}

      {/* Spacer */}
      <Box sx={{ flex: 1 }} />

      {/* System Resources */}
      <Tooltip title="CPU Usage">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <PerformanceIcon sx={{ fontSize: 14 }} />
          <Typography variant="caption">{cpuUsage.toFixed(0)}%</Typography>
        </Box>
      </Tooltip>

      <Tooltip title="Memory Usage">
        <Typography variant="caption">
          {memoryUsage.toFixed(0)}% MEM
        </Typography>
      </Tooltip>

      {/* Connection Status */}
      <Tooltip title={`Backend: ${connectionStatus}`}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {getConnectionIcon()}
        </Box>
      </Tooltip>

      {/* Kit SDK Version */}
      <Typography variant="caption" sx={{ opacity: 0.7 }}>
        Kit SDK 106.0
      </Typography>
    </Box>
  );
};

export default StatusBar;

// Helper function to emit build status updates
export const emitBuildStatus = (
  status: 'idle' | 'building' | 'success' | 'error',
  errors: number = 0,
  warnings: number = 0
) => {
  window.dispatchEvent(
    new CustomEvent('build-status', {
      detail: { status, errors, warnings },
    })
  );
};