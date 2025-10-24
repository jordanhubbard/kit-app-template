/**
 * Main Layout Component with Split Panes for Side-by-Side Editing
 */

import React, { useState, useCallback, useRef } from 'react';
import { Box, IconButton, Tooltip, Tab, Tabs, Paper } from '@mui/material';
import {
  ViewModule as SplitViewIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Build as BuildIcon,
  Refresh as RefreshIcon,
  Fullscreen as FullscreenIcon,
  ViewSidebar as SidebarIcon,
  CloudDownload as DeployIcon,
  ContentCopy as CopyIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import TemplateBrowser from '../browser/TemplateBrowser';
import TemplateGallery from '../gallery/TemplateGallery';
import CodeEditor from '../editor/CodeEditor';
import PreviewPane from '../preview/PreviewPane';
import ConnectionEditor from '../connections/ConnectionEditor';
import Console from '../console/Console';
import StatusBar from './StatusBar';
import FileExplorer from '../controls/FileExplorer';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { setActiveView, toggleSidebar } from '../../store/slices/uiSlice';
import { setOutputPath } from '../../store/slices/projectSlice';
import './MainLayout.css';

type ViewMode = 'gallery' | 'browser' | 'editor' | 'connections' | 'split';

const MainLayout: React.FC = () => {
  const dispatch = useAppDispatch();
  const { activeView, sidebarVisible } = useAppSelector(state => state.ui);
  const { currentProject, isBuilding, isRunning } = useAppSelector(state => state.project);

  const [viewMode, setViewMode] = useState<ViewMode>('split');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [editorContent, setEditorContent] = useState<string>('');
  const [consoleHeight, setConsoleHeight] = useState(200);
  const [leftPaneSize, setLeftPaneSize] = useState<string | number>('50%');
  const [outputPath, setOutputPathLocal] = useState<string>('');

  const previewRef = useRef<any>(null);

  // Load template for editing and preview
  const loadTemplate = useCallback(async (templateId: string) => {
    try {
      // Fetch template code
      const response = await fetch(`/api/templates/${templateId}/code`);
      const code = await response.text();
      setEditorContent(code);

      // Set preview URL if template is running
      if (currentProject?.runningTemplates?.includes(templateId)) {
        setPreviewUrl(`http://localhost:8080/preview/${templateId}`);
      }
    } catch (error) {
      console.error('Failed to load template:', error);
    }
  }, [currentProject]);

  // Handle template selection from browser/gallery
  const handleTemplateSelect = useCallback((templateId: string) => {
    setSelectedTemplate(templateId);
    // Load template code and preview
    loadTemplate(templateId);
  }, [loadTemplate]);

  // Update preview with new code
  const updatePreview = useCallback(async (code: string) => {
    if (!selectedTemplate) return;

    try {
      await fetch(`/api/templates/${selectedTemplate}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      // Refresh preview
      if (previewRef.current) {
        previewRef.current.reload();
      }
    } catch (error) {
      console.error('Failed to update preview:', error);
    }
  }, [selectedTemplate]);

  // Handle code changes with debounced preview update
  const handleCodeChange = useCallback((newCode: string) => {
    setEditorContent(newCode);
    // Trigger hot reload if enabled
    if (currentProject?.hotReload) {
      updatePreview(newCode);
    }
  }, [currentProject, updatePreview]);

  // Build current project/template
  const handleBuild = async () => {
    if (!selectedTemplate) return;

    try {
      await fetch(`/api/templates/${selectedTemplate}/build`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Build failed:', error);
    }
  };

  // Run/Stop template
  const handleRunStop = async () => {
    if (!selectedTemplate) return;

    const endpoint = isRunning ? 'stop' : 'run';
    try {
      const response = await fetch(`/api/templates/${selectedTemplate}/${endpoint}`, {
        method: 'POST'
      });

      if (endpoint === 'run') {
        const data = await response.json();
        setPreviewUrl(data.previewUrl);
      } else {
        setPreviewUrl('');
      }
    } catch (error) {
      console.error(`Failed to ${endpoint}:`, error);
    }
  };

  // Deploy template
  const handleDeploy = async () => {
    if (!selectedTemplate) return;

    try {
      const response = await fetch(`/api/templates/${selectedTemplate}/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: 'standalone', // or 'cloud', 'container'
          options: {}
        })
      });

      const data = await response.json();
      if (data.success) {
        // Show success message with path
        alert(`Template deployed successfully to:\n${data.outputPath}`);
      }
    } catch (error) {
      console.error('Deploy failed:', error);
    }
  };

  // Copy template
  const handleCopy = async () => {
    if (!selectedTemplate) return;

    try {
      const response = await fetch(`/api/templates/${selectedTemplate}/copy`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        // Select the new copy
        handleTemplateSelect(data.newTemplateId);
      }
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  // Handle create project from template
  const handleCreateProject = (projectInfo: any) => {
    console.log('Project created:', projectInfo);
    // Show success notification
    alert(`Project "${projectInfo.displayName}" created successfully!\n\nLocation: ${projectInfo.outputDir}/${projectInfo.projectName}.kit\n\nYou can now build and run your project.`);

    // TODO: Refresh project list, switch to build view, etc.
    // For now, just log the success
  };

  // Render main content based on view mode
  const renderMainContent = () => {
    switch (viewMode) {
      case 'gallery':
        return (
          <TemplateGallery
            onSelectTemplate={handleTemplateSelect}
            selectedTemplate={selectedTemplate}
          />
        );

      case 'browser':
        return (
          <TemplateBrowser
            onSelectTemplate={handleTemplateSelect}
            onEditTemplate={(id) => {
              handleTemplateSelect(id);
              setViewMode('split');
            }}
            onCopyTemplate={handleCopy}
            onDeployTemplate={handleDeploy}
          />
        );

      case 'editor':
        return (
          <CodeEditor
            value={editorContent}
            onChange={handleCodeChange}
            language="python"
            templateId={selectedTemplate}
          />
        );

      case 'connections':
        return (
          <ConnectionEditor
            templates={(currentProject?.templates as any) || []}
            connections={(currentProject?.connections as any) || []}
            onConnectionsChange={(connections) => {
              // Update connections in store
            }}
          />
        );

      case 'split':
      default:
        return (
          <Box sx={{ display: 'flex', height: '100%', overflow: 'hidden', flexDirection: 'column' }}>
            {/* Tabs for Templates, Code, and Preview */}
            <Tabs
              value={activeView === 'gallery' ? 0 : activeView === 'editor' ? 1 : 2}
              onChange={(e, v) => dispatch(setActiveView(v === 0 ? 'gallery' : v === 1 ? 'editor' : 'preview'))}
              sx={{ borderBottom: 1, borderColor: 'divider', minHeight: 36 }}
            >
              <Tab label="Templates" sx={{ minHeight: 36 }} />
              <Tab label="Code" sx={{ minHeight: 36 }} />
              <Tab label="Preview" sx={{ minHeight: 36 }} />
            </Tabs>

            {/* Main Content Area */}
            <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              {activeView === 'gallery' ? (
                <TemplateGallery
                  onSelectTemplate={handleTemplateSelect}
                  selectedTemplate={selectedTemplate}
                  onCreateProject={handleCreateProject}
                />
              ) : activeView === 'editor' ? (
                <CodeEditor
                  value={editorContent}
                  onChange={handleCodeChange}
                  language="python"
                  templateId={selectedTemplate}
                />
              ) : (
                <>
                  {/* Preview Toolbar */}
              <Paper
                elevation={0}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  p: 0.5,
                  borderBottom: 1,
                  borderColor: 'divider',
                  backgroundColor: 'background.paper'
                }}
              >
                <Tooltip title="Build">
                  <IconButton
                    size="small"
                    onClick={handleBuild}
                    disabled={!selectedTemplate || isBuilding}
                  >
                    <BuildIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={isRunning ? "Stop" : "Run"}>
                  <IconButton
                    size="small"
                    onClick={handleRunStop}
                    disabled={!selectedTemplate}
                    color={isRunning ? "error" : "primary"}
                  >
                    {isRunning ? <StopIcon /> : <PlayIcon />}
                  </IconButton>
                </Tooltip>

                <Tooltip title="Refresh Preview">
                  <IconButton
                    size="small"
                    onClick={() => previewRef.current?.reload()}
                    disabled={!previewUrl}
                  >
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>

                <Box sx={{ flex: 1 }} />

                <Tooltip title="Edit Template">
                  <IconButton
                    size="small"
                    onClick={() => setViewMode('editor')}
                    disabled={!selectedTemplate}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Copy Template">
                  <IconButton
                    size="small"
                    onClick={handleCopy}
                    disabled={!selectedTemplate}
                  >
                    <CopyIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Deploy">
                  <IconButton
                    size="small"
                    onClick={handleDeploy}
                    disabled={!selectedTemplate}
                  >
                    <DeployIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Fullscreen Preview">
                  <IconButton
                    size="small"
                    onClick={() => previewRef.current?.fullscreen()}
                    disabled={!previewUrl}
                  >
                    <FullscreenIcon />
                  </IconButton>
                </Tooltip>
              </Paper>

              {/* Preview Area and Controls */}
              <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {/* Preview */}
                <Box sx={{ flex: 1, position: 'relative', backgroundColor: '#000' }}>
                  {previewUrl ? (
                    <PreviewPane
                      ref={previewRef}
                      url={previewUrl}
                      templateId={selectedTemplate}
                      onError={(error) => console.error('Preview error:', error)}
                    />
                  ) : (
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '100%',
                        color: 'text.secondary'
                      }}
                    >
                      {selectedTemplate
                        ? 'Click Run to preview this template'
                        : 'Select a template to preview'}
                    </Box>
                  )}
                </Box>

                {/* File Explorer - Build Output Directory Selector */}
                <Box
                  sx={{
                    height: 250,
                    p: 2,
                    borderTop: 1,
                    borderColor: 'divider',
                    backgroundColor: '#1e1e1e',
                    overflow: 'auto',
                  }}
                >
                  <FileExplorer
                    selectedPath={outputPath}
                    onPathChange={(path) => {
                      setOutputPathLocal(path);
                      dispatch(setOutputPath(path));
                    }}
                    title="Build Output Directory"
                    showFiles={false}
                  />
                </Box>
              </Box>
                </>
              )}
            </Box>
          </Box>
        );
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Top Toolbar */}
      <Paper
        elevation={2}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 1,
          borderBottom: 2,
          borderColor: 'primary.main',
          backgroundColor: 'background.paper'
        }}
      >
        <Tooltip title="Toggle Sidebar">
          <IconButton onClick={() => dispatch(toggleSidebar())}>
            <SidebarIcon />
          </IconButton>
        </Tooltip>

        {/* View Mode Buttons */}
        <Tooltip title="Template Gallery">
          <IconButton
            onClick={() => setViewMode('gallery')}
            color={viewMode === 'gallery' ? 'primary' : 'default'}
          >
            <SplitViewIcon />
          </IconButton>
        </Tooltip>

        <Tooltip title="Template Browser">
          <IconButton
            onClick={() => setViewMode('browser')}
            color={viewMode === 'browser' ? 'primary' : 'default'}
          >
            <DeployIcon />
          </IconButton>
        </Tooltip>

        <Tooltip title="Split View">
          <IconButton
            onClick={() => setViewMode('split')}
            color={viewMode === 'split' ? 'primary' : 'default'}
          >
            <SplitViewIcon />
          </IconButton>
        </Tooltip>

        <Box sx={{ flex: 1 }} />

        {/* Project Name */}
        {currentProject && (
          <Box sx={{ fontSize: 14, color: 'text.secondary' }}>
            {currentProject.name}
          </Box>
        )}
      </Paper>

      {/* Main Content Area with Sidebar */}
      <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex' }}>
        {/* Left Sidebar */}
        {sidebarVisible && (
          <Box
            sx={{
              width: 250,
              borderRight: 1,
              borderColor: 'divider',
              backgroundColor: 'background.paper',
              overflow: 'auto',
              p: 2,
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
        )}

        {/* Main Content */}
        <Box sx={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ flex: 1, overflow: 'hidden' }}>
            {renderMainContent()}
          </Box>
          <Box sx={{ height: consoleHeight, borderTop: 1, borderColor: 'divider' }}>
            <Console height={consoleHeight} />
          </Box>
        </Box>
      </Box>

      {/* Status Bar */}
      <StatusBar />
    </Box>
  );
};

export default MainLayout;