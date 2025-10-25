import React from 'react';
import { X } from 'lucide-react';

interface PanelHeaderProps {
  title: string;
  icon?: React.ReactNode;
  canClose?: boolean;
  isActive?: boolean;
  onClose?: () => void;
  actions?: React.ReactNode;
  className?: string;
}

/**
 * PanelHeader
 *
 * Header component for panels with title, actions, and close button.
 *
 * Usage:
 * <PanelHeader
 *   title="Templates"
 *   icon={<IconComponent />}
 *   canClose={true}
 *   onClose={() => handleClose()}
 *   actions={<CustomActions />}
 * />
 */
export const PanelHeader: React.FC<PanelHeaderProps> = ({
  title,
  icon,
  canClose = true,
  isActive = false,
  onClose,
  actions,
  className = '',
}) => {
  return (
    <div
      className={`
        flex items-center justify-between
        h-12 px-4
        border-b border-border-panel
        ${isActive ? 'bg-bg-panel border-l-2 border-l-nvidia-green' : 'bg-bg-dark'}
        transition-colors
        ${className}
      `}
    >
      {/* Left: Icon + Title */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
        {icon && (
          <div className="flex-shrink-0 text-text-secondary">
            {icon}
          </div>
        )}
        <h2
          className="text-sm font-semibold text-text-primary truncate"
          title={title}
        >
          {title}
        </h2>
      </div>

      {/* Right: Actions + Close */}
      <div className="flex items-center gap-1 ml-2 flex-shrink-0">
        {/* Custom actions */}
        {actions && (
          <div className="flex items-center gap-1">
            {actions}
          </div>
        )}

        {/* Close button */}
        {canClose && onClose && (
          <button
            onClick={onClose}
            className="
              p-1.5 rounded
              text-text-secondary hover:text-text-primary
              hover:bg-bg-card
              transition-colors
              group
            "
            title="Close panel"
            aria-label="Close panel"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * HeaderActionButton
 *
 * A styled button for panel header actions.
 *
 * Usage:
 * <HeaderActionButton icon={<IconComponent />} onClick={handleClick} title="Action" />
 */
interface HeaderActionButtonProps {
  icon: React.ReactNode;
  onClick: () => void;
  title?: string;
  className?: string;
  disabled?: boolean;
}

export const HeaderActionButton: React.FC<HeaderActionButtonProps> = ({
  icon,
  onClick,
  title,
  className = '',
  disabled = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`
        p-1.5 rounded
        text-text-secondary hover:text-text-primary
        hover:bg-bg-card
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-colors
        ${className}
      `}
    >
      {icon}
    </button>
  );
};
