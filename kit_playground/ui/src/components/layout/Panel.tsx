import React from 'react';
import { PanelHeader } from './PanelHeader';
import { PanelResizer } from './PanelResizer';
import { usePanelStore, type PanelState } from '../../stores/panelStore';

interface PanelProps {
  panel: PanelState;
  isActive: boolean;
  isLast: boolean;
  children: React.ReactNode;
  className?: string;
}

/**
 * Panel
 *
 * A resizable panel that can be opened, closed, and resized.
 * Contains a header and content area.
 *
 * Usage:
 * <Panel panel={panelState} isActive={true} isLast={false}>
 *   <PanelContent />
 * </Panel>
 */
export const Panel: React.FC<PanelProps> = ({
  panel,
  isActive,
  isLast,
  children,
  className = '',
}) => {
  const { closePanel, resizePanel, setActivePanel } = usePanelStore();

  const handleClose = () => {
    if (panel.canClose) {
      closePanel(panel.id);
    }
  };

  const handleResize = (delta: number) => {
    if (panel.canResize) {
      const newWidth = panel.width + delta;
      resizePanel(panel.id, newWidth);
    }
  };

  const handleClick = () => {
    if (!isActive) {
      setActivePanel(panel.id);
    }
  };

  return (
    <div
      className={`
        panel
        flex flex-row
        transition-all duration-200 ease-in-out
        ${isActive ? 'z-10' : 'z-0'}
        ${panel.width === 0 ? 'flex-1' : ''}
        ${className}
      `}
      style={{
        width: panel.width > 0 ? `${panel.width}px` : undefined,
        minWidth: `${panel.minWidth}px`,
        maxWidth: panel.maxWidth ? `${panel.maxWidth}px` : undefined,
      }}
      onClick={handleClick}
      role="region"
      aria-label={panel.title}
    >
      {/* Panel content */}
      <div className="flex-1 flex flex-col bg-bg-panel overflow-hidden">
        {/* Header */}
        <PanelHeader
          title={panel.title}
          canClose={panel.canClose}
          isActive={isActive}
          onClose={handleClose}
        />

        {/* Content */}
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </div>

      {/* Resizer (not shown for last panel) */}
      {!isLast && panel.canResize && (
        <PanelResizer onResize={handleResize} />
      )}
    </div>
  );
};
