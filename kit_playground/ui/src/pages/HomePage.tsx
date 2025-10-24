import React from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/common';

export const HomePage: React.FC = () => {
  return (
    <div className="space-y-8">
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
