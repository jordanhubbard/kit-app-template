import React from 'react';
import { ChevronDown } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  description?: string;
  badge?: string;
  disabled?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  label?: string;
  error?: string;
  helperText?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  onChange,
  label,
  error,
  helperText,
  placeholder,
  disabled = false,
  className = '',
}) => {
  return (
    <div className={`w-full ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-semibold text-text-primary mb-2">
          {label}
        </label>
      )}

      {/* Select Wrapper */}
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className={`
            w-full px-4 py-3 pr-10 rounded-lg
            bg-bg-card border
            ${error ? 'border-status-error' : 'border-border-subtle'}
            text-text-primary
            focus:outline-none focus:ring-2 focus:ring-nvidia-green focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all
            appearance-none
            cursor-pointer
          `}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
              {option.badge && ` (${option.badge})`}
            </option>
          ))}
        </select>

        {/* Chevron Icon */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-text-muted">
          <ChevronDown className="w-5 h-5" />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-2 text-sm text-status-error">{error}</p>
      )}

      {/* Helper Text */}
      {helperText && !error && (
        <p className="mt-2 text-xs text-text-muted">{helperText}</p>
      )}
    </div>
  );
};

export default Select;

