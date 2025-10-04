/**
 * Main Layout - Workflow-Based Design
 * Progressive disclosure UI with sliding panels
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Box } from '@mui/material';
import SlidingPanelLayout from './SlidingPanelLayout';
import WorkflowSidebar from './WorkflowSidebar';
import WorkflowBreadcrumbs from './WorkflowBreadcrumbs';
import TemplateGallery from '../gallery/TemplateGallery';
import CodeEditor from '../editor/CodeEditor';
import PreviewPane from '../preview/PreviewPane';
import Console from '../console/Console';
import StatusBar from './StatusBar';
import FileExplorer from '../controls/FileExplorer';
import { WorkflowStep, WorkflowNode } from '../../types/workflow';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { setOutputPath } from '../../store/slices/projectSlice';

const MainLayoutWorkflow: React.FC = () => {
  const dispatch = useAppDispatch();
  const { currentProject, isBuilding, isRunning } = useAppSelector(state => state.project);

  // Workflow state
  const [workflowStep, setWorkflowStep] = useState<WorkflowStep>('browse');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [history, setHistory] = useState<WorkflowStep[]>(['browse']);
  const [historyIndex, setHistoryIndex] = useState(0);

  // Editor state
  const [editorContent, setEditorContent] = useState<string>('');
  const [outputPath, setOutputPathLocal] = useState<string>('');
  const [previewUrl, setPreviewUrl] = useState<string>('');

  // Load user projects from API
  const projectNodes = useMemo((): WorkflowNode[] => {
    // TODO: Load user projects from API
    // For now, return empty array - projects will be added when users create them
    return [];
  }, []);

  // Navigation handlers
  const navigateToStep = useCallback((step: WorkflowStep) => {
    setWorkflowStep(step);
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(step);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  }, [history, historyIndex]);

  const navigateBack = useCallback(() => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setWorkflowStep(history[newIndex]);
    }
  }, [history, historyIndex]);

  const navigateForward = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setWorkflowStep(history[newIndex]);
    }
  }, [history, historyIndex]);

  const navigateHome = useCallback(() => {
    navigateToStep('browse');
    setSelectedTemplate(null);
    setSelectedProject(null);
  }, [navigateToStep]);

  // Sidebar node selection (only for projects)
  const handleSelectNode = useCallback((node: WorkflowNode) => {
    if (node.type === 'project') {
      setSelectedProject(node.id);
      setSelectedTemplate(null);
      // TODO: Load project files
      navigateToStep('edit');
    }
    // Categories are not selectable, just expand/collapse
  }, [navigateToStep]);

  // Template/Project operations
  const loadTemplate = useCallback(async (templateId: string) => {
    try {
      const response = await fetch(`/api/templates/${templateId}/code`);
      const code = await response.text();
      setEditorContent(code);
    } catch (error) {
      console.error('Failed to load template:', error);
    }
  }, []);

  const handleCodeChange = useCallback((newCode: string) => {
    setEditorContent(newCode);
  }, []);

  const handleBuild = useCallback(async () => {
    if (!selectedTemplate && !selectedProject) return;
    // TODO: Call build API
    console.log('Building...');
  }, [selectedTemplate, selectedProject]);

  const handleRun = useCallback(async () => {
    if (!selectedTemplate && !selectedProject) return;
    // TODO: Call run API and set preview URL
    setPreviewUrl('http://localhost:10000'); // Example Xpra URL
    navigateToStep('preview');
  }, [selectedTemplate, selectedProject, navigateToStep]);

  const handleStop = useCallback(() => {
    setPreviewUrl('');
    navigateToStep('edit');
  }, [navigateToStep]);

  const handleCreateProject = useCallback((projectInfo: any) => {
    console.log('Project created:', projectInfo);
    // Refresh project list
    // TODO: Load new project
  }, []);

  // Get current selection for breadcrumbs
  const getSelectedId = () => {
    if (workflowStep === 'browse') return null;
    return selectedProject || selectedTemplate;
  };

  // Render panels
  const renderBrowsePanel = () => (
    <Box sx={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <TemplateGallery
        onSelectTemplate={(id) => {
          // Just select the template, don't navigate yet
          setSelectedTemplate(id);
        }}
        selectedTemplate={selectedTemplate}
        onCreateProject={(projectInfo) => {
          handleCreateProject(projectInfo);
          // Load the template code for editing
          if (selectedTemplate) {
            loadTemplate(selectedTemplate);
          }
          navigateToStep('edit');
        }}
      />
    </Box>
  );

  const renderEditPanel = () => (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Editor and build controls */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <CodeEditor
          value={editorContent}
          onChange={handleCodeChange}
          language="python"
          templateId={selectedTemplate}
          readOnly={false}
        />
      </Box>

      {/* File browser at bottom */}
      <Box
        sx={{
          height: 200,
          borderTop: 1,
          borderColor: 'divider',
          overflow: 'hidden',
        }}
      >
        <FileExplorer
          selectedPath={outputPath}
          onPathChange={(path) => {
            setOutputPathLocal(path);
            dispatch(setOutputPath(path));
          }}
          title="Project Files"
          showFiles={true}
        />
      </Box>
    </Box>
  );

  const renderPreviewPanel = () => (
    <Box sx={{ width: '100%', height: '100%' }}>
      {previewUrl ? (
        <PreviewPane
          url={previewUrl}
          templateId={selectedTemplate}
          mode="xpra"
        />
      ) : (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            color: 'text.secondary',
          }}
        >
          Click "Run" to start preview
        </Box>
      )}
    </Box>
  );

  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        backgroundColor: '#1e1e1e',
      }}
    >
      {/* Breadcrumb Navigation */}
      <WorkflowBreadcrumbs
        step={workflowStep}
        selectedTemplate={selectedTemplate}
        selectedProject={selectedProject}
        canGoBack={historyIndex > 0}
        canGoForward={historyIndex < history.length - 1}
        onNavigateBack={navigateBack}
        onNavigateForward={navigateForward}
        onNavigateHome={navigateHome}
        onNavigateToStep={navigateToStep}
      />

      {/* Main content with sidebar */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Sidebar - Only show projects, not templates */}
        <WorkflowSidebar
          templates={[]}
          projects={projectNodes}
          selectedId={getSelectedId()}
          onSelectNode={handleSelectNode}
        />

        {/* Sliding panels */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            <SlidingPanelLayout
              step={workflowStep}
              browsePanel={renderBrowsePanel()}
              editPanel={renderEditPanel()}
              previewPanel={renderPreviewPanel()}
            />
          </Box>

          {/* Console at bottom */}
          <Box sx={{ height: 200, borderTop: 1, borderColor: 'divider' }}>
            <Console height={200} />
          </Box>
        </Box>
      </Box>

      {/* Status Bar */}
      <StatusBar />
    </Box>
  );
};

export default MainLayoutWorkflow;
