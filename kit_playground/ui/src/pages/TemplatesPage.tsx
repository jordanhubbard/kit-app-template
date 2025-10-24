import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, Button, LoadingSpinner } from '../components/common';
import { apiService } from '../services/api';
import type { Template } from '../services/types';

type TemplateType = 'all' | 'application' | 'extension' | 'microservice';

export const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<TemplateType>('all');

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.listTemplates();
      const templateArray = Object.values(response.templates);
      setTemplates(templateArray);
    } catch (err) {
      console.error('Failed to load templates:', err);
      setError('Failed to load templates. Please ensure the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = filter === 'all'
    ? templates
    : templates.filter(t => t.type === filter);

  const getTemplateIcon = (type: string) => {
    switch (type) {
      case 'application':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
          </svg>
        );
      case 'extension':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
          </svg>
        );
      case 'microservice':
        return (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
          </svg>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" className="mx-auto text-nvidia-green" />
          <p className="text-gray-400">Loading templates...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="max-w-2xl mx-auto">
        <div className="text-center space-y-4">
          <div className="text-red-500 text-5xl">⚠️</div>
          <h2 className="text-2xl font-bold text-white">Error Loading Templates</h2>
          <p className="text-gray-400">{error}</p>
          <Button onClick={loadTemplates}>Retry</Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Templates</h1>
          <p className="text-gray-400 mt-1">Browse and create from available templates</p>
        </div>
        <Button onClick={loadTemplates} variant="secondary" size="sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(['all', 'application', 'extension', 'microservice'] as TemplateType[]).map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`
              px-4 py-2 rounded-lg font-medium capitalize transition-all duration-200
              ${filter === type
                ? 'bg-nvidia-green text-white'
                : 'bg-dark-card text-gray-300 hover:bg-dark-hover border border-gray-700'
              }
            `}
          >
            {type}
            {type !== 'all' && (
              <span className="ml-2 text-sm opacity-75">
                ({templates.filter(t => t.type === type).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-400">No templates found</p>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <Card key={template.name} hover className="flex flex-col">
              <div className="flex items-start gap-3 mb-4">
                <div className="flex-shrink-0 w-12 h-12 bg-nvidia-green rounded-lg flex items-center justify-center text-white">
                  {getTemplateIcon(template.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-white truncate">
                    {template.display_name}
                  </h3>
                  <p className="text-sm text-gray-400 capitalize">{template.type}</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-4 flex-1">
                {template.description}
              </p>
              <Link to={`/templates/create/${template.name}`}>
                <Button className="w-full">
                  Create Project
                </Button>
              </Link>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TemplatesPage;

