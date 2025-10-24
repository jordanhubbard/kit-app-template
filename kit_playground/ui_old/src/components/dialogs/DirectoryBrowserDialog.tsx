/**
 * Directory Browser Dialog
 * Browse and select directories from the filesystem
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  TextField,
  Box,
  Typography,
  CircularProgress,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Folder as FolderIcon,
  ArrowUpward as UpIcon,
  Home as HomeIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface DirectoryItem {
  name: string;
  path: string;
  isDirectory: boolean;
  size: number;
  modified: string;
}

interface DirectoryBrowserDialogProps {
  open: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
  initialPath?: string;
}

const DirectoryBrowserDialog: React.FC<DirectoryBrowserDialogProps> = ({
  open,
  onClose,
  onSelect,
  initialPath,
}) => {
  const [currentPath, setCurrentPath] = useState<string>(initialPath || '');
  const [items, setItems] = useState<DirectoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [manualPath, setManualPath] = useState<string>('');

  // Load initial directory
  useEffect(() => {
    if (open && !currentPath) {
      // Load home directory initially
      loadHomeDirectory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // Update manual path when current path changes
  useEffect(() => {
    setManualPath(currentPath);
  }, [currentPath]);

  const loadHomeDirectory = async () => {
    try {
      const response = await fetch('/api/filesystem/cwd');
      const data = await response.json();
      if (data.cwd) {
        loadDirectory(data.cwd);
      }
    } catch (err) {
      setError('Failed to load home directory');
    }
  };

  const loadDirectory = async (path: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/filesystem/list?path=${encodeURIComponent(path)}`);
      const data = await response.json();

      if (response.ok) {
        // Sort: directories first, then files
        const sorted = data.sort((a: DirectoryItem, b: DirectoryItem) => {
          if (a.isDirectory && !b.isDirectory) return -1;
          if (!a.isDirectory && b.isDirectory) return 1;
          return a.name.localeCompare(b.name);
        });

        setItems(sorted);
        setCurrentPath(path);
      } else {
        setError(data.error || 'Failed to load directory');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load directory');
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = (item: DirectoryItem) => {
    if (item.isDirectory) {
      loadDirectory(item.path);
    }
  };

  const handleParentDirectory = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    loadDirectory(parentPath);
  };

  const handleSelectCurrent = () => {
    onSelect(currentPath);
    onClose();
  };

  const handleManualPathSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualPath) {
      loadDirectory(manualPath);
    }
  };

  // Generate breadcrumb parts
  const getBreadcrumbs = () => {
    if (!currentPath) return [];
    const parts = currentPath.split('/').filter(Boolean);
    return ['/', ...parts];
  };

  const handleBreadcrumbClick = (index: number) => {
    if (index === 0) {
      loadDirectory('/');
    } else {
      const parts = currentPath.split('/').filter(Boolean).slice(0, index);
      const path = '/' + parts.join('/');
      loadDirectory(path);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { height: '70vh' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
        <Typography variant="h6">Select Directory</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        {/* Path Input */}
        <Box component="form" onSubmit={handleManualPathSubmit} sx={{ mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            label="Current Path"
            value={manualPath}
            onChange={(e) => setManualPath(e.target.value)}
            InputProps={{
              endAdornment: (
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <IconButton size="small" onClick={handleParentDirectory} disabled={currentPath === '/'}>
                    <UpIcon />
                  </IconButton>
                  <IconButton size="small" onClick={loadHomeDirectory}>
                    <HomeIcon />
                  </IconButton>
                  <IconButton size="small" onClick={() => loadDirectory(currentPath)}>
                    <RefreshIcon />
                  </IconButton>
                </Box>
              )
            }}
          />
        </Box>

        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 2 }}>
          {getBreadcrumbs().map((part, index) => (
            <Link
              key={index}
              component="button"
              variant="body2"
              onClick={() => handleBreadcrumbClick(index)}
              sx={{ cursor: 'pointer' }}
            >
              {index === 0 ? <HomeIcon sx={{ fontSize: 16 }} /> : part}
            </Link>
          ))}
        </Breadcrumbs>

        {/* Error Message */}
        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        {/* Loading Indicator */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Directory List */}
        {!loading && !error && (
          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {items.filter(item => item.isDirectory).map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton onClick={() => handleItemClick(item)}>
                  <ListItemIcon>
                    <FolderIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={item.name}
                    secondary={new Date(item.modified).toLocaleString()}
                  />
                </ListItemButton>
              </ListItem>
            ))}
            {items.filter(item => item.isDirectory).length === 0 && (
              <Typography color="text.secondary" align="center" sx={{ py: 2 }}>
                No subdirectories found
              </Typography>
            )}
          </List>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleSelectCurrent}
          disabled={!currentPath}
        >
          Select This Directory
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DirectoryBrowserDialog;
