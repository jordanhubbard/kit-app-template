/**
 * Main Layout Component with Split Panes for Side-by-Side Editing
 */

import React, { useState, useCallback, useRef } from 'react';
import { Box, IconButton, Tooltip, Tab, Tabs, Paper } from '@mui/material';
import {
  ViewModule as SplitViewIcon,
  Code as CodeIcon,
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
import SplitPane from 'react-split-pane';
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

  // Handle template selection from browser/gallery
  const handleTemplateSelect = useCallback((templateId: string) => {
    setSelectedTemplate(templateId);
    // Load template code and preview
    loadTemplate(templateId);
  }, []);

  // Load template for editing and preview
  const loadTemplate = async (templateId: string) => {
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
  };

  // Handle code changes with debounced preview update
  const handleCodeChange = useCallback((newCode: string) => {
    setEditorContent(newCode);
    // Trigger hot reload if enabled
    if (currentProject?.hotReload) {
      updatePreview(newCode);
    }
  }, [currentProject]);

  // Update preview with new code
  const updatePreview = async (code: string) => {
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
  };

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
        // Open deployment location
        if (window.electronAPI) {
          window.electronAPI.showItemInFolder(data.outputPath);
        }
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
            templates={currentProject?.templates || []}
            connections={currentProject?.connections || []}
            onConnectionsChange={(connections) => {
              // Update connections in store
            }}
          />
        );

      case 'split':
      default:
        return (
          <SplitPane
            split="vertical"
            minSize={300}
            maxSize={-300}
            defaultSize={leftPaneSize}
            onChange={setLeftPaneSize}
            resizerStyle={{
              background: '#000',
              opacity: 0.2,
              zIndex: 1,
              boxSizing: 'border-box',
              backgroundClip: 'padding-box',
              width: 11,
              margin: '0 -5px',
              borderLeft: '5px solid transparent',
              borderRight: '5px solid transparent',
              cursor: 'col-resize'
            }}
          >
            {/* Left Pane - Editor/Gallery */}
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Tabs
                value={activeView === 'gallery' ? 0 : 1}
                onChange={(e, v) => dispatch(setActiveView(v === 0 ? 'gallery' : 'editor'))}
                sx={{ borderBottom: 1, borderColor: 'divider', minHeight: 36 }}
              >
                <Tab label="Templates" sx={{ minHeight: 36 }} />
                <Tab label="Code" sx={{ minHeight: 36 }} />
              </Tabs>

              <Box sx={{ flex: 1, overflow: 'hidden' }}>
                {activeView === 'gallery' ? (
                  <TemplateGallery
                    onSelectTemplate={handleTemplateSelect}
                    selectedTemplate={selectedTemplate}
                    compact
                  />
                ) : (
                  <CodeEditor
                    value={editorContent}
                    onChange={handleCodeChange}
                    language="python"
                    templateId={selectedTemplate}
                  />
                )}
              </Box>
            </Box>

            {/* Right Pane - Preview/Browser */}
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
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
                    height: 320,
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
            </Box>
          </SplitPane>
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
            <ViewModule />
          </IconButton>
        </Tooltip>

        <Tooltip title="Template Browser">
          <IconButton
            onClick={() => setViewMode('browser')}
            color={viewMode === 'browser' ? 'primary' : 'default'}
          >
            <CloudDownload />
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

      {/* Main Content Area */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <SplitPane
          split="horizontal"
          minSize={100}
          maxSize={-50}
          defaultSize={-consoleHeight}
          onChange={(size) => setConsoleHeight(window.innerHeight - size)}
          primary="first"
        >
          {renderMainContent()}
          <Console height={consoleHeight} />
        </SplitPane>
      </Box>

      {/* Status Bar */}
      <StatusBar />
    </Box>
  );
};

export default MainLayout;