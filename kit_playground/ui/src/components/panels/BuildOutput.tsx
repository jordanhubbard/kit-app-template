import React, { useState, useEffect, useRef } from 'react';
import { X, Square, RotateCcw, CheckCircle, XCircle, Loader, Terminal, Play, Zap } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { useJob, type Job } from '../../hooks/useJob';
import { useWebSocket } from '../../hooks/useWebSocket';

interface BuildOutputProps {
  jobId?: string;
  projectName?: string;
  jobType?: Job['type'];
  autoStart?: boolean;
}

/**
 * BuildOutput
 *
 * Real-time build output panel (Panel 4/5).
 * Displays live log streaming from build/launch jobs.
 *
 * Features:
 * - Real-time log streaming via WebSocket
 * - Job status indicators
 * - Progress bar
 * - Job control actions (cancel, retry, clear)
 * - Auto-scroll with manual override
 * - ANSI color support (basic)
 */
export const BuildOutput: React.FC<BuildOutputProps> = ({
  jobId: initialJobId,
  projectName,
  jobType = 'build',
  autoStart = false,
}) => {
  const { closePanel, getPanelsByType, openPanel } = usePanelStore();
  const { job, startJob, cancelJob, stopProject } = useJob();
  const [buildCompleted, setBuildCompleted] = useState(false); // Track build completion locally
  const [buildFailed, setBuildFailed] = useState(false); // Track build failure locally
  const [isStreamingActive, setIsStreamingActive] = useState(false); // Track if streaming is enabled
  const hasStartedJob = useRef(false); // Track if we've already started the job

  // WebSocket for real-time updates
  const { connected } = useWebSocket({
    onJobStatus: (data) => {
      console.log('[BuildOutput] Job status:', data);
      // Job status updates from backend
    },
    onJobProgress: (data) => {
      console.log('[BuildOutput] Job progress:', data);
      // Progress updates from backend
    },
    onLogMessage: (data) => {
      // Logs are now shown only in the bottom Output panel
      // Build/Launch panels show status info only
      console.log('[BuildOutput] Received log:', data);

      // Detect build completion from log messages
      if (jobType === 'build') {
        const logLine = data.message || JSON.stringify(data);
        if (logLine.includes('BUILD (RELEASE) SUCCEEDED') || logLine.includes('Build completed successfully')) {
          console.log('[BuildOutput] Detected successful build completion');
          setBuildCompleted(true);
          setBuildFailed(false);
        } else if (logLine.includes('BUILD (RELEASE) FAILED') || logLine.includes('Build failed')) {
          console.log('[BuildOutput] Detected failed build');
          setBuildCompleted(false);
          setBuildFailed(true);
        }
      }

      // Detect streaming mode activation (for launch jobs)
      if (jobType === 'launch') {
        const logLine = data.message || JSON.stringify(data);
        if (logLine.includes('Kit App Streaming') || logLine.includes('Streaming Mode') || logLine.includes('WebRTC')) {
          console.log('[BuildOutput] Detected streaming mode activation');
          setIsStreamingActive(true);
        }
      }
    },
    onStreamingReady: (data) => {
      console.log('[BuildOutput] Streaming ready:', data);
      setIsStreamingActive(true); // Mark streaming as active
      if (data.url && jobType === 'launch') {
        // Auto-open streaming URL in new tab
        console.log('[BuildOutput] Auto-opening streaming URL:', data.url);
        window.open(data.url, '_blank');
      }
    },
    onXpraReady: (data) => {
      console.log('[BuildOutput] Xpra ready:', data);
      if (data.url && jobType === 'launch') {
        // Auto-open Xpra URL in new tab
        console.log('[BuildOutput] Auto-opening Xpra URL:', data.url);
        window.open(data.url, '_blank');
      }
    },
  });

  // Initialize job if needed (only once)
  useEffect(() => {
    console.log('[BuildOutput] useEffect check:', {
      initialJobId,
      projectName,
      autoStart,
      hasStarted: hasStartedJob.current
    });

    if (!initialJobId && projectName && autoStart && !hasStartedJob.current) {
      hasStartedJob.current = true;
      // Reset streaming state for new launch
      setIsStreamingActive(false);
      console.log(`[BuildOutput] Auto-starting ${jobType} job for ${projectName}`);
      // Start a new job
      startJob(jobType, projectName);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialJobId, projectName, jobType, autoStart]); // Intentionally omit startJob to prevent loop

  const handleCancel = async () => {
    if (job && job.id) {
      await cancelJob(job.id);
    }
  };

  const handleRetry = async () => {
    if (projectName) {
      setBuildCompleted(false);
      setBuildFailed(false);
      setIsStreamingActive(false); // Reset streaming state
      hasStartedJob.current = false; // Reset so we can start again
      await startJob(jobType, projectName);
    }
  };

  const handleStart = async () => {
    if (projectName) {
      setBuildCompleted(false);
      setBuildFailed(false);
      setIsStreamingActive(false); // Reset streaming state
      hasStartedJob.current = false; // Reset so we can start again
      await startJob(jobType, projectName);
    }
  };

  const handleRelaunch = async () => {
    if (!projectName) {
      alert('No project name available for re-launch');
      return;
    }

    console.log('[BuildOutput] Re-launching application:', projectName);

    // First, stop the currently running instance (if any)
    const stopped = await stopProject(projectName);
    if (stopped) {
      console.log('[BuildOutput] Successfully stopped running instance');
    }

    // Wait a brief moment for cleanup
    await new Promise(resolve => setTimeout(resolve, 500));

    // Reset state
    setBuildCompleted(false);
    setBuildFailed(false);
    setIsStreamingActive(false);
    hasStartedJob.current = false;

    // Start again
    await startJob('launch', projectName);
  };

  const handleClose = async () => {
    // If there's a running or pending job, cancel it first
    if (job && (job.status === 'running' || job.status === 'pending')) {
      console.log('[BuildOutput] Canceling running job before close:', job.id);
      await cancelJob(job.id);
    }

    // Close the panel
    const panels = getPanelsByType('build-output');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
  };

  const getStatusConfig = () => {
    if (!job) return { icon: <Terminal className="w-5 h-5" />, color: 'text-text-muted', label: 'Idle' };

    // Check local completion state first (for builds that detect completion via log parsing)
    if (buildCompleted) {
      return { icon: <CheckCircle className="w-5 h-5" />, color: 'text-status-success', label: 'Completed' };
    }
    if (buildFailed) {
      return { icon: <XCircle className="w-5 h-5" />, color: 'text-status-error', label: 'Failed' };
    }

    // Otherwise, use job status from backend
    switch (job.status) {
      case 'pending':
        return { icon: <Loader className="w-5 h-5 animate-spin" />, color: 'text-status-info', label: 'Pending' };
      case 'running':
        return { icon: <Loader className="w-5 h-5 animate-spin" />, color: 'text-nvidia-green', label: 'Running' };
      case 'completed':
        return { icon: <CheckCircle className="w-5 h-5" />, color: 'text-status-success', label: 'Completed' };
      case 'failed':
        return { icon: <XCircle className="w-5 h-5" />, color: 'text-status-error', label: 'Failed' };
      case 'cancelled':
        return { icon: <Square className="w-5 h-5" />, color: 'text-text-muted', label: 'Cancelled' };
      default:
        return { icon: <Terminal className="w-5 h-5" />, color: 'text-text-muted', label: 'Unknown' };
    }
  };

  const handleLaunch = async () => {
    if (!projectName) {
      alert('No project name available for launch');
      return;
    }

    console.log('[BuildOutput] Launching application:', projectName);

    // Open a new panel for launch output
    openPanel('build-output', {
      projectName,
      jobType: 'launch',
      autoStart: true,  // This will trigger startJob in the new panel's useEffect
    });
  };

  const statusConfig = getStatusConfig();
  const canStart = !job || (!initialJobId && !job.id);
  const canCancel = job?.status === 'pending' || job?.status === 'running';
  const canRetry = job?.status === 'failed' || job?.status === 'cancelled' || job?.status === 'completed' || buildFailed;
  const canLaunch = jobType === 'build' && buildCompleted && projectName;
  const canRelaunch = jobType === 'launch' && projectName && (job?.status === 'running' || job?.status === 'completed');

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-3">
          <div className={`relative ${statusConfig.color}`}>
            {statusConfig.icon}
            {/* Lightning bolt icon for streaming mode */}
            {isStreamingActive && jobType === 'launch' && (
              <div
                className="absolute -top-1 -right-1 bg-yellow-500 rounded-full p-0.5"
                title="Kit App Streaming enabled"
              >
                <Zap className="w-3 h-3 text-black" fill="currentColor" />
              </div>
            )}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              {job?.type === 'build' && 'Build Output'}
              {job?.type === 'launch' && 'Launch Output'}
              {job?.type === 'create' && 'Create Output'}
              {!job && 'Output'}
            </h3>
            <div className="flex items-center gap-2 text-xs">
              <span className={statusConfig.color}>{statusConfig.label}</span>
              {projectName && (
                <>
                  <span className="text-text-muted">•</span>
                  <span className="text-text-secondary">{projectName}</span>
                </>
              )}
              {connected && (
                <>
                  <span className="text-text-muted">•</span>
                  <span className="text-status-success flex items-center gap-1">
                    <span className="w-2 h-2 bg-status-success rounded-full animate-pulse" />
                    Live
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Launch button next to title */}
          {canLaunch && (
            <button
              onClick={handleLaunch}
              className="
                ml-4 px-4 py-2 rounded
                bg-blue-600 hover:bg-blue-700
                text-white text-sm font-semibold
                transition-colors
                flex items-center gap-2
                shadow-sm
              "
              title="Launch application"
            >
              <Play className="w-4 h-4" />
              Launch
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {canStart && projectName && (
            <button
              onClick={handleStart}
              className="
                px-4 py-2 rounded
                bg-nvidia-green hover:bg-nvidia-green-dark
                text-white text-sm font-semibold
                transition-colors
                flex items-center gap-2
                shadow-sm
              "
              title="Start build"
            >
              <Play className="w-4 h-4" />
              Start {jobType === 'build' ? 'Build' : jobType === 'launch' ? 'Launch' : 'Job'}
            </button>
          )}

          {canRelaunch && (
            <button
              onClick={handleRelaunch}
              className="
                px-4 py-2 rounded
                bg-blue-600 hover:bg-blue-700
                text-white text-sm font-semibold
                transition-colors
                flex items-center gap-2
                shadow-sm
              "
              title="Stop and restart the application"
            >
              <RotateCcw className="w-4 h-4" />
              Re-launch
            </button>
          )}

          {((canStart && projectName) || canRelaunch) && <div className="w-px h-6 bg-border-subtle mx-2" />}

          {canCancel && (
            <button
              onClick={handleCancel}
              className="
                p-2 rounded
                bg-status-error/10 hover:bg-status-error/20
                text-status-error
                transition-colors
              "
              title="Cancel job (stop process)"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          )}

          {canRetry && !canRelaunch && (
            <button
              onClick={handleRetry}
              className="
                p-2 rounded
                hover:bg-bg-card
                text-text-secondary hover:text-nvidia-green
                transition-colors
              "
              title="Retry"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          )}

          <div className="w-px h-6 bg-border-subtle mx-1" />

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

      {/* Progress Bar */}
      {job?.progress !== undefined && job.status === 'running' && (
        <div className="h-1 bg-bg-card overflow-hidden">
          <div
            className="h-full bg-nvidia-green transition-all duration-300"
            style={{ width: `${job.progress}%` }}
          />
        </div>
      )}

      {/* Status Summary */}
      <div className="flex-1 overflow-y-auto p-6 bg-bg-dark">
        <div className="max-w-2xl mx-auto">
          <div className="flex flex-col items-center justify-center space-y-6">
            {/* Status Icon */}
            <div className="flex items-center justify-center">
              {statusConfig.icon}
            </div>

            {/* Status Message */}
            <div className="text-center">
              <h3 className={`text-xl font-semibold mb-2 ${statusConfig.color}`}>
                {statusConfig.label}
              </h3>
              {projectName && (
                <p className="text-text-secondary">
                  {jobType === 'build' ? 'Building' : 'Launching'}: <span className="text-text-primary font-mono">{projectName}</span>
                </p>
              )}
            </div>

            {/* Job Details */}
            {job && (
              <div className="w-full max-w-md bg-bg-card rounded-lg p-4 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Status:</span>
                  <span className={`font-semibold ${statusConfig.color}`}>{statusConfig.label}</span>
                </div>

                {job.startTime && (
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Started:</span>
                    <span className="text-text-primary">{new Date(job.startTime).toLocaleTimeString()}</span>
                  </div>
                )}

                {job.endTime && (
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Finished:</span>
                    <span className="text-text-primary">{new Date(job.endTime).toLocaleTimeString()}</span>
                  </div>
                )}

                {job.progress !== undefined && (
                  <div className="flex justify-between text-sm">
                    <span className="text-text-secondary">Progress:</span>
                    <span className="text-text-primary">{job.progress}%</span>
                  </div>
                )}
              </div>
            )}

            {/* Instructions */}
            <div className="text-center text-sm text-text-secondary max-w-md">
              {job?.status === 'pending' && (
                <p>Job is queued and will start shortly...</p>
              )}
              {job?.status === 'running' && (
                <p>View detailed logs in the Output panel at the bottom of the screen.</p>
              )}
              {buildCompleted && (
                <p className="text-nvidia-green">Build successful! Click the Launch button to run your application.</p>
              )}
              {buildFailed && (
                <p className="text-status-error">Build failed. Check the Output panel for error details.</p>
              )}
              {jobType === 'launch' && job?.status === 'running' && (
                <p className="text-nvidia-green">Application is starting... Preview will open automatically when ready.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border-subtle bg-bg-dark">
        <div className="text-xs text-text-muted">
          {connected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </div>
    </div>
  );
};
