import React from 'react';

export interface ProgressBarProps {
  progress: number; // 0-100
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-3',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  showLabel = true,
  size = 'md',
  className = '',
}) => {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm text-gray-400">Progress</span>
          <span className="text-sm font-medium text-white">{Math.round(clampedProgress)}%</span>
        </div>
      )}
      <div className={`w-full bg-dark-bg rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <div
          className="h-full bg-nvidia-green transition-all duration-300 ease-out"
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;

