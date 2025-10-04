/**
 * Template Detail Panel
 * Shows detailed information about a selected template or project
 */

import React from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Code as CodeIcon,
  Apps as AppsIcon,
  Extension as ExtensionIcon,
  Cloud as CloudIcon,
  Folder as FolderIcon,
  Info as InfoIcon,
  Label as TagIcon,
  Person as AuthorIcon,
  CalendarToday as DateIcon,
  Build as BuildIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material';

interface Template {
  name: string;
  display_name: string;
  type: 'application' | 'extension' | 'microservice' | 'component';
  category: string;
  description: string;
  thumbnail?: string;
  icon?: string;
  color_scheme?: {
    primary?: string;
    accent?: string;
  };
  connectors: {
    name: string;
    type: string;
    direction: string;
  }[];
  metadata?: {
    version?: string;
    author?: string;
    tags?: string[];
  };
}

interface Project {
  id: string;
  name: string;
  displayName: string;
  path: string;
  kitFile: string;
  status: string;
  lastModified: number;
}

interface TemplateDetailPanelProps {
  template?: Template;
  project?: Project;
  onClose: () => void;
  onCreateProject?: (template: Template) => void;
  onOpenProject?: (project: Project) => void;
}

const TemplateDetailPanel: React.FC<TemplateDetailPanelProps> = ({
  template,
  project,
  onClose,
  onCreateProject,
  onOpenProject,
}) => {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'application':
        return <AppsIcon />;
      case 'extension':
        return <ExtensionIcon />;
      case 'microservice':
        return <CloudIcon />;
      default:
        return <CodeIcon />;
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  // Render template details
  if (template) {
    return (
      <Paper
        elevation={3}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderLeft: 2,
          borderColor: 'divider',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            backgroundColor: '#252526',
            borderBottom: 1,
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="h6" sx={{ fontSize: 18 }}>
            Template Details
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          {/* Thumbnail */}
          <Box
            sx={{
              width: '100%',
              height: 200,
              backgroundColor: template.color_scheme?.primary || '#333',
              backgroundImage: template.thumbnail
                ? `url(${template.thumbnail})`
                : `linear-gradient(135deg, ${template.color_scheme?.primary || '#333'} 0%, ${template.color_scheme?.accent || '#555'} 100%)`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              borderRadius: 1,
              mb: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {!template.thumbnail && (
              <Box sx={{ fontSize: 72, opacity: 0.3 }}>
                {getTypeIcon(template.type)}
              </Box>
            )}
          </Box>

          {/* Title and Type */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="h5" sx={{ mb: 1 }}>
              {template.display_name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Chip
                icon={getTypeIcon(template.type)}
                label={template.type}
                size="small"
                color="primary"
              />
              <Chip label={template.category} size="small" variant="outlined" />
            </Box>
          </Box>

          {/* Description */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" color="text.secondary">
              {template.description}
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* Metadata */}
          {template.metadata && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold' }}>
                <InfoIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                Information
              </Typography>
              <List dense>
                {template.metadata.version && (
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <TagIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Version"
                      secondary={template.metadata.version}
                    />
                  </ListItem>
                )}
                {template.metadata.author && (
                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <AuthorIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Author"
                      secondary={template.metadata.author}
                    />
                  </ListItem>
                )}
                <ListItem>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <FolderIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary="Template ID" secondary={template.name} />
                </ListItem>
              </List>
            </Box>
          )}

          {/* Tags */}
          {template.metadata?.tags && template.metadata.tags.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                Tags
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {template.metadata.tags.map((tag, index) => (
                  <Chip key={index} label={tag} size="small" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}

          {/* Connectors */}
          {template.connectors && template.connectors.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                Connectors ({template.connectors.length})
              </Typography>
              <List dense>
                {template.connectors.map((conn, index) => (
                  <ListItem key={index}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <CodeIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary={conn.name}
                      secondary={`${conn.type} (${conn.direction})`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>

        {/* Footer Actions */}
        <Box
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            backgroundColor: '#252526',
          }}
        >
          <Button
            fullWidth
            variant="contained"
            color="primary"
            size="large"
            startIcon={<AddIcon />}
            onClick={() => onCreateProject && onCreateProject(template)}
          >
            Create Project from Template
          </Button>
        </Box>
      </Paper>
    );
  }

  // Render project details
  if (project) {
    return (
      <Paper
        elevation={3}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderLeft: 2,
          borderColor: 'divider',
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            backgroundColor: '#252526',
            borderBottom: 1,
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="h6" sx={{ fontSize: 18 }}>
            Project Details
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Content */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          {/* Project Icon */}
          <Box
            sx={{
              width: '100%',
              height: 200,
              backgroundColor: '#1a5490',
              backgroundImage: 'linear-gradient(135deg, #1a5490 0%, #76b900 100%)',
              borderRadius: 1,
              mb: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AppsIcon sx={{ fontSize: 72, opacity: 0.5, color: 'white' }} />
          </Box>

          {/* Title and Status */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="h5" sx={{ mb: 1 }}>
              {project.displayName}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Chip
                label={project.status}
                size="small"
                color={project.status === 'ready' ? 'success' : 'default'}
              />
              <Chip label="Kit Application" size="small" variant="outlined" />
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* Project Info */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold' }}>
              <InfoIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
              Information
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <FolderIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText primary="Project ID" secondary={project.id} />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CodeIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Configuration File"
                  secondary={project.kitFile}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <DateIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Last Modified"
                  secondary={formatDate(project.lastModified)}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <FolderIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Location"
                  secondary={
                    <Tooltip title={project.path}>
                      <Typography
                        variant="caption"
                        sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          display: 'block',
                        }}
                      >
                        {project.path}
                      </Typography>
                    </Tooltip>
                  }
                />
              </ListItem>
            </List>
          </Box>
        </Box>

        {/* Footer Actions */}
        <Box
          sx={{
            p: 2,
            borderTop: 1,
            borderColor: 'divider',
            backgroundColor: '#252526',
            display: 'flex',
            gap: 1,
          }}
        >
          <Button
            fullWidth
            variant="contained"
            color="primary"
            size="large"
            startIcon={<CodeIcon />}
            onClick={() => onOpenProject && onOpenProject(project)}
          >
            Open in Editor
          </Button>
          <Tooltip title="Build project">
            <IconButton color="primary" size="large">
              <BuildIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Run project">
            <IconButton color="success" size="large">
              <RunIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
    );
  }

  return null;
};

export default TemplateDetailPanel;
