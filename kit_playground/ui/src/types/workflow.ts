/**
 * Workflow State Types
 * Defines the progressive disclosure workflow for the Kit Playground
 */

export type WorkflowStep =
  | 'browse'      // Browsing templates/projects
  | 'edit'        // Editing code, building
  | 'preview';    // Running and previewing

export interface WorkflowState {
  step: WorkflowStep;
  selectedTemplate: string | null;
  selectedProject: string | null;
  isRunning: boolean;
  canGoBack: boolean;
  canGoForward: boolean;
}

export type StatusState = 'success' | 'failed' | undefined;

export interface ProjectStatus {
  created?: StatusState;      // undefined | 'success' | 'failed'
  built?: StatusState;         // undefined | 'success' | 'failed'
  launched?: StatusState;      // undefined | 'success' | 'failed'
  isBuilding?: boolean;        // Currently building
  isRunning?: boolean;         // Currently running
  lastBuildTime?: string;
  lastLaunchTime?: string;
}

export interface WorkflowNode {
  id: string;
  label: string;
  type: 'template' | 'project' | 'category';
  icon?: string;
  children?: WorkflowNode[];
  expanded?: boolean;
  status?: ProjectStatus;  // Only for projects
}
