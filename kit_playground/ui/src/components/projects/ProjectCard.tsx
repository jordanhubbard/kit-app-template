import React from 'react';
import { Play, Hammer, Trash2, FileText, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import type { Project } from '../../hooks/useProjects';

interface ProjectCardProps {
  project: Project;
  onBuild?: (project: Project) => void;
  onLaunch?: (project: Project) => void;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
}

/**
 * Get status badge styling and icon
 */
const getStatusConfig = (status: Project['status']) => {
  switch (status) {
    case 'created':
      return {
        icon: <Clock className="w-4 h-4" />,
        color: 'text-text-muted',
        bg: 'bg-bg-card',
        label: 'Created',
      };
    case 'built':
      return {
        icon: <CheckCircle className="w-4 h-4" />,
        color: 'text-status-success',
        bg: 'bg-status-success/10',
        label: 'Built',
      };
    case 'running':
      return {
        icon: <Loader className="w-4 h-4 animate-spin" />,
        color: 'text-status-info',
        bg: 'bg-status-info/10',
        label: 'Running',
      };
    case 'failed':
      return {
        icon: <XCircle className="w-4 h-4" />,
        color: 'text-status-error',
        bg: 'bg-status-error/10',
        label: 'Failed',
      };
  }
};

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
}) => {
  const statusConfig = getStatusConfig(project.status);
  
  const typeColor = {
    application: 'text-nvidia-green',
    extension: 'text-blue-400',
    microservice: 'text-purple-400',
  }[project.type];

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
        <div className={`
          flex items-center gap-1.5 px-2 py-1 rounded
          ${statusConfig.bg} ${statusConfig.color}
          text-xs font-medium
        `}>
          {statusConfig.icon}
          <span>{statusConfig.label}</span>
        </div>
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

