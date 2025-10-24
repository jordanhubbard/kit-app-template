/**
 * Workflow Breadcrumbs
 * Navigation breadcrumbs showing current location in workflow
 */

import React from 'react';
import { Box, Breadcrumbs, Link, IconButton, Tooltip, Paper } from '@mui/material';
import {
  NavigateBefore as BackIcon,
  NavigateNext as ForwardIcon,
  Home as HomeIcon,
  Code as CodeIcon,
  PlayArrow as PreviewIcon,
} from '@mui/icons-material';
import { WorkflowStep } from '../../types/workflow';

interface WorkflowBreadcrumbsProps {
  step: WorkflowStep;
  selectedTemplate: string | null;
  selectedProject: string | null;
  canGoBack: boolean;
  canGoForward: boolean;
  onNavigateBack: () => void;
  onNavigateForward: () => void;
  onNavigateHome: () => void;
  onNavigateToStep: (step: WorkflowStep) => void;
}

const WorkflowBreadcrumbs: React.FC<WorkflowBreadcrumbsProps> = ({
  step,
  selectedTemplate,
  selectedProject,
  canGoBack,
  canGoForward,
  onNavigateBack,
  onNavigateForward,
  onNavigateHome,
  onNavigateToStep,
}) => {
  const getStepLabel = () => {
    if (selectedProject) return selectedProject;
    if (selectedTemplate) return selectedTemplate;
    return 'Templates';
  };

  return (
    <Paper
      elevation={1}
      sx={{
        px: 2,
        py: 1,
        borderRadius: 0,
        borderBottom: 1,
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        gap: 2,
      }}
    >
      {/* Navigation Controls */}
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        <Tooltip title="Back">
          <span>
            <IconButton
              size="small"
              onClick={onNavigateBack}
              disabled={!canGoBack}
            >
              <BackIcon />
            </IconButton>
          </span>
        </Tooltip>
        <Tooltip title="Forward">
          <span>
            <IconButton
              size="small"
              onClick={onNavigateForward}
              disabled={!canGoForward}
            >
              <ForwardIcon />
            </IconButton>
          </span>
        </Tooltip>
        <Tooltip title="Home">
          <IconButton size="small" onClick={onNavigateHome}>
            <HomeIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Breadcrumb Trail */}
      <Breadcrumbs>
        <Link
          component="button"
          underline="hover"
          color={step === 'browse' ? 'primary' : 'inherit'}
          onClick={() => onNavigateToStep('browse')}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            fontWeight: step === 'browse' ? 'bold' : 'normal',
          }}
        >
          <HomeIcon fontSize="small" />
          {getStepLabel()}
        </Link>

        {(step === 'edit' || step === 'preview') && (
          <Link
            component="button"
            underline="hover"
            color={step === 'edit' ? 'primary' : 'inherit'}
            onClick={() => onNavigateToStep('edit')}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              fontWeight: step === 'edit' ? 'bold' : 'normal',
            }}
          >
            <CodeIcon fontSize="small" />
            Edit & Build
          </Link>
        )}

        {step === 'preview' && (
          <Link
            component="button"
            underline="hover"
            color="primary"
            onClick={() => onNavigateToStep('preview')}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              fontWeight: 'bold',
            }}
          >
            <PreviewIcon fontSize="small" />
            Preview
          </Link>
        )}
      </Breadcrumbs>
    </Paper>
  );
};

export default WorkflowBreadcrumbs;
