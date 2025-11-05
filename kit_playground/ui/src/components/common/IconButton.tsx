import React from 'react';

export type IconButtonVariant = 'ghost' | 'primary' | 'danger' | 'secondary';
export type IconButtonSize = 'sm' | 'md' | 'lg';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  variant?: IconButtonVariant;
  size?: IconButtonSize;
  loading?: boolean;
  tooltip?: string;
}

const variantClasses: Record<IconButtonVariant, string> = {
  ghost: 'bg-transparent hover:bg-bg-card-hover text-text-secondary hover:text-text-primary',
  primary: 'bg-nvidia-green hover:bg-nvidia-green-dark text-white',
  danger: 'bg-transparent hover:bg-status-error/10 text-status-error hover:text-status-error',
  secondary: 'bg-bg-card hover:bg-bg-card-hover text-text-primary border border-border-subtle',
};

const sizeClasses: Record<IconButtonSize, { button: string; icon: string }> = {
  sm: { button: 'p-1.5', icon: 'w-3 h-3' },
  md: { button: 'p-2', icon: 'w-4 h-4' },
  lg: { button: 'p-3', icon: 'w-5 h-5' },
};

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  variant = 'ghost',
  size = 'md',
  loading = false,
  tooltip,
  className = '',
  disabled,
  ...props
}) => {
  const isDisabled = disabled || loading;

  return (
    <button
      className={`
        inline-flex items-center justify-center
        rounded transition-all duration-200
        ${variantClasses[variant]}
        ${sizeClasses[size].button}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-110 active:scale-95'}
        ${className}
      `}
      disabled={isDisabled}
      title={tooltip}
      {...props}
    >
      {loading ? (
        <svg
          className={`animate-spin ${sizeClasses[size].icon}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : (
        <div className={sizeClasses[size].icon}>{icon}</div>
      )}
    </button>
  );
};

export default IconButton;

