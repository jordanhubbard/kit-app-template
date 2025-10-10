/**
 * Workflow Sidebar
 * Tree navigation for templates, projects, and workflow states
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  ExpandLess,
  ExpandMore,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as TemplateIcon,
  Code as ProjectIcon,
  Apps as AppsIcon,
  Extension as ExtensionIcon,
  Cloud as CloudIcon,
  FolderSpecial as BrowseIcon,
  Refresh as RefreshIcon,
  KeyboardArrowDown as CollapseIcon,
  KeyboardArrowRight as ExpandIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { WorkflowNode } from '../../types/workflow';
import DirectoryBrowserDialog from '../dialogs/DirectoryBrowserDialog';

interface WorkflowSidebarProps {
  templates: WorkflowNode[];
  projects: WorkflowNode[];
  selectedId: string | null;
  templatesPath: string;
  projectsPath: string;
  onSelectNode: (node: WorkflowNode) => void;
  onTemplatesPathChange: (path: string) => void;
  onProjectsPathChange: (path: string) => void;
  onRefreshTemplates: () => void;
  onRefreshProjects: () => void;
  onDeleteProject?: (projectId: string) => void;
}

const WorkflowSidebar: React.FC<WorkflowSidebarProps> = ({
  templates,
  projects,
  selectedId,
  templatesPath,
  projectsPath,
  onSelectNode,
  onTemplatesPathChange,
  onProjectsPathChange,
  onRefreshTemplates,
  onRefreshProjects,
  onDeleteProject,
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [templatesCollapsed, setTemplatesCollapsed] = useState(false);
  const [projectsCollapsed, setProjectsCollapsed] = useState(false);
  const [editingTemplatesPath, setEditingTemplatesPath] = useState(false);
  const [editingProjectsPath, setEditingProjectsPath] = useState(false);
  const [tempTemplatesPath, setTempTemplatesPath] = useState(templatesPath);
  const [tempProjectsPath, setTempProjectsPath] = useState(projectsPath);
  const [browserOpen, setBrowserOpen] = useState(false);
  const [browserType, setBrowserType] = useState<'templates' | 'projects'>('templates');

  const toggleExpand = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const getNodeIcon = (node: WorkflowNode, isExpanded: boolean) => {
    if (node.type === 'category') {
      return isExpanded ? <FolderOpenIcon /> : <FolderIcon />;
    }
    if (node.type === 'project') {
      return <ProjectIcon />;
    }
    // Template type icons
    if (node.id.includes('application')) return <AppsIcon />;
    if (node.id.includes('extension')) return <ExtensionIcon />;
    if (node.id.includes('service')) return <CloudIcon />;
    return <TemplateIcon />;
  };

  const renderNode = (node: WorkflowNode, depth: number = 0, isProject: boolean = false) => {
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedId === node.id;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <React.Fragment key={node.id}>
        <ListItem
          disablePadding
          secondaryAction={
            isProject && onDeleteProject ? (
              <Tooltip title="Delete project">
                <IconButton
                  edge="end"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Are you sure you want to delete "${node.label}"?`)) {
                      onDeleteProject(node.id);
                    }
                  }}
                  sx={{
                    color: 'text.secondary',
                    '&:hover': {
                      color: 'error.main',
                    },
                  }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ) : null
          }
        >
          <ListItemButton
            selected={isSelected}
            onClick={() => {
              if (hasChildren) {
                toggleExpand(node.id);
              }
              onSelectNode(node);
            }}
            sx={{
              pl: 2 + depth * 2,
              '&.Mui-selected': {
                backgroundColor: 'primary.dark',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>
              {getNodeIcon(node, isExpanded)}
            </ListItemIcon>
            <ListItemText
              primary={node.label}
              primaryTypographyProps={{
                fontSize: 14,
                fontWeight: isSelected ? 'bold' : 'normal',
              }}
            />
            {hasChildren && (
              isExpanded ? <ExpandLess /> : <ExpandMore />
            )}
          </ListItemButton>
        </ListItem>

        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {node.children!.map(child => renderNode(child, depth + 1, isProject))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  // Path section component
  const PathSelector: React.FC<{
    path: string;
    tempPath: string;
    editing: boolean;
    onBrowse: () => void;
    onRefresh: () => void;
    onStartEdit: () => void;
    onPathChange: (path: string) => void;
    onSavePath: () => void;
    onCancelEdit: () => void;
    setTempPath: (path: string) => void;
  }> = ({ path, tempPath, editing, onBrowse, onRefresh, onStartEdit, onPathChange, onSavePath, onCancelEdit, setTempPath }) => {
    if (editing) {
      return (
        <Box sx={{ px: 2, py: 1 }}>
          <TextField
            fullWidth
            size="small"
            value={tempPath}
            onChange={(e) => setTempPath(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                onPathChange(tempPath);
                onSavePath();
              } else if (e.key === 'Escape') {
                onCancelEdit();
              }
            }}
            onBlur={() => {
              onPathChange(tempPath);
              onSavePath();
            }}
            autoFocus
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <FolderIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Box>
      );
    }

    return (
      <Box
        sx={{
          px: 2,
          py: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          backgroundColor: '#2a2a2a',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Tooltip title={path}>
          <Typography
            variant="caption"
            sx={{
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              cursor: 'pointer',
              '&:hover': { color: 'primary.main' },
            }}
            onClick={onStartEdit}
          >
            {path}
          </Typography>
        </Tooltip>
        <Tooltip title="Browse directory">
          <IconButton size="small" onClick={onBrowse}>
            <BrowseIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Refresh">
          <IconButton size="small" onClick={onRefresh}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    );
  };

  return (
    <Box
      sx={{
        width: 280,
        height: '100%',
        borderRight: 1,
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Templates Section */}
      <Box sx={{ borderBottom: 2, borderColor: 'divider' }}>
        {/* Templates Header */}
        <Box
          sx={{
            px: 2,
            py: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#252526',
            cursor: 'pointer',
            '&:hover': { backgroundColor: '#2a2a2a' },
          }}
          onClick={() => setTemplatesCollapsed(!templatesCollapsed)}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {templatesCollapsed ? (
              <ExpandIcon fontSize="small" />
            ) : (
              <CollapseIcon fontSize="small" />
            )}
            <Typography variant="subtitle2" fontWeight="bold">
              Templates
            </Typography>
          </Box>
          {templates.length > 0 && <Chip label={templates.length} size="small" />}
        </Box>

        {/* Templates Path Selector */}
        {!templatesCollapsed && (
          <PathSelector
            path={templatesPath}
            tempPath={tempTemplatesPath}
            editing={editingTemplatesPath}
            onBrowse={() => {
              setBrowserType('templates');
              setBrowserOpen(true);
            }}
            onRefresh={onRefreshTemplates}
            onStartEdit={() => setEditingTemplatesPath(true)}
            onPathChange={onTemplatesPathChange}
            onSavePath={() => setEditingTemplatesPath(false)}
            onCancelEdit={() => {
              setTempTemplatesPath(templatesPath);
              setEditingTemplatesPath(false);
            }}
            setTempPath={setTempTemplatesPath}
          />
        )}

        {/* Templates List */}
        {!templatesCollapsed && (
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {templates.length === 0 ? (
              <Box
                sx={{
                  p: 3,
                  textAlign: 'center',
                  color: 'text.secondary',
                }}
              >
                <Typography variant="body2" sx={{ mb: 1 }}>
                  No templates found
                </Typography>
                <Typography variant="caption">
                  Check the templates path
                </Typography>
              </Box>
            ) : (
              <List dense>
                {templates.map(node => renderNode(node))}
              </List>
            )}
          </Box>
        )}
      </Box>

      {/* Projects Section */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Projects Header */}
        <Box
          sx={{
            px: 2,
            py: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#252526',
            cursor: 'pointer',
            '&:hover': { backgroundColor: '#2a2a2a' },
          }}
          onClick={() => setProjectsCollapsed(!projectsCollapsed)}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {projectsCollapsed ? (
              <ExpandIcon fontSize="small" />
            ) : (
              <CollapseIcon fontSize="small" />
            )}
            <Typography variant="subtitle2" fontWeight="bold">
              My Projects
            </Typography>
          </Box>
          {projects.length > 0 && <Chip label={projects.length} size="small" />}
        </Box>

        {/* Projects Path Selector */}
        {!projectsCollapsed && (
          <PathSelector
            path={projectsPath}
            tempPath={tempProjectsPath}
            editing={editingProjectsPath}
            onBrowse={() => {
              setBrowserType('projects');
              setBrowserOpen(true);
            }}
            onRefresh={onRefreshProjects}
            onStartEdit={() => setEditingProjectsPath(true)}
            onPathChange={onProjectsPathChange}
            onSavePath={() => setEditingProjectsPath(false)}
            onCancelEdit={() => {
              setTempProjectsPath(projectsPath);
              setEditingProjectsPath(false);
            }}
            setTempPath={setTempProjectsPath}
          />
        )}

        {/* Projects List */}
        {!projectsCollapsed && (
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            {projects.length === 0 ? (
              <Box
                sx={{
                  p: 3,
                  textAlign: 'center',
                  color: 'text.secondary',
                }}
              >
                <Typography variant="body2" sx={{ mb: 1 }}>
                  No projects yet
                </Typography>
                <Typography variant="caption">
                  Browse templates and click<br/>"Create Project" to get started
                </Typography>
              </Box>
            ) : (
              <List dense>
                {projects.map(node => renderNode(node, 0, true))}
              </List>
            )}
          </Box>
        )}
      </Box>

      {/* Directory Browser Dialog */}
      <DirectoryBrowserDialog
        open={browserOpen}
        onClose={() => setBrowserOpen(false)}
        onSelect={(path) => {
          if (browserType === 'templates') {
            onTemplatesPathChange(path);
          } else {
            onProjectsPathChange(path);
          }
          setBrowserOpen(false);
        }}
        initialPath={browserType === 'templates' ? templatesPath : projectsPath}
      />
    </Box>
  );
};

export default WorkflowSidebar;
