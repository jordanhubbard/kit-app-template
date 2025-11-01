import React, { useState, useEffect } from 'react';
import { X, Download, Trash2, ExternalLink, Plus, FolderOpen, Check, Loader } from 'lucide-react';
import { usePanelStore } from '../../stores/panelStore';

interface USDAsset {
  id: string;
  name: string;
  description: string;
  url: string;
  category: string;
  size_mb: number;
  tags: string[];
  custom?: boolean;
  downloaded?: boolean;
  local_path?: string;
}

interface USDMediaProps {
  // Optional props for panel configuration
}

/**
 * USD Media Library
 *
 * Browse, download, and manage USD sample files.
 * Provides a curated list of well-known USD samples plus
 * the ability to add custom URLs.
 */
export const USDMedia: React.FC<USDMediaProps> = () => {
  const { closePanel, getPanelsByType } = usePanelStore();
  const [assets, setAssets] = useState<USDAsset[]>([]);
  const [assetsDir, setAssetsDir] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // New asset form
  const [newAsset, setNewAsset] = useState({
    id: '',
    name: '',
    description: '',
    url: '',
    category: 'custom',
    size_mb: 0,
    tags: ''
  });

  useEffect(() => {
    loadLibrary();
  }, []);

  const loadLibrary = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/usd-media/library');
      const data = await response.json();

      if (data.success) {
        setAssets(data.library);
        setAssetsDir(data.assets_dir);
      }
    } catch (error) {
      console.error('Error loading USD library:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (assetId: string) => {
    try {
      setDownloading(assetId);
      const response = await fetch(`/api/usd-media/download/${assetId}`, {
        method: 'POST'
      });
      const data = await response.json();

      if (data.success) {
        // Refresh library to update download status
        await loadLibrary();
      } else {
        alert(`Download failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Error downloading asset:', error);
      alert('Download failed');
    } finally {
      setDownloading(null);
    }
  };

  const handleDeleteLocal = async (assetId: string) => {
    if (!confirm('Delete this downloaded file?')) return;

    try {
      const response = await fetch(`/api/usd-media/delete/${assetId}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.success) {
        await loadLibrary();
      }
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  const handleAddAsset = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch('/api/usd-media/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newAsset,
          tags: newAsset.tags.split(',').map(t => t.trim()).filter(t => t)
        })
      });
      const data = await response.json();

      if (data.success) {
        await loadLibrary();
        setShowAddDialog(false);
        setNewAsset({
          id: '',
          name: '',
          description: '',
          url: '',
          category: 'custom',
          size_mb: 0,
          tags: ''
        });
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error adding asset:', error);
      alert('Failed to add asset');
    }
  };

  const handleRemoveAsset = async (assetId: string) => {
    if (!confirm('Remove this asset from the library?')) return;

    try {
      const response = await fetch(`/api/usd-media/remove/${assetId}`, {
        method: 'DELETE'
      });
      const data = await response.json();

      if (data.success) {
        await loadLibrary();
      }
    } catch (error) {
      console.error('Error removing asset:', error);
    }
  };

  const handleOpenAssetsDir = () => {
    alert(`Assets are stored in:\n${assetsDir}\n\nYou can access this directory from your file manager.`);
  };

  const handleClose = () => {
    const panels = getPanelsByType('usd-media');
    if (panels.length > 0) {
      closePanel(panels[panels.length - 1].id);
    }
  };

  const categories = ['all', ...new Set(assets.map(a => a.category))];
  const filteredAssets = selectedCategory === 'all' 
    ? assets 
    : assets.filter(a => a.category === selectedCategory);

  const downloadedCount = assets.filter(a => a.downloaded).length;

  return (
    <div className="flex flex-col h-full bg-bg-panel">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border-subtle bg-bg-dark">
        <div className="flex items-center gap-3">
          <FolderOpen className="w-5 h-5 text-nvidia-green" />
          <div>
            <h3 className="text-sm font-semibold text-text-primary">
              USD Media Library
            </h3>
            <p className="text-xs text-text-muted">
              {assets.length} assets • {downloadedCount} downloaded
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleOpenAssetsDir}
            className="
              px-3 py-1.5 rounded text-xs
              bg-bg-card hover:bg-bg-hover
              text-text-secondary hover:text-text-primary
              border border-border-subtle
              transition-colors
              flex items-center gap-2
            "
            title="Open assets directory"
          >
            <FolderOpen className="w-3.5 h-3.5" />
            Open Folder
          </button>

          <button
            onClick={() => setShowAddDialog(true)}
            className="
              px-3 py-1.5 rounded text-xs font-semibold
              bg-nvidia-green hover:bg-nvidia-green-dark
              text-white
              transition-colors
              flex items-center gap-2
            "
          >
            <Plus className="w-3.5 h-3.5" />
            Add Asset
          </button>

          <div className="w-px h-6 bg-border-subtle mx-1" />

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

      {/* Category Filter */}
      <div className="flex gap-2 p-4 border-b border-border-subtle bg-bg-dark overflow-x-auto">
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`
              px-3 py-1.5 rounded text-xs font-medium whitespace-nowrap
              transition-colors
              ${selectedCategory === category
                ? 'bg-nvidia-green text-white'
                : 'bg-bg-card text-text-secondary hover:bg-bg-hover hover:text-text-primary'
              }
            `}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>

      {/* Assets Grid */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <Loader className="w-8 h-8 text-nvidia-green animate-spin" />
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="flex items-center justify-center h-full text-text-muted">
            No assets in this category
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAssets.map(asset => (
              <div
                key={asset.id}
                className="
                  bg-bg-card rounded-lg p-4
                  border border-border-subtle
                  hover:border-nvidia-green/30
                  transition-colors
                "
              >
                {/* Asset Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-text-primary mb-1">
                      {asset.name}
                    </h4>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs text-text-muted">
                        {asset.size_mb.toFixed(1)} MB
                      </span>
                      {asset.downloaded && (
                        <div className="flex items-center gap-1 text-xs text-nvidia-green">
                          <Check className="w-3 h-3" />
                          Downloaded
                        </div>
                      )}
                    </div>
                  </div>
                  {asset.custom && (
                    <button
                      onClick={() => handleRemoveAsset(asset.id)}
                      className="text-text-muted hover:text-status-error transition-colors"
                      title="Remove from library"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Description */}
                <p className="text-xs text-text-secondary mb-3 line-clamp-2">
                  {asset.description}
                </p>

                {/* Tags */}
                {asset.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {asset.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 rounded text-xs bg-bg-dark text-text-muted"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  {asset.downloaded ? (
                    <>
                      <button
                        onClick={() => handleDeleteLocal(asset.id)}
                        className="
                          flex-1 px-3 py-2 rounded text-xs font-medium
                          bg-status-error/10 hover:bg-status-error/20
                          text-status-error
                          transition-colors
                          flex items-center justify-center gap-2
                        "
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                      </button>
                      <a
                        href={asset.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="
                          px-3 py-2 rounded text-xs
                          bg-bg-dark hover:bg-bg-hover
                          text-text-secondary hover:text-text-primary
                          transition-colors
                          flex items-center justify-center
                        "
                        title="View original URL"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => handleDownload(asset.id)}
                        disabled={downloading === asset.id}
                        className="
                          flex-1 px-3 py-2 rounded text-xs font-medium
                          bg-nvidia-green hover:bg-nvidia-green-dark
                          text-white
                          disabled:opacity-50 disabled:cursor-not-allowed
                          transition-colors
                          flex items-center justify-center gap-2
                        "
                      >
                        {downloading === asset.id ? (
                          <>
                            <Loader className="w-3.5 h-3.5 animate-spin" />
                            Downloading...
                          </>
                        ) : (
                          <>
                            <Download className="w-3.5 h-3.5" />
                            Download
                          </>
                        )}
                      </button>
                      <a
                        href={asset.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="
                          px-3 py-2 rounded text-xs
                          bg-bg-dark hover:bg-bg-hover
                          text-text-secondary hover:text-text-primary
                          transition-colors
                          flex items-center justify-center
                        "
                        title="View original URL"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Asset Dialog */}
      {showAddDialog && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-bg-panel rounded-lg p-6 max-w-md w-full border border-border-subtle">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-text-primary">Add Custom Asset</h3>
              <button
                onClick={() => setShowAddDialog(false)}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddAsset} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  ID *
                </label>
                <input
                  type="text"
                  required
                  value={newAsset.id}
                  onChange={(e) => setNewAsset({ ...newAsset, id: e.target.value })}
                  className="
                    w-full px-3 py-2 rounded text-sm
                    bg-bg-dark border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:border-nvidia-green
                  "
                  placeholder="my_custom_asset"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  required
                  value={newAsset.name}
                  onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
                  className="
                    w-full px-3 py-2 rounded text-sm
                    bg-bg-dark border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:border-nvidia-green
                  "
                  placeholder="My Custom USD File"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  URL *
                </label>
                <input
                  type="url"
                  required
                  value={newAsset.url}
                  onChange={(e) => setNewAsset({ ...newAsset, url: e.target.value })}
                  className="
                    w-full px-3 py-2 rounded text-sm
                    bg-bg-dark border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:border-nvidia-green
                  "
                  placeholder="https://example.com/file.usd"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  Description
                </label>
                <textarea
                  value={newAsset.description}
                  onChange={(e) => setNewAsset({ ...newAsset, description: e.target.value })}
                  className="
                    w-full px-3 py-2 rounded text-sm
                    bg-bg-dark border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:border-nvidia-green
                    resize-none
                  "
                  rows={3}
                  placeholder="Brief description of the asset"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={newAsset.tags}
                  onChange={(e) => setNewAsset({ ...newAsset, tags: e.target.value })}
                  className="
                    w-full px-3 py-2 rounded text-sm
                    bg-bg-dark border border-border-subtle
                    text-text-primary
                    focus:outline-none focus:border-nvidia-green
                  "
                  placeholder="custom, model, scene"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddDialog(false)}
                  className="
                    flex-1 px-4 py-2 rounded text-sm font-medium
                    bg-bg-card hover:bg-bg-hover
                    text-text-secondary
                    transition-colors
                  "
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="
                    flex-1 px-4 py-2 rounded text-sm font-medium
                    bg-nvidia-green hover:bg-nvidia-green-dark
                    text-white
                    transition-colors
                  "
                >
                  Add Asset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

