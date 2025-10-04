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
  Divider,
  Chip,
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
} from '@mui/icons-material';
import { WorkflowNode } from '../../types/workflow';

interface WorkflowSidebarProps {
  templates: WorkflowNode[];
  projects: WorkflowNode[];
  selectedId: string | null;
  onSelectNode: (node: WorkflowNode) => void;
}

const WorkflowSidebar: React.FC<WorkflowSidebarProps> = ({
  templates,
  projects,
  selectedId,
  onSelectNode,
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

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

  const renderNode = (node: WorkflowNode, depth: number = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedId === node.id;
    const hasChildren = node.children && node.children.length > 0;

    return (
      <React.Fragment key={node.id}>
        <ListItem disablePadding>
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
              {node.children!.map(child => renderNode(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
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
      <Box>
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="subtitle2" fontWeight="bold">
            Templates
          </Typography>
          <Chip label={templates.length} size="small" />
        </Box>
        <List dense>
          {templates.map(node => renderNode(node))}
        </List>
      </Box>

      <Divider />

      {/* Projects Section */}
      <Box sx={{ flex: 1 }}>
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="subtitle2" fontWeight="bold">
            Projects
          </Typography>
          <Chip label={projects.length} size="small" />
        </Box>
        {projects.length === 0 ? (
          <Box
            sx={{
              p: 2,
              textAlign: 'center',
              color: 'text.secondary',
            }}
          >
            <Typography variant="body2">
              No projects yet
            </Typography>
            <Typography variant="caption">
              Create from a template
            </Typography>
          </Box>
        ) : (
          <List dense>
            {projects.map(node => renderNode(node))}
          </List>
        )}
      </Box>
    </Box>
  );
};

export default WorkflowSidebar;
