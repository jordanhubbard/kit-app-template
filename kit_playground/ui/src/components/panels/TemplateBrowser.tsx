import React, { useState } from 'react';
import { Search, Plus, FolderOpen } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';

/**
 * TemplateBrowser
 * 
 * The main template browsing interface (Panel 1 - Always visible).
 * Displays templates as visual cards with category filtering and search.
 * 
 * This is a Phase 1 placeholder - will be enhanced in Phase 2 with:
 * - Visual card layout (NIM-style)
 * - Real template data from API
 * - Category filtering
 * - Search functionality
 * - Tag-based navigation
 */
export const TemplateBrowser: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'templates' | 'projects'>('templates');
  const { openPanel } = usePanelStore();

  // Placeholder template data (will be replaced with API call in Phase 2)
  const placeholderTemplates = [
    { id: 'kit_base_editor', name: 'Kit Base Editor', type: 'app', icon: '🎮', tags: ['editor', 'usd', '3d'] },
    { id: 'omni_usd_viewer', name: 'USD Viewer', type: 'app', icon: '🔧', tags: ['viewer', 'usd'] },
    { id: 'omni_usd_explorer', name: 'USD Explorer', type: 'app', icon: '🚀', tags: ['explorer', '3d', 'nav'] },
    { id: 'omni_usd_composer', name: 'USD Composer', type: 'app', icon: '🎨', tags: ['composer', 'usd'] },
    { id: 'kit_service', name: 'Kit Service', type: 'service', icon: '⚡', tags: ['service', 'microservice'] },
  ];

  const handleTemplateClick = (template: any) => {
    // Open template detail panel (Phase 3)
    openPanel('template-detail', { template });
  };

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
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'templates' ? (
          <div className="space-y-2">
            <p className="text-xs text-text-muted mb-4">
              Click a template to view details →
            </p>
            
            {placeholderTemplates.map((template) => (
              <button
                key={template.id}
                onClick={() => handleTemplateClick(template)}
                className="
                  w-full p-4 rounded-lg
                  bg-bg-card border border-border-subtle
                  hover:border-nvidia-green hover:bg-bg-card-hover
                  transition-all
                  text-left group
                "
              >
                <div className="flex items-start gap-3">
                  <div className="text-2xl flex-shrink-0">
                    {template.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-text-primary mb-1 group-hover:text-nvidia-green transition-colors">
                      {template.name}
                    </h3>
                    <div className="flex flex-wrap gap-1">
                      {template.tags.map((tag) => (
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
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
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

      {/* Phase indicator */}
      <div className="p-3 border-t border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className="px-2 py-0.5 rounded bg-nvidia-green/20 text-nvidia-green font-mono">
            PHASE 1
          </span>
          <span>
            Panel system foundation • Enhanced visuals in Phase 2
          </span>
        </div>
      </div>
    </div>
  );
};

