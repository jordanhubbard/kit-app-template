import React, { useState, useEffect } from 'react';
import { Save, X, RotateCcw, FileText, Loader, Play } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';
import { apiService } from '../../services/api';

interface CodeEditorProps {
  filePath?: string;
  fileName?: string;
  initialContent?: string;
  readOnly?: boolean;
  projectName?: string;
}

/**
 * CodeEditor
 *
 * Simple code editor panel for viewing/editing .kit files.
 * Basic text editing with save/discard functionality.
 *
 * Features:
 * - Auto-loads file content from filePath
 * - Syntax highlighting (basic, via textarea)
 * - Save changes
 * - Discard changes
 * - Read-only mode
 *
 * Note: For Phase 4, this is a simple textarea.
 * In Phase 5, this could be enhanced with Monaco editor or similar.
 */
export const CodeEditor: React.FC<CodeEditorProps> = ({
  filePath,
  fileName = 'Untitled',
  initialContent = '',
  readOnly = false,
  projectName,
}) => {
  const { closePanel, getPanelsByType, openPanel } = usePanelStore();
  const [content, setContent] = useState(initialContent);
  const [originalContent, setOriginalContent] = useState(initialContent);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Load file content when filePath changes
  useEffect(() => {
    if (filePath && !initialContent) {
      setIsLoading(true);
      setLoadError(null);

      apiService.readFile(filePath)
        .then((fileContent) => {
          setContent(fileContent);
          setOriginalContent(fileContent);
          setIsDirty(false);
        })
        .catch((err) => {
          console.error('Failed to load file:', err);
          setLoadError(err instanceof Error ? err.message : 'Failed to load file');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [filePath, initialContent]);

  const handleContentChange = (value: string) => {
    setContent(value);
    setIsDirty(value !== originalContent);
  };

  const handleSave = async () => {
    if (!filePath) {
      console.error('No file path provided');
      return;
    }

    setIsSaving(true);
    try {
      await apiService.saveFile(filePath, content);
      setOriginalContent(content);
      setIsDirty(false);
      console.log('File saved successfully:', filePath);
    } catch (err) {
      console.error('Failed to save file:', err);
      alert(`Failed to save file: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDiscard = () => {
    if (isDirty && !confirm('Discard unsaved changes?')) {
      return;
    }
    setContent(originalContent);
    setIsDirty(false);
  };

  const handleClose = () => {
    if (isDirty && !confirm('Close without saving changes?')) {
      return;
    }
    const panels = getPanelsByType('code-editor');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
  };

  const handleBuild = () => {
    if (isDirty) {
      if (!confirm('You have unsaved changes. Build anyway?')) {
        return;
      }
    }

    if (!projectName) {
      alert('No project name available for build');
      return;
    }

    // Open build output panel and start build
    openPanel('build-output', {
      projectName,
      jobType: 'build',
      autoStart: true,
    });
  };

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-nvidia-green" />
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              {fileName}
              {isDirty && <span className="text-status-warning ml-2">•</span>}
            </h3>
            {filePath && (
              <p className="text-xs text-text-muted truncate max-w-md">
                {filePath}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClose}
            className="
              p-2 rounded
              hover:bg-bg-card
              text-text-secondary hover:text-text-primary
              transition-colors
            "
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Action Toolbar - Above Editor */}
      {!readOnly && !isLoading && !loadError && (
        <div className="flex items-center justify-between px-4 py-3 bg-bg-card border-y border-border-subtle">
          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              disabled={!isDirty || isSaving}
              className="
                px-5 py-2.5 rounded
                bg-nvidia-green hover:bg-nvidia-green-dark
                disabled:bg-nvidia-green/30 disabled:cursor-not-allowed
                text-white text-sm font-semibold
                transition-colors
                flex items-center gap-2
                shadow-sm
              "
              title={isDirty ? "Save changes" : "No changes to save"}
            >
              <Save className="w-4 h-4" />
              {isSaving ? 'Saving...' : 'Save'}
            </button>

            <button
              onClick={handleDiscard}
              disabled={!isDirty || isSaving}
              className="
                px-5 py-2.5 rounded
                bg-bg-dark hover:bg-bg-panel
                border-2 border-border-subtle hover:border-text-secondary
                text-text-primary hover:text-text-primary
                disabled:opacity-40 disabled:cursor-not-allowed disabled:border-border-subtle
                text-sm font-semibold
                transition-all
                flex items-center gap-2
              "
              title={isDirty ? "Discard changes" : "No changes to discard"}
            >
              <RotateCcw className="w-4 h-4" />
              Discard
            </button>

            {projectName && (
              <>
                <div className="w-px h-8 bg-border-subtle mx-2" />
                <button
                  onClick={handleBuild}
                  disabled={isSaving}
                  className="
                    px-5 py-2.5 rounded
                    bg-blue-600 hover:bg-blue-700
                    disabled:opacity-50 disabled:cursor-not-allowed
                    text-white text-sm font-semibold
                    transition-colors
                    flex items-center gap-2
                    shadow-sm
                  "
                  title="Build project"
                >
                  <Play className="w-4 h-4" />
                  Build
                </button>
              </>
            )}
          </div>

          {isDirty && (
            <div className="flex items-center gap-2 text-xs text-status-warning">
              <span className="w-2 h-2 rounded-full bg-status-warning animate-pulse" />
              <span className="font-medium">Unsaved changes</span>
            </div>
          )}
        </div>
      )}

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full bg-bg-dark">
            <div className="flex flex-col items-center gap-3">
              <Loader className="w-8 h-8 text-nvidia-green animate-spin" />
              <p className="text-text-secondary text-sm">Loading {fileName}...</p>
            </div>
          </div>
        ) : loadError ? (
          <div className="flex items-center justify-center h-full bg-bg-dark">
            <div className="text-center max-w-md p-6">
              <p className="text-status-error text-sm mb-2">Failed to load file</p>
              <p className="text-text-muted text-xs">{loadError}</p>
            </div>
          </div>
        ) : (
          <textarea
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            readOnly={readOnly || isLoading}
            className="
              w-full h-full p-4
              bg-bg-dark
              text-text-primary
              font-mono text-sm
              resize-none
              focus:outline-none
              placeholder:text-text-muted
            "
            placeholder={readOnly ? 'No content' : 'Start typing...'}
            spellCheck={false}
          />
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between p-3 border-t border-border-subtle bg-bg-dark">
        <div className="text-xs text-text-muted">
          {readOnly ? 'Read-only' : isDirty ? 'Modified' : 'Saved'}
        </div>

        <div className="flex items-center gap-4 text-xs text-text-muted">
          <span>Lines: {content.split('\n').length}</span>
          <span>Chars: {content.length}</span>
        </div>
      </div>
    </div>
  );
};
