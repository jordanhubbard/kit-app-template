/**
 * Template Gallery Component
 * Visual gallery for browsing local templates (applications, extensions, microservices)
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Extension as ExtensionIcon,
  Apps as AppsIcon,
  Cloud as CloudIcon,
  Code as CodeIcon,
  Info as InfoIcon,
  Folder as FolderIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  FilterList as FilterIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import CreateProjectDialog from '../dialogs/CreateProjectDialog';

interface Template {
  name: string;
  display_name: string;
  type: 'application' | 'extension' | 'microservice' | 'component';
  category: string;
  description: string;
  thumbnail?: string;
  icon?: string;
  color_scheme?: {
    primary?: string;
    accent?: string;
  };
  connectors: {
    name: string;
    type: string;
    direction: string;
  }[];
  metadata?: {
    version?: string;
    author?: string;
    tags?: string[];
  };
}

interface TemplateGalleryProps {
  onSelectTemplate: (templateId: string) => void;
  selectedTemplate: string | null;
  compact?: boolean;
  onEditTemplate?: (templateId: string) => void;
  onRunTemplate?: (templateId: string) => void;
  onCreateProject?: (projectInfo: any) => void;
}

const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  onSelectTemplate,
  selectedTemplate,
  compact = false,
  onEditTemplate,
  onRunTemplate,
  onCreateProject,
}) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<'all' | 'applications' | 'extensions' | 'microservices'>('all');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [templateForCreate, setTemplateForCreate] = useState<Template | null>(null);

  // Load templates from API
  useEffect(() => {
    loadTemplates();
    loadFavorites();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      // Use v2 API endpoint which returns all templates
      const response = await fetch('/api/v2/templates');
      const data = await response.json();

      // v2 API returns array directly with camelCase fields, map to component's format
      const templateArray = data.map((t: any) => ({
        name: t.id || t.name,
        display_name: t.displayName,
        type: t.type,
        category: t.category || 'general',
        description: t.description,
        thumbnail: undefined,
        icon: undefined,
        color_scheme: undefined,
        connectors: [],
        metadata: {
          version: t.version,
          tags: t.tags || []
        }
      })) as Template[];

      setTemplates(templateArray);
    } catch (error) {
      console.error('Failed to load templates:', error);
      // Fallback to mock data for development
      setTemplates(getMockTemplates());
    } finally {
      setLoading(false);
    }
  };

  const loadFavorites = () => {
    const stored = localStorage.getItem('kit-playground-favorites');
    if (stored) {
      setFavorites(new Set(JSON.parse(stored)));
    }
  };

  const saveFavorites = (newFavorites: Set<string>) => {
    localStorage.setItem('kit-playground-favorites', JSON.stringify(Array.from(newFavorites)));
    setFavorites(newFavorites);
  };

  const toggleFavorite = (templateName: string) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(templateName)) {
      newFavorites.delete(templateName);
    } else {
      newFavorites.add(templateName);
    }
    saveFavorites(newFavorites);
  };

  // Filter templates
  const filteredTemplates = useMemo(() => {
    let filtered = templates;

    // Tab filter
    if (activeTab !== 'all') {
      const typeMap = {
        applications: 'application',
        extensions: 'extension',
        microservices: 'microservice',
      };
      filtered = filtered.filter(t => t.type === typeMap[activeTab]);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.display_name.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.name.toLowerCase().includes(query) ||
        t.metadata?.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Type filter
    if (selectedType !== 'all') {
      filtered = filtered.filter(t => t.type === selectedType);
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    return filtered;
  }, [templates, searchQuery, selectedType, selectedCategory, activeTab]);

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(templates.map(t => t.category));
    return Array.from(cats).sort();
  }, [templates]);

  // Get template icon
  const getTemplateIcon = (type: string) => {
    switch (type) {
      case 'application':
        return <AppsIcon />;
      case 'extension':
        return <ExtensionIcon />;
      case 'microservice':
        return <CloudIcon />;
      case 'component':
        return <CodeIcon />;
      default:
        return <FolderIcon />;
    }
  };

  // Get type counts
  const typeCounts = useMemo(() => {
    return {
      all: templates.length,
      applications: templates.filter(t => t.type === 'application').length,
      extensions: templates.filter(t => t.type === 'extension').length,
      microservices: templates.filter(t => t.type === 'microservice').length,
    };
  }, [templates]);

  // Template card component
  const TemplateCard: React.FC<{ template: Template }> = ({ template }) => {
    const isSelected = selectedTemplate === template.name;
    const isFavorite = favorites.has(template.name);

    return (
      <Card
        sx={{
          height: compact ? 280 : 320,
          display: 'flex',
          flexDirection: 'column',
          cursor: 'pointer',
          border: isSelected ? 2 : 0,
          borderColor: 'primary.main',
          transition: 'all 0.2s',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: 6,
          },
        }}
        onClick={() => onSelectTemplate(template.name)}
      >
        {/* Thumbnail */}
        <Box
          sx={{
            position: 'relative',
            height: compact ? 120 : 160,
            backgroundColor: template.color_scheme?.primary || '#333',
            backgroundImage: template.thumbnail
              ? `url(${template.thumbnail})`
              : `linear-gradient(135deg, ${template.color_scheme?.primary || '#333'} 0%, ${template.color_scheme?.accent || '#555'} 100%)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {/* Type Badge */}
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              left: 8,
              backgroundColor: 'rgba(0,0,0,0.7)',
              borderRadius: 1,
              px: 1,
              py: 0.5,
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            {getTemplateIcon(template.type)}
            <Typography variant="caption" sx={{ color: 'white' }}>
              {template.type}
            </Typography>
          </Box>

          {/* Favorite Star */}
          <IconButton
            size="small"
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(0,0,0,0.7)',
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.9)',
              },
            }}
            onClick={(e) => {
              e.stopPropagation();
              toggleFavorite(template.name);
            }}
          >
            {isFavorite ? (
              <StarIcon sx={{ color: '#ffd700' }} fontSize="small" />
            ) : (
              <StarBorderIcon sx={{ color: 'white' }} fontSize="small" />
            )}
          </IconButton>

          {/* Connector Count */}
          {template.connectors && template.connectors.length > 0 && (
            <Chip
              label={`${template.connectors.length} connectors`}
              size="small"
              sx={{
                position: 'absolute',
                bottom: 8,
                right: 8,
                backgroundColor: 'rgba(118, 185, 0, 0.9)',
                color: 'white',
                fontSize: 11,
              }}
            />
          )}
        </Box>

        {/* Content */}
        <CardContent sx={{ flex: 1, pb: 1 }}>
          <Typography variant="h6" sx={{ fontSize: compact ? 14 : 16, mb: 0.5 }}>
            {template.display_name}
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              fontSize: compact ? 12 : 13,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: compact ? 2 : 3,
              WebkitBoxOrient: 'vertical',
              mb: 1,
            }}
          >
            {template.description}
          </Typography>

          {/* Category */}
          <Chip
            label={template.category}
            size="small"
            variant="outlined"
            sx={{ fontSize: 10, height: 20 }}
          />
        </CardContent>

        {/* Actions */}
        <CardActions sx={{ justifyContent: 'space-between', px: 2, pt: 0 }}>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title="Details">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectTemplate(template.name);
                }}
              >
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <Button
            size="small"
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={(e) => {
              e.stopPropagation();
              setTemplateForCreate(template);
              setCreateDialogOpen(true);
            }}
          >
            Create Project
          </Button>
        </CardActions>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography color="text.secondary">Loading templates...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Create Project Dialog */}
      <CreateProjectDialog
        open={createDialogOpen}
        template={templateForCreate}
        onClose={() => {
          setCreateDialogOpen(false);
          setTemplateForCreate(null);
        }}
        onSuccess={(projectInfo) => {
          setCreateDialogOpen(false);
          setTemplateForCreate(null);
          if (onCreateProject) {
            onCreateProject(projectInfo);
          }
        }}
      />

      {/* Search and Filters */}
      {!compact && (
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search templates..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="all">All Categories</MenuItem>
                  {categories.map(cat => (
                    <MenuItem key={cat} value={cat}>
                      {cat}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Type</InputLabel>
                <Select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="application">Applications</MenuItem>
                  <MenuItem value="extension">Extensions</MenuItem>
                  <MenuItem value="microservice">Microservices</MenuItem>
                  <MenuItem value="component">Components</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={(e, v) => setActiveTab(v)}
        sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
      >
        <Tab label={`All (${typeCounts.all})`} value="all" />
        <Tab
          label={`Applications (${typeCounts.applications})`}
          value="applications"
          icon={<AppsIcon />}
          iconPosition="start"
        />
        <Tab
          label={`Extensions (${typeCounts.extensions})`}
          value="extensions"
          icon={<ExtensionIcon />}
          iconPosition="start"
        />
        <Tab
          label={`Microservices (${typeCounts.microservices})`}
          value="microservices"
          icon={<CloudIcon />}
          iconPosition="start"
        />
      </Tabs>

      {/* Gallery Grid */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {filteredTemplates.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary',
            }}
          >
            <FilterIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
            <Typography variant="h6">No templates found</Typography>
            <Typography variant="body2">
              Try adjusting your search or filters
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={compact ? 2 : 3}>
            {filteredTemplates.map(template => (
              <Grid
                item
                key={template.name}
                xs={12}
                sm={compact ? 12 : 6}
                md={compact ? 6 : 4}
                lg={compact ? 4 : 3}
              >
                <TemplateCard template={template} />
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Box>
  );
};

// Mock data for development
function getMockTemplates(): Template[] {
  return [
    {
      name: 'omni_usd_composer_setup',
      display_name: 'USD Composer Setup',
      type: 'application',
      category: 'editor',
      description: 'Full-featured USD scene composition and editing application with viewport and timeline.',
      color_scheme: { primary: '#1a5490', accent: '#76b900' },
      connectors: [
        { name: 'usd_output', type: 'usd_stage', direction: 'output' },
        { name: 'extensions', type: 'extension', direction: 'bidirectional' },
      ],
      metadata: { version: '1.0.0', tags: ['usd', 'editor', 'viewport'] },
    },
    {
      name: 'omni_usd_viewer_setup',
      display_name: 'USD Viewer',
      type: 'application',
      category: 'viewer',
      description: 'Lightweight USD stage viewer for visualizing 3D scenes.',
      color_scheme: { primary: '#2d5a27', accent: '#76b900' },
      connectors: [
        { name: 'usd_input', type: 'usd_stage', direction: 'input' },
      ],
      metadata: { version: '1.0.0', tags: ['usd', 'viewer'] },
    },
    {
      name: 'basic_python',
      display_name: 'Basic Python Extension',
      type: 'extension',
      category: 'general',
      description: 'Simple Python extension template for adding custom functionality.',
      color_scheme: { primary: '#3776ab', accent: '#ffd43b' },
      connectors: [],
      metadata: { version: '1.0.0', tags: ['python', 'extension'] },
    },
    {
      name: 'python_ui',
      display_name: 'Python UI Extension',
      type: 'extension',
      category: 'ui',
      description: 'Extension template with UI components and windows.',
      color_scheme: { primary: '#3776ab', accent: '#ffd43b' },
      connectors: [],
      metadata: { version: '1.0.0', tags: ['python', 'ui', 'extension'] },
    },
    {
      name: 'usd_viewer_messaging',
      display_name: 'USD Viewer with Messaging',
      type: 'microservice',
      category: 'service',
      description: 'USD Viewer with WebSocket messaging for remote control.',
      color_scheme: { primary: '#e17000', accent: '#76b900' },
      connectors: [
        { name: 'usd_input', type: 'usd_stage', direction: 'input' },
        { name: 'websocket', type: 'websocket', direction: 'bidirectional' },
      ],
      metadata: { version: '1.0.0', tags: ['usd', 'messaging', 'websocket'] },
    },
  ];
}

export default TemplateGallery;