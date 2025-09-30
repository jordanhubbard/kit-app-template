/**
 * Code Editor Component
 * Monaco-based code editor with syntax highlighting and hot reload
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Box, IconButton, Tooltip, Typography, Alert, Chip } from '@mui/material';
import {
  Save as SaveIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
  FormatAlignLeft as FormatIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import Editor, { Monaco, OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  templateId: string | null;
  readOnly?: boolean;
  minimap?: boolean;
  lineNumbers?: 'on' | 'off' | 'relative';
  theme?: 'vs-dark' | 'vs-light' | 'hc-black';
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'python',
  templateId,
  readOnly = false,
  minimap = true,
  lineNumbers = 'on',
  theme = 'vs-dark',
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [editorLanguage, setEditorLanguage] = useState(language);

  // Detect language from templateId
  useEffect(() => {
    if (templateId) {
      // Detect file type from template
      if (templateId.includes('python') || language === 'python') {
        setEditorLanguage('python');
      } else if (templateId.includes('cpp') || templateId.includes('c++')) {
        setEditorLanguage('cpp');
      } else if (templateId.includes('kit')) {
        setEditorLanguage('json'); // .kit files are JSON-like
      } else {
        setEditorLanguage(language);
      }
    }
  }, [templateId, language]);

  // Handle editor mount
  const handleEditorMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      fontFamily: '"SF Mono", "Monaco", "Inconsolata", "Fira Code", monospace',
      minimap: { enabled: minimap },
      scrollBeyondLastLine: false,
      renderWhitespace: 'selection',
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true,
      },
      suggestOnTriggerCharacters: true,
      quickSuggestions: true,
      formatOnPaste: true,
      formatOnType: true,
    });

    // Add custom keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSave();
    });

    // Add custom theme
    monaco.editor.defineTheme('kit-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
        { token: 'keyword', foreground: '569CD6' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'number', foreground: 'B5CEA8' },
        { token: 'type', foreground: '4EC9B0' },
        { token: 'function', foreground: 'DCDCAA' },
      ],
      colors: {
        'editor.background': '#1e1e1e',
        'editor.foreground': '#D4D4D4',
        'editor.lineHighlightBackground': '#2A2D2E',
        'editorCursor.foreground': '#76b900',
        'editor.selectionBackground': '#264F78',
        'editor.inactiveSelectionBackground': '#3A3D41',
      },
    });

    monaco.editor.setTheme('kit-dark');

    // Watch for content changes
    editor.onDidChangeModelContent(() => {
      setHasChanges(true);
      setError(null);
    });

    // Setup error markers
    setupErrorMarkers(monaco);
  };

  // Setup error markers for syntax checking
  const setupErrorMarkers = (monaco: Monaco) => {
    if (!editorRef.current) return;

    const model = editorRef.current.getModel();
    if (!model) return;

    // Clear existing markers
    monaco.editor.setModelMarkers(model, 'syntax', []);

    // Add syntax validation (basic example)
    // In production, this would call a backend linter
    try {
      // Example: Check for common Python errors
      if (editorLanguage === 'python') {
        const content = model.getValue();
        const lines = content.split('\n');
        const markers: editor.IMarkerData[] = [];

        lines.forEach((line, index) => {
          // Check for tabs (PEP 8 violation)
          if (line.includes('\t')) {
            markers.push({
              severity: monaco.MarkerSeverity.Warning,
              startLineNumber: index + 1,
              startColumn: line.indexOf('\t') + 1,
              endLineNumber: index + 1,
              endColumn: line.indexOf('\t') + 2,
              message: 'PEP 8: Use spaces instead of tabs',
            });
          }

          // Check for trailing whitespace
          if (line.match(/\s+$/)) {
            markers.push({
              severity: monaco.MarkerSeverity.Info,
              startLineNumber: index + 1,
              startColumn: line.trimEnd().length + 1,
              endLineNumber: index + 1,
              endColumn: line.length + 1,
              message: 'Trailing whitespace',
            });
          }
        });

        monaco.editor.setModelMarkers(model, 'syntax', markers);
      }
    } catch (err) {
      console.error('Error setting markers:', err);
    }
  };

  // Handle save
  const handleSave = useCallback(async () => {
    if (!editorRef.current || !hasChanges) return;

    const content = editorRef.current.getValue();

    try {
      onChange(content);
      setHasChanges(false);
      setError(null);

      // Show saved indicator briefly
      const model = editorRef.current.getModel();
      if (model && monacoRef.current) {
        const decoration = editorRef.current.deltaDecorations(
          [],
          [
            {
              range: new monacoRef.current.Range(1, 1, 1, 1),
              options: {
                isWholeLine: false,
                className: 'saved-indicator',
              },
            },
          ]
        );

        setTimeout(() => {
          if (editorRef.current) {
            editorRef.current.deltaDecorations(decoration, []);
          }
        }, 1000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    }
  }, [hasChanges, onChange]);

  // Handle undo
  const handleUndo = () => {
    if (editorRef.current) {
      editorRef.current.trigger('keyboard', 'undo', {});
    }
  };

  // Handle redo
  const handleRedo = () => {
    if (editorRef.current) {
      editorRef.current.trigger('keyboard', 'redo', {});
    }
  };

  // Handle format
  const handleFormat = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument')?.run();
    }
  };

  // Handle search
  const handleSearch = () => {
    if (editorRef.current) {
      editorRef.current.getAction('actions.find')?.run();
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: '#1e1e1e',
      }}
    >
      {/* Toolbar */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          p: 0.5,
          backgroundColor: '#252526',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        {/* File info */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            {templateId ? `Editing: ${templateId}` : 'No template selected'}
          </Typography>
          <Chip
            label={editorLanguage}
            size="small"
            sx={{ height: 20, fontSize: 11 }}
          />
          {hasChanges && (
            <Chip
              label="Modified"
              size="small"
              color="warning"
              sx={{ height: 20, fontSize: 11 }}
            />
          )}
        </Box>

        {/* Actions */}
        <Tooltip title="Undo (Ctrl+Z)">
          <IconButton size="small" onClick={handleUndo}>
            <UndoIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Redo (Ctrl+Y)">
          <IconButton size="small" onClick={handleRedo}>
            <RedoIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Format Code">
          <IconButton size="small" onClick={handleFormat}>
            <FormatIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Search (Ctrl+F)">
          <IconButton size="small" onClick={handleSearch}>
            <SearchIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Save (Ctrl+S)">
          <IconButton
            size="small"
            onClick={handleSave}
            disabled={!hasChanges}
            color={hasChanges ? 'primary' : 'default'}
          >
            <SaveIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Settings">
          <IconButton
            size="small"
            onClick={() => setShowSettings(!showSettings)}
          >
            <SettingsIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Error/Warning Display */}
      {error && (
        <Alert
          severity="error"
          sx={{ m: 1 }}
          onClose={() => setError(null)}
          action={
            <IconButton size="small" onClick={() => setError(null)}>
              <CloseIcon fontSize="small" />
            </IconButton>
          }
        >
          {error}
        </Alert>
      )}

      {/* Monaco Editor */}
      <Box sx={{ flex: 1, position: 'relative' }}>
        {templateId ? (
          <Editor
            height="100%"
            language={editorLanguage}
            value={value}
            onChange={(val) => {
              if (val !== undefined) {
                onChange(val);
              }
            }}
            onMount={handleEditorMount}
            theme={theme}
            options={{
              readOnly,
              minimap: { enabled: minimap },
              lineNumbers,
              automaticLayout: true,
            }}
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
            <Typography>Select a template to edit</Typography>
          </Box>
        )}
      </Box>

      {/* Status Footer */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 1,
          py: 0.5,
          backgroundColor: '#252526',
          borderTop: 1,
          borderColor: 'divider',
          fontSize: 12,
          color: 'text.secondary',
        }}
      >
        <Box>
          {editorRef.current && (
            <>
              Line {editorRef.current.getPosition()?.lineNumber || 0}, Col{' '}
              {editorRef.current.getPosition()?.column || 0}
            </>
          )}
        </Box>
        <Box>
          {editorRef.current?.getValue().split('\n').length || 0} lines
        </Box>
      </Box>
    </Box>
  );
};

export default CodeEditor;