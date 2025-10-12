/**
 * Main Layout - Workflow-Based Design
 * Progressive disclosure UI with sliding panels
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Box, Toolbar, IconButton, Tooltip, Typography, Divider, Checkbox, FormControlLabel, Button } from '@mui/material';
import {
  Build as BuildIcon,
  PlayArrow as RunIcon,
  Stop as StopIcon,
  Save as SaveIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material';
import SlidingPanelLayout from './SlidingPanelLayout';
import WorkflowSidebar from './WorkflowSidebar';
import WorkflowBreadcrumbs from './WorkflowBreadcrumbs';
import TemplateGallery from '../gallery/TemplateGallery';
import CodeEditor from '../editor/CodeEditor';
import Console from '../console/Console';
import StatusBar from './StatusBar';
import FileExplorer from '../controls/FileExplorer';
import PreviewPane from '../preview/PreviewPane';
import { WorkflowStep, WorkflowNode } from '../../types/workflow';
import { useAppDispatch } from '../../hooks/redux';
import { setOutputPath } from '../../store/slices/projectSlice';
import { emitConsoleLog } from '../console/Console';

const MainLayoutWorkflow: React.FC = () => {
  const dispatch = useAppDispatch();

  // Workflow state
  const [workflowStep, setWorkflowStep] = useState<WorkflowStep>('browse');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [history, setHistory] = useState<WorkflowStep[]>(['browse']);
  const [historyIndex, setHistoryIndex] = useState(0);

  // Path state
  const [templatesPath, setTemplatesPath] = useState<string>('templates');
  const [projectsPath, setProjectsPath] = useState<string>('_build/apps');

  // Editor state
  const [editorContent, setEditorContent] = useState<string>('');
  const [outputPath, setOutputPathLocal] = useState<string>('');
  const [isBuilding, setIsBuilding] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [currentProjectPath, setCurrentProjectPath] = useState<string>('');
  const [useXpra, setUseXpra] = useState(true);  // Default to true for Browser Preview
  const [previewUrl, setPreviewUrl] = useState<string>('');

  // Templates and projects state
  const [templates, setTemplates] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);

  // Load default paths from backend
  const loadDefaultPaths = useCallback(async () => {
    try {
      const response = await fetch('/api/config/paths');
      const data = await response.json();
      setTemplatesPath(data.templatesPath);
      setProjectsPath(data.projectsPath);
    } catch (error) {
      console.error('Failed to load default paths:', error);
    }
  }, []);

  // Load templates from API
  const loadTemplatesData = useCallback(async () => {
    try {
      const response = await fetch('/api/v2/templates');
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
      setTemplates([]);
    }
  }, []);

  // Load projects from backend
  const loadProjectsData = useCallback(async () => {
    try {
      const response = await fetch(`/api/projects/discover?path=${encodeURIComponent(projectsPath)}`);
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      setProjects([]);
    }
  }, [projectsPath]);

  // Load default paths on mount
  React.useEffect(() => {
    loadDefaultPaths();
  }, [loadDefaultPaths]);

  // Load templates when path changes
  React.useEffect(() => {
    loadTemplatesData();
  }, [loadTemplatesData, templatesPath]);

  // Load projects when path changes
  React.useEffect(() => {
    loadProjectsData();
  }, [loadProjectsData, projectsPath]);

  // Convert templates to WorkflowNode tree structure
  const templateNodes = useMemo((): WorkflowNode[] => {
    if (templates.length === 0) return [];

    // Group templates by type
    const applicationTemplates = templates.filter(t => t.type === 'application');
    const extensionTemplates = templates.filter(t => t.type === 'extension');
    const serviceTemplates = templates.filter(t => t.type === 'microservice');

    const nodes: WorkflowNode[] = [];

    // Applications category
    if (applicationTemplates.length > 0) {
      nodes.push({
        id: 'cat-applications',
        label: `Applications (${applicationTemplates.length})`,
        type: 'category',
        children: applicationTemplates.map(t => ({
          id: t.id || t.name,
          label: t.displayName || t.display_name,
          type: 'template' as const,
        })),
      });
    }

    // Extensions category
    if (extensionTemplates.length > 0) {
      nodes.push({
        id: 'cat-extensions',
        label: `Extensions (${extensionTemplates.length})`,
        type: 'category',
        children: extensionTemplates.map(t => ({
          id: t.id || t.name,
          label: t.displayName || t.display_name,
          type: 'template' as const,
        })),
      });
    }

    // Services category
    if (serviceTemplates.length > 0) {
      nodes.push({
        id: 'cat-services',
        label: `Services (${serviceTemplates.length})`,
        type: 'category',
        children: serviceTemplates.map(t => ({
          id: t.id || t.name,
          label: t.displayName || t.display_name,
          type: 'template' as const,
        })),
      });
    }

    return nodes;
  }, [templates]);

  // Convert projects to WorkflowNode format with status indicators
  const projectNodes = useMemo((): WorkflowNode[] => {
    return projects.map(project => {
      // Add status icon to label
      let statusIcon = '';
      if (project.status === 'ready') {
        statusIcon = '✓ ';
      } else if (project.status === 'building') {
        statusIcon = '⚙ ';
      } else if (project.status === 'running') {
        statusIcon = '▶ ';
      } else if (project.status === 'error') {
        statusIcon = '✗ ';
      }

      return {
        id: project.id,
        label: `${statusIcon}${project.displayName}`,
        type: 'project' as const,
      };
    });
  }, [projects]);

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

  // Sidebar node selection
  const handleSelectNode = useCallback((node: WorkflowNode) => {
    if (node.type === 'template') {
      setSelectedTemplate(node.id);
      setSelectedProject(null);
      // Navigate to browse to show template details
      navigateToStep('browse');
    } else if (node.type === 'project') {
      setSelectedProject(node.id);
      setSelectedTemplate(null);

      // Load project files
      const project = projects.find(p => p.id === node.id);
      if (project) {
        setCurrentProjectPath(project.path);
        emitConsoleLog('info', 'system', `Loading project: ${project.displayName}`);
        emitConsoleLog('info', 'system', `Reading file: ${project.kitFile}`);

        // Try to load the .kit file
        fetch(`/api/filesystem/read?path=${encodeURIComponent(project.kitFile)}`)
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.text();
          })
          .then(content => {
            setEditorContent(content);
            setOutputPathLocal(project.path);
            emitConsoleLog('success', 'system', `Successfully loaded project: ${project.displayName}`);
          })
          .catch(error => {
            console.error('Failed to load project file:', error);
            emitConsoleLog('error', 'system', `Failed to load project file: ${error.message}`);
            setEditorContent(`# ${project.displayName}
#
# Failed to load project configuration file
# File: ${project.kitFile}
# Error: ${error.message}
#
# Troubleshooting:
# 1. Verify the file exists at the path shown above
# 2. Check file permissions
# 3. Try refreshing the Projects list
# 4. Check the console output for more details
`);
          });
      }

      navigateToStep('edit');
    }
    // Categories are not selectable, just expand/collapse
  }, [navigateToStep, projects]);

  // Template/Project operations
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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

  const handleSave = useCallback(async () => {
    if (!currentProjectPath) return;

    try {
      // TODO: Implement save via API
      console.log('Saving project...');
    } catch (error) {
      console.error('Failed to save:', error);
    }
  }, [currentProjectPath]);

  const handleBuild = useCallback(async () => {
    if (!selectedProject || !currentProjectPath) return;

    setIsBuilding(true);
    emitConsoleLog('info', 'build', `Starting build for ${selectedProject}...`);

    try {
      // Call repo.sh build command via API
      const response = await fetch('/api/projects/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectPath: currentProjectPath,
          projectName: selectedProject,
        }),
      });

      // Get response text first (can only read body once)
      const responseText = await response.text();

      // Check if response itself failed
      if (!response.ok) {
        emitConsoleLog('error', 'build', `Build request failed: ${responseText || response.statusText}`);
        return;
      }

      // Parse JSON response
      let result;
      try {
        result = JSON.parse(responseText);
      } catch (jsonError: any) {
        emitConsoleLog('error', 'build', `Invalid response from server: ${responseText.substring(0, 200)}`);
        console.error('JSON parse error:', jsonError, 'Response text:', responseText);
        return;
      }

      if (result.success) {
        emitConsoleLog('success', 'build', `Build completed successfully for ${selectedProject}`);
      } else {
        emitConsoleLog('error', 'build', `Build failed: ${result.error || 'Unknown error'}`);
        // Log the full result for debugging
        console.error('Build result:', result);
      }
    } catch (error: any) {
      emitConsoleLog('error', 'build', `Build error: ${error.message || error}`);
      console.error('Build error details:', error);
    } finally {
      setIsBuilding(false);
    }
  }, [selectedProject, currentProjectPath]);

  const handleRun = useCallback(async () => {
    if (!selectedProject || !currentProjectPath) return;

    setIsRunning(true);
    emitConsoleLog('info', 'runtime', `Launching ${selectedProject}...`);
    if (useXpra) {
      emitConsoleLog('info', 'runtime', 'Using Xpra for browser preview...');
    }

    try {
      // Build first, then run
      await handleBuild();

      // Call repo.sh launch command via API
      const response = await fetch('/api/projects/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectPath: currentProjectPath,
          projectName: selectedProject,
          useXpra: useXpra,  // Pass Xpra flag
        }),
      });

      const result = await response.json();
      console.log('[DEBUG] API response from /api/projects/run:', result);
      if (result.success) {
        emitConsoleLog('success', 'runtime', `Application launched: ${selectedProject}`);
        // Open Xpra preview in new tab if available
        if (result.previewUrl) {
          console.log('[DEBUG] Preview URL from API:', result.previewUrl);
          setPreviewUrl(result.previewUrl);

          emitConsoleLog('info', 'runtime', `Preview available at: ${result.previewUrl}`);
          emitConsoleLog('info', 'runtime', `Opening preview in new tab...`);

          // Open preview in new tab and focus it
          const previewWindow = window.open(result.previewUrl, '_blank');
          if (previewWindow) {
            previewWindow.focus();
            emitConsoleLog('success', 'runtime', `Preview opened in new tab`);
          } else {
            emitConsoleLog('warning', 'runtime', `Could not open preview tab (popup blocked?). Click the link to open manually.`);
          }

          // Navigate to preview panel which now shows "opened in new tab" message
          navigateToStep('preview');
        } else if (useXpra) {
          console.log('[DEBUG] No previewUrl in response');
          emitConsoleLog('warning', 'runtime', `Xpra preview not available. Check if Xpra is installed (see XPRA_SETUP.md)`);
        }
      } else {
        emitConsoleLog('error', 'runtime', `Launch failed: ${result.error || 'Unknown error'}`);
        setIsRunning(false);
      }
    } catch (error: any) {
      emitConsoleLog('error', 'runtime', `Run error: ${error.message || error}`);
      setIsRunning(false);
    }
  }, [selectedProject, currentProjectPath, handleBuild, navigateToStep, useXpra]);

  const handleStop = useCallback(async () => {
    if (!selectedProject) return;

    emitConsoleLog('info', 'runtime', `Stopping ${selectedProject}...`);

    try {
      const response = await fetch('/api/projects/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectName: selectedProject,
        }),
      });

      if (response.ok) {
        setIsRunning(false);
        emitConsoleLog('success', 'runtime', `Application stopped: ${selectedProject}`);
      } else {
        emitConsoleLog('error', 'runtime', `Failed to stop application`);
      }
    } catch (error: any) {
      emitConsoleLog('error', 'runtime', `Stop error: ${error.message || error}`);
    }
  }, [selectedProject]);

  const handleDeleteProject = useCallback(async (projectId: string) => {
    emitConsoleLog('info', 'system', `Deleting project: ${projectId}`);

    try {
      const response = await fetch('/api/projects/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectId: projectId,
          projectsPath: projectsPath,
        }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        emitConsoleLog('success', 'system', `Project deleted successfully: ${projectId}`);

        // Clear selection if deleted project was selected
        if (selectedProject === projectId) {
          setSelectedProject(null);
          setEditorContent('');
          setCurrentProjectPath('');
          navigateToStep('browse');
        }

        // Refresh projects list
        await loadProjectsData();
      } else {
        emitConsoleLog('error', 'system', `Failed to delete project: ${result.error || 'Unknown error'}`);
      }
    } catch (error: any) {
      emitConsoleLog('error', 'system', `Delete error: ${error.message || error}`);
    }
  }, [projectsPath, selectedProject, loadProjectsData, navigateToStep]);

  const handleCreateProject = useCallback(async (projectInfo: any) => {
    emitConsoleLog('info', 'build', `Creating project: ${projectInfo.displayName}`);

    // Store project info for build/run operations
    setSelectedProject(projectInfo.projectName);

    // Load the generated project's .kit configuration file (TOML)
    try {
      // Get repo root path from backend
      const configResponse = await fetch('/api/config/paths');

      if (!configResponse.ok) {
        throw new Error(`Failed to get config paths: ${configResponse.statusText}`);
      }

      const configData = await configResponse.json();

      if (!configData.repoRoot) {
        throw new Error('repoRoot not found in config response');
      }

      const repoRoot = configData.repoRoot;

      // Projects are created in _build/apps/{projectName}/ directory structure
      // The backend automatically moves them from source/apps (where omni.repo.man creates them)
      // to _build/apps with proper directory structure (as per repo.toml applications_path)
      const outputDir = projectInfo.outputDir || '_build/apps';

      // Use relative path for currentProjectPath (for build/run operations)
      const relativeProjectPath = `${outputDir}/${projectInfo.projectName}`;
      setCurrentProjectPath(relativeProjectPath);

      // Projects are created with flat structure: _build/apps/{name}/{name}.kit
      // Use kitFile path from API response (already includes full relative path)
      let kitFilePath: string;
      if (projectInfo.kitFile) {
        // API provides relative path like "_build/apps/name/name.kit"
        if (projectInfo.kitFile.startsWith('/')) {
          kitFilePath = projectInfo.kitFile;  // Already absolute
        } else {
          kitFilePath = `${repoRoot}/${projectInfo.kitFile}`;  // Make absolute
        }
      } else {
        // Fallback: construct flat structure path
        kitFilePath = `${repoRoot}/${relativeProjectPath}/${projectInfo.projectName}.kit`;
      }

      emitConsoleLog('info', 'build', `Loading project file: ${kitFilePath}`);

      // Try to read the .kit configuration file
      const response = await fetch(`/api/filesystem/read?path=${encodeURIComponent(kitFilePath)}`);

      if (response.ok) {
        const content = await response.text();
        setEditorContent(content);
        setOutputPathLocal(relativeProjectPath);
        emitConsoleLog('success', 'build', `Project created successfully: ${projectInfo.displayName}`);
        emitConsoleLog('info', 'build', `Project location: ${relativeProjectPath}`);

        // Refresh projects list so the new project appears in the sidebar
        loadProjectsData();
      } else {
        const errorText = await response.text();
        emitConsoleLog('warning', 'build', `Project created but configuration file not found: ${errorText}`);

        // Fallback: show a welcome message with project info
        emitConsoleLog('info', 'build', `File not found, showing welcome message`);
        emitConsoleLog('info', 'build', `Attempted to read: ${kitFilePath}`);
        setEditorContent(`# ${projectInfo.displayName}
#
# Project created successfully!
# Template: ${projectInfo.templateName}
# Location: ${relativeProjectPath}
#
# Your Kit application has been generated and is ready to use.
#
# Main configuration file: ${projectInfo.projectName}.kit
#
# Next steps:
# 1. Click on the project in the left sidebar to load the configuration
# 2. Click "Build" to compile your project
# 3. Click "Run" to launch your application
#
# Note: The project files are located in ${relativeProjectPath}/
`);
      }
    } catch (error: any) {
        emitConsoleLog('error', 'build', `Failed to load project files: ${error.message || error}`);

        const outputDir = projectInfo.outputDir || '_build/apps';
        const relPath = `${outputDir}/${projectInfo.projectName}`;

        setEditorContent(`# Project: ${projectInfo.displayName}
#
# Error loading configuration file.
# This may be because the project was created but the file path is incorrect.
#
# Expected location: ${relPath}/${projectInfo.projectName}.kit
#
# Please check the console output above for more details.
# You can also try:
# 1. Refresh the Projects section in the left sidebar
# 2. Click on your project to reload it
# 3. Run: cd ${relPath} && ls -la
`);
    }

    // Reload projects list to show the new project
    await loadProjectsData();
  }, [loadProjectsData]);

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
          // handleCreateProject already loads the project files
          handleCreateProject(projectInfo);
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
      {/* Editor */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <CodeEditor
          value={editorContent}
          onChange={handleCodeChange}
          language="toml"
          templateId={selectedProject || selectedTemplate}
          readOnly={false}
        />
      </Box>

      {/* Toolbar - MOVED BELOW EDITOR */}
      <Toolbar
        variant="dense"
        sx={{
          backgroundColor: '#252526',
          borderTop: 1,
          borderBottom: 1,
          borderColor: '#3e3e42',
          minHeight: 40,
          gap: 1,
          px: 2,
        }}
      >
        {/* Project Info - Moved to front */}
        <Typography
          variant="caption"
          sx={{
            color: '#cccccc',
            fontFamily: 'monospace',
            fontWeight: 500,
          }}
        >
          {selectedProject || 'No project selected'}
          {isBuilding && ' • Building...'}
          {isRunning && ' • Running'}
        </Typography>

        <Divider orientation="vertical" flexItem sx={{ mx: 1, backgroundColor: '#3e3e42' }} />

        {/* Save Button */}
        <Tooltip title="Save (Ctrl+S)">
          <IconButton
            size="small"
            onClick={handleSave}
            disabled={!currentProjectPath}
            sx={{ color: '#cccccc' }}
          >
            <SaveIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Divider orientation="vertical" flexItem sx={{ mx: 1, backgroundColor: '#3e3e42' }} />

        {/* Build Button */}
        <Tooltip title="Build project">
          <IconButton
            size="small"
            onClick={handleBuild}
            disabled={!currentProjectPath || isBuilding || isRunning}
            sx={{
              color: isBuilding ? '#4ec9b0' : '#cccccc',
              '&:hover': { backgroundColor: '#2d2d30' },
            }}
          >
            <BuildIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        {/* Run/Stop Button */}
        {!isRunning ? (
          <Tooltip title="Run (Build + Launch)">
            <IconButton
              size="small"
              onClick={handleRun}
              disabled={!currentProjectPath || isBuilding || isRunning}
              sx={{
                color: '#4ec9b0',
                '&:hover': { backgroundColor: '#2d2d30' },
              }}
            >
              <RunIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        ) : (
          <Tooltip title="Stop application">
            <IconButton
              size="small"
              onClick={handleStop}
              sx={{
                color: '#f48771',
                '&:hover': { backgroundColor: '#2d2d30' },
              }}
            >
              <StopIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}

        <Divider orientation="vertical" flexItem sx={{ mx: 1, backgroundColor: '#3e3e42' }} />

        {/* Browser Preview Checkbox */}
        <Tooltip title="Launch in browser using Xpra (requires Xpra to be installed)">
          <FormControlLabel
            control={
              <Checkbox
                checked={useXpra}
                onChange={(e) => setUseXpra(e.target.checked)}
                disabled={isBuilding || isRunning}
                size="small"
                sx={{
                  color: '#858585',
                  '&.Mui-checked': { color: '#4ec9b0' },
                }}
              />
            }
            label={
              <Typography variant="caption" sx={{ color: '#cccccc', userSelect: 'none' }}>
                Browser Preview
              </Typography>
            }
            sx={{ mr: 1 }}
          />
        </Tooltip>
      </Toolbar>

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

  const renderPreviewPanel = () => {
    if (!previewUrl) {
      return (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            width: '100%',
            color: 'text.secondary',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          <Typography variant="h6">No Preview Available</Typography>
          <Typography variant="body2">
            Run a project with Xpra enabled to see the preview
          </Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
        {/* Preview toolbar with stop button */}
        <Toolbar
          variant="dense"
          sx={{
            backgroundColor: '#2d2d30',
            borderBottom: 1,
            borderColor: 'divider',
            minHeight: 48,
            gap: 1,
          }}
        >
          <Typography variant="body2" sx={{ color: '#cccccc', mr: 2 }}>
            Application Preview
          </Typography>

          {/* Stop Button */}
          {isRunning && (
            <Tooltip title="Stop application">
              <IconButton
                size="small"
                onClick={handleStop}
                sx={{
                  color: '#f48771',
                  '&:hover': { backgroundColor: '#3e3e42' },
                }}
              >
                <StopIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}

          <Box sx={{ flex: 1 }} />

          {/* Preview URL display */}
          <Typography
            variant="caption"
            sx={{
              color: '#858585',
              fontFamily: 'monospace',
              px: 1,
              py: 0.5,
              backgroundColor: '#1e1e1e',
              borderRadius: 1,
            }}
          >
            {previewUrl}
          </Typography>

          {/* Open in new tab */}
          <Tooltip title="Open in new tab">
            <IconButton
              size="small"
              onClick={() => {
                const win = window.open(previewUrl, '_blank');
                if (win) win.focus();
              }}
              sx={{
                color: '#4ec9b0',
                '&:hover': { backgroundColor: '#3e3e42' },
              }}
            >
              <OpenInNewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Toolbar>

        {/* Preview message - opened in new tab */}
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 3,
            p: 4,
            backgroundColor: '#1e1e1e',
          }}
        >
          {/* Success icon */}
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <OpenInNewIcon sx={{ fontSize: 48, color: '#4caf50' }} />
          </Box>

          {/* Message */}
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ color: '#e0e0e0', mb: 1, fontWeight: 500 }}>
              Preview Opened in New Tab
            </Typography>
            <Typography variant="body1" sx={{ color: '#b0b0b0', mb: 3 }}>
              The application is running in a separate browser tab for full-screen interaction
            </Typography>
          </Box>

          {/* Action buttons */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<OpenInNewIcon />}
              onClick={() => {
                const win = window.open(previewUrl, '_blank');
                if (win) win.focus();
              }}
              sx={{
                backgroundColor: '#0e639c',
                '&:hover': { backgroundColor: '#1177bb' },
                textTransform: 'none',
                px: 3,
              }}
            >
              Reopen Preview Tab
            </Button>

            <Button
              variant="outlined"
              onClick={() => {
                navigator.clipboard.writeText(previewUrl);
                emitConsoleLog('info', 'system', 'Preview URL copied to clipboard');
              }}
              sx={{
                borderColor: '#3e3e42',
                color: '#cccccc',
                '&:hover': {
                  borderColor: '#4ec9b0',
                  backgroundColor: 'rgba(78, 201, 176, 0.08)',
                },
                textTransform: 'none',
                px: 3,
              }}
            >
              Copy URL
            </Button>
          </Box>

          {/* URL display */}
          <Box
            sx={{
              mt: 2,
              p: 2,
              backgroundColor: '#252526',
              borderRadius: 1,
              border: '1px solid #3e3e42',
            }}
          >
            <Typography
              variant="body2"
              sx={{
                fontFamily: 'monospace',
                color: '#4ec9b0',
                wordBreak: 'break-all',
              }}
            >
              {previewUrl}
            </Typography>
          </Box>

          {/* Help text */}
          <Box sx={{ mt: 2, textAlign: 'center', maxWidth: 600 }}>
            <Typography variant="caption" sx={{ color: '#858585' }}>
              💡 The application requires full screen space to interact properly.
              If the preview tab didn't open automatically, check your browser's popup blocker settings.
            </Typography>
          </Box>
        </Box>
      </Box>
    );
  };

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
        {/* Sidebar - Show templates and projects */}
        <WorkflowSidebar
          templates={templateNodes}
          projects={projectNodes}
          selectedId={getSelectedId()}
          templatesPath={templatesPath}
          projectsPath={projectsPath}
          onSelectNode={handleSelectNode}
          onTemplatesPathChange={(path) => {
            setTemplatesPath(path);
            loadTemplatesData();
          }}
          onProjectsPathChange={(path) => {
            setProjectsPath(path);
            loadProjectsData();
          }}
          onRefreshTemplates={loadTemplatesData}
          onRefreshProjects={loadProjectsData}
          onDeleteProject={handleDeleteProject}
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
