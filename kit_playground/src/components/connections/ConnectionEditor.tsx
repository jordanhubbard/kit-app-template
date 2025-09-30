/**
 * Connection Editor Component
 * Visual editor for connecting templates using drag-and-drop
 * (Simplified version - full implementation would use react-flow or similar)
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Tooltip,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Link as LinkIcon,
  LinkOff as UnlinkIcon,
  AutoFixHigh as AutoConnectIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

interface Template {
  id: string;
  name: string;
  connectors: Connector[];
}

interface Connector {
  name: string;
  type: string;
  direction: 'input' | 'output' | 'bidirectional';
}

interface Connection {
  from: string;
  fromConnector: string;
  to: string;
  toConnector: string;
}

interface ConnectionEditorProps {
  templates: Template[];
  connections: Connection[];
  onConnectionsChange: (connections: Connection[]) => void;
}

const ConnectionEditor: React.FC<ConnectionEditorProps> = ({
  templates,
  connections,
  onConnectionsChange,
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [selectedConnector, setSelectedConnector] = useState<string | null>(null);
  const [compatibleConnections, setCompatibleConnections] = useState<string[]>([]);

  // Handle connector selection for creating connections
  const handleConnectorClick = useCallback(
    (templateId: string, connectorName: string, direction: string) => {
      if (!selectedTemplate) {
        // First selection
        setSelectedTemplate(templateId);
        setSelectedConnector(connectorName);

        // Find compatible connectors
        const compatible = templates
          .filter(t => t.id !== templateId)
          .flatMap(t =>
            t.connectors
              .filter(c => {
                // Simplified compatibility check
                if (direction === 'output') return c.direction === 'input';
                if (direction === 'input') return c.direction === 'output';
                return true; // bidirectional can connect to anything
              })
              .map(c => `${t.id}.${c.name}`)
          );

        setCompatibleConnections(compatible);
      } else {
        // Second selection - create connection
        const newConnection: Connection = {
          from: selectedTemplate,
          fromConnector: selectedConnector!,
          to: templateId,
          toConnector: connectorName,
        };

        onConnectionsChange([...connections, newConnection]);

        // Reset selection
        setSelectedTemplate(null);
        setSelectedConnector(null);
        setCompatibleConnections([]);
      }
    },
    [selectedTemplate, selectedConnector, templates, connections, onConnectionsChange]
  );

  // Cancel connection creation
  const handleCancelConnection = () => {
    setSelectedTemplate(null);
    setSelectedConnector(null);
    setCompatibleConnections([]);
  };

  // Delete connection
  const handleDeleteConnection = (index: number) => {
    const newConnections = connections.filter((_, i) => i !== index);
    onConnectionsChange(newConnections);
  };

  // Auto-connect templates
  const handleAutoConnect = async () => {
    try {
      const response = await fetch('/api/templates/auto-connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ templates: templates.map(t => t.id) }),
      });

      const data = await response.json();
      if (data.connections) {
        onConnectionsChange(data.connections);
      }
    } catch (error) {
      console.error('Auto-connect failed:', error);
    }
  };

  // Get connector color based on direction
  const getConnectorColor = (direction: string) => {
    switch (direction) {
      case 'input':
        return '#2196f3';
      case 'output':
        return '#76b900';
      case 'bidirectional':
        return '#ff9800';
      default:
        return '#9e9e9e';
    }
  };

  // Check if connector is selected or compatible
  const getConnectorState = (templateId: string, connectorName: string) => {
    if (
      selectedTemplate === templateId &&
      selectedConnector === connectorName
    ) {
      return 'selected';
    }
    if (compatibleConnections.includes(`${templateId}.${connectorName}`)) {
      return 'compatible';
    }
    return 'normal';
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: '#1e1e1e',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="h6">Connection Editor</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {selectedTemplate && (
            <Button
              size="small"
              variant="outlined"
              onClick={handleCancelConnection}
            >
              Cancel
            </Button>
          )}
          <Tooltip title="Auto-connect compatible templates">
            <IconButton onClick={handleAutoConnect} disabled={templates.length < 2}>
              <AutoConnectIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Instructions */}
      {selectedTemplate ? (
        <Alert severity="info" sx={{ m: 2 }}>
          Select a compatible connector to complete the connection
        </Alert>
      ) : (
        <Alert severity="info" sx={{ m: 2 }}>
          Click on a connector to start creating a connection
        </Alert>
      )}

      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {/* Templates Grid */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 2,
            mb: 3,
          }}
        >
          {templates.map(template => (
            <Card
              key={template.id}
              sx={{
                border: selectedTemplate === template.id ? 2 : 0,
                borderColor: 'primary.main',
              }}
            >
              <CardContent>
                <Typography variant="h6" sx={{ fontSize: 14, mb: 2 }}>
                  {template.name}
                </Typography>

                {/* Connectors */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  {template.connectors.map(connector => {
                    const state = getConnectorState(template.id, connector.name);

                    return (
                      <Box
                        key={connector.name}
                        onClick={() =>
                          handleConnectorClick(
                            template.id,
                            connector.name,
                            connector.direction
                          )
                        }
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          p: 1,
                          borderRadius: 1,
                          cursor: 'pointer',
                          backgroundColor:
                            state === 'selected'
                              ? 'rgba(118, 185, 0, 0.2)'
                              : state === 'compatible'
                              ? 'rgba(33, 150, 243, 0.1)'
                              : 'transparent',
                          border: 1,
                          borderColor:
                            state === 'selected'
                              ? '#76b900'
                              : state === 'compatible'
                              ? '#2196f3'
                              : 'divider',
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.05)',
                          },
                        }}
                      >
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            backgroundColor: getConnectorColor(connector.direction),
                          }}
                        />
                        <Typography variant="body2" sx={{ flex: 1, fontSize: 12 }}>
                          {connector.name}
                        </Typography>
                        <Chip
                          label={connector.direction}
                          size="small"
                          sx={{ fontSize: 10, height: 18 }}
                        />
                      </Box>
                    );
                  })}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Existing Connections */}
        {connections.length > 0 && (
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Active Connections
            </Typography>
            <List>
              {connections.map((conn, index) => (
                <ListItem
                  key={index}
                  sx={{
                    backgroundColor: '#252526',
                    borderRadius: 1,
                    mb: 1,
                  }}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteConnection(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <LinkIcon sx={{ mr: 2, color: '#76b900' }} />
                  <ListItemText
                    primary={`${conn.from}.${conn.fromConnector} → ${conn.to}.${conn.toConnector}`}
                    primaryTypographyProps={{ fontSize: 14 }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Empty State */}
        {templates.length === 0 && (
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
            <UnlinkIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
            <Typography variant="h6">No templates in project</Typography>
            <Typography variant="body2">
              Add templates to your project to start creating connections
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default ConnectionEditor;