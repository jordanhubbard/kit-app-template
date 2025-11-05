import React from 'react';
import { Button } from './Button';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = '',
}) => {
  return (
    <div
      className={`
        flex flex-col items-center justify-center
        py-12 px-4 text-center
        ${className}
      `}
    >
      {/* Icon */}
      {icon && (
        <div className="text-text-muted mb-4 opacity-50">
          {icon}
        </div>
      )}

      {/* Title */}
      <h3 className="text-lg font-semibold text-text-primary mb-2">
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className="text-text-secondary text-sm max-w-md mb-6">
          {description}
        </p>
      )}

      {/* Action Button */}
      {action && (
        <Button
          onClick={action.onClick}
          icon={action.icon}
          variant="primary"
          size="md"
        >
          {action.label}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;

