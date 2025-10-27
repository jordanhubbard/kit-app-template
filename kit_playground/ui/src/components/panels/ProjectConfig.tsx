import React, { useState } from 'react';
import { ArrowLeft, Sparkles, Folder, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { apiService } from '../../services/api';
import type { TemplateModel } from '../../hooks/useTemplates';

interface ProjectConfigProps {
  template: TemplateModel;
}

// Random word lists for generating default project names
const ADJECTIVES = [
  'happy', 'swift', 'bright', 'clever', 'cosmic', 'crystal', 'cyber',
  'digital', 'dynamic', 'electric', 'emerald', 'golden', 'lunar', 'neon',
  'nova', 'pixel', 'quantum', 'ruby', 'silver', 'solar', 'stellar', 'turbo',
  'ultra', 'vapor', 'vivid', 'zenith'
];

const NOUNS = [
  'falcon', 'phoenix', 'comet', 'nebula', 'horizon', 'summit', 'cosmos',
  'thunder', 'lightning', 'aurora', 'eclipse', 'vertex', 'nexus', 'prism',
  'matrix', 'vector', 'catalyst', 'beacon', 'crystal', 'fusion', 'zenith',
  'odyssey', 'vortex', 'spectrum', 'galaxy', 'cascade'
];

/**
 * Generate a random project name with format: adjective_noun_1
 * Example: happy_falcon_1, swift_nebula_1
 */
const generateDefaultProjectName = (): string => {
  const adjective = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)];
  return `${adjective}_${noun}_1`;
};

/**
 * Convert project name to display name
 * Example: happy_falcon_1 -> Happy Falcon
 */
const toDisplayName = (projectName: string): string => {
  return projectName
    .replace(/_\d+$/, '') // Remove trailing _1, _2, etc.
    .replace(/[_-]/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * ProjectConfig
 *
 * Project configuration and creation panel (Panel 3).
 * Allows users to configure and create a new project from a template.
 *
 * Features:
 * - Auto-generated default project names for quick playground testing
 * - Project name validation
 * - Display name
 * - Output directory selection
 * - Advanced options (streaming, per-app deps, standalone)
 * - Real-time validation
 * - Progress feedback
 * - Success/error handling
 */
export const ProjectConfig: React.FC<ProjectConfigProps> = ({ template }) => {
  const { closePanel, getPanelsByType } = usePanelStore();

  // Generate default project name on component mount
  const [defaultProjectName] = useState(() => generateDefaultProjectName());
  const [defaultDisplayName] = useState(() => toDisplayName(defaultProjectName));

  // Form state with auto-generated defaults
  const [projectName, setProjectName] = useState(defaultProjectName);
  const [displayName, setDisplayName] = useState(defaultDisplayName);
  const [outputDir, setOutputDir] = useState('source/apps');
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Advanced options
  const [enableStreaming, setEnableStreaming] = useState(false);
  const [perAppDeps, setPerAppDeps] = useState(false);
  const [standalone, setStandalone] = useState(false);

  // UI state
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Auto-update display name when project name changes
  React.useEffect(() => {
    if (projectName) {
      const generated = toDisplayName(projectName);
      setDisplayName(generated);
    }
  }, [projectName]);

  // Validate project name
  const validateProjectName = (name: string): string | null => {
    if (!name) return 'Project name is required';
    if (name.length < 3) return 'Project name must be at least 3 characters';
    if (!/^[a-z0-9_-]+$/i.test(name)) return 'Only letters, numbers, hyphens, and underscores allowed';
    if (/^[0-9]/.test(name)) return 'Project name cannot start with a number';
    return null;
  };

  // Handle project name change with validation
  const handleProjectNameChange = (value: string) => {
    setProjectName(value);
    const error = validateProjectName(value);
    setValidationErrors(prev => ({
      ...prev,
      projectName: error || '',
    }));
  };

  // Handle form submission
  const handleCreate = async () => {
    // Validate
    const nameError = validateProjectName(projectName);
    if (nameError) {
      setValidationErrors({ projectName: nameError });
      return;
    }

    setIsCreating(true);
    setError(null);

    try {
      const response = await apiService.createProject({
        template: template.name,
        name: projectName,
        displayName: displayName || projectName,
        outputDir: outputDir || undefined,
        standalone,
        perAppDeps,
        enableStreaming,
      });

      if (response.success && response.projectInfo) {
        const { openPanel } = usePanelStore.getState();

        // Close project-config and template-detail panels
        const configPanels = getPanelsByType('project-config');
        const detailPanels = getPanelsByType('template-detail');

        if (configPanels.length > 0) {
          closePanel(configPanels[configPanels.length - 1].id);
        }
        if (detailPanels.length > 0) {
          closePanel(detailPanels[detailPanels.length - 1].id);
        }

        // Open code editor panel with the .kit file
        // User can click "Build" to open the build output panel and start a build
        openPanel('code-editor', {
          filePath: response.projectInfo.kitFile,
          fileName: `${response.projectInfo.projectName}.kit`,
          projectName: response.projectInfo.projectName,
        });

        console.log('Project created successfully:', response);
      } else {
        setError(response.error || 'Failed to create project');
      }
    } catch (err) {
      console.error('Failed to create project:', err);
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setIsCreating(false);
    }
  };

  const handleBack = () => {
    // Close the project-config panel to go back to template detail
    const panels = getPanelsByType('project-config');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
    // Template detail should still be visible, no need to reopen
  };

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Header */}
      <div className="p-4 border-b border-border-subtle">
        <button
          onClick={handleBack}
          className="
            flex items-center gap-2 px-3 py-2 rounded
            text-text-secondary hover:text-text-primary
            hover:bg-bg-card
            transition-colors
            mb-3
          "
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back to Template</span>
        </button>

        <div className="flex items-start gap-3">
          <div className="text-3xl">{template.icon || '📦'}</div>
          <div>
            <h2 className="text-xl font-bold text-text-primary">
              Create {template.displayName}
            </h2>
            <p className="text-sm text-text-secondary">
              Configure your new {template.type}
            </p>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl space-y-6">
          {/* Error Display */}
          {error && (
            <div className="p-4 rounded-lg bg-status-error/10 border border-status-error/30 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-status-error shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-status-error mb-1">Creation Failed</h4>
                <p className="text-sm text-text-secondary">{error}</p>
              </div>
            </div>
          )}

          {/* Project Name */}
          <div>
            <label className="block text-sm font-semibold text-text-primary mb-2">
              Project Name *
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => handleProjectNameChange(e.target.value)}
              placeholder="cosmic_falcon_1"
              disabled={isCreating}
              className={`
                w-full px-4 py-3 rounded-lg
                bg-bg-card border
                ${validationErrors.projectName ? 'border-status-error' : 'border-border-subtle'}
                text-text-primary
                focus:outline-none focus:ring-2 focus:ring-nvidia-green focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all
              `}
            />
            {validationErrors.projectName && (
              <p className="mt-2 text-sm text-status-error flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {validationErrors.projectName}
              </p>
            )}
            <p className="mt-2 text-xs text-text-muted">
              Use lowercase letters, numbers, hyphens, and underscores only
            </p>
          </div>

          {/* Display Name */}
          <div>
            <label className="block text-sm font-semibold text-text-primary mb-2">
              Display Name
            </label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="Cosmic Falcon"
              disabled={isCreating}
              className="
                w-full px-4 py-3 rounded-lg
                bg-bg-card border border-border-subtle
                text-text-primary
                focus:outline-none focus:ring-2 focus:ring-nvidia-green focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all
              "
            />
            <p className="mt-2 text-xs text-text-muted">
              Human-readable name for your project (auto-updated from project name)
            </p>
          </div>

          {/* Output Directory */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-text-primary mb-2">
              <Folder className="w-4 h-4" />
              Output Directory
            </label>
            <input
              type="text"
              value={outputDir}
              onChange={(e) => setOutputDir(e.target.value)}
              placeholder="source/apps"
              disabled={isCreating}
              className="
                w-full px-4 py-3 rounded-lg
                bg-bg-card border border-border-subtle
                text-text-primary
                focus:outline-none focus:ring-2 focus:ring-nvidia-green focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all
              "
            />
            <p className="mt-2 text-xs text-text-muted">
              Where to create the project (default: source/apps)
            </p>
          </div>

          {/* Advanced Options */}
          <div className="border border-border-subtle rounded-lg overflow-hidden">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              disabled={isCreating}
              className="
                w-full px-4 py-3
                bg-bg-card hover:bg-bg-card-hover
                flex items-center justify-between
                transition-colors
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              <span className="text-sm font-semibold text-text-primary">
                Advanced Options
              </span>
              {showAdvanced ? (
                <ChevronUp className="w-5 h-5 text-text-secondary" />
              ) : (
                <ChevronDown className="w-5 h-5 text-text-secondary" />
              )}
            </button>

            {showAdvanced && (
              <div className="p-4 space-y-4 border-t border-border-subtle">
                {/* Enable Kit App Streaming */}
                <label className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={enableStreaming}
                    onChange={(e) => setEnableStreaming(e.target.checked)}
                    disabled={isCreating}
                    className="
                      mt-1 w-5 h-5 rounded
                      border-border-subtle
                      text-nvidia-green
                      focus:ring-2 focus:ring-nvidia-green
                      disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-text-primary group-hover:text-nvidia-green transition-colors">
                      Enable Kit App Streaming
                    </div>
                    <div className="text-xs text-text-muted mt-1">
                      Add WebRTC streaming extensions for remote access
                    </div>
                  </div>
                </label>

                {/* Per-App Dependencies */}
                <label className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={perAppDeps}
                    onChange={(e) => setPerAppDeps(e.target.checked)}
                    disabled={isCreating}
                    className="
                      mt-1 w-5 h-5 rounded
                      border-border-subtle
                      text-nvidia-green
                      focus:ring-2 focus:ring-nvidia-green
                      disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-text-primary group-hover:text-nvidia-green transition-colors">
                      Per-Application Dependencies
                    </div>
                    <div className="text-xs text-text-muted mt-1">
                      Isolate Kit SDK and dependencies for this application
                    </div>
                  </div>
                </label>

                {/* Standalone Project */}
                <label className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={standalone}
                    onChange={(e) => setStandalone(e.target.checked)}
                    disabled={isCreating}
                    className="
                      mt-1 w-5 h-5 rounded
                      border-border-subtle
                      text-nvidia-green
                      focus:ring-2 focus:ring-nvidia-green
                      disabled:opacity-50 disabled:cursor-not-allowed
                    "
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-text-primary group-hover:text-nvidia-green transition-colors">
                      Create as Standalone Project
                    </div>
                    <div className="text-xs text-text-muted mt-1">
                      Include all build tools for independent operation
                    </div>
                  </div>
                </label>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="p-4 border-t border-border-subtle bg-bg-dark">
        <div className="flex gap-3">
          <button
            onClick={handleBack}
            disabled={isCreating}
            className="
              px-6 py-3 rounded-lg
              bg-bg-card hover:bg-bg-card-hover
              border border-border-subtle
              text-text-primary font-medium
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            "
          >
            Cancel
          </button>

          <button
            onClick={handleCreate}
            disabled={isCreating || !!validationErrors.projectName || !projectName}
            className="
              flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg
              bg-nvidia-green hover:bg-nvidia-green-dark
              disabled:opacity-50 disabled:cursor-not-allowed
              text-white font-semibold
              transition-colors
            "
          >
            {isCreating ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Create Project
              </>
            )}
          </button>
        </div>

        <p className="text-xs text-text-muted text-center mt-3">
          This will create a new {template.type} from the {template.displayName} template
        </p>
      </div>
    </div>
  );
};
