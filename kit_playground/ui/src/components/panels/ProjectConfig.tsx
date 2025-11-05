import React, { useState, useEffect } from 'react';
import { ArrowLeft, Sparkles, Folder, ChevronDown, ChevronUp, AlertCircle, Layers, Package } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { apiService } from '../../services/api';
import type { TemplateModel } from '../../hooks/useTemplates';
import { useLayers } from '../../hooks/useLayers';

interface KitVersion {
  version: string;
  label: string;
  recommended: boolean;
}

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

  // Fetch available layers
  const { data: layersData, isLoading: isLoadingLayers } = useLayers();

  // Generate default project name on component mount
  const [defaultProjectName] = useState(() => generateDefaultProjectName());
  const [defaultDisplayName] = useState(() => toDisplayName(defaultProjectName));

  // Form state with auto-generated defaults
  const [projectName, setProjectName] = useState(defaultProjectName);
  const [displayName, setDisplayName] = useState(defaultDisplayName);
  const [outputDir, setOutputDir] = useState('source/apps');

  // Kit SDK version selection
  const [kitVersions, setKitVersions] = useState<KitVersion[]>([]);
  const [selectedKitVersion, setSelectedKitVersion] = useState<string>('');
  const [isLoadingVersions, setIsLoadingVersions] = useState(true);

  // Layer selection
  const [selectedLayers, setSelectedLayers] = useState<string[]>([]);

  // UI state
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Fetch available Kit SDK versions
  useEffect(() => {
    const fetchKitVersions = async () => {
      try {
        setIsLoadingVersions(true);
        const response = await fetch('/api/projects/kit-versions');
        const data = await response.json();
        if (data.success && data.versions) {
          setKitVersions(data.versions);
          // Set default to the recommended version
          const recommended = data.versions.find((v: KitVersion) => v.recommended);
          if (recommended) {
            setSelectedKitVersion(recommended.version);
          } else if (data.versions.length > 0) {
            setSelectedKitVersion(data.versions[0].version);
          }
        }
      } catch (err) {
        console.error('[ProjectConfig] Failed to fetch Kit versions:', err);
      } finally {
        setIsLoadingVersions(false);
      }
    };

    fetchKitVersions();
  }, []);

  // Detect if template is a streaming template (matches logic from TemplateCard)
  const isStreamingTemplate = React.useMemo(() => {
    const streamingKeywords = ['streaming', 'webrtc', 'remote'];
    const nameMatch = streamingKeywords.some(kw =>
      template.name.toLowerCase().includes(kw) ||
      (template.displayName && template.displayName.toLowerCase().includes(kw))
    );
    const tagsMatch = template.tags && streamingKeywords.some(kw =>
      template.tags.some(tag => tag.toLowerCase().includes(kw))
    );
    return nameMatch || tagsMatch;
  }, [template.name, template.displayName, template.tags]);

  // Auto-select streaming layer for streaming templates
  React.useEffect(() => {
    if (isStreamingTemplate && layersData && layersData.layers.length > 0) {
      // Find the default streaming layer (omni_default_streaming)
      const defaultStreamingLayer = layersData.layers.find(
        layer => layer.name === 'omni_default_streaming'
      );

      if (defaultStreamingLayer && !selectedLayers.includes(defaultStreamingLayer.name)) {
        console.log('[ProjectConfig] Auto-selecting streaming layer for template:', template.name);
        setSelectedLayers([defaultStreamingLayer.name]);
      }
    }
  }, [isStreamingTemplate, layersData, template.name]); // Intentionally exclude selectedLayers to run only once

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
      console.log('[ProjectConfig] Starting project creation:', {
        template: template.name,
        projectName,
        displayName,
        selectedLayers,
        kitVersion: selectedKitVersion,
      });

      const response = await apiService.createProject({
        template: template.name,
        name: projectName,
        displayName: displayName || projectName,
        layers: selectedLayers.length > 0 ? selectedLayers : undefined,
        kitVersion: selectedKitVersion || undefined,
      });

      console.log('[ProjectConfig] Received response:', response);

      if (response.success && response.projectInfo) {
        console.log('[ProjectConfig] Project created successfully, opening editor');
        const { openPanel } = usePanelStore.getState();

        // Close project-config and template-detail panels
        const configPanels = getPanelsByType('project-config');
        const detailPanels = getPanelsByType('template-detail');

        console.log('[ProjectConfig] Closing panels:', {
          configPanels: configPanels.length,
          detailPanels: detailPanels.length,
        });

        if (configPanels.length > 0) {
          closePanel(configPanels[configPanels.length - 1].id);
        }
        if (detailPanels.length > 0) {
          closePanel(detailPanels[detailPanels.length - 1].id);
        }

        // Open code editor panel with the .kit file
        // User can click "Build" to open the build output panel and start a build
        console.log('[ProjectConfig] Opening code-editor panel with:', {
          filePath: response.projectInfo.kitFile,
          fileName: `${response.projectInfo.projectName}.kit`,
          projectName: response.projectInfo.projectName,
        });

        openPanel('code-editor', {
          filePath: response.projectInfo.kitFile,
          fileName: `${response.projectInfo.projectName}.kit`,
          projectName: response.projectInfo.projectName,
        });

        console.log('[ProjectConfig] Project creation complete');
      } else {
        console.error('[ProjectConfig] Project creation failed:', response.error);
        setError(response.error || 'Failed to create project');
      }
    } catch (err) {
      console.error('[ProjectConfig] Exception during project creation:', err);
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      console.log('[ProjectConfig] Setting isCreating to false');
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

          {/* Kit SDK Version */}
          <div>
            <label className="flex items-center gap-2 text-sm font-semibold text-text-primary mb-2">
              <Package className="w-4 h-4" />
              Kit SDK Version *
            </label>
            {isLoadingVersions ? (
              <div className="
                w-full px-4 py-3 rounded-lg
                bg-bg-card border border-border-subtle
                text-text-muted
                flex items-center gap-2
              ">
                <Sparkles className="w-4 h-4 animate-spin" />
                Loading Kit SDK versions...
              </div>
            ) : (
              <select
                value={selectedKitVersion}
                onChange={(e) => setSelectedKitVersion(e.target.value)}
                disabled={isCreating}
                className="
                  w-full px-4 py-3 rounded-lg
                  bg-bg-card border border-border-subtle
                  text-text-primary
                  focus:outline-none focus:ring-2 focus:ring-nvidia-green focus:border-transparent
                  disabled:opacity-50 disabled:cursor-not-allowed
                  transition-all
                  cursor-pointer
                "
              >
                {kitVersions.map((kitVer) => (
                  <option key={kitVer.version} value={kitVer.version}>
                    {kitVer.label} {kitVer.recommended ? '(Recommended)' : ''}
                  </option>
                ))}
              </select>
            )}
            <p className="mt-2 text-xs text-text-muted">
              Choose the Omniverse Kit SDK version for your project. Each project can use a different Kit version.
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

          {/* Application Layers */}
          {template.type === 'application' && layersData && layersData.count > 0 && (
            <div className="border border-border-subtle rounded-lg p-4 space-y-4">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-nvidia-green" />
                <h3 className="text-sm font-semibold text-text-primary">
                  Application Layers
                </h3>
              </div>
              <p className="text-xs text-text-muted">
                Layers add additional functionality to your base application (e.g., streaming capabilities).
                They create separate .kit files that depend on your base application.
              </p>

              {/* Streaming Layers */}
              {layersData.categorized.streaming && layersData.categorized.streaming.length > 0 && (
                <div>
                  <h4 className="text-xs font-medium text-text-secondary uppercase tracking-wide mb-2">
                    Streaming
                  </h4>
                  <div className="space-y-2">
                    {layersData.categorized.streaming.map((layer: any) => (
                      <label
                        key={layer.name}
                        className="flex items-start gap-3 cursor-pointer group p-3 rounded-lg hover:bg-bg-card-hover transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={selectedLayers.includes(layer.name)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedLayers([...selectedLayers, layer.name]);
                            } else {
                              setSelectedLayers(selectedLayers.filter(l => l !== layer.name));
                            }
                          }}
                          disabled={isCreating}
                          className="
                            mt-1 w-4 h-4 rounded
                            border-border-subtle
                            text-nvidia-green
                            focus:ring-2 focus:ring-nvidia-green
                            disabled:opacity-50 disabled:cursor-not-allowed
                          "
                        />
                        <div className="flex-1">
                          <div className="text-sm font-medium text-text-primary">
                            {layer.display_name}
                          </div>
                          <div className="text-xs text-text-muted mt-1">
                            {layer.description}
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {isLoadingLayers && (
                <div className="text-xs text-text-muted flex items-center gap-2">
                  <Sparkles className="w-4 h-4 animate-spin" />
                  Loading available layers...
                </div>
              )}
            </div>
          )}

          {/* Advanced Options - REMOVED
              All options removed due to issues:
              - "Enable Kit App Streaming" → DEPRECATED, use Application Layers instead
              - "Per-Application Dependencies" → Untested, unclear if it works
              - "Create as Standalone Project" → Has upstream bugs (see test_api_argument_mapping.py @xfail)
          */}
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
