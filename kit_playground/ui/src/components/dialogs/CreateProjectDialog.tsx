/**
 * Create Project from Template Dialog
 * Collects project variables and generates a new project from a template
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Divider,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Folder as FolderIcon,
  Info as InfoIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

interface Template {
  name: string;
  display_name: string;
  type: string;
  category: string;
  description: string;
  version?: string;
  documentation?: string;
}

interface CreateProjectDialogProps {
  open: boolean;
  template: Template | null;
  onClose: () => void;
  onSuccess: (projectInfo: any) => void;
}

const CreateProjectDialog: React.FC<CreateProjectDialogProps> = ({
  open,
  template,
  onClose,
  onSuccess,
}) => {
  // Form state
  const [projectName, setProjectName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [version, setVersion] = useState('0.1.0');
  const [outputDir, setOutputDir] = useState('');
  const [useCustomOutput, setUseCustomOutput] = useState(false);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Reset form when template changes
  useEffect(() => {
    if (template) {
      setProjectName('');
      setDisplayName('');
      setVersion('0.1.0');
      setOutputDir('');
      setUseCustomOutput(false);
      setError(null);
      setValidationErrors({});
    }
  }, [template]);

  // Validation
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // Validate project name (lowercase, alphanumeric, dots, underscores)
    if (!projectName) {
      errors.projectName = 'Project name is required';
    } else if (!/^[a-z0-9._]+$/.test(projectName)) {
      errors.projectName = 'Use lowercase letters, numbers, dots, and underscores only (e.g., my_company.my_app)';
    }

    // Validate display name
    if (!displayName) {
      errors.displayName = 'Display name is required';
    }

    // Validate version (semantic versioning)
    if (!version) {
      errors.version = 'Version is required';
    } else if (!/^\d+\.\d+\.\d+$/.test(version)) {
      errors.version = 'Use semantic versioning format (e.g., 1.0.0)';
    }

    // Validate output directory if custom
    if (useCustomOutput && !outputDir) {
      errors.outputDir = 'Output directory is required when using custom location';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle create project
  const handleCreate = async () => {
    if (!template) return;

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: any = {
        templateName: template.name,
        name: projectName,
        displayName: displayName,
        version: version,
      };

      if (useCustomOutput && outputDir) {
        payload.outputDir = outputDir;
      }

      const response = await fetch('/api/v2/templates/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (result.success) {
        onSuccess({
          templateName: template.name,
          projectName: projectName,
          displayName: displayName,
          outputDir: result.outputDir || 'source/apps',
          playbackFile: result.playbackFile,
        });
        onClose();
      } else {
        setError(result.error || 'Failed to create project');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create project. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate display name from project name
  const handleProjectNameChange = (value: string) => {
    setProjectName(value);

    // Auto-generate display name if it's empty
    if (!displayName) {
      const parts = value.split('.');
      const lastPart = parts[parts.length - 1] || '';
      const generated = lastPart
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      setDisplayName(generated);
    }
  };

  if (!template) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: 500 }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6">Create Project from Template</Typography>
          <Chip label={template.type} size="small" color="primary" />
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers>
        {/* Template Info */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
            {template.display_name}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {template.description}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip label={template.category} size="small" variant="outlined" />
            {template.version && (
              <Chip label={`v${template.version}`} size="small" variant="outlined" />
            )}
          </Box>
        </Box>

        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }} icon={<InfoIcon />}>
          You are creating a <strong>new {template.type}</strong> based on the <strong>{template.display_name}</strong> template.
          This will not modify the original template.
        </Alert>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Form Fields */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          {/* Project Name */}
          <Box>
            <TextField
              fullWidth
              required
              label="Project Name"
              value={projectName}
              onChange={(e) => handleProjectNameChange(e.target.value)}
              error={!!validationErrors.projectName}
              helperText={validationErrors.projectName || 'Lowercase, dot-separated namespace (e.g., my_company.my_app)'}
              placeholder="my_company.my_app"
              disabled={loading}
            />
          </Box>

          {/* Display Name */}
          <Box>
            <TextField
              fullWidth
              required
              label="Display Name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              error={!!validationErrors.displayName}
              helperText={validationErrors.displayName || 'Human-readable name shown to users'}
              placeholder="My Application"
              disabled={loading}
            />
          </Box>

          {/* Version */}
          <Box>
            <TextField
              fullWidth
              required
              label="Version"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              error={!!validationErrors.version}
              helperText={validationErrors.version || 'Semantic versioning (e.g., 1.0.0)'}
              placeholder="0.1.0"
              disabled={loading}
            />
          </Box>

          <Divider />

          {/* Custom Output Directory (Optional) */}
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={useCustomOutput}
                  onChange={(e) => setUseCustomOutput(e.target.checked)}
                  disabled={loading}
                />
              }
              label="Use custom output directory (create standalone project)"
            />

            {useCustomOutput && (
              <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  label="Output Directory"
                  value={outputDir}
                  onChange={(e) => setOutputDir(e.target.value)}
                  error={!!validationErrors.outputDir}
                  helperText={validationErrors.outputDir || 'Absolute path to create standalone project'}
                  placeholder="/path/to/my-project"
                  disabled={loading}
                  InputProps={{
                    startAdornment: <FolderIcon sx={{ mr: 1, color: 'action.active' }} />,
                  }}
                />
                <Tooltip title="Browse for directory">
                  <IconButton disabled={loading}>
                    <FolderIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            )}
            {!useCustomOutput && (
              <Typography variant="caption" color="text.secondary" sx={{ ml: 4, display: 'block', mt: 0.5 }}>
                Project will be created in: <code>source/apps/{projectName}.kit</code>
              </Typography>
            )}
          </Box>
        </Box>

        {/* Example */}
        {projectName && (
          <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.900', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              Equivalent CLI command:
            </Typography>
            <Typography
              variant="body2"
              component="pre"
              sx={{
                fontFamily: 'monospace',
                color: 'success.light',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
                margin: 0,
              }}
            >
              ./repo.sh template new {template.name} \{'\n'}
              {'  '}--name={projectName} \{'\n'}
              {'  '}--display-name="{displayName}" \{'\n'}
              {'  '}--version={version}
              {useCustomOutput && outputDir && `\n  --output-dir=${outputDir}`}
            </Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleCreate}
          disabled={loading || !projectName || !displayName || !version}
          startIcon={loading ? <CircularProgress size={16} /> : null}
        >
          {loading ? 'Creating...' : 'Create Project'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateProjectDialog;
