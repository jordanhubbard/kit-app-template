import React from 'react';
import { ArrowLeft, FileText, Sparkles, Package, Copy, ExternalLink } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import type { TemplateModel } from '../../hooks/useTemplates';

interface TemplateDetailProps {
  template: TemplateModel;
}

/**
 * TemplateDetail
 *
 * Enhanced template detail view (Panel 2).
 * Shows comprehensive information about a template and allows
 * quick project creation.
 *
 * Features:
 * - Large preview image
 * - Detailed description
 * - Feature list
 * - Requirements
 * - Quick create button
 * - Links to documentation
 */
export const TemplateDetail: React.FC<TemplateDetailProps> = ({ template }) => {
  const { closePanel, openPanel, getPanelsByType } = usePanelStore();

  const handleCreateClick = () => {
    // Open project config panel (Phase 3)
    openPanel('project-config', { template });
  };

  const handleBack = () => {
    // Get the current template-detail panel and close it
    const panels = getPanelsByType('template-detail');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
  };

  const typeColor = {
    application: 'text-nvidia-green',
    extension: 'text-blue-400',
    microservice: 'text-purple-400',
  }[template.type];

  const typeBg = {
    application: 'bg-nvidia-green/10 border-nvidia-green/30',
    extension: 'bg-blue-500/10 border-blue-500/30',
    microservice: 'bg-purple-500/10 border-purple-500/30',
  }[template.type];

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Back Button */}
      <div className="p-4 border-b border-border-subtle">
        <button
          onClick={handleBack}
          className="
            flex items-center gap-2 px-3 py-2 rounded
            text-text-secondary hover:text-text-primary
            hover:bg-bg-card
            transition-colors
          "
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back to Templates</span>
        </button>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Hero Section */}
          <div>
            {/* Template Icon/Thumbnail */}
            <div className="relative h-48 rounded-lg overflow-hidden mb-4 bg-gradient-to-br from-bg-card to-bg-panel">
              {template.thumbnail ? (
                <img
                  src={template.thumbnail}
                  alt={template.displayName || template.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className={`text-8xl ${typeColor} opacity-30`}>
                    {template.icon || '📦'}
                  </div>
                </div>
              )}

              {/* Type Badge (Large) */}
              <div className="absolute top-4 right-4">
                <div className={`
                  px-4 py-2 rounded-lg border
                  ${typeBg} ${typeColor}
                  backdrop-blur-sm
                  font-semibold capitalize
                `}>
                  {template.type}
                </div>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              {template.displayName || template.name}
            </h1>

            {/* Description */}
            <p className="text-text-secondary leading-relaxed">
              {template.description || 'No description available.'}
            </p>
          </div>

          {/* Stats */}
          {(template.usageCount !== undefined && template.usageCount > 0) && (
            <div className={`
              p-4 rounded-lg border
              ${typeBg}
            `}>
              <div className="flex items-center gap-3">
                <div className="text-2xl">🔥</div>
                <div>
                  <div className={`text-lg font-semibold ${typeColor}`}>
                    {template.usageCount} times created
                  </div>
                  <div className="text-xs text-text-muted">
                    Popular template in the community
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tags */}
          {template.tags && template.tags.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-text-secondary mb-2 uppercase tracking-wide">
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {template.tags.map((tag) => (
                  <span
                    key={tag}
                    className="
                      px-3 py-1.5 rounded-lg
                      bg-bg-card border border-border-subtle
                      text-text-primary text-sm
                    "
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Features (Would come from template metadata) */}
          <div>
            <h3 className="text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wide flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              What's Included
            </h3>
            <ul className="space-y-2">
              <li className="flex items-start gap-3 text-text-primary">
                <span className="text-nvidia-green mt-0.5">✓</span>
                <span>Complete project structure and configuration</span>
              </li>
              <li className="flex items-start gap-3 text-text-primary">
                <span className="text-nvidia-green mt-0.5">✓</span>
                <span>Build and launch scripts</span>
              </li>
              <li className="flex items-start gap-3 text-text-primary">
                <span className="text-nvidia-green mt-0.5">✓</span>
                <span>Sample code and documentation</span>
              </li>
              {template.type === 'application' && (
                <li className="flex items-start gap-3 text-text-primary">
                  <span className="text-nvidia-green mt-0.5">✓</span>
                  <span>Kit SDK integration and dependencies</span>
                </li>
              )}
            </ul>
          </div>

          {/* Requirements */}
          <div>
            <h3 className="text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wide flex items-center gap-2">
              <Package className="w-4 h-4" />
              Requirements
            </h3>
            <ul className="space-y-2 text-text-primary">
              <li className="flex items-start gap-3">
                <span className="text-text-muted">•</span>
                <span>NVIDIA Omniverse Kit SDK</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-text-muted">•</span>
                <span>Python 3.10 or newer</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-text-muted">•</span>
                <span>Git for version control</span>
              </li>
            </ul>
          </div>

          {/* Documentation Links (Placeholder) */}
          <div>
            <h3 className="text-sm font-semibold text-text-secondary mb-3 uppercase tracking-wide flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Documentation
            </h3>
            <div className="space-y-2">
              <a
                href="#"
                className="
                  flex items-center justify-between p-3 rounded-lg
                  bg-bg-card border border-border-subtle
                  hover:border-nvidia-green
                  text-text-primary hover:text-nvidia-green
                  transition-colors
                  group
                "
              >
                <span>Template README</span>
                <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
              <a
                href="#"
                className="
                  flex items-center justify-between p-3 rounded-lg
                  bg-bg-card border border-border-subtle
                  hover:border-nvidia-green
                  text-text-primary hover:text-nvidia-green
                  transition-colors
                  group
                "
              >
                <span>Kit SDK Documentation</span>
                <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="p-4 border-t border-border-subtle bg-bg-dark">
        <div className="flex gap-2">
          <button
            onClick={handleCreateClick}
            className="
              flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg
              bg-nvidia-green hover:bg-nvidia-green-dark
              text-white font-semibold
              transition-colors
            "
          >
              <Sparkles className="w-5 h-5" />
            Create Application
          </button>

          <button
            onClick={() => {
              // Copy template name to clipboard
              navigator.clipboard.writeText(template.name);
            }}
            className="
              px-4 py-3 rounded-lg
              bg-bg-card hover:bg-bg-card-hover
              border border-border-subtle
              text-text-secondary hover:text-text-primary
              transition-colors
            "
            title="Copy template name"
          >
            <Copy className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs text-text-muted text-center mt-3">
          Click "Create Application" to configure and generate your project
        </p>
      </div>
    </div>
  );
};
