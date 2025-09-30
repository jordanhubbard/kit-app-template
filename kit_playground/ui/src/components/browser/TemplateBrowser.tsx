/**
 * Template Browser Component
 * Browse, search, and interact with templates from marketplace/repository
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Badge,
  Avatar,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  CloudDownload as DownloadIcon,
  Visibility as PreviewIcon,
  ContentCopy as CopyIcon,
  Edit as EditIcon,
  Star as StarIcon,
  Code as CodeIcon,
  PlayArrow as PlayIcon,
  Info as InfoIcon,
  GitHub as GitHubIcon,
  TrendingUp as TrendingIcon,
  NewReleases as NewIcon,
  Favorite as FavoriteIcon,
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../../hooks/redux';
import { fetchMarketplaceTemplates, downloadTemplate } from '../../services/marketplace';
import './TemplateBrowser.css';

interface MarketplaceTemplate {
  id: string;
  name: string;
  displayName: string;
  description: string;
  category: string;
  type: string;
  thumbnail: string;
  author: string;
  authorAvatar?: string;
  rating: number;
  downloads: number;
  stars: number;
  version: string;
  tags: string[];
  lastUpdated: string;
  size: string;
  license: string;
  githubUrl?: string;
  demoUrl?: string;
  connectors: {
    inputs: number;
    outputs: number;
    bidirectional: number;
  };
}

interface TemplateBrowserProps {
  onSelectTemplate: (templateId: string) => void;
  onEditTemplate?: (templateId: string) => void;
  onCopyTemplate?: (templateId: string) => void;
  onDeployTemplate?: (templateId: string) => void;
}

const TemplateBrowser: React.FC<TemplateBrowserProps> = ({
  onSelectTemplate,
  onEditTemplate,
  onCopyTemplate,
  onDeployTemplate,
}) => {
  const dispatch = useAppDispatch();
  const [templates, setTemplates] = useState<MarketplaceTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [sortBy, setSortBy] = useState<'popular' | 'newest' | 'rating'>('popular');
  const [selectedTemplate, setSelectedTemplate] = useState<MarketplaceTemplate | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'featured' | 'trending' | 'recent' | 'favorites'>('featured');

  // Fetch templates from marketplace
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await fetchMarketplaceTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort templates
  const filteredTemplates = useMemo(() => {
    let filtered = templates;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.displayName.toLowerCase().includes(query) ||
        t.description.toLowerCase().includes(query) ||
        t.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    // Type filter
    if (selectedType !== 'all') {
      filtered = filtered.filter(t => t.type === selectedType);
    }

    // Tab-specific filtering
    switch (activeTab) {
      case 'trending':
        filtered = filtered.filter(t => t.downloads > 1000);
        break;
      case 'recent':
        filtered = filtered.filter(t => {
          const daysSinceUpdate = Math.floor(
            (Date.now() - new Date(t.lastUpdated).getTime()) / (1000 * 60 * 60 * 24)
          );
          return daysSinceUpdate <= 30;
        });
        break;
      case 'favorites':
        // Would filter by user favorites
        break;
    }

    // Sort
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) =>
          new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
        );
        break;
      case 'rating':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case 'popular':
      default:
        filtered.sort((a, b) => b.downloads - a.downloads);
        break;
    }

    return filtered;
  }, [templates, searchQuery, selectedCategory, selectedType, sortBy, activeTab]);

  // Handle template download/install
  const handleDownload = async (template: MarketplaceTemplate) => {
    try {
      await downloadTemplate(template.id);
      // Refresh local templates
      dispatch({ type: 'templates/refresh' });
    } catch (error) {
      console.error('Failed to download template:', error);
    }
  };

  // Handle template preview
  const handlePreview = (template: MarketplaceTemplate) => {
    if (template.demoUrl) {
      window.open(template.demoUrl, '_blank');
    } else {
      setSelectedTemplate(template);
      setDetailsOpen(true);
    }
  };

  // Template card component
  const TemplateCard: React.FC<{ template: MarketplaceTemplate }> = ({ template }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={() => onSelectTemplate(template.id)}
    >
      {/* Thumbnail */}
      <Box sx={{ position: 'relative' }}>
        <CardMedia
          component="img"
          height="200"
          image={template.thumbnail || '/assets/default-template.png'}
          alt={template.displayName}
          sx={{ objectFit: 'cover' }}
        />

        {/* Category Badge */}
        <Chip
          label={template.category}
          size="small"
          sx={{
            position: 'absolute',
            top: 8,
            left: 8,
            backgroundColor: 'rgba(0,0,0,0.7)',
            color: 'white',
          }}
        />

        {/* New Badge */}
        {isNew(template.lastUpdated) && (
          <Badge
            badgeContent={<NewIcon fontSize="small" />}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              '& .MuiBadge-badge': {
                backgroundColor: '#ff5722',
                color: 'white',
              },
            }}
          />
        )}

        {/* Connector Info */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 8,
            right: 8,
            display: 'flex',
            gap: 0.5,
            backgroundColor: 'rgba(0,0,0,0.7)',
            borderRadius: 1,
            p: 0.5,
          }}
        >
          {template.connectors.inputs > 0 && (
            <Chip
              label={`↓${template.connectors.inputs}`}
              size="small"
              sx={{ height: 20, fontSize: 11 }}
            />
          )}
          {template.connectors.outputs > 0 && (
            <Chip
              label={`↑${template.connectors.outputs}`}
              size="small"
              sx={{ height: 20, fontSize: 11 }}
            />
          )}
          {template.connectors.bidirectional > 0 && (
            <Chip
              label={`↔${template.connectors.bidirectional}`}
              size="small"
              sx={{ height: 20, fontSize: 11 }}
            />
          )}
        </Box>
      </Box>

      <CardContent sx={{ flex: 1 }}>
        {/* Title and Author */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ flex: 1, fontSize: 16 }}>
            {template.displayName}
          </Typography>
          <Avatar
            src={template.authorAvatar}
            sx={{ width: 24, height: 24 }}
          >
            {template.author[0]}
          </Avatar>
        </Box>

        {/* Description */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {template.description}
        </Typography>

        {/* Stats */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Rating value={template.rating} size="small" readOnly />
            <Typography variant="caption">({template.rating})</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <DownloadIcon fontSize="small" />
            <Typography variant="caption">{formatNumber(template.downloads)}</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <StarIcon fontSize="small" />
            <Typography variant="caption">{formatNumber(template.stars)}</Typography>
          </Box>
        </Box>

        {/* Tags */}
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {template.tags.slice(0, 3).map(tag => (
            <Chip
              key={tag}
              label={tag}
              size="small"
              variant="outlined"
              sx={{ height: 20, fontSize: 11 }}
            />
          ))}
        </Box>
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ justifyContent: 'space-between', px: 2 }}>
        <Box>
          <Tooltip title="Preview">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handlePreview(template);
              }}
            >
              <PreviewIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View Code">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                if (template.githubUrl) {
                  window.open(template.githubUrl, '_blank');
                }
              }}
              disabled={!template.githubUrl}
            >
              <GitHubIcon />
            </IconButton>
          </Tooltip>
        </Box>
        <Button
          size="small"
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={(e) => {
            e.stopPropagation();
            handleDownload(template);
          }}
        >
          Install
        </Button>
      </CardActions>
    </Card>
  );

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Search and Filters */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
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
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                label="Category"
              >
                <MenuItem value="all">All Categories</MenuItem>
                <MenuItem value="editor">Editors</MenuItem>
                <MenuItem value="viewer">Viewers</MenuItem>
                <MenuItem value="service">Services</MenuItem>
                <MenuItem value="connector">Connectors</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={6} md={2}>
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
          <Grid item xs={6} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                label="Sort By"
              >
                <MenuItem value="popular">Most Popular</MenuItem>
                <MenuItem value="newest">Newest</MenuItem>
                <MenuItem value="rating">Highest Rated</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={(e, v) => setActiveTab(v)}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="Featured" value="featured" />
        <Tab label="Trending" value="trending" icon={<TrendingIcon />} iconPosition="start" />
        <Tab label="Recent" value="recent" icon={<NewIcon />} iconPosition="start" />
        <Tab label="Favorites" value="favorites" icon={<FavoriteIcon />} iconPosition="start" />
      </Tabs>

      {/* Template Grid */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <Grid container spacing={3}>
          {filteredTemplates.map(template => (
            <Grid item key={template.id} xs={12} sm={6} md={4} lg={3}>
              <TemplateCard template={template} />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Template Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedTemplate && (
          <>
            <DialogTitle>{selectedTemplate.displayName}</DialogTitle>
            <DialogContent>
              {/* Details content */}
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsOpen(false)}>Close</Button>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={() => handleDownload(selectedTemplate)}
              >
                Install Template
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

// Helper functions
const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

const isNew = (dateStr: string): boolean => {
  const date = new Date(dateStr);
  const daysSince = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
  return daysSince <= 7;
};

export default TemplateBrowser;