/**
 * Centralized icon mapping for template types
 * Ensures consistent iconography across the UI
 */
import { Monitor, Package, Server, Zap } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type TemplateType = 'application' | 'extension' | 'microservice' | 'component';

/**
 * Icon configuration for each template type
 */
export const TEMPLATE_TYPE_ICONS: Record<TemplateType, {
  Icon: LucideIcon;
  color: string;
  bgColor: string;
  label: string;
}> = {
  application: {
    Icon: Monitor,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    label: 'Application'
  },
  extension: {
    Icon: Package,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10',
    label: 'Extension'
  },
  microservice: {
    Icon: Server,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    label: 'Service'
  },
  component: {
    Icon: Package,
    color: 'text-gray-400',
    bgColor: 'bg-gray-500/10',
    label: 'Component'
  }
};

/**
 * Streaming indicator configuration
 */
export const STREAMING_ICON = {
  Icon: Zap,
  color: 'text-yellow-400',
  bgColor: 'bg-yellow-500/10',
  label: 'Kit App Streaming'
};

/**
 * Get icon component for a template type
 */
export function getTemplateTypeIcon(type: TemplateType | string): LucideIcon {
  const normalizedType = (type || 'application').toLowerCase() as TemplateType;
  return TEMPLATE_TYPE_ICONS[normalizedType]?.Icon || Monitor;
}

/**
 * Get color classes for a template type
 */
export function getTemplateTypeColors(type: TemplateType | string): {
  color: string;
  bgColor: string;
} {
  const normalizedType = (type || 'application').toLowerCase() as TemplateType;
  return {
    color: TEMPLATE_TYPE_ICONS[normalizedType]?.color || 'text-blue-400',
    bgColor: TEMPLATE_TYPE_ICONS[normalizedType]?.bgColor || 'bg-blue-500/10'
  };
}

/**
 * Get human-readable label for a template type
 */
export function getTemplateTypeLabel(type: TemplateType | string): string {
  const normalizedType = (type || 'application').toLowerCase() as TemplateType;
  return TEMPLATE_TYPE_ICONS[normalizedType]?.label || 'Application';
}

/**
 * Component: Template type badge with icon
 */
interface TemplateTypeBadgeProps {
  type: TemplateType | string;
  showLabel?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function TemplateTypeBadge({
  type,
  showLabel = true,
  className = '',
  size = 'md'
}: TemplateTypeBadgeProps) {
  const Icon = getTemplateTypeIcon(type);
  const { color, bgColor } = getTemplateTypeColors(type);
  const label = getTemplateTypeLabel(type);

  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  const paddingClasses = {
    sm: 'px-1.5 py-0.5',
    md: 'px-2 py-1',
    lg: 'px-3 py-1.5'
  };

  const textClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 rounded
        ${bgColor} ${paddingClasses[size]}
        ${className}
      `}
      title={label}
    >
      <Icon className={`${sizeClasses[size]} ${color}`} />
      {showLabel && (
        <span className={`font-medium ${color} ${textClasses[size]}`}>
          {label}
        </span>
      )}
    </div>
  );
}

/**
 * Component: Streaming indicator badge
 */
interface StreamingBadgeProps {
  showLabel?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function StreamingBadge({
  showLabel = false,
  className = '',
  size = 'sm'
}: StreamingBadgeProps) {
  const { Icon, color, bgColor, label } = STREAMING_ICON;

  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  const paddingClasses = {
    sm: 'px-1 py-0.5',
    md: 'px-1.5 py-0.5',
    lg: 'px-2 py-1'
  };

  const textClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div
      className={`
        inline-flex items-center gap-1 rounded
        ${bgColor} ${paddingClasses[size]}
        ${className}
      `}
      title={label}
    >
      <Icon className={`${sizeClasses[size]} ${color}`} />
      {showLabel && (
        <span className={`font-medium ${color} ${textClasses[size]}`}>
          {label}
        </span>
      )}
    </div>
  );
}

/**
 * Component: Combined type + streaming badges
 */
interface TemplateIconsProps {
  type: TemplateType | string;
  isStreaming?: boolean;
  showLabels?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function TemplateIcons({
  type,
  isStreaming = false,
  showLabels = false,
  size = 'md',
  className = ''
}: TemplateIconsProps) {
  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <TemplateTypeBadge type={type} showLabel={showLabels} size={size} />
      {isStreaming && <StreamingBadge showLabel={showLabels} size={size} />}
    </div>
  );
}
