import React, { useState, useMemo } from 'react';
import { Search, Filter, Grid3x3, List } from 'lucide-react';
import { TemplateCard, TemplateCardSkeleton } from '../templates/TemplateCard';
import { usePanelStore } from '../../stores/panelStore';
import type { TemplateModel } from '../../hooks/useTemplates';

type SortOption = 'alphabetical' | 'recent' | 'popular';
type ViewMode = 'grid' | 'list';

interface TemplateGridProps {
  templates: TemplateModel[];
  filterType?: 'all' | 'application' | 'extension' | 'microservice';
  title?: string;
}

/**
 * TemplateGrid
 *
 * Displays templates in a responsive 2D grid layout.
 * This is the main content area that uses all available screen space.
 */
export const TemplateGrid: React.FC<TemplateGridProps> = ({
  templates,
  filterType = 'all',
  title,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('alphabetical');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const { openPanel } = usePanelStore();

  // Debug logging - remove after testing
  if (typeof window !== 'undefined' && !(window as any).__TEMPLATE_GRID_LOGGED) {
    console.log('🎛️ TemplateGrid v2.0-redesign: MULTI-COLUMN GRID (grid-cols-1 sm:2 md:2 lg:3 xl:4)');
    (window as any).__TEMPLATE_GRID_LOGGED = true;
  }

  // Get title based on filter type
  const displayTitle = title || (
    filterType === 'all' ? 'All Templates' :
    filterType === 'application' ? 'Applications' :
    filterType === 'extension' ? 'Extensions' :
    'Services'
  );

  // Filter and sort templates
  const filteredTemplates = useMemo(() => {
    let result = templates;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(t => {
        const searchableText = [
          t.name,
          t.displayName || '',
          t.description || '',
          ...(t.tags || [])
        ].join(' ').toLowerCase();
        return searchableText.includes(query);
      });
    }

    // Sort
    result = [...result].sort((a, b) => {
      switch (sortBy) {
        case 'alphabetical':
          return (a.displayName || a.name).localeCompare(b.displayName || b.name);
        case 'recent':
          return 0; // Would use lastUsed if available
        case 'popular':
          return (b.usageCount || 0) - (a.usageCount || 0);
        default:
          return 0;
      }
    });

    return result;
  }, [templates, searchQuery, sortBy]);

  const handleTemplateClick = (template: TemplateModel) => {
    openPanel('template-detail', { template });
  };

  return (
    <div className="flex flex-col h-full bg-bg-dark">
      {/* Header */}
      <div className="p-6 border-b border-border-subtle bg-bg-panel">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{displayTitle}</h1>
            <p className="text-sm text-text-muted mt-1">
              {filteredTemplates.length} {filteredTemplates.length === 1 ? 'template' : 'templates'}
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`
                p-2 rounded
                transition-colors
                ${viewMode === 'grid'
                  ? 'bg-nvidia-green text-white'
                  : 'bg-bg-card text-text-secondary hover:bg-bg-card-hover'
                }
              `}
              title="Grid view"
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`
                p-2 rounded
                transition-colors
                ${viewMode === 'list'
                  ? 'bg-nvidia-green text-white'
                  : 'bg-bg-card text-text-secondary hover:bg-bg-card-hover'
                }
              `}
              title="List view"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="
                w-full pl-10 pr-4 py-2
                bg-bg-card border border-border-subtle rounded
                text-text-primary text-sm
                focus:outline-none focus:ring-2 focus:ring-nvidia-green focus:border-transparent
                placeholder:text-text-muted
              "
            />
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-text-muted" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="
                px-3 py-2 rounded text-sm
                bg-bg-card border border-border-subtle
                text-text-primary
                focus:outline-none focus:ring-2 focus:ring-nvidia-green
              "
            >
              <option value="alphabetical">Alphabetical</option>
              <option value="recent">Recently Used</option>
              <option value="popular">Most Popular</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredTemplates.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <Search className="w-16 h-16 text-text-muted mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              No Templates Found
            </h3>
            <p className="text-text-secondary text-sm">
              Try adjusting your search or filters.
            </p>
          </div>
        ) : viewMode === 'grid' ? (
          /* Grid View */
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6 auto-rows-fr">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                {...template}
                onClick={() => handleTemplateClick(template)}
              />
            ))}
          </div>
        ) : (
          /* List View */
          <div className="space-y-3 max-w-5xl mx-auto">
            {filteredTemplates.map((template) => (
              <div
                key={template.id}
                onClick={() => handleTemplateClick(template)}
                className="
                  flex items-center gap-4 p-4 rounded-lg
                  bg-bg-card border border-border-subtle
                  hover:border-nvidia-green hover:shadow-lg
                  cursor-pointer transition-all
                "
              >
                {/* Icon/Thumbnail */}
                {template.icon ? (
                  <img src={template.icon} alt={template.displayName} className="w-12 h-12 rounded" />
                ) : (
                  <div className="w-12 h-12 flex items-center justify-center bg-bg-dark rounded">
                    {template.type === 'application' && <span className="text-nvidia-green">App</span>}
                    {template.type === 'extension' && <span className="text-blue-400">Ext</span>}
                    {template.type === 'microservice' && <span className="text-purple-400">Svc</span>}
                  </div>
                )}

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-base font-semibold text-text-primary truncate">
                      {template.displayName}
                    </h3>
                    <span className={`
                      px-2 py-0.5 rounded-full text-xs font-medium
                      ${template.type === 'application' ? 'text-nvidia-green bg-nvidia-green/10' :
                        template.type === 'extension' ? 'text-blue-400 bg-blue-400/10' :
                        'text-purple-400 bg-purple-400/10'}
                    `}>
                      {template.type === 'microservice' ? 'Service' :
                       template.type.charAt(0).toUpperCase() + template.type.slice(1)}
                    </span>
                  </div>
                  <p className="text-sm text-text-secondary line-clamp-2">
                    {template.description}
                  </p>
                  {template.tags && template.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {template.tags.slice(0, 4).map((tag, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-bg-dark text-text-muted text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Usage Count */}
                {template.usageCount !== undefined && (
                  <div className="text-sm text-text-muted">
                    {template.usageCount} uses
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * TemplateGridSkeleton
 *
 * Loading state for the grid
 */
export const TemplateGridSkeleton: React.FC = () => {
  return (
    <div className="flex flex-col h-full bg-bg-dark">
      <div className="p-6 border-b border-border-subtle bg-bg-panel">
        <div className="h-8 w-48 bg-bg-card rounded mb-2 animate-pulse" />
        <div className="h-4 w-32 bg-bg-card rounded animate-pulse" />
        <div className="mt-4 h-10 w-full bg-bg-card rounded animate-pulse" />
      </div>
      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
          {[...Array(10)].map((_, i) => (
            <TemplateCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
};
