import React from 'react';
import { Panel } from './Panel';
import { usePanelStore } from '../../stores/panelStore';

interface PanelContainerProps {
  className?: string;
  renderPanel: (panelId: string, panelType: string, panelData: any) => React.ReactNode;
}

/**
 * PanelContainer
 *
 * Main container for the panel-based layout system.
 * Manages the rendering and layout of all panels.
 *
 * Usage:
 * <PanelContainer
 *   renderPanel={(id, type, data) => {
 *     switch(type) {
 *       case 'template-browser': return <TemplateBrowser {...data} />;
 *       case 'template-detail': return <TemplateDetail {...data} />;
 *       default: return <div>Unknown panel type</div>;
 *     }
 *   }}
 * />
 */
export const PanelContainer: React.FC<PanelContainerProps> = ({
  className = '',
  renderPanel,
}) => {
  const { panels, activePanel } = usePanelStore();

  // Only render visible panels
  const visiblePanels = panels.filter(p => p.isVisible);

  return (
    <div
      className={`
        panel-container
        flex flex-row
        w-full h-full
        bg-bg-dark
        overflow-x-auto overflow-y-hidden
        ${className}
      `}
      style={{
        // Disable default scrollbar styling for custom scrollbar
        scrollbarWidth: 'thin',
        scrollbarColor: 'rgba(118, 185, 0, 0.5) rgba(0, 0, 0, 0.3)',
      }}
    >
      {visiblePanels.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-text-muted">
          <p>No panels open</p>
        </div>
      ) : (
        visiblePanels.map((panel, index) => (
          <Panel
            key={panel.id}
            panel={panel}
            isActive={panel.id === activePanel}
            isLast={index === visiblePanels.length - 1}
          >
            {renderPanel(panel.id, panel.type, panel.data)}
          </Panel>
        ))
      )}
    </div>
  );
};

/**
 * PanelPlaceholder
 *
 * A placeholder component for when a panel type is not yet implemented.
 *
 * Usage:
 * <PanelPlaceholder type="template-detail" />
 */
interface PanelPlaceholderProps {
  type: string;
  message?: string;
}

export const PanelPlaceholder: React.FC<PanelPlaceholderProps> = ({
  type,
  message,
}) => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
      <div className="text-6xl mb-4">🚧</div>
      <h3 className="text-xl font-semibold text-text-primary mb-2">
        Panel Under Construction
      </h3>
      <p className="text-text-secondary mb-4">
        {message || `The "${type}" panel is not yet implemented.`}
      </p>
      <p className="text-text-muted text-sm">
        This panel will be available in a future update.
      </p>
    </div>
  );
};
