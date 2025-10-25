import React from 'react';
import { Layers, Box, Zap, ArrowRight } from 'lucide-react';

interface TemplateCardProps {
  id: string;
  name: string;
  displayName?: string;
  description?: string;
  type: 'application' | 'extension' | 'microservice';
  tags?: string[];
  icon?: string;
  thumbnail?: string;
  usageCount?: number;
  lastUsed?: Date;
  onClick?: () => void;
}

/**
 * Get gradient background based on template type
 */
const getGradient = (type: TemplateCardProps['type']): string => {
  switch (type) {
    case 'application':
      return 'from-nvidia-green/20 to-nvidia-green/5';
    case 'extension':
      return 'from-blue-500/20 to-blue-500/5';
    case 'microservice':
      return 'from-purple-500/20 to-purple-500/5';
    default:
      return 'from-gray-500/20 to-gray-500/5';
  }
};

/**
 * Get icon for template type
 */
const getTypeIcon = (type: TemplateCardProps['type']) => {
  switch (type) {
    case 'application':
      return <Layers className="w-5 h-5" />;
    case 'extension':
      return <Box className="w-5 h-5" />;
    case 'microservice':
      return <Zap className="w-5 h-5" />;
    default:
      return <Layers className="w-5 h-5" />;
  }
};

/**
 * Get color for template type
 */
const getTypeColor = (type: TemplateCardProps['type']): string => {
  switch (type) {
    case 'application':
      return 'text-nvidia-green';
    case 'extension':
      return 'text-blue-400';
    case 'microservice':
      return 'text-purple-400';
    default:
      return 'text-gray-400';
  }
};

/**
 * TemplateCard
 *
 * NVIDIA NIM-style visual card for template browsing.
 * Features:
 * - Gradient background per template type
 * - Icon/thumbnail display
 * - Tags and metadata
 * - Hover effects (lift, glow, scale)
 * - Click-to-open behavior
 */
export const TemplateCard: React.FC<TemplateCardProps> = ({
  id: _id,
  name,
  displayName,
  description,
  type,
  tags = [],
  icon,
  thumbnail,
  usageCount,
  onClick,
}) => {
  const gradient = getGradient(type);
  const typeIcon = getTypeIcon(type);
  const typeColor = getTypeColor(type);
  const title = displayName || name;

  return (
    <button
      onClick={onClick}
      className={`
        w-full h-full min-h-[320px] flex flex-col
        rounded-lg overflow-hidden
        bg-gradient-to-br ${gradient}
        border border-border-subtle
        hover:border-nvidia-green
        hover:shadow-lg hover:shadow-nvidia-green/20
        hover:scale-[1.02]
        transition-all duration-200
        text-left
        group
      `}
      aria-label={`Open ${title} template`}
    >
      {/* Thumbnail or Icon Area */}
      <div className="relative h-48 bg-bg-card overflow-hidden flex-shrink-0">
        {thumbnail ? (
          <img
            src={thumbnail}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-bg-panel to-bg-card">
            <div className={`text-6xl ${typeColor} opacity-20`}>
              {icon || '📦'}
            </div>
          </div>
        )}

        {/* Type Badge */}
        <div className="absolute top-2 right-2">
          <div className={`
            flex items-center gap-1.5 px-2 py-1 rounded
            bg-bg-dark/80 backdrop-blur-sm
            ${typeColor}
            text-xs font-medium
          `}>
            {typeIcon}
            <span className="capitalize">{type}</span>
          </div>
        </div>

        {/* Usage Count (if available) */}
        {usageCount !== undefined && usageCount > 0 && (
          <div className="absolute bottom-2 left-2">
            <div className="
              px-2 py-0.5 rounded
              bg-bg-dark/80 backdrop-blur-sm
              text-text-muted text-xs
            ">
              🔥 {usageCount} uses
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col">
        {/* Title */}
        <h3 className="
          text-base font-semibold text-text-primary mb-2
          group-hover:text-nvidia-green
          transition-colors
          line-clamp-1
        ">
          {title}
        </h3>

        {/* Description */}
        {description && (
          <p className="text-sm text-text-secondary mb-3 line-clamp-2">
            {description}
          </p>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="
                  px-2 py-0.5 rounded
                  bg-bg-dark text-text-muted
                  text-xs
                "
              >
                #{tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="
                px-2 py-0.5
                text-text-muted text-xs
              ">
                +{tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Quick Action */}
        <div className="flex items-center justify-between pt-2 mt-auto border-t border-border-subtle">
          <span className="text-xs text-text-muted">
            Click to view details
          </span>
          <ArrowRight className="
            w-4 h-4 text-nvidia-green
            group-hover:translate-x-1
            transition-transform
          " />
        </div>
      </div>
    </button>
  );
};

/**
 * TemplateCardSkeleton
 *
 * Loading skeleton for TemplateCard during data fetch.
 */
export const TemplateCardSkeleton: React.FC = () => {
  return (
    <div className="
      w-full h-full min-h-[320px] flex flex-col
      rounded-lg overflow-hidden
      bg-bg-card border border-border-subtle
      animate-pulse
    ">
      {/* Thumbnail skeleton */}
      <div className="h-48 bg-bg-panel flex-shrink-0" />

      {/* Content skeleton */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <div className="h-5 bg-bg-panel rounded w-3/4" />

        {/* Description */}
        <div className="space-y-2">
          <div className="h-4 bg-bg-panel rounded w-full" />
          <div className="h-4 bg-bg-panel rounded w-2/3" />
        </div>

        {/* Tags */}
        <div className="flex gap-1">
          <div className="h-5 bg-bg-panel rounded w-16" />
          <div className="h-5 bg-bg-panel rounded w-20" />
          <div className="h-5 bg-bg-panel rounded w-12" />
        </div>
      </div>
    </div>
  );
};
