# Kit App Template REST API Usage

**Version**: 2.0
**Last Updated**: October 24, 2025
**API Documentation**: http://localhost:5000/api/docs/ui (Swagger UI)

## Overview

The Kit App Template REST API provides programmatic access to template management, job execution, and project operations. This guide covers practical usage with `curl` examples.

> **📚 Complete API Reference**: For detailed API specifications, schemas, and interactive testing, see the Swagger UI at `http://localhost:5000/api/docs/ui` when the server is running.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Template Management](#template-management)
4. [Job Management](#job-management)
5. [WebSocket Streaming](#websocket-streaming)
6. [Project Operations](#project-operations)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

---

## Quick Start

### Start the API Server

```bash
# Option 1: Start backend only
cd kit_playground/backend
python3 web_server.py

# Option 2: Start full playground (UI + backend)
cd kit-app-template
./playground.sh

# API available at: http://localhost:5000
# Swagger UI at: http://localhost:5000/api/docs/ui
```

### Test the API

```bash
# Health check
curl http://localhost:5000/api/templates/list

# View API documentation
open http://localhost:5000/api/docs/ui
```

### Base URL

All examples use `http://localhost:5000` as the base URL. Adjust if running on a different host/port.

---

## Authentication

**Current Version**: No authentication required (local development)

For production deployments, you may want to add:
- API keys
- JWT tokens
- OAuth2

See the backend code for integration points.

---

## Template Management

### List All Templates

Get a list of all available templates.

```bash
curl -X GET http://localhost:5000/api/templates/list

# Or the alias:
curl -X GET http://localhost:5000/api/templates
```

**Response**:
```json
{
  "templates": {
    "kit_base_editor": {
      "name": "kit_base_editor",
      "display_name": "Kit Base Editor",
      "description": "Full-featured Omniverse editor application",
      "type": "application",
      "version": "1.0.0"
    },
    "omni_usd_viewer": {
      "name": "omni_usd_viewer",
      "display_name": "USD Viewer",
      "description": "USD file viewer application",
      "type": "application"
    }
    // ... more templates
  }
}
```

### Get Template Details

Get detailed information about a specific template.

```bash
curl -X GET http://localhost:5000/api/templates/get/kit_base_editor
```

**Response**:
```json
{
  "template": {
    "name": "kit_base_editor",
    "display_name": "Kit Base Editor",
    "description": "Full-featured Omniverse editor application",
    "type": "application",
    "version": "1.0.0",
    "metadata": {
      "category": "application",
      "tags": ["editor", "base", "full-featured"],
      "requirements": {
        "min_kit_version": "105.0"
      }
    }
  }
}
```

### Create Project from Template

Create a new project from a template.

```bash
curl -X POST http://localhost:5000/api/templates/create \
  -H "Content-Type: application/json" \
  -d '{
    "template": "kit_base_editor",
    "name": "my.new.app",
    "displayName": "My New Application",
    "version": "1.0.0"
  }'
```

**Request Body**:
```json
{
  "template": "kit_base_editor",      // Required: template name
  "name": "my.new.app",               // Required: project name
  "displayName": "My Application",    // Optional: display name
  "version": "1.0.0",                 // Optional: version (default: "1.0.0")
  "outputDir": null,                  // Optional: output directory
  "options": {}                       // Optional: template-specific options
}
```

**Response**:
```json
{
  "success": true,
  "projectInfo": {
    "projectName": "my.new.app",
    "displayName": "My New Application",
    "outputDir": null,
    "kitFile": "my.new.app.kit"
  }
}
```

**Error Response**:
```json
{
  "error": "template and name are required"
}
```

---

## Job Management

The API supports asynchronous job execution for long-running operations like builds and launches.

### List All Jobs

Get a list of all jobs.

```bash
# All jobs
curl -X GET http://localhost:5000/api/jobs

# Filter by status
curl -X GET "http://localhost:5000/api/jobs?status=running"

# Filter by type
curl -X GET "http://localhost:5000/api/jobs?type=build"
```

**Response**:
```json
{
  "jobs": [
    {
      "id": "job_abc123",
      "type": "build",
      "status": "running",
      "progress": 45,
      "created_at": "2025-10-24T10:30:00Z",
      "started_at": "2025-10-24T10:30:05Z",
      "project_name": "my.app"
    },
    {
      "id": "job_def456",
      "type": "template_create",
      "status": "completed",
      "progress": 100,
      "created_at": "2025-10-24T10:25:00Z",
      "completed_at": "2025-10-24T10:25:30Z"
    }
  ],
  "count": 2
}
```

### Get Job Status

Get details about a specific job.

```bash
curl -X GET http://localhost:5000/api/jobs/job_abc123
```

**Response**:
```json
{
  "job": {
    "id": "job_abc123",
    "type": "build",
    "status": "running",
    "progress": 45,
    "created_at": "2025-10-24T10:30:00Z",
    "started_at": "2025-10-24T10:30:05Z",
    "project_name": "my.app",
    "logs": [
      "[10:30:05] Starting build process...",
      "[10:30:10] Compiling extensions...",
      "[10:30:15] Building application..."
    ]
  }
}
```

### Cancel Job

Cancel a running or pending job.

```bash
curl -X POST http://localhost:5000/api/jobs/job_abc123/cancel
```

**Response**:
```json
{
  "success": true,
  "message": "Job cancelled",
  "job_id": "job_abc123"
}
```

### Delete Job

Delete a completed, failed, or cancelled job.

```bash
curl -X DELETE http://localhost:5000/api/jobs/job_abc123
```

**Response**:
```json
{
  "success": true,
  "message": "Job deleted",
  "job_id": "job_abc123"
}
```

### Get Job Statistics

Get aggregate statistics about jobs.

```bash
curl -X GET http://localhost:5000/api/jobs/stats
```

**Response**:
```json
{
  "total": 150,
  "by_status": {
    "pending": 2,
    "running": 3,
    "completed": 120,
    "failed": 20,
    "cancelled": 5
  },
  "by_type": {
    "build": 80,
    "launch": 50,
    "template_create": 20
  },
  "recent_completed": 15,
  "recent_failed": 2
}
```

---

## WebSocket Streaming

Real-time updates for job progress, logs, and status changes via WebSocket (Socket.IO).

### Connect to WebSocket

```javascript
// JavaScript/Node.js example
const io = require('socket.io-client');

const socket = io('http://localhost:5000', {
  transports: ['websocket', 'polling']
});

socket.on('connect', () => {
  console.log('Connected to WebSocket');
});

// Listen for job logs
socket.on('job_log', (data) => {
  console.log(`[${data.job_id}] ${data.message}`);
});

// Listen for job progress
socket.on('job_progress', (data) => {
  console.log(`Job ${data.job_id}: ${data.progress}%`);
});

// Listen for job status changes
socket.on('job_status', (data) => {
  console.log(`Job ${data.job_id}: ${data.status}`);
});
```

### Python Example

```python
import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to WebSocket')

@sio.on('job_log')
def on_job_log(data):
    print(f"[{data['job_id']}] {data['message']}")

@sio.on('job_progress')
def on_job_progress(data):
    print(f"Job {data['job_id']}: {data['progress']}%")

@sio.on('job_status')
def on_job_status(data):
    print(f"Job {data['job_id']}: {data['status']}")

sio.connect('http://localhost:5000')
sio.wait()
```

### WebSocket Events

| Event | Data | Description |
|-------|------|-------------|
| `job_log` | `{job_id, timestamp, message}` | Log message from job |
| `job_progress` | `{job_id, progress, total}` | Progress update (0-100) |
| `job_status` | `{job_id, status, timestamp}` | Status change (pending, running, completed, failed, cancelled) |

---

## Project Operations

### Build Project

Trigger a build for a specific project.

```bash
curl -X POST http://localhost:5000/api/projects/build \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my.app",
    "config": "release"
  }'
```

**Response**:
```json
{
  "success": true,
  "job_id": "job_abc123",
  "message": "Build started"
}
```

### Launch Application

Launch a built application.

```bash
curl -X POST http://localhost:5000/api/projects/launch \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my.app",
    "config": "release",
    "headless": false
  }'
```

**Response**:
```json
{
  "success": true,
  "job_id": "job_def456",
  "message": "Application launched",
  "process_id": 12345
}
```

### Stop Application

Stop a running application.

```bash
curl -X POST http://localhost:5000/api/projects/stop \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my.app"
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Application stopped"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional context"
  }
}
```

### Common Errors

**Missing Required Parameters**:
```json
{
  "error": "template and name are required"
}
```

**Template Not Found**:
```json
{
  "error": "Template 'invalid_template' not found"
}
```

**Job Not Found**:
```json
{
  "error": "Job 'job_invalid' not found"
}
```

**Build Failed**:
```json
{
  "error": "Build failed",
  "details": {
    "exit_code": 1,
    "logs": "...error output..."
  }
}
```

---

## Examples

### Complete Workflow: Create, Build, Launch

```bash
#!/bin/bash

API_BASE="http://localhost:5000/api"

# 1. Create project from template
echo "Creating project..."
CREATE_RESULT=$(curl -s -X POST ${API_BASE}/templates/create \
  -H "Content-Type: application/json" \
  -d '{
    "template": "kit_base_editor",
    "name": "demo.app",
    "displayName": "Demo Application"
  }')

echo "Create result: $CREATE_RESULT"

# Check if successful
if echo "$CREATE_RESULT" | jq -e '.success' > /dev/null; then
  echo "✓ Project created successfully"
else
  echo "✗ Project creation failed"
  exit 1
fi

# 2. Wait a moment for file system operations
sleep 2

# 3. Build project
echo "Building project..."
BUILD_RESULT=$(curl -s -X POST ${API_BASE}/projects/build \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "demo.app",
    "config": "release"
  }')

JOB_ID=$(echo "$BUILD_RESULT" | jq -r '.job_id')
echo "Build job ID: $JOB_ID"

# 4. Poll job status
echo "Waiting for build to complete..."
while true; do
  JOB_STATUS=$(curl -s -X GET ${API_BASE}/jobs/${JOB_ID})
  STATUS=$(echo "$JOB_STATUS" | jq -r '.job.status')
  PROGRESS=$(echo "$JOB_STATUS" | jq -r '.job.progress')

  echo "Status: $STATUS, Progress: $PROGRESS%"

  if [ "$STATUS" = "completed" ]; then
    echo "✓ Build completed successfully"
    break
  elif [ "$STATUS" = "failed" ]; then
    echo "✗ Build failed"
    echo "$JOB_STATUS" | jq '.job.logs'
    exit 1
  fi

  sleep 5
done

# 5. Launch application
echo "Launching application..."
LAUNCH_RESULT=$(curl -s -X POST ${API_BASE}/projects/launch \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "demo.app",
    "config": "release"
  }')

echo "Launch result: $LAUNCH_RESULT"
echo "✓ Application launched"
```

### Monitor Job with WebSocket

```python
#!/usr/bin/env python3
"""
Monitor job progress in real-time using WebSocket
"""
import socketio
import requests
import json
import time

API_BASE = "http://localhost:5000/api"
sio = socketio.Client()

# Track job status
job_complete = False
job_status = None

@sio.on('connect')
def on_connect():
    print('✓ Connected to WebSocket')

@sio.on('job_log')
def on_job_log(data):
    print(f"[LOG] {data['message']}")

@sio.on('job_progress')
def on_job_progress(data):
    print(f"[PROGRESS] {data['progress']}%")

@sio.on('job_status')
def on_job_status(data):
    global job_complete, job_status
    print(f"[STATUS] {data['status']}")
    job_status = data['status']
    if data['status'] in ['completed', 'failed', 'cancelled']:
        job_complete = True

# Connect to WebSocket
sio.connect('http://localhost:5000')

# Create a project (this will trigger job events)
print("Creating project...")
response = requests.post(f"{API_BASE}/templates/create", json={
    "template": "kit_base_editor",
    "name": "websocket.demo",
    "displayName": "WebSocket Demo"
})

result = response.json()
if result.get('success'):
    print("✓ Project creation started")

    # Wait for job to complete
    print("Waiting for job to complete...")
    while not job_complete:
        time.sleep(0.5)

    print(f"✓ Job finished with status: {job_status}")
else:
    print(f"✗ Failed: {result.get('error')}")

sio.disconnect()
```

### Batch Create Multiple Projects

```bash
#!/bin/bash

API_BASE="http://localhost:5000/api"

# Array of projects to create
declare -a projects=(
  "kit_base_editor:editor.app:Editor Application"
  "omni_usd_viewer:viewer.app:USD Viewer"
  "omni_usd_explorer:explorer.app:USD Explorer"
)

# Create each project
for project in "${projects[@]}"; do
  IFS=':' read -r template name display <<< "$project"

  echo "Creating $name from $template..."

  curl -s -X POST ${API_BASE}/templates/create \
    -H "Content-Type: application/json" \
    -d "{
      \"template\": \"$template\",
      \"name\": \"$name\",
      \"displayName\": \"$display\"
    }" | jq .

  echo "---"
  sleep 1
done

echo "✓ All projects created"
```

### List Jobs and Clean Up

```bash
#!/bin/bash

API_BASE="http://localhost:5000/api"

# Get all completed jobs
echo "Fetching completed jobs..."
JOBS=$(curl -s -X GET "${API_BASE}/jobs?status=completed")

echo "Completed jobs:"
echo "$JOBS" | jq '.jobs[] | {id, type, completed_at}'

# Delete old completed jobs
echo "Cleaning up completed jobs..."
JOB_IDS=$(echo "$JOBS" | jq -r '.jobs[].id')

for job_id in $JOB_IDS; do
  echo "Deleting job: $job_id"
  curl -s -X DELETE "${API_BASE}/jobs/${job_id}"
done

echo "✓ Cleanup complete"
```

---

## API Reference Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/templates` | GET | List all templates |
| `/api/templates/get/<name>` | GET | Get template details |
| `/api/templates/create` | POST | Create project from template |
| `/api/jobs` | GET | List all jobs |
| `/api/jobs/<id>` | GET | Get job status |
| `/api/jobs/<id>/cancel` | POST | Cancel job |
| `/api/jobs/<id>` | DELETE | Delete job |
| `/api/jobs/stats` | GET | Get job statistics |
| `/api/projects/build` | POST | Build project |
| `/api/projects/launch` | POST | Launch application |
| `/api/projects/stop` | POST | Stop application |
| `/api/docs` | GET | OpenAPI spec (JSON) |
| `/api/docs/ui` | GET | Swagger UI |

---

## Additional Resources

- **Swagger UI**: http://localhost:5000/api/docs/ui (interactive API documentation)
- **OpenAPI Spec**: http://localhost:5000/api/docs (JSON)
- **CLI Documentation**: [docs/README.md](README.md)
- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)

---

**For complete, up-to-date API specifications, always refer to the Swagger UI at `/api/docs/ui`.**
