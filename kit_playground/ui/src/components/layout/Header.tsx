import React, { useState } from 'react';
import { Trash2, Home, FolderOpen, Package } from 'lucide-react';
import { apiService } from '../../services/api';
import { usePanelStore } from '../../stores/panelStore';

/**
 * Header
 *
 * Application header with branding and title.
 * Simplified for panel-based UI (no routing needed).
 */
export const Header: React.FC = () => {
  const [cleaning, setCleaning] = useState(false);
  const { closeAllPanels, openPanel } = usePanelStore();

  const handleResetView = () => {
    // Close all panels except the sidebar
    closeAllPanels(['template-sidebar']);
    // Open the template grid to show all templates
    openPanel('template-grid', {});
  };

  const handleCleanProjects = async () => {
    if (!confirm('Are you sure you want to delete all user-created projects?\n\nThis will:\n• Delete all projects in source/apps/\n• Delete template-generated extensions\n• Clear repo.toml apps list\n\nTest projects will be excluded.\n\nThis action cannot be undone!')) {
      return;
    }

    try {
      setCleaning(true);
      const result = await apiService.cleanProjects(false); // Don't include test projects

      if (result.success) {
        const { counts } = result;
        alert(`✓ Successfully cleaned ${counts.total} item(s):\n• ${counts.projects} project(s)\n• ${counts.extensions} extension(s)\n\nThe sidebar will refresh automatically.`);

        // Reload the page to refresh the sidebar
        window.location.reload();
      } else {
        alert(`Failed to clean projects: ${result.errors?.[0]?.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Failed to clean projects:', err);
      alert(`Error cleaning projects: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setCleaning(false);
    }
  };

  return (
    <header className="bg-bg-dark border-b border-border-subtle">
      <div className="px-6 py-4">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <div className="w-10 h-10 bg-nvidia-green rounded flex items-center justify-center font-bold text-white text-xl">
            K
          </div>

          {/* Title */}
          <div>
            <h1 className="text-xl font-bold text-text-primary">Kit Playground</h1>
            <p className="text-xs text-text-muted">NVIDIA Omniverse • Template Development Environment</p>
          </div>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Reset View Button */}
          <button
            onClick={handleResetView}
            className="
              px-4 py-2 rounded
              bg-nvidia-green/10 hover:bg-nvidia-green/20
              text-nvidia-green
              border border-nvidia-green/30
              transition-colors
              flex items-center gap-2
              text-sm font-medium
            "
            title="Return to template browser"
          >
            <Home className="w-4 h-4" />
            Home
          </button>

          {/* USD Media Library Button */}
          <button
            onClick={() => openPanel('usd-media', {})}
            className="
              px-4 py-2 rounded
              bg-blue-500/10 hover:bg-blue-500/20
              text-blue-400
              border border-blue-500/30
              transition-colors
              flex items-center gap-2
              text-sm font-medium
            "
            title="Browse and download USD sample files"
          >
            <FolderOpen className="w-4 h-4" />
            USD Media
          </button>

          {/* Component Showcase Button */}
          <button
            onClick={() => openPanel('component-showcase', {})}
            className="
              px-4 py-2 rounded
              bg-purple-500/10 hover:bg-purple-500/20
              text-purple-400
              border border-purple-500/30
              transition-colors
              flex items-center gap-2
              text-sm font-medium
            "
            title="View UI component showcase and examples"
          >
            <Package className="w-4 h-4" />
            Components
          </button>

          {/* Clean Projects Button */}
          <button
            onClick={handleCleanProjects}
            disabled={cleaning}
            className="
              px-4 py-2 rounded
              bg-status-error/10 hover:bg-status-error/20
              text-status-error
              border border-status-error/30
              transition-colors
              flex items-center gap-2
              text-sm font-medium
              disabled:opacity-50 disabled:cursor-not-allowed
            "
            title="Delete all user-created projects (test projects excluded)"
          >
            {cleaning ? (
              <>
                <div className="w-4 h-4 border-2 border-status-error border-t-transparent rounded-full animate-spin" />
                Cleaning...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4" />
                Clean Projects
              </>
            )}
          </button>

          {/* Version Badge */}
          <div className="px-3 py-1 rounded bg-nvidia-green/10 border border-nvidia-green/30">
            <span className="text-xs font-mono text-nvidia-green">v2.0</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
