import React, { useCallback, useState } from 'react';

interface PanelResizerProps {
  onResize: (delta: number) => void;
  className?: string;
}

/**
 * PanelResizer
 * 
 * A draggable vertical divider between panels that allows resizing.
 * 
 * Usage:
 * <PanelResizer onResize={(delta) => handleResize(panelId, delta)} />
 */
export const PanelResizer: React.FC<PanelResizerProps> = ({ onResize, className = '' }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setStartX(e.clientX);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging) return;
      
      const delta = e.clientX - startX;
      onResize(delta);
      setStartX(e.clientX);
    },
    [isDragging, startX, onResize]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div
      className={`
        relative w-1 cursor-col-resize group
        flex items-center justify-center
        hover:bg-nvidia-green/20 transition-colors
        ${isDragging ? 'bg-nvidia-green/40' : 'bg-border-panel'}
        ${className}
      `}
      onMouseDown={handleMouseDown}
      role="separator"
      aria-orientation="vertical"
      aria-label="Panel resizer"
    >
      {/* Visual handle indicator (shows on hover) */}
      <div 
        className="
          absolute inset-y-0 left-1/2 -translate-x-1/2
          w-1 h-full
          opacity-0 group-hover:opacity-100
          transition-opacity
          pointer-events-none
        "
      >
        <div className="w-full h-full bg-nvidia-green/50" />
      </div>
      
      {/* Hit area for easier grabbing */}
      <div className="absolute inset-y-0 -left-2 w-5" />
    </div>
  );
};

