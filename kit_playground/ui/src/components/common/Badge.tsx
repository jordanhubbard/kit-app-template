import React from 'react';

export type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info' | 'nvidia';
export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  icon?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-bg-card text-text-primary border border-border-subtle',
  success: 'bg-status-success/10 text-status-success border border-status-success/30',
  warning: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30',
  error: 'bg-status-error/10 text-status-error border border-status-error/30',
  info: 'bg-status-info/10 text-status-info border border-status-info/30',
  nvidia: 'bg-nvidia-green/10 text-nvidia-green border border-nvidia-green/30',
};

const sizeClasses: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
  lg: 'px-4 py-1.5 text-base',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  icon,
  className = '',
  onClick,
}) => {
  const Component = onClick ? 'button' : 'span';

  return (
    <Component
      onClick={onClick}
      className={`
        inline-flex items-center gap-1.5
        rounded font-medium
        transition-colors
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${onClick ? 'cursor-pointer hover:opacity-80' : ''}
        ${className}
      `}
    >
      {icon}
      {children}
    </Component>
  );
};

export default Badge;

