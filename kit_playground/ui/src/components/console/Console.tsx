/**
 * Console Component
 * Terminal-style output for build logs, errors, and runtime messages
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  Box,
  IconButton,
  Tooltip,
  Typography,
  Tabs,
  Tab,
  Badge,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Clear as ClearIcon,
  GetApp as DownloadIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  KeyboardArrowUp as CollapseIcon,
  KeyboardArrowDown as ExpandIcon,
  FiberManualRecord as RecordIcon,
} from '@mui/icons-material';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error' | 'success' | 'debug';
  source: 'build' | 'runtime' | 'system';
  message: string;
}

interface ConsoleProps {
  height?: number;
}

const Console: React.FC<ConsoleProps> = ({ height = 200 }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'all' | 'build' | 'runtime' | 'system'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLevel, setFilterLevel] = useState<string[]>(['info', 'warning', 'error', 'success', 'debug']);
  const [filterMenuAnchor, setFilterMenuAnchor] = useState<null | HTMLElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const consoleRef = useRef<HTMLDivElement>(null);
  const endOfLogsRef = useRef<HTMLDivElement>(null);

  // Log level counts
  const logCounts = {
    errors: logs.filter(l => l.level === 'error').length,
    warnings: logs.filter(l => l.level === 'warning').length,
    info: logs.filter(l => l.level === 'info').length,
  };

  // Add log entry
  const addLog = useCallback((entry: Omit<LogEntry, 'id' | 'timestamp'>) => {
    const newLog: LogEntry = {
      ...entry,
      id: `${Date.now()}-${Math.random()}`,
      timestamp: new Date(),
    };
    setLogs(prev => [...prev, newLog]);
  }, []);

  // Listen for log events from other components
  useEffect(() => {
    const handleLogEvent = (event: CustomEvent) => {
      addLog(event.detail);
    };

    window.addEventListener('console-log' as any, handleLogEvent);
    return () => {
      window.removeEventListener('console-log' as any, handleLogEvent);
    };
  }, [addLog]);

  // Connect to WebSocket for streaming logs
  useEffect(() => {
    // Disable WebSocket connection for now - will be re-enabled with Socket.IO
    // The console will still capture logs from console intercept
    console.log('Console initialized (WebSocket disabled temporarily)');

    addLog({
      level: 'info',
      source: 'system',
      message: 'Console ready - WebSocket log streaming disabled',
    });

    return () => {
      // Cleanup if needed
    };
  }, [addLog]);

  // Filter logs based on tab, search, and level
  useEffect(() => {
    let filtered = logs;

    // Tab filter
    if (activeTab !== 'all') {
      filtered = filtered.filter(log => log.source === activeTab);
    }

    // Level filter
    filtered = filtered.filter(log => filterLevel.includes(log.level));

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(query)
      );
    }

    setFilteredLogs(filtered);
  }, [logs, activeTab, searchQuery, filterLevel]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && endOfLogsRef.current) {
      endOfLogsRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs, autoScroll]);

  // Handle scroll to detect if user scrolled up
  const handleScroll = () => {
    if (consoleRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = consoleRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setAutoScroll(isAtBottom);
    }
  };

  // Clear logs
  const handleClear = () => {
    setLogs([]);
  };

  // Download logs
  const handleDownload = () => {
    const logText = logs
      .map(log => `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`)
      .join('\n');

    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kit-playground-logs-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Toggle filter level
  const toggleFilterLevel = (level: string) => {
    if (filterLevel.includes(level)) {
      setFilterLevel(filterLevel.filter(l => l !== level));
    } else {
      setFilterLevel([...filterLevel, level]);
    }
  };

  // Get log level color
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      case 'success':
        return '#76b900';
      case 'info':
        return '#2196f3';
      case 'debug':
        return '#9e9e9e';
      default:
        return '#ffffff';
    }
  };

  // Get source icon
  const getSourceBadge = (source: string) => {
    const colors = {
      build: '#76b900',
      runtime: '#2196f3',
      system: '#9e9e9e',
    };
    return (
      <Box
        component="span"
        sx={{
          display: 'inline-block',
          width: 8,
          height: 8,
          borderRadius: '50%',
          backgroundColor: colors[source as keyof typeof colors] || '#ffffff',
          mr: 1,
        }}
      />
    );
  };

  if (isCollapsed) {
    return (
      <Box
        sx={{
          height: 32,
          display: 'flex',
          alignItems: 'center',
          backgroundColor: '#1e1e1e',
          borderTop: 1,
          borderColor: 'divider',
          px: 2,
        }}
      >
        <Typography variant="body2" sx={{ flex: 1, color: 'text.secondary' }}>
          Console (collapsed)
        </Typography>
        {logCounts.errors > 0 && (
          <Badge badgeContent={logCounts.errors} color="error" sx={{ mr: 2 }} />
        )}
        {logCounts.warnings > 0 && (
          <Badge badgeContent={logCounts.warnings} color="warning" sx={{ mr: 2 }} />
        )}
        <IconButton size="small" onClick={() => setIsCollapsed(false)}>
          <ExpandIcon />
        </IconButton>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        height: height,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#1e1e1e',
        borderTop: 1,
        borderColor: 'divider',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          borderBottom: 1,
          borderColor: 'divider',
          backgroundColor: '#252526',
        }}
      >
        {/* Tabs */}
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          sx={{ minHeight: 36, flex: 1 }}
        >
          <Tab
            label={`All (${logs.length})`}
            value="all"
            sx={{ minHeight: 36, py: 0 }}
          />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                Build
                {logCounts.errors > 0 && (
                  <Badge badgeContent={logCounts.errors} color="error" />
                )}
              </Box>
            }
            value="build"
            sx={{ minHeight: 36, py: 0 }}
          />
          <Tab
            label="Runtime"
            value="runtime"
            sx={{ minHeight: 36, py: 0 }}
          />
          <Tab
            label="System"
            value="system"
            sx={{ minHeight: 36, py: 0 }}
          />
        </Tabs>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 0.5, pr: 1 }}>
          <Tooltip title="Filter">
            <IconButton
              size="small"
              onClick={(e) => setFilterMenuAnchor(e.currentTarget)}
            >
              <FilterIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Clear">
            <IconButton size="small" onClick={handleClear}>
              <ClearIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Download Logs">
            <IconButton size="small" onClick={handleDownload}>
              <DownloadIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Collapse">
            <IconButton size="small" onClick={() => setIsCollapsed(true)}>
              <CollapseIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Search Bar */}
      <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider' }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search logs..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              fontSize: 13,
            },
          }}
        />
      </Box>

      {/* Log Output */}
      <Box
        ref={consoleRef}
        onScroll={handleScroll}
        sx={{
          flex: 1,
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: 12,
          p: 1,
          backgroundColor: '#1e1e1e',
        }}
      >
        {filteredLogs.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary',
            }}
          >
            <Typography variant="body2">
              {logs.length === 0 ? 'No logs yet' : 'No logs match your filters'}
            </Typography>
          </Box>
        ) : (
          filteredLogs.map(log => (
            <Box
              key={log.id}
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 1,
                py: 0.25,
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.05)',
                },
              }}
            >
              {/* Timestamp */}
              <Typography
                variant="caption"
                sx={{
                  color: 'text.secondary',
                  minWidth: 80,
                  fontSize: 11,
                }}
              >
                {log.timestamp.toLocaleTimeString()}
              </Typography>

              {/* Source Badge */}
              {getSourceBadge(log.source)}

              {/* Level Indicator */}
              <RecordIcon
                sx={{
                  fontSize: 12,
                  color: getLevelColor(log.level),
                  mt: 0.25,
                }}
              />

              {/* Message */}
              <Typography
                variant="body2"
                sx={{
                  flex: 1,
                  color: log.level === 'error' ? '#f44336' : 'inherit',
                  fontWeight: log.level === 'error' ? 'bold' : 'normal',
                  fontSize: 12,
                  fontFamily: 'monospace',
                  wordBreak: 'break-word',
                }}
              >
                {log.message}
              </Typography>
            </Box>
          ))
        )}
        <div ref={endOfLogsRef} />
      </Box>

      {/* Auto-scroll indicator */}
      {!autoScroll && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 8,
            right: 8,
            backgroundColor: 'primary.main',
            color: 'white',
            px: 1,
            py: 0.5,
            borderRadius: 1,
            fontSize: 11,
            cursor: 'pointer',
          }}
          onClick={() => {
            setAutoScroll(true);
            endOfLogsRef.current?.scrollIntoView({ behavior: 'smooth' });
          }}
        >
          ↓ New messages
        </Box>
      )}

      {/* Filter Menu */}
      <Menu
        anchorEl={filterMenuAnchor}
        open={Boolean(filterMenuAnchor)}
        onClose={() => setFilterMenuAnchor(null)}
      >
        <MenuItem onClick={() => toggleFilterLevel('error')}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RecordIcon sx={{ fontSize: 12, color: getLevelColor('error') }} />
            <Typography>Errors</Typography>
            {filterLevel.includes('error') && <span>✓</span>}
          </Box>
        </MenuItem>
        <MenuItem onClick={() => toggleFilterLevel('warning')}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RecordIcon sx={{ fontSize: 12, color: getLevelColor('warning') }} />
            <Typography>Warnings</Typography>
            {filterLevel.includes('warning') && <span>✓</span>}
          </Box>
        </MenuItem>
        <MenuItem onClick={() => toggleFilterLevel('info')}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RecordIcon sx={{ fontSize: 12, color: getLevelColor('info') }} />
            <Typography>Info</Typography>
            {filterLevel.includes('info') && <span>✓</span>}
          </Box>
        </MenuItem>
        <MenuItem onClick={() => toggleFilterLevel('success')}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RecordIcon sx={{ fontSize: 12, color: getLevelColor('success') }} />
            <Typography>Success</Typography>
            {filterLevel.includes('success') && <span>✓</span>}
          </Box>
        </MenuItem>
        <MenuItem onClick={() => toggleFilterLevel('debug')}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RecordIcon sx={{ fontSize: 12, color: getLevelColor('debug') }} />
            <Typography>Debug</Typography>
            {filterLevel.includes('debug') && <span>✓</span>}
          </Box>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default Console;

// Helper function to emit log events from other components
export const emitConsoleLog = (
  level: 'info' | 'warning' | 'error' | 'success' | 'debug',
  source: 'build' | 'runtime' | 'system',
  message: string
) => {
  window.dispatchEvent(
    new CustomEvent('console-log', {
      detail: { level, source, message },
    })
  );
};