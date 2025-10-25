import React, { useState, useMemo } from 'react';
import { Search, Plus, FolderOpen, AlertCircle, RefreshCw } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { useTemplates, type TemplateModel } from '../../hooks/useTemplates';
import { useProjects } from '../../hooks/useProjects';
import { TemplateCard, TemplateCardSkeleton } from '../templates/TemplateCard';
import { ProjectCard } from '../projects/ProjectCard';

type TemplateType = 'all' | 'application' | 'extension' | 'microservice';
type SortOption = 'alphabetical' | 'recent' | 'popular';

/**
 * TemplateBrowser
 *
 * The main template browsing interface (Panel 1 - Always visible).
 * Features:
 * - NVIDIA NIM-style visual card layout
 * - Real template data from API
 * - Category filtering (All, Apps, Extensions, Services)
 * - Live search with fuzzy matching
 * - Sort options (Alphabetical, Recent, Popular)
 * - Loading states and error handling
 */
export const TemplateBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'templates' | 'projects'>('templates');
  const [activeType, setActiveType] = useState<TemplateType>('all');
  const [sortBy, setSortBy] = useState<SortOption>('alphabetical');
  const { openPanel } = usePanelStore();

  // Fetch templates from API
  const { templates, loading, error, refetch } = useTemplates();
  
  // Fetch user projects
  const { projects, loading: projectsLoading, error: projectsError } = useProjects();

  // Filter and sort templates
  const filteredTemplates = useMemo(() => {
    let result = templates;

    // Filter by type
    if (activeType !== 'all') {
      result = result.filter(t => t.type === activeType);
    }

    // Filter by search query
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
          // Would sort by lastUsed if available
          return 0;
        case 'popular':
          // Would sort by usageCount if available
          return (b.usageCount || 0) - (a.usageCount || 0);
        default:
          return 0;
      }
    });

    return result;
  }, [templates, activeType, searchQuery, sortBy]);

  const handleTemplateClick = (template: TemplateModel) => {
    // Open template detail panel
    openPanel('template-detail', { template });
  };

  const typeFilters: { value: TemplateType; label: string; count?: number }[] = [
    { value: 'all', label: 'All Templates', count: templates.length },
    { value: 'application', label: 'Applications', count: templates.filter(t => t.type === 'application').length },
    { value: 'extension', label: 'Extensions', count: templates.filter(t => t.type === 'extension').length },
    { value: 'microservice', label: 'Services', count: templates.filter(t => t.type === 'microservice').length },
  ];

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Search Bar */}
      <div className="p-4 border-b border-border-subtle">
        <div className="relative">
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
              transition-all
            "
          />
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex border-b border-border-subtle">
        <button
          onClick={() => setActiveTab('templates')}
          className={`
            flex-1 px-4 py-3 text-sm font-medium
            transition-colors
            ${activeTab === 'templates'
              ? 'text-nvidia-green border-b-2 border-nvidia-green'
              : 'text-text-secondary hover:text-text-primary'
            }
          `}
        >
          Templates
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`
            flex-1 px-4 py-3 text-sm font-medium
            transition-colors
            ${activeTab === 'projects'
              ? 'text-nvidia-green border-b-2 border-nvidia-green'
              : 'text-text-secondary hover:text-text-primary'
            }
          `}
        >
          My Projects
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'templates' ? (
          <>
            {/* Category Filters */}
            <div className="p-4 border-b border-border-subtle">
              <div className="flex flex-wrap gap-2">
                {typeFilters.map((filter) => (
                  <button
                    key={filter.value}
                    onClick={() => setActiveType(filter.value)}
                    className={`
                      px-3 py-1.5 rounded text-xs font-medium
                      transition-all
                      ${activeType === filter.value
                        ? 'bg-nvidia-green text-white'
                        : 'bg-bg-card text-text-secondary hover:text-text-primary hover:bg-bg-card-hover'
                      }
                    `}
                  >
                    {filter.label} {filter.count !== undefined && `(${filter.count})`}
                  </button>
                ))}
              </div>

              {/* Sort Options */}
              <div className="mt-3 flex items-center gap-2">
                <span className="text-xs text-text-muted">Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                  className="
                    px-2 py-1 rounded text-xs
                    bg-bg-card border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:ring-1 focus:ring-nvidia-green
                  "
                >
                  <option value="alphabetical">Alphabetical</option>
                  <option value="recent">Recently Used</option>
                  <option value="popular">Most Popular</option>
                </select>
              </div>
            </div>

            {/* Template Grid */}
            <div className="p-4">
              {/* Loading State */}
              {loading && (
                <div className="grid gap-4">
                  {[...Array(6)].map((_, i) => (
                    <TemplateCardSkeleton key={i} />
                  ))}
                </div>
              )}

              {/* Error State */}
              {error && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <AlertCircle className="w-12 h-12 text-status-error mb-4" />
                  <h3 className="text-lg font-semibold text-text-primary mb-2">
                    Failed to Load Templates
                  </h3>
                  <p className="text-text-secondary text-sm mb-4">
                    {error}
                  </p>
                  <button
                    onClick={refetch}
                    className="
                      flex items-center gap-2 px-4 py-2 rounded
                      bg-nvidia-green hover:bg-nvidia-green-dark
                      text-white font-medium text-sm
                      transition-colors
                    "
                  >
                    <RefreshCw className="w-4 h-4" />
                    Retry
                  </button>
                </div>
              )}

              {/* Templates */}
              {!loading && !error && (
                <>
                  {filteredTemplates.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <Search className="w-12 h-12 text-text-muted mb-4" />
                      <h3 className="text-lg font-semibold text-text-primary mb-2">
                        No Templates Found
                      </h3>
                      <p className="text-text-secondary text-sm">
                        Try adjusting your search or filters.
                      </p>
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {filteredTemplates.map((template) => (
                        <TemplateCard
                          key={template.id}
                          {...template}
                          onClick={() => handleTemplateClick(template)}
                        />
                      ))}
                    </div>
                  )}

                  {/* Results count */}
                  <div className="mt-4 text-center text-xs text-text-muted">
                    Showing {filteredTemplates.length} of {templates.length} templates
                  </div>
                </>
              )}
            </div>
          </>
        ) : (
          <div className="p-4">
            {/* Loading State */}
            {projectsLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-nvidia-green border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                  <p className="text-text-secondary">Loading projects...</p>
                </div>
              </div>
            )}

            {/* Error State */}
            {projectsError && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <AlertCircle className="w-12 h-12 text-status-error mb-4" />
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Failed to Load Projects
                </h3>
                <p className="text-text-secondary text-sm mb-4">
                  {projectsError}
                </p>
              </div>
            )}

            {/* Projects List */}
            {!projectsLoading && !projectsError && projects.length > 0 && (
              <div className="space-y-4">
                {projects.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    onBuild={(proj) => console.log('Build:', proj)}
                    onLaunch={(proj) => console.log('Launch:', proj)}
                    onEdit={(proj) => console.log('Edit:', proj)}
                    onDelete={(proj) => console.log('Delete:', proj)}
                  />
                ))}
              </div>
            )}

            {/* Empty State */}
            {!projectsLoading && !projectsError && projects.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 text-center px-4">
                <FolderOpen className="w-16 h-16 text-text-muted mb-4" />
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  No Projects Yet
                </h3>
                <p className="text-text-secondary text-sm mb-6">
                  Create your first project from a template to get started.
                </p>
                <button
                  onClick={() => setActiveTab('templates')}
                  className="
                    flex items-center gap-2 px-4 py-2 rounded
                    bg-nvidia-green hover:bg-nvidia-green-dark
                    text-white font-medium text-sm
                    transition-colors
                  "
                >
                  <Plus className="w-4 h-4" />
                  Browse Templates
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Phase indicator */}
      <div className="p-3 border-t border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className="px-2 py-0.5 rounded bg-nvidia-green/20 text-nvidia-green font-mono">
            PHASE 2
          </span>
          <span>
            Visual cards • Real API data • Filtering & Search
          </span>
        </div>
      </div>
    </div>
  );
};
