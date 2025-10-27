import React, { useRef, useEffect, useState } from 'react';
import {
  ChevronUp,
  ChevronDown,
  X,
  Trash2,
  Filter,
  Terminal,
  Circle
} from 'lucide-react';
import { useOutputStore } from '../../stores/outputStore';
import { useWebSocket } from '../../hooks/useWebSocket';

/**
 * OutputPanel
 *
 * Persistent bottom panel that displays all command output and logs.
 * Similar to VS Code's Output/Terminal panel.
 *
 * Features:
 * - Shows all stdout/stderr from backend processes
 * - Collapsible/expandable
 * - Resizable height
 * - Auto-scroll with manual override
 * - Log level filtering
 * - Clear logs
 * - Color-coded by log level
 */
export const OutputPanel: React.FC = () => {
  const {
    logs,
    isCollapsed,
    height,
    minHeight,
    maxHeight,
    autoScroll,
    clearLogs,
    toggleCollapsed,
    setHeight,
    setAutoScroll,
    addLog,
  } = useOutputStore();

  const [filterLevel, setFilterLevel] = useState<string>('all');
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Connect to WebSocket and listen for log events
  useWebSocket({
    onLogMessage: (data) => {
      // Add log from WebSocket
      const level = data.level === 'error' ? 'error' :
                   data.level === 'warning' ? 'warning' :
                   data.level === 'debug' ? 'debug' : 'info';
      addLog(level, data.source || 'system', data.message);
    },
    onJobLog: (data) => {
      // Add job-specific logs
      addLog('info', data.job_id || 'job', data.message || data.log || '');
    },
  });

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current && !isCollapsed) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll, isCollapsed]);

  // Detect manual scroll
  const handleScroll = () => {
    if (!logsContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = logsContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setAutoScroll(isAtBottom);
  };

  // Handle resize drag
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!panelRef.current) return;
      const rect = panelRef.current.getBoundingClientRect();
      const newHeight = window.innerHeight - e.clientY;
      setHeight(newHeight);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, setHeight]);

  // Filter logs
  const filteredLogs = logs.filter(log => {
    if (filterLevel === 'all') return true;
    return log.level === filterLevel;
  });

  // Get log level color
  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-status-error';
      case 'warning':
        return 'text-status-warning';
      case 'debug':
        return 'text-text-muted';
      default:
        return 'text-text-primary';
    }
  };

  // Get log level icon color
  const getLogLevelIconColor = (level: string) => {
    switch (level) {
      case 'error':
        return 'text-status-error';
      case 'warning':
        return 'text-status-warning';
      case 'info':
        return 'text-status-info';
      default:
        return 'text-text-muted';
    }
  };

  return (
    <div
      ref={panelRef}
      className="output-panel flex flex-col bg-bg-panel border-t border-border-subtle"
      style={{
        height: isCollapsed ? '40px' : `${height}px`,
        minHeight: isCollapsed ? '40px' : `${minHeight}px`,
        maxHeight: isCollapsed ? '40px' : `${maxHeight}px`,
        transition: isDragging ? 'none' : 'height 0.2s ease-in-out',
      }}
    >
      {/* Resize Handle */}
      {!isCollapsed && (
        <div
          className={`
            h-1 w-full cursor-ns-resize
            ${isDragging ? 'bg-nvidia-green' : 'bg-border-subtle hover:bg-nvidia-green'}
            transition-colors
          `}
          onMouseDown={handleMouseDown}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-bg-dark border-b border-border-subtle">
        <div className="flex items-center gap-3">
          <Terminal className="w-4 h-4 text-nvidia-green" />
          <h3 className="text-sm font-semibold text-text-primary">Output</h3>
          {logs.length > 0 && (
            <span className="text-xs text-text-muted">
              ({logs.length} {logs.length === 1 ? 'line' : 'lines'})
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Filter */}
          {!isCollapsed && (
            <>
              <div className="flex items-center gap-2">
                <Filter className="w-3.5 h-3.5 text-text-muted" />
                <select
                  value={filterLevel}
                  onChange={(e) => setFilterLevel(e.target.value)}
                  className="
                    px-2 py-1 text-xs rounded
                    bg-bg-card border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:ring-1 focus:ring-nvidia-green
                  "
                >
                  <option value="all">All</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                  <option value="debug">Debug</option>
                </select>
              </div>

              {/* Clear */}
              <button
                onClick={clearLogs}
                disabled={logs.length === 0}
                className="
                  p-1.5 rounded
                  hover:bg-bg-card
                  text-text-secondary hover:text-text-primary
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-colors
                "
                title="Clear output"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>

              <div className="w-px h-4 bg-border-subtle" />
            </>
          )}

          {/* Collapse/Expand */}
          <button
            onClick={toggleCollapsed}
            className="
              p-1.5 rounded
              hover:bg-bg-card
              text-text-secondary hover:text-text-primary
              transition-colors
            "
            title={isCollapsed ? 'Expand output' : 'Collapse output'}
          >
            {isCollapsed ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div
          ref={logsContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4 bg-bg-dark font-mono text-xs leading-relaxed"
        >
          {filteredLogs.length === 0 ? (
            <div className="flex items-center justify-center h-full text-text-muted">
              <p className="text-sm">
                {logs.length === 0
                  ? 'No output yet. Logs will appear here when commands execute.'
                  : 'No logs match the current filter.'}
              </p>
            </div>
          ) : (
            <div className="space-y-0.5">
              {filteredLogs.map((log) => (
                <div
                  key={log.id}
                  className="flex items-start gap-2 hover:bg-bg-panel/50 px-2 py-0.5 -mx-2 rounded"
                >
                  {/* Level Indicator */}
                  <Circle
                    className={`w-2 h-2 mt-1.5 shrink-0 ${getLogLevelIconColor(log.level)}`}
                    fill="currentColor"
                  />

                  {/* Timestamp */}
                  <span className="text-text-muted shrink-0 w-20">
                    {log.timestamp.toLocaleTimeString('en-US', {
                      hour12: false,
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit'
                    })}
                  </span>

                  {/* Source */}
                  <span className="text-nvidia-green shrink-0 w-24 truncate" title={log.source}>
                    [{log.source}]
                  </span>

                  {/* Message */}
                  <span className={`flex-1 whitespace-pre-wrap break-all ${getLogLevelColor(log.level)}`}>
                    {log.message}
                  </span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
