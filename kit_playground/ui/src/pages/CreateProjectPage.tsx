import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Input, LoadingSpinner } from '../components/common';
import { apiService } from '../services/api';
import type { Template } from '../services/types';

export const CreateProjectPage: React.FC = () => {
  const { templateName } = useParams<{ templateName?: string }>();
  const navigate = useNavigate();

  const [template, setTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    displayName: '',
    version: '1.0.0',
    standalone: false,
    perAppDeps: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (templateName) {
      loadTemplate(templateName);
    }
  }, [templateName]);

  const loadTemplate = async (name: string) => {
    try {
      setLoading(true);
      const response = await apiService.getTemplate(name);
      setTemplate(response.template);
    } catch (err) {
      console.error('Failed to load template:', err);
      setError('Failed to load template details');
    } finally {
      setLoading(false);
    }
  };

  const validateField = (field: string, value: string): string | null => {
    if (field === 'name') {
      if (!value) return 'Project name is required';
      if (!/^[a-z0-9._]+$/.test(value)) {
        return 'Project name must contain only lowercase letters, numbers, dots, and underscores';
      }
    }
    if (field === 'version') {
      if (!/^\d+\.\d+\.\d+$/.test(value)) {
        return 'Version must be in format X.Y.Z (e.g., 1.0.0)';
      }
    }
    return null;
  };

  const handleFieldChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    if (typeof value === 'string') {
      const error = validateField(field, value);
      setErrors(prev => ({
        ...prev,
        [field]: error || '',
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    const nameError = validateField('name', formData.name);
    if (nameError) newErrors.name = nameError;
    
    const versionError = validateField('version', formData.version);
    if (versionError) newErrors.version = versionError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm() || !template) return;

    try {
      setCreating(true);
      setError(null);

      const response = await apiService.createProject({
        template: template.name,
        name: formData.name,
        displayName: formData.displayName || formData.name,
        version: formData.version,
        standalone: formData.standalone,
        perAppDeps: formData.perAppDeps,
      });

      if (response.success) {
        // Navigate to jobs page to monitor progress
        navigate('/jobs');
      } else {
        setError(response.error || 'Failed to create project');
      }
    } catch (err) {
      console.error('Failed to create project:', err);
      setError('Failed to create project. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" className="text-nvidia-green" />
      </div>
    );
  }

  if (!template) {
    return (
      <Card className="max-w-2xl mx-auto text-center space-y-4">
        <h2 className="text-2xl font-bold text-white">Template Not Found</h2>
        <p className="text-gray-400">Please select a template from the templates page</p>
        <Button onClick={() => navigate('/templates')}>Browse Templates</Button>
      </Card>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/templates')}
        >
          ← Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-white">Create Project</h1>
          <p className="text-gray-400 mt-1">Template: {template.display_name}</p>
        </div>
      </div>

      {/* Template Info */}
      <Card>
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-12 h-12 bg-nvidia-green rounded-lg flex items-center justify-center text-white font-bold text-xl">
            {template.display_name[0]}
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">{template.display_name}</h3>
            <p className="text-sm text-gray-400 mt-1 capitalize">{template.type}</p>
            <p className="text-gray-300 mt-2">{template.description}</p>
          </div>
        </div>
      </Card>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <h2 className="text-xl font-semibold text-white mb-4">Project Details</h2>
          
          <div className="space-y-4">
            <Input
              label="Project Name"
              required
              placeholder="com.company.myapp"
              value={formData.name}
              onChange={(e) => handleFieldChange('name', e.target.value)}
              error={errors.name}
              helperText="Lowercase letters, numbers, dots, and underscores only"
            />

            <Input
              label="Display Name"
              placeholder="My Application"
              value={formData.displayName}
              onChange={(e) => handleFieldChange('displayName', e.target.value)}
              helperText="Human-readable name for your application"
            />

            <Input
              label="Version"
              required
              placeholder="1.0.0"
              value={formData.version}
              onChange={(e) => handleFieldChange('version', e.target.value)}
              error={errors.version}
              helperText="Semantic version (X.Y.Z)"
            />
          </div>
        </Card>

        {/* Advanced Options */}
        <Card>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center justify-between w-full text-left"
          >
            <h2 className="text-xl font-semibold text-white">Advanced Options</h2>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showAdvanced && (
            <div className="mt-4 space-y-4">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.standalone}
                  onChange={(e) => handleFieldChange('standalone', e.target.checked)}
                  className="mt-1 w-4 h-4 rounded bg-dark-bg border-gray-600 text-nvidia-green focus:ring-nvidia-green focus:ring-offset-dark-bg"
                />
                <div>
                  <div className="text-white font-medium">Create as standalone project</div>
                  <div className="text-sm text-gray-400">
                    Creates a self-contained project that can be distributed independently
                  </div>
                </div>
              </label>

              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.perAppDeps}
                  onChange={(e) => handleFieldChange('perAppDeps', e.target.checked)}
                  className="mt-1 w-4 h-4 rounded bg-dark-bg border-gray-600 text-nvidia-green focus:ring-nvidia-green focus:ring-offset-dark-bg"
                />
                <div>
                  <div className="text-white font-medium">Use per-app dependencies</div>
                  <div className="text-sm text-gray-400">
                    Isolates Kit SDK for this application to prevent dependency conflicts
                  </div>
                </div>
              </label>
            </div>
          )}
        </Card>

        {/* Error Message */}
        {error && (
          <Card className="bg-red-900/20 border-red-500">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="font-semibold text-red-500">Error</h3>
                <p className="text-red-400 text-sm mt-1">{error}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/templates')}
            disabled={creating}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={creating}
            disabled={creating || Object.keys(errors).some(k => errors[k])}
          >
            {creating ? 'Creating...' : 'Create Project'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CreateProjectPage;

