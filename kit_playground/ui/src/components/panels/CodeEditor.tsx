import React, { useState } from 'react';
import { Save, X, RotateCcw, FileText } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';

interface CodeEditorProps {
  filePath?: string;
  fileName?: string;
  initialContent?: string;
  readOnly?: boolean;
}

/**
 * CodeEditor
 * 
 * Simple code editor panel for viewing/editing .kit files.
 * Basic text editing with save/discard functionality.
 * 
 * Features:
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
}) => {
  const { closePanel, getPanelsByType } = usePanelStore();
  const [content, setContent] = useState(initialContent);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleContentChange = (value: string) => {
    setContent(value);
    setIsDirty(value !== initialContent);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // TODO: Implement save via API
      // await apiService.saveFile({ path: filePath, content });
      console.log('Saving file:', filePath, content);
      
      // Simulate save delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setIsDirty(false);
    } catch (err) {
      console.error('Failed to save file:', err);
      alert('Failed to save file');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDiscard = () => {
    if (isDirty && !confirm('Discard unsaved changes?')) {
      return;
    }
    setContent(initialContent);
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
          {!readOnly && (
            <>
              <button
                onClick={handleDiscard}
                disabled={!isDirty || isSaving}
                className="
                  px-3 py-2 rounded
                  bg-bg-card hover:bg-bg-card-hover
                  border border-border-subtle
                  text-text-secondary hover:text-text-primary
                  disabled:opacity-50 disabled:cursor-not-allowed
                  text-sm font-medium
                  transition-colors
                  flex items-center gap-2
                "
                title="Discard changes"
              >
                <RotateCcw className="w-4 h-4" />
                Discard
              </button>
              
              <button
                onClick={handleSave}
                disabled={!isDirty || isSaving}
                className="
                  px-3 py-2 rounded
                  bg-nvidia-green hover:bg-nvidia-green-dark
                  disabled:opacity-50 disabled:cursor-not-allowed
                  text-white text-sm font-medium
                  transition-colors
                  flex items-center gap-2
                "
                title="Save changes"
              >
                <Save className="w-4 h-4" />
                {isSaving ? 'Saving...' : 'Save'}
              </button>
              
              <div className="w-px h-6 bg-border-subtle mx-1" />
            </>
          )}
          
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

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <textarea
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          readOnly={readOnly}
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

