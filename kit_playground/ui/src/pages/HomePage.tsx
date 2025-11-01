import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, Button } from '../components/common';
import { websocketService } from '../services/websocket';
import { DependencyPreparer } from '../components/dependencies';
import { useDependencies } from '../hooks/useDependencies';

export const HomePage: React.FC = () => {
  const [streamingNotification, setStreamingNotification] = useState<{
    project: string;
    url: string;
  } | null>(null);

  // Dependency preparation
  const { status, isFirstLaunch } = useDependencies();
  const [showPreparer, setShowPreparer] = useState(false);
  const [showFirstLaunchPrompt, setShowFirstLaunchPrompt] = useState(false);

  // Check for first launch
  useEffect(() => {
    // Wait for status to load
    if (status !== null) {
      const isFirst = isFirstLaunch();
      const hasSeenPrompt = localStorage.getItem('kit_deps_prompt_seen');

      if (isFirst && !hasSeenPrompt && !status.cached) {
        // Show prompt after 2 seconds
        const timer = setTimeout(() => {
          setShowFirstLaunchPrompt(true);
          localStorage.setItem('kit_deps_prompt_seen', 'true');
        }, 2000);
        return () => clearTimeout(timer);
      }
    }
  }, [status, isFirstLaunch]);

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();

    // Listen for streaming_ready events
    const unsubscribe = websocketService.onStreamingReady((data) => {
      console.log('Streaming ready:', data);

      // Auto-open browser tab
      window.open(data.url, '_blank', 'noopener,noreferrer');

      // Show notification
      setStreamingNotification({
        project: data.project,
        url: data.url,
      });

      // Auto-hide after 10 seconds
      setTimeout(() => {
        setStreamingNotification(null);
      }, 10000);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <div className="space-y-8">
      {/* Streaming Notification */}
      {streamingNotification && (
        <div className="fixed top-4 right-4 z-50 max-w-md animate-fade-in">
          <Card className="bg-nvidia-green/10 border-nvidia-green shadow-lg">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-nvidia-green rounded-full flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-nvidia-green mb-1">
                  🎉 Streaming Ready!
                </h3>
                <p className="text-sm text-gray-300 mb-2">
                  {streamingNotification.project} is now streaming
                </p>
                <a
                  href={streamingNotification.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-nvidia-green hover:underline"
                >
                  {streamingNotification.url}
                </a>
                <p className="text-xs text-gray-400 mt-2">
                  ℹ️ Accept the SSL certificate warning if prompted
                </p>
              </div>
              <button
                onClick={() => setStreamingNotification(null)}
                className="flex-shrink-0 text-gray-400 hover:text-white"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </Card>
        </div>
      )}
      {/* Hero Section */}
      <div className="text-center space-y-4 py-12">
        <h1 className="text-5xl font-bold text-white">
          Welcome to Kit App Template
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          Build GPU-accelerated applications with NVIDIA Omniverse.
          Choose from powerful templates and get started in minutes.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        <Link to="/templates">
          <Card hover padding="lg" className="h-full">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 bg-nvidia-green rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">Browse Templates</h3>
                <p className="text-gray-400">
                  Explore applications, extensions, and microservices
                </p>
              </div>
            </div>
          </Card>
        </Link>

        <Link to="/templates/create">
          <Card hover padding="lg" className="h-full">
            <div className="flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 bg-nvidia-green rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">Create Project</h3>
                <p className="text-gray-400">
                  Start a new project from a template
                </p>
              </div>
            </div>
          </Card>
        </Link>
      </div>

      {/* Dependency Preparation Card */}
      {status && !status.cached && (
        <Card className="max-w-3xl mx-auto bg-blue-900 bg-opacity-20 border-blue-600">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-2">📦 Prepare Dependencies</h3>
              <p className="text-gray-300 mb-3">
                Pre-download Kit extensions (~12 GB, ~150 extensions) to speed up first launch.
                Without preparation, applications may take 5-10 minutes to start while downloading dependencies.
              </p>
              <div className="flex items-center space-x-4">
                <Button
                  variant="primary"
                  onClick={() => setShowPreparer(true)}
                >
                  Prepare Now
                </Button>
                <span className="text-sm text-gray-400">
                  Current cache: {status.count} extensions ({status.size})
                </span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* First Launch Prompt */}
      {showFirstLaunchPrompt && !status?.cached && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg p-4">
          <Card className="bg-blue-900 bg-opacity-95 border-blue-600 shadow-2xl">
            <div className="mb-4">
              <h3 className="text-2xl font-bold text-white mb-2">👋 First Time Setup</h3>
              <p className="text-gray-300 mb-4">
                It looks like this is your first time using Kit App Template. Would you like to prepare dependencies now?
              </p>
              <div className="p-3 bg-blue-800 bg-opacity-50 rounded mb-4">
                <p className="text-sm text-gray-300 mb-2">
                  <strong className="text-white">Without preparation:</strong> Applications will download extensions on first launch (5-10 minutes, may appear frozen)
                </p>
                <p className="text-sm text-gray-300">
                  <strong className="text-white">With preparation:</strong> Download once (~12 GB), then all apps launch fast (&lt;30 seconds)
                </p>
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <Button
                variant="secondary"
                onClick={() => setShowFirstLaunchPrompt(false)}
              >
                Skip for Now
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setShowFirstLaunchPrompt(false);
                  setShowPreparer(true);
                }}
              >
                Prepare Dependencies
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Dependency Preparer Modal */}
      <DependencyPreparer
        isOpen={showPreparer}
        onClose={() => setShowPreparer(false)}
        config="release"
      />

      {/* Quick Start Guide */}
      <Card className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6">Quick Start</h2>
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-nvidia-green rounded-full flex items-center justify-center text-white font-bold">
              1
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Browse Templates</h3>
              <p className="text-gray-400">
                Explore available templates for applications, extensions, and microservices
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-nvidia-green rounded-full flex items-center justify-center text-white font-bold">
              2
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Create Your First App</h3>
              <p className="text-gray-400">
                Choose a template and configure your project settings
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-nvidia-green rounded-full flex items-center justify-center text-white font-bold">
              3
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Build and Launch</h3>
              <p className="text-gray-400">
                Monitor build progress and launch your application
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-white mb-2">Real-Time Monitoring</h3>
          <p className="text-gray-400">
            Monitor builds and launches with live progress updates
          </p>
        </Card>
        <Card>
          <h3 className="text-lg font-semibold text-white mb-2">Per-App Dependencies</h3>
          <p className="text-gray-400">
            Isolate Kit SDK per application for conflict-free development
          </p>
        </Card>
        <Card>
          <h3 className="text-lg font-semibold text-white mb-2">Standalone Projects</h3>
          <p className="text-gray-400">
            Create self-contained, portable applications
          </p>
        </Card>
      </div>
    </div>
  );
};

export default HomePage;
