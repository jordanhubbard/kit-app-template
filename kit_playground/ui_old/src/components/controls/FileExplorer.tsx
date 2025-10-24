/**
 * File Explorer Component
 * Directory browser with path selector for choosing build output locations
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Breadcrumbs,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  Home as HomeIcon,
  ArrowUpward as UpIcon,
  CreateNewFolder as NewFolderIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface FileItem {
  name: string;
  path: string;
  isDirectory: boolean;
  size?: number;
  modified?: Date;
}

interface FileExplorerProps {
  selectedPath: string;
  onPathChange: (path: string) => void;
  title?: string;
  showFiles?: boolean;
}

const FileExplorer: React.FC<FileExplorerProps> = ({
  selectedPath,
  onPathChange,
  title = "Select Output Directory",
  showFiles = false,
}) => {
  const [currentPath, setCurrentPath] = useState(selectedPath || '');
  const [items, setItems] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');

  // Load directory contents
  const loadDirectory = useCallback(async (path: string) => {
    setLoading(true);
    setError(null);

    try {
      // Use backend API
      const response = await fetch(`/api/filesystem/list?path=${encodeURIComponent(path)}`);
      if (!response.ok) throw new Error('Failed to load directory');
      let files: FileItem[] = await response.json();

      // Filter to show only directories unless showFiles is true
      if (!showFiles) {
        files = files.filter(f => f.isDirectory);
      }

      // Sort: directories first, then files, alphabetically
      files.sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });

      setItems(files);
    } catch (err) {
      console.error('Failed to load directory:', err);
      setError(err instanceof Error ? err.message : 'Failed to load directory');
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [showFiles]);

  useEffect(() => {
    if (currentPath) {
      loadDirectory(currentPath);
    }
  }, [currentPath, loadDirectory]);

  // Initialize with home directory - only runs once on mount
  useEffect(() => {
    if (!currentPath) {
      loadHomeDirectory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadHomeDirectory = async () => {
    try {
      // Get current working directory from backend API
      const response = await fetch('/api/filesystem/cwd');
      if (response.ok) {
        const data = await response.json();
        setCurrentPath(data.realpath || data.cwd);
      } else {
        // Fallback to sensible default
        const platform = navigator.platform.toLowerCase();
        const isWindows = platform.includes('win');
        const defaultHome = isWindows ? 'C:\\Users' : '/home';
        setCurrentPath(defaultHome);
      }
    } catch (err) {
      console.error('Failed to get current directory:', err);
      // Fallback to root
      setCurrentPath('/');
    }
  };

  const handleItemClick = (item: FileItem) => {
    if (item.isDirectory) {
      setCurrentPath(item.path);
    }
  };

  const handleGoUp = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
  };

  const handleBreadcrumbClick = (index: number) => {
    const parts = currentPath.split('/').filter(p => p);
    const newPath = '/' + parts.slice(0, index + 1).join('/');
    setCurrentPath(newPath);
  };

  const handleSelect = () => {
    onPathChange(currentPath);
  };

  const handleCreateFolder = async () => {
    if (!newFolderName) return;

    try {
      const newPath = `${currentPath}/${newFolderName}`;

      const response = await fetch('/api/filesystem/mkdir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: newPath }),
      });

      if (!response.ok) throw new Error('Failed to create directory');

      setDialogOpen(false);
      setNewFolderName('');
      loadDirectory(currentPath);
    } catch (err) {
      console.error('Failed to create folder:', err);
      setError(err instanceof Error ? err.message : 'Failed to create folder');
    }
  };

  // Get breadcrumb parts
  const pathParts = currentPath.split('/').filter(p => p);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Title */}
      {title && (
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
          {title}
        </Typography>
      )}

      {/* Toolbar */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          mb: 1,
        }}
      >
        <IconButton size="small" onClick={loadHomeDirectory}>
          <HomeIcon />
        </IconButton>
        <IconButton size="small" onClick={handleGoUp} disabled={currentPath === '/'}>
          <UpIcon />
        </IconButton>
        <IconButton size="small" onClick={() => loadDirectory(currentPath)}>
          <RefreshIcon />
        </IconButton>
        <IconButton size="small" onClick={() => setDialogOpen(true)}>
          <NewFolderIcon />
        </IconButton>
      </Box>

      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 1, fontSize: 12 }}>
        <Link
          component="button"
          underline="hover"
          color="inherit"
          onClick={() => setCurrentPath('/')}
          sx={{ fontSize: 12 }}
        >
          /
        </Link>
        {pathParts.map((part, index) => (
          <Link
            key={index}
            component="button"
            underline="hover"
            color={index === pathParts.length - 1 ? 'text.primary' : 'inherit'}
            onClick={() => handleBreadcrumbClick(index)}
            sx={{ fontSize: 12 }}
          >
            {part}
          </Link>
        ))}
      </Breadcrumbs>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 1 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* File List */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          border: 1,
          borderColor: 'divider',
          borderRadius: 1,
          backgroundColor: '#252526',
        }}
      >
        {loading ? (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
            }}
          >
            <Typography color="text.secondary">Loading...</Typography>
          </Box>
        ) : items.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary',
            }}
          >
            <Typography variant="body2">Empty directory</Typography>
          </Box>
        ) : (
          <List dense sx={{ py: 0 }}>
            {items.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  onClick={() => handleItemClick(item)}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(255,255,255,0.05)',
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {item.isDirectory ? (
                      <FolderIcon sx={{ color: '#dcb67a' }} />
                    ) : (
                      <FileIcon sx={{ color: '#519aba' }} />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.name}
                    primaryTypographyProps={{ fontSize: 13 }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      {/* Selected Path Display */}
      <Box sx={{ mt: 2 }}>
        <TextField
          fullWidth
          label="Selected Path"
          value={currentPath}
          onChange={(e) => setCurrentPath(e.target.value)}
          size="small"
          sx={{ mb: 1 }}
        />
        <Button
          fullWidth
          variant="contained"
          onClick={handleSelect}
          disabled={!currentPath}
        >
          Select This Directory
        </Button>
      </Box>

      {/* Create Folder Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Create New Folder</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Folder Name"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleCreateFolder();
              }
            }}
            sx={{ mt: 2 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Location: {currentPath}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateFolder} variant="contained" disabled={!newFolderName}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileExplorer;