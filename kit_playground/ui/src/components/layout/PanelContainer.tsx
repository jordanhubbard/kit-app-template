import React, { useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
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
  const {
    panels,
    activePanel,
    scrollLeft,
    scrollRight,
    canScrollLeft,
    canScrollRight,
    checkCapacityAndRetire,
  } = usePanelStore();

  const containerRef = useRef<HTMLDivElement>(null);

  // Only render visible panels
  const visiblePanels = panels.filter(p => p.isVisible);

  // Check capacity on window resize
  useEffect(() => {
    const handleResize = () => {
      checkCapacityAndRetire();
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [checkCapacityAndRetire]);

  const showLeftNav = canScrollLeft();
  const showRightNav = canScrollRight();

  // Debug logging
  useEffect(() => {
    console.log('[PanelContainer] Navigation state:', {
      showLeftNav,
      showRightNav,
      visiblePanelCount: visiblePanels.length,
      visiblePanelTypes: visiblePanels.map(p => p.type),
    });
  }, [showLeftNav, showRightNav, visiblePanels]);

  return (
    <div className="relative w-full h-full">
      {/* Left navigation arrow */}
      {showLeftNav && (
        <button
          onClick={scrollLeft}
          className="
            absolute left-0 top-1/2 -translate-y-1/2 z-50
            w-10 h-20
            bg-nvidia-green/90 hover:bg-nvidia-green
            text-white
            flex items-center justify-center
            transition-all duration-200
            shadow-lg hover:shadow-xl
            rounded-r-lg
          "
          title="Show previous panels"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
      )}

      {/* Right navigation arrow */}
      {showRightNav && (
        <button
          onClick={scrollRight}
          className="
            absolute right-0 top-1/2 -translate-y-1/2 z-50
            w-10 h-20
            bg-nvidia-green/90 hover:bg-nvidia-green
            text-white
            flex items-center justify-center
            transition-all duration-200
            shadow-lg hover:shadow-xl
            rounded-l-lg
          "
          title="Show next panels"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      )}

      {/* Panel container with smooth transitions */}
      <div
        ref={containerRef}
        className={`
          panel-container
          flex flex-row
          w-full h-full
          bg-bg-dark
          overflow-hidden
          ${className}
        `}
        style={{
          transition: 'transform 0.3s ease-in-out',
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
