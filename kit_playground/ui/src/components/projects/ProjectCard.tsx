import React from 'react';
import { Play, Hammer, Trash2, FileText, Download } from 'lucide-react';
import type { Project } from '../../hooks/useProjects';
import { useDependencies } from '../../hooks/useDependencies';
import { StatusBadge } from '../common';

interface ProjectCardProps {
  project: Project;
  onBuild?: (project: Project) => void;
  onLaunch?: (project: Project) => void;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
  onPrepare?: () => void;
}


/**
 * ProjectCard
 *
 * Card component for displaying user-created projects.
 * Shows project info and quick actions.
 */
export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onBuild,
  onLaunch,
  onEdit,
  onDelete,
  onPrepare,
}) => {
  const { status: depStatus } = useDependencies();

  const typeColor = {
    application: 'text-nvidia-green',
    extension: 'text-blue-400',
    microservice: 'text-purple-400',
  }[project.type];

  // Check if this is a streaming app and dependencies aren't cached
  const isStreamingApp = project.name.includes('streaming') || project.template?.includes('streaming');
  const showDepWarning = isStreamingApp && depStatus && !depStatus.cached;

  return (
    <div className="
      p-4 rounded-lg
      bg-bg-card border border-border-subtle
      hover:border-nvidia-green/50
      transition-all
      group
    ">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-text-primary mb-1 truncate">
            {project.displayName}
          </h3>
          <p className="text-xs text-text-muted">
            {project.name}
          </p>
        </div>

        {/* Status Badge */}
        <StatusBadge status={project.status} size="sm" />
      </div>

      {/* Info */}
      <div className="flex items-center gap-4 mb-3 text-xs text-text-muted">
        <div className={`flex items-center gap-1 ${typeColor}`}>
          <span className="capitalize">{project.type}</span>
        </div>
        <div>
          Template: {project.template}
        </div>
      </div>

      {/* Metadata */}
      <div className="text-xs text-text-muted mb-4">
        <div>Modified: {formatDate(project.lastModified)}</div>
        <div className="truncate">Path: {project.path}</div>
      </div>

      {/* Dependency Warning */}
      {showDepWarning && (
        <div className="mb-3 p-2 bg-yellow-900 bg-opacity-30 border border-yellow-600 rounded text-xs">
          <div className="flex items-center gap-2 text-yellow-400 mb-1">
            <Download className="w-3 h-3" />
            <span className="font-medium">Dependencies Not Cached</span>
          </div>
          <p className="text-yellow-300 text-xs mb-2">
            First launch may take 5-10 minutes while downloading extensions.
          </p>
          {onPrepare && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPrepare();
              }}
              className="text-yellow-400 hover:text-yellow-300 underline text-xs"
            >
              Prepare now →
            </button>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        {onBuild && (
          <button
            onClick={() => onBuild(project)}
            disabled={project.status === 'running'}
            className="
              flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded
              bg-nvidia-green/10 hover:bg-nvidia-green/20
              border border-nvidia-green/30 hover:border-nvidia-green
              text-nvidia-green text-sm font-medium
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            "
            title="Build project"
          >
            <Hammer className="w-4 h-4" />
            Build
          </button>
        )}

        {onLaunch && (
          <button
            onClick={() => onLaunch(project)}
            disabled={project.status !== 'built'}
            className="
              flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded
              bg-status-info/10 hover:bg-status-info/20
              border border-status-info/30 hover:border-status-info
              text-status-info text-sm font-medium
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            "
            title="Launch application"
          >
            <Play className="w-4 h-4" />
            Launch
          </button>
        )}

        {onEdit && (
          <button
            onClick={() => onEdit(project)}
            className="
              px-3 py-2 rounded
              bg-bg-panel hover:bg-bg-card-hover
              border border-border-subtle hover:border-text-secondary
              text-text-secondary hover:text-text-primary
              transition-colors
            "
            title="Edit .kit file"
          >
            <FileText className="w-4 h-4" />
          </button>
        )}

        {onDelete && (
          <button
            onClick={() => onDelete(project)}
            disabled={project.status === 'running'}
            className="
              px-3 py-2 rounded
              bg-bg-panel hover:bg-status-error/10
              border border-border-subtle hover:border-status-error
              text-text-secondary hover:text-status-error
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-colors
            "
            title="Delete project"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Format date for display
 */
function formatDate(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}
