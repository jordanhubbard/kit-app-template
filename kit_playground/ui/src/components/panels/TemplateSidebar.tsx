import React, { useState, useMemo } from 'react';
import { Search, ChevronDown, ChevronRight, Sparkles, Package, Box, FolderOpen } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { useTemplates, type TemplateModel } from '../../hooks/useTemplates';
import { useProjects } from '../../hooks/useProjects';

/**
 * TemplateSidebar
 *
 * Compact text-based sidebar for template navigation (like VSCode file explorer).
 * Replaces the old card-based browser in the left panel.
 */
export const TemplateSidebar: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['templates', 'applications', 'extensions', 'services'])
  );
  const { openPanel } = usePanelStore();

  // Fetch templates and projects
  const { templates, loading, error } = useTemplates();
  const { projects, loading: loadingProjects } = useProjects();

  // Group templates by type
  const groupedTemplates = useMemo(() => {
    let filtered = templates;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = templates.filter(t => {
        const searchableText = [
          t.name,
          t.displayName || '',
          t.description || '',
          ...(t.tags || [])
        ].join(' ').toLowerCase();
        return searchableText.includes(query);
      });
    }

    return {
      // Only show actual applications (exclude setup/component templates)
      applications: filtered.filter(t =>
        t.type === 'application' &&
        !t.name.includes('_setup') &&
        t.type !== 'component'
      ),
      // Only show actual extensions (exclude setup/component templates)
      extensions: filtered.filter(t =>
        t.type === 'extension' &&
        t.type !== 'component'
      ),
      // Only show actual microservices (exclude setup/component templates)
      microservices: filtered.filter(t =>
        t.type === 'microservice' &&
        t.type !== 'component'
      ),
    };
  }, [templates, searchQuery]);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    const wasExpanded = newExpanded.has(section);

    if (wasExpanded) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);

    // Also show the filtered grid when expanding a section
    if (!wasExpanded) {
      if (section === 'applications') {
        handleShowApplications();
      } else if (section === 'extensions') {
        handleShowExtensions();
      } else if (section === 'services') {
        handleShowServices();
      }
    }
  };

  const handleTemplateClick = (template: TemplateModel) => {
    // Close the template grid panel to make room for the creation workflow
    const { closePanel, getPanelsByType } = usePanelStore.getState();
    const gridPanels = getPanelsByType('template-grid');
    if (gridPanels.length > 0) {
      closePanel(gridPanels[0].id);
    }

    // Open template detail panel (will now be leftmost after sidebar)
    openPanel('template-detail', { template });
  };

  const handleShowAllTemplates = () => {
    openPanel('template-grid', { templates, filterType: 'all' });
  };

  const handleShowApplications = () => {
    openPanel('template-grid', { templates: groupedTemplates.applications, filterType: 'application' });
  };

  const handleShowExtensions = () => {
    openPanel('template-grid', { templates: groupedTemplates.extensions, filterType: 'extension' });
  };

  const handleShowServices = () => {
    openPanel('template-grid', { templates: groupedTemplates.microservices, filterType: 'microservice' });
  };

  return (
    <div className="flex flex-col h-full bg-bg-panel text-text-primary text-sm">
      {/* Search */}
      <div className="p-3 border-b border-border-subtle">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted" />
          <input
            type="text"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="
              w-full pl-8 pr-2 py-1.5 text-xs
              bg-bg-card border border-border-subtle rounded
              text-text-primary placeholder:text-text-muted
              focus:outline-none focus:ring-1 focus:ring-nvidia-green focus:border-nvidia-green
            "
          />
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-text-muted text-xs">Loading...</div>
        ) : error ? (
          <div className="p-4 text-status-error text-xs">{error}</div>
        ) : (
          <>
            {/* Templates Section */}
            <div className="border-b border-border-subtle">
              <button
                onClick={() => toggleSection('templates')}
                className="
                  w-full flex items-center gap-2 px-3 py-2
                  hover:bg-bg-card-hover
                  transition-colors
                "
              >
                {expandedSections.has('templates') ? (
                  <ChevronDown className="w-3.5 h-3.5 text-text-muted" />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 text-text-muted" />
                )}
                <Sparkles className="w-3.5 h-3.5 text-nvidia-green" />
                <span className="font-medium">Templates</span>
                <span className="ml-auto text-xs text-text-muted">{templates.length}</span>
              </button>

              {expandedSections.has('templates') && (
                <div className="pl-6">
                  {/* All Templates */}
                  <button
                    onClick={handleShowAllTemplates}
                    className="
                      w-full flex items-center gap-2 px-3 py-1.5
                      hover:bg-bg-card-hover
                      transition-colors text-left
                    "
                  >
                    <span className="text-text-secondary">All Templates</span>
                    <span className="ml-auto text-xs text-text-muted">{templates.length}</span>
                  </button>

                  {/* Applications */}
                  <div>
                    <button
                      onClick={() => toggleSection('applications')}
                      className="
                        w-full flex items-center gap-2 px-3 py-1.5
                        hover:bg-bg-card-hover
                        transition-colors
                      "
                    >
                      {expandedSections.has('applications') ? (
                        <ChevronDown className="w-3 h-3 text-text-muted" />
                      ) : (
                        <ChevronRight className="w-3 h-3 text-text-muted" />
                      )}
                      <Sparkles className="w-3 h-3 text-nvidia-green" />
                      <span className="text-text-secondary">Applications</span>
                      <span className="ml-auto text-xs text-text-muted">{groupedTemplates.applications.length}</span>
                    </button>

                    {expandedSections.has('applications') && (
                      <div className="pl-6">
                        <button
                          onClick={handleShowApplications}
                          className="
                            w-full flex items-center gap-2 px-3 py-1
                            hover:bg-bg-card-hover
                            transition-colors text-left text-xs
                          "
                        >
                          <span className="text-text-muted">View all</span>
                        </button>
                        {groupedTemplates.applications.slice(0, 5).map((template) => (
                          <button
                            key={template.id}
                            onClick={() => handleTemplateClick(template)}
                            className="
                              w-full flex items-center gap-2 px-3 py-1
                              hover:bg-bg-card-hover
                              transition-colors text-left
                            "
                            title={template.description}
                          >
                            <span className="text-text-secondary truncate">{template.displayName}</span>
                          </button>
                        ))}
                        {groupedTemplates.applications.length > 5 && (
                          <button
                            onClick={handleShowApplications}
                            className="
                              w-full flex items-center gap-2 px-3 py-1
                              hover:bg-bg-card-hover
                              transition-colors text-left text-xs
                            "
                          >
                            <span className="text-nvidia-green">
                              +{groupedTemplates.applications.length - 5} more...
                            </span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Extensions */}
                  <div>
                    <button
                      onClick={() => toggleSection('extensions')}
                      className="
                        w-full flex items-center gap-2 px-3 py-1.5
                        hover:bg-bg-card-hover
                        transition-colors
                      "
                    >
                      {expandedSections.has('extensions') ? (
                        <ChevronDown className="w-3 h-3 text-text-muted" />
                      ) : (
                        <ChevronRight className="w-3 h-3 text-text-muted" />
                      )}
                      <Package className="w-3 h-3 text-blue-400" />
                      <span className="text-text-secondary">Extensions</span>
                      <span className="ml-auto text-xs text-text-muted">{groupedTemplates.extensions.length}</span>
                    </button>

                    {expandedSections.has('extensions') && (
                      <div className="pl-6">
                        <button
                          onClick={handleShowExtensions}
                          className="
                            w-full flex items-center gap-2 px-3 py-1
                            hover:bg-bg-card-hover
                            transition-colors text-left text-xs
                          "
                        >
                          <span className="text-text-muted">View all</span>
                        </button>
                        {groupedTemplates.extensions.slice(0, 5).map((template) => (
                          <button
                            key={template.id}
                            onClick={() => handleTemplateClick(template)}
                            className="
                              w-full flex items-center gap-2 px-3 py-1
                              hover:bg-bg-card-hover
                              transition-colors text-left
                            "
                            title={template.description}
                          >
                            <span className="text-text-secondary truncate">{template.displayName}</span>
                          </button>
                        ))}
                        {groupedTemplates.extensions.length > 5 && (
                          <button
                            onClick={handleShowExtensions}
                            className="
                              w-full flex items-center gap-2 px-3 py-1
                              hover:bg-bg-card-hover
                              transition-colors text-left text-xs
                            "
                          >
                            <span className="text-nvidia-green">
                              +{groupedTemplates.extensions.length - 5} more...
                            </span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Services */}
                  <div>
                    <button
                      onClick={() => toggleSection('services')}
                      className="
                        w-full flex items-center gap-2 px-3 py-1.5
                        hover:bg-bg-card-hover
                        transition-colors
                      "
                    >
                      {expandedSections.has('services') ? (
                        <ChevronDown className="w-3 h-3 text-text-muted" />
                      ) : (
                        <ChevronRight className="w-3 h-3 text-text-muted" />
                      )}
                      <Box className="w-3 h-3 text-purple-400" />
                      <span className="text-text-secondary">Services</span>
                      <span className="ml-auto text-xs text-text-muted">{groupedTemplates.microservices.length}</span>
                    </button>

                    {expandedSections.has('services') && (
                      <div className="pl-6">
                        <button
                          onClick={handleShowServices}
                          className="
                            w-full flex items-center gap-2 px-3 py-1
                            hover:bg-bg-card-hover
                            transition-colors text-left text-xs
                          "
                        >
                          <span className="text-text-muted">View all</span>
                        </button>
                        {groupedTemplates.microservices.slice(0, 5).map((template) => (
                          <button
                            key={template.id}
                            onClick={() => handleTemplateClick(template)}
                            className="
                              w-full flex items-center gap-2 px-3 py-1
                              hover:bg-bg-card-hover
                              transition-colors text-left
                            "
                            title={template.description}
                          >
                            <span className="text-text-secondary truncate">{template.displayName}</span>
                          </button>
                        ))}
                        {groupedTemplates.microservices.length > 5 && (
                          <button
                            onClick={handleShowServices}
                            className="
                              w-full flex items-center gap-2 px-3 py-1
                              hover:bg-bg-card-hover
                              transition-colors text-left text-xs
                            "
                          >
                            <span className="text-nvidia-green">
                              +{groupedTemplates.microservices.length - 5} more...
                            </span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* My Projects Section */}
            <div>
              <button
                onClick={() => toggleSection('projects')}
                className="
                  w-full flex items-center gap-2 px-3 py-2
                  hover:bg-bg-card-hover
                  transition-colors
                "
              >
                {expandedSections.has('projects') ? (
                  <ChevronDown className="w-3.5 h-3.5 text-text-muted" />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5 text-text-muted" />
                )}
                <FolderOpen className="w-3.5 h-3.5 text-nvidia-green" />
                <span className="font-medium">My Projects</span>
                <span className="ml-auto text-xs text-text-muted">{projects.length}</span>
              </button>

              {expandedSections.has('projects') && (
                <div className="pl-6">
                  {loadingProjects && (
                    <div className="px-3 py-2 text-xs text-text-muted flex items-center gap-2">
                      <div className="w-3 h-3 border-2 border-nvidia-green border-t-transparent rounded-full animate-spin" />
                      Loading...
                    </div>
                  )}
                  {!loadingProjects && projects.length === 0 && (
                    <div className="px-3 py-2 text-xs text-text-muted">No projects yet</div>
                  )}
                  {!loadingProjects && projects.length > 0 && projects.slice(0, 10).map((project) => {
                    // Determine action based on project status
                    const getStatusBadge = () => {
                      const status = project.status || 'created';
                      switch (status) {
                        case 'running':
                          return <span className="px-1.5 py-0.5 text-xs bg-nvidia-green/20 text-nvidia-green rounded">Running</span>;
                        case 'built':
                          return <span className="px-1.5 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded">Built</span>;
                        default:
                          return <span className="px-1.5 py-0.5 text-xs bg-yellow-500/20 text-yellow-400 rounded">New</span>;
                      }
                    };

                    const handleProjectClick = () => {
                      const status = project.status || 'created';
                      
                      if (status === 'running') {
                        // Project is running - open preview panel
                        openPanel('preview', { 
                          projectName: project.name,
                          mode: 'xpra'  // Default to xpra for running projects
                        });
                      } else if (status === 'built') {
                        // Project is built - open build output with launch ready
                        openPanel('build-output', {
                          projectName: project.name,
                          jobType: 'launch',
                          autoStart: false  // Don't auto-launch, just show the launch button
                        });
                      } else {
                        // Project is new - open build panel
                        openPanel('build-output', {
                          projectName: project.name,
                          jobType: 'build',
                          autoStart: false  // Let user initiate build
                        });
                      }
                    };

                    return (
                      <button
                        key={project.id}
                        onClick={handleProjectClick}
                        className="
                          w-full flex items-center gap-2 px-3 py-1.5
                          hover:bg-bg-card-hover
                          transition-colors text-left
                        "
                        title={`${project.status === 'running' ? 'View' : project.status === 'built' ? 'Launch' : 'Build'} ${project.name}`}
                      >
                        <span className="text-text-secondary truncate flex-1">{project.displayName || project.name}</span>
                        {getStatusBadge()}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border-subtle">
        <div className="text-xs text-text-muted">
          v2.0 • {templates.length} templates
        </div>
      </div>
    </div>
  );
};
