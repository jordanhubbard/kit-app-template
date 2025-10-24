/**
 * Sliding Panel Layout
 * Horizontal sliding panels that reveal progressively based on workflow state
 */

import React, { ReactNode } from 'react';
import { Box } from '@mui/material';
import { WorkflowStep } from '../../types/workflow';

interface SlidingPanelLayoutProps {
  step: WorkflowStep;
  browsePanel: ReactNode;
  editPanel: ReactNode;
  previewPanel: ReactNode;
}

const SlidingPanelLayout: React.FC<SlidingPanelLayoutProps> = ({
  step,
  browsePanel,
  editPanel,
  previewPanel,
}) => {
  // Calculate transform based on current step
  const getTransform = () => {
    switch (step) {
      case 'browse':
        return 'translateX(0%)';
      case 'edit':
        return 'translateX(-33.333%)';
      case 'preview':
        return 'translateX(-66.666%)';
      default:
        return 'translateX(0%)';
    }
  };

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          width: '300%', // 3 panels
          height: '100%',
          transform: getTransform(),
          transition: 'transform 0.4s cubic-bezier(0.4, 0.0, 0.2, 1)',
        }}
      >
        {/* Browse Panel */}
        <Box
          sx={{
            width: '33.333%',
            height: '100%',
            flexShrink: 0,
            overflow: 'hidden',
          }}
        >
          {browsePanel}
        </Box>

        {/* Edit Panel */}
        <Box
          sx={{
            width: '33.333%',
            height: '100%',
            flexShrink: 0,
            overflow: 'hidden',
          }}
        >
          {editPanel}
        </Box>

        {/* Preview Panel */}
        <Box
          sx={{
            width: '33.333%',
            height: '100%',
            flexShrink: 0,
            overflow: 'hidden',
          }}
        >
          {previewPanel}
        </Box>
      </Box>
    </Box>
  );
};

export default SlidingPanelLayout;
