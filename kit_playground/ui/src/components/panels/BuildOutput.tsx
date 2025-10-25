import React, { useState, useEffect, useRef } from 'react';
import { X, Square, RotateCcw, Trash2, CheckCircle, XCircle, Loader, Terminal } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { useJob, type Job } from '../../hooks/useJob';
import { useWebSocket } from '../../hooks/useWebSocket';

interface BuildOutputProps {
  jobId?: string;
  projectName?: string;
  jobType?: Job['type'];
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
}) => {
  const { closePanel, getPanelsByType } = usePanelStore();
  const { job, startJob, cancelJob } = useJob();
  const [logs, setLogs] = useState<string[]>([]);
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  // WebSocket for real-time updates
  const { connected } = useWebSocket({
    onJobStatus: (data) => {
      console.log('Job status:', data);
      // Update job status
    },
    onJobProgress: (data) => {
      console.log('Job progress:', data);
      // Update progress bar
    },
    onJobLog: (data) => {
      // Add log message
      setLogs(prev => [...prev, data.message || data.log || JSON.stringify(data)]);
    },
  });

  // Initialize job if needed
  useEffect(() => {
    if (!initialJobId && projectName) {
      // Start a new job
      startJob(jobType, projectName);
    }
  }, [initialJobId, projectName, jobType, startJob]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!logsContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = logsContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  const handleCancel = async () => {
    if (job && job.id) {
      await cancelJob(job.id);
    }
  };

  const handleRetry = async () => {
    if (projectName) {
      setLogs([]);
      await startJob(jobType, projectName);
    }
  };

  const handleClear = () => {
    setLogs([]);
  };

  const handleClose = () => {
    const panels = getPanelsByType('build-output');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
  };

  const getStatusConfig = () => {
    if (!job) return { icon: <Terminal className="w-5 h-5" />, color: 'text-text-muted', label: 'Idle' };
    
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

  const statusConfig = getStatusConfig();
  const canCancel = job?.status === 'pending' || job?.status === 'running';
  const canRetry = job?.status === 'failed' || job?.status === 'cancelled' || job?.status === 'completed';

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-3">
          <div className={statusConfig.color}>
            {statusConfig.icon}
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
        </div>

        <div className="flex items-center gap-2">
          {canCancel && (
            <button
              onClick={handleCancel}
              className="
                p-2 rounded
                hover:bg-bg-card
                text-text-secondary hover:text-status-error
                transition-colors
              "
              title="Cancel job"
            >
              <Square className="w-4 h-4" />
            </button>
          )}
          
          {canRetry && (
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
          
          <button
            onClick={handleClear}
            disabled={logs.length === 0}
            className="
              p-2 rounded
              hover:bg-bg-card
              text-text-secondary hover:text-text-primary
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            "
            title="Clear logs"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          
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

      {/* Log Output */}
      <div
        ref={logsContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 bg-bg-dark font-mono text-sm"
      >
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Terminal className="w-12 h-12 text-text-muted mb-4" />
            <p className="text-text-secondary">
              {job?.status === 'pending' ? 'Waiting for job to start...' : 'No output yet'}
            </p>
          </div>
        ) : (
          <>
            {logs.map((log, index) => (
              <div key={index} className="text-text-primary whitespace-pre-wrap break-words">
                {log}
              </div>
            ))}
            <div ref={logsEndRef} />
          </>
        )}
      </div>

      {/* Auto-scroll indicator */}
      {!autoScroll && logs.length > 0 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
          <button
            onClick={() => {
              setAutoScroll(true);
              logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="
              px-4 py-2 rounded-full
              bg-nvidia-green hover:bg-nvidia-green-dark
              text-white text-xs font-medium
              shadow-lg
              transition-colors
            "
          >
            ↓ Scroll to bottom
          </button>
        </div>
      )}

      {/* Footer */}
      <div className="p-3 border-t border-border-subtle bg-bg-dark">
        <div className="text-xs text-text-muted">
          {logs.length} lines • {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
    </div>
  );
};

