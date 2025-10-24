#!/usr/bin/env python3
"""
OpenAPI Specification Generator.

Generates OpenAPI 3.0 specification for Kit Playground API.
"""

from typing import Dict, Any


def get_openapi_spec() -> Dict[str, Any]:
    """
    Generate OpenAPI 3.0 specification for all API endpoints.

    Returns:
        OpenAPI specification dictionary
    """

    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Kit Playground API",
            "version": "1.0.0",
            "description": "REST API for NVIDIA Omniverse Kit Application Template management, builds, and job execution.",
            "contact": {
                "name": "Kit Playground",
                "url": "https://github.com/NVIDIA-Omniverse/kit-app-template"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8200",
                "description": "Local development server"
            }
        ],
        "tags": [
            {
                "name": "templates",
                "description": "Template management operations"
            },
            {
                "name": "jobs",
                "description": "Asynchronous job management"
            },
            {
                "name": "projects",
                "description": "Project build and launch operations"
            }
        ],
        "paths": {
            "/api/templates/list": {
                "get": {
                    "summary": "List all templates",
                    "description": "Get a list of all available templates",
                    "tags": ["templates"],
                    "parameters": [
                        {
                            "name": "type",
                            "in": "query",
                            "description": "Filter by template type (application, extension, microservice)",
                            "required": False,
                            "schema": {"type": "string", "enum": ["application", "extension", "microservice"]}
                        },
                        {
                            "name": "category",
                            "in": "query",
                            "description": "Filter by category",
                            "required": False,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of templates",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TemplateList"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/templates/get/{name}": {
                "get": {
                    "summary": "Get template details",
                    "description": "Get detailed information about a specific template",
                    "tags": ["templates"],
                    "parameters": [
                        {
                            "name": "name",
                            "in": "path",
                            "required": True,
                            "description": "Template name",
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Template details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TemplateDetail"}
                                }
                            }
                        },
                        "404": {
                            "description": "Template not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/templates/create": {
                "post": {
                    "summary": "Create project from template",
                    "description": "Generate a new project from a template",
                    "tags": ["templates"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateTemplateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Project created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CreateTemplateResponse"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/jobs": {
                "get": {
                    "summary": "List jobs",
                    "description": "Get a list of jobs with optional filtering",
                    "tags": ["jobs"],
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "description": "Filter by job status",
                            "required": False,
                            "schema": {"type": "string", "enum": ["pending", "running", "completed", "failed", "cancelled"]}
                        },
                        {
                            "name": "type",
                            "in": "query",
                            "description": "Filter by job type",
                            "required": False,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Maximum number of jobs to return",
                            "required": False,
                            "schema": {"type": "integer", "default": 50}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of jobs",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/JobList"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/jobs/{job_id}": {
                "get": {
                    "summary": "Get job details",
                    "description": "Get detailed information about a specific job",
                    "tags": ["jobs"],
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "description": "Job ID",
                            "schema": {"type": "string", "format": "uuid"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Job details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Job"}
                                }
                            }
                        },
                        "404": {
                            "description": "Job not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Delete job",
                    "description": "Delete a job from history",
                    "tags": ["jobs"],
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "description": "Job ID",
                            "schema": {"type": "string", "format": "uuid"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Job deleted successfully"
                        },
                        "404": {
                            "description": "Job not found"
                        }
                    }
                }
            },
            "/api/jobs/{job_id}/cancel": {
                "post": {
                    "summary": "Cancel job",
                    "description": "Cancel a running or pending job",
                    "tags": ["jobs"],
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "description": "Job ID",
                            "schema": {"type": "string", "format": "uuid"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Job cancelled successfully"
                        },
                        "400": {
                            "description": "Job cannot be cancelled"
                        }
                    }
                }
            },
            "/api/jobs/{job_id}/logs": {
                "get": {
                    "summary": "Get job logs",
                    "description": "Retrieve log output from a job",
                    "tags": ["jobs"],
                    "parameters": [
                        {
                            "name": "job_id",
                            "in": "path",
                            "required": True,
                            "description": "Job ID",
                            "schema": {"type": "string", "format": "uuid"}
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Maximum number of log lines",
                            "required": False,
                            "schema": {"type": "integer", "default": 1000}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Job logs",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/JobLogs"}
                                }
                            }
                        },
                        "404": {
                            "description": "Job not found"
                        }
                    }
                }
            },
            "/api/jobs/stats": {
                "get": {
                    "summary": "Get job statistics",
                    "description": "Get statistics about jobs (counts by status, etc.)",
                    "tags": ["jobs"],
                    "responses": {
                        "200": {
                            "description": "Job statistics",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/JobStats"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Template": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "example": "kit_base_editor"},
                        "display_name": {"type": "string", "example": "Kit Base Editor"},
                        "type": {"type": "string", "enum": ["application", "extension", "microservice"]},
                        "description": {"type": "string"},
                        "category": {"type": "string"}
                    }
                },
                "TemplateList": {
                    "type": "object",
                    "properties": {
                        "templates": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Template"}
                        }
                    }
                },
                "TemplateDetail": {
                    "type": "object",
                    "properties": {
                        "template": {"$ref": "#/components/schemas/Template"}
                    }
                },
                "CreateTemplateRequest": {
                    "type": "object",
                    "required": ["template", "name"],
                    "properties": {
                        "template": {"type": "string", "example": "kit_base_editor"},
                        "name": {"type": "string", "example": "my_app"},
                        "displayName": {"type": "string", "example": "My Application"},
                        "version": {"type": "string", "example": "1.0.0"},
                        "outputDir": {"type": "string", "example": "_build/apps"}
                    }
                },
                "CreateTemplateResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "success"},
                        "path": {"type": "string", "example": "_build/apps/my_app"}
                    }
                },
                "Job": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "type": {"type": "string", "example": "build"},
                        "status": {"type": "string", "enum": ["pending", "running", "completed", "failed", "cancelled"]},
                        "created_at": {"type": "string", "format": "date-time"},
                        "started_at": {"type": "string", "format": "date-time"},
                        "completed_at": {"type": "string", "format": "date-time"},
                        "progress": {"type": "integer", "minimum": 0, "maximum": 100},
                        "message": {"type": "string"},
                        "error": {"type": "string"},
                        "metadata": {"type": "object"}
                    }
                },
                "JobList": {
                    "type": "object",
                    "properties": {
                        "jobs": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Job"}
                        },
                        "count": {"type": "integer"}
                    }
                },
                "JobLogs": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string", "format": "uuid"},
                        "logs": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "count": {"type": "integer"}
                    }
                },
                "JobStats": {
                    "type": "object",
                    "properties": {
                        "total": {"type": "integer"},
                        "by_status": {
                            "type": "object",
                            "properties": {
                                "pending": {"type": "integer"},
                                "running": {"type": "integer"},
                                "completed": {"type": "integer"},
                                "failed": {"type": "integer"},
                                "cancelled": {"type": "integer"}
                            }
                        }
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"}
                    }
                }
            }
        }
    }

    return spec
