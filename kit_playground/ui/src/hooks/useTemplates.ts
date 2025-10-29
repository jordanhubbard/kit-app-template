import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Template as APITemplate } from '../services/types';

export interface TemplateModel {
  id: string;
  name: string;
  displayName: string;
  description: string;
  type: 'application' | 'extension' | 'microservice' | 'component';
  tags?: string[];
  icon?: string;
  thumbnail?: string;
  usageCount?: number;
  lastUsed?: Date;
  documentation?: {
    overview?: string;
    getting_started?: string;
    key_features?: string[];
    use_cases?: string[];
  };
  // Keep original API template for reference
  _original?: APITemplate;
}

interface UseTemplatesResult {
  templates: TemplateModel[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * useTemplates
 *
 * Custom hook to fetch templates from the API.
 * Handles loading states, errors, and data transformation.
 */
export const useTemplates = (): UseTemplatesResult => {
  const [templates, setTemplates] = useState<TemplateModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiService.listTemplates();

      // Transform API response to TemplateModel interface
      const transformedTemplates = Object.values(response.templates).map((t): TemplateModel => ({
        id: t.name, // Use name as ID
        name: t.name,
        displayName: t.display_name,
        description: t.description,
        // Use type from backend API, fallback to heuristic mapping if not provided
        type: (t.type as TemplateModel['type']) || mapTemplateType(t.name),
        tags: t.metadata?.tags || extractTags(t.name, t.description),
        icon: getIconForTemplate(t.name),
        documentation: t.documentation,
        _original: t,
        // usageCount and lastUsed would come from backend tracking
      }));

      setTemplates(transformedTemplates);
    } catch (err) {
      console.error('Failed to fetch templates:', err);
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  return {
    templates,
    loading,
    error,
    refetch: fetchTemplates,
  };
};

/**
 * Map template name to type
 */
function mapTemplateType(name: string): TemplateModel['type'] {
  if (name.includes('kit_service') || name.includes('service')) {
    return 'microservice';
  }
  if (name.includes('_ext') || name.includes('extension') || name.includes('_binding')) {
    return 'extension';
  }
  return 'application';
}

/**
 * Extract tags from template name and description
 */
function extractTags(name: string, description?: string): string[] {
  const tags: string[] = [];

  // Extract from name
  if (name.includes('usd')) tags.push('usd');
  if (name.includes('editor')) tags.push('editor');
  if (name.includes('viewer')) tags.push('viewer');
  if (name.includes('explorer')) tags.push('explorer');
  if (name.includes('composer')) tags.push('composer');
  if (name.includes('service')) tags.push('service');
  if (name.includes('python')) tags.push('python');
  if (name.includes('cpp') || name.includes('c++')) tags.push('c++');

  // Extract from description (if available)
  if (description) {
    const lowerDesc = description.toLowerCase();
    if (lowerDesc.includes('3d')) tags.push('3d');
    if (lowerDesc.includes('rtx') || lowerDesc.includes('rendering')) tags.push('rtx');
    if (lowerDesc.includes('streaming')) tags.push('streaming');
    if (lowerDesc.includes('microservice')) tags.push('microservice');
  }

  // Remove duplicates
  return [...new Set(tags)];
}

/**
 * Get emoji icon for template
 */
function getIconForTemplate(name: string): string {
  if (name.includes('editor')) return '🎮';
  if (name.includes('viewer')) return '🔧';
  if (name.includes('explorer')) return '🚀';
  if (name.includes('composer')) return '🎨';
  if (name.includes('service')) return '⚡';
  if (name.includes('python')) return '🐍';
  if (name.includes('cpp') || name.includes('c++')) return '⚙️';
  return '📦';
}
