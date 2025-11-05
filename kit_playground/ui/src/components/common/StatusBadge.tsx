import React from 'react';
import { CheckCircle, XCircle, Loader, Clock, AlertCircle, Package } from 'lucide-react';

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type ProjectStatus = 'created' | 'built' | 'running' | 'failed';
export type Status = JobStatus | ProjectStatus;

export interface StatusBadgeProps {
  status: Status;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showLabel?: boolean;
  className?: string;
}

interface StatusConfig {
  icon: React.ReactNode;
  color: string;
  bg: string;
  label: string;
}

const getStatusConfig = (status: Status, size: 'sm' | 'md' | 'lg'): StatusConfig => {
  const iconSize = size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5';

  switch (status) {
    case 'pending':
      return {
        icon: <Clock className={iconSize} />,
        color: 'text-text-muted',
        bg: 'bg-text-muted/10',
        label: 'Pending',
      };
    case 'running':
      return {
        icon: <Loader className={`${iconSize} animate-spin`} />,
        color: 'text-status-info',
        bg: 'bg-status-info/10',
        label: 'Running',
      };
    case 'completed':
      return {
        icon: <CheckCircle className={iconSize} />,
        color: 'text-status-success',
        bg: 'bg-status-success/10',
        label: 'Completed',
      };
    case 'failed':
      return {
        icon: <XCircle className={iconSize} />,
        color: 'text-status-error',
        bg: 'bg-status-error/10',
        label: 'Failed',
      };
    case 'cancelled':
      return {
        icon: <AlertCircle className={iconSize} />,
        color: 'text-text-muted',
        bg: 'bg-text-muted/10',
        label: 'Cancelled',
      };
    case 'created':
      return {
        icon: <Clock className={iconSize} />,
        color: 'text-yellow-400',
        bg: 'bg-yellow-500/20',
        label: 'New',
      };
    case 'built':
      return {
        icon: <Package className={iconSize} />,
        color: 'text-blue-400',
        bg: 'bg-blue-500/20',
        label: 'Built',
      };
    default:
      return {
        icon: <Clock className={iconSize} />,
        color: 'text-text-muted',
        bg: 'bg-text-muted/10',
        label: 'Unknown',
      };
  }
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showIcon = true,
  showLabel = true,
  className = '',
}) => {
  const config = getStatusConfig(status, size);
  
  const sizeClasses = {
    sm: 'px-1.5 py-0.5 text-xs',
    md: 'px-2 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 rounded font-medium
        ${config.bg} ${config.color}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {showIcon && config.icon}
      {showLabel && <span>{config.label}</span>}
    </div>
  );
};

export default StatusBadge;

