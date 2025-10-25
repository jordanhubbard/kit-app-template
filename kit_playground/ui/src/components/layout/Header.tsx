import React from 'react';

/**
 * Header
 * 
 * Application header with branding and title.
 * Simplified for panel-based UI (no routing needed).
 */
export const Header: React.FC = () => {
  return (
    <header className="bg-bg-dark border-b border-border-subtle">
      <div className="px-6 py-4">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <div className="w-10 h-10 bg-nvidia-green rounded flex items-center justify-center font-bold text-white text-xl">
            K
          </div>
          
          {/* Title */}
          <div>
            <h1 className="text-xl font-bold text-text-primary">Kit Playground</h1>
            <p className="text-xs text-text-muted">NVIDIA Omniverse • Template Development Environment</p>
          </div>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Version Badge */}
          <div className="px-3 py-1 rounded bg-nvidia-green/10 border border-nvidia-green/30">
            <span className="text-xs font-mono text-nvidia-green">v2.0</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
