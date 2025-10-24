#!/usr/bin/env python3
"""
WebSocket Routes for Real-Time Communication.

Provides WebSocket event handlers for:
- Real-time log streaming
- Job progress updates
- Build/launch status updates
"""

import logging
import time
from flask_socketio import emit, join_room, leave_room
from typing import Dict, Any

from kit_playground.backend.source.job_manager import get_job_manager

logger = logging.getLogger(__name__)


def register_websocket_handlers(socketio):
    """
    Register WebSocket event handlers.
    
    Args:
        socketio: Flask-SocketIO instance
    """
    
    job_manager = get_job_manager()
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"WebSocket client connected")
        emit('connected', {'message': 'Connected to Kit Playground'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"WebSocket client disconnected")
    
    @socketio.on('subscribe_job')
    def handle_subscribe_job(data: Dict[str, Any]):
        """
        Subscribe to job updates.
        
        Client will receive real-time updates for the specified job.
        
        Data format:
            {
                "job_id": "uuid-string"
            }
        """
        try:
            job_id = data.get('job_id')
            if not job_id:
                emit('error', {'message': 'job_id required'})
                return
            
            # Join room for this job
            join_room(f'job_{job_id}')
            
            # Send current job status
            job = job_manager.get_job(job_id)
            if job:
                emit('job_status', job.to_dict())
            else:
                emit('error', {'message': f'Job {job_id} not found'})
            
            logger.info(f"Client subscribed to job {job_id}")
            
        except Exception as e:
            logger.error(f"Error subscribing to job: {e}", exc_info=True)
            emit('error', {'message': str(e)})
    
    @socketio.on('unsubscribe_job')
    def handle_unsubscribe_job(data: Dict[str, Any]):
        """
        Unsubscribe from job updates.
        
        Data format:
            {
                "job_id": "uuid-string"
            }
        """
        try:
            job_id = data.get('job_id')
            if not job_id:
                emit('error', {'message': 'job_id required'})
                return
            
            # Leave room for this job
            leave_room(f'job_{job_id}')
            
            logger.info(f"Client unsubscribed from job {job_id}")
            emit('unsubscribed', {'job_id': job_id})
            
        except Exception as e:
            logger.error(f"Error unsubscribing from job: {e}", exc_info=True)
            emit('error', {'message': str(e)})
    
    @socketio.on('get_job_logs')
    def handle_get_job_logs(data: Dict[str, Any]):
        """
        Get job logs via WebSocket.
        
        Data format:
            {
                "job_id": "uuid-string",
                "limit": 1000  # optional
            }
        """
        try:
            job_id = data.get('job_id')
            limit = data.get('limit', 1000)
            
            if not job_id:
                emit('error', {'message': 'job_id required'})
                return
            
            logs = job_manager.get_job_logs(job_id, limit=limit)
            emit('job_logs', {
                'job_id': job_id,
                'logs': logs,
                'count': len(logs)
            })
            
        except Exception as e:
            logger.error(f"Error getting job logs: {e}", exc_info=True)
            emit('error', {'message': str(e)})
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping for connection keepalive."""
        emit('pong', {'timestamp': time.time()})
    
    # Utility functions for emitting events to job subscribers
    def emit_job_log(job_id: str, log_line: str):
        """Emit log line to all subscribers of a job."""
        socketio.emit('job_log', {
            'job_id': job_id,
            'log': log_line
        }, room=f'job_{job_id}')
    
    def emit_job_progress(job_id: str, progress: int, message: str = ""):
        """Emit progress update to all subscribers of a job."""
        socketio.emit('job_progress', {
            'job_id': job_id,
            'progress': progress,
            'message': message
        }, room=f'job_{job_id}')
    
    def emit_job_status(job_id: str, status: str, **kwargs):
        """Emit status change to all subscribers of a job."""
        data = {
            'job_id': job_id,
            'status': status,
            **kwargs
        }
        socketio.emit('job_status_change', data, room=f'job_{job_id}')
    
    def emit_job_complete(job_id: str, result: Any = None):
        """Emit job completion to all subscribers."""
        socketio.emit('job_complete', {
            'job_id': job_id,
            'result': result
        }, room=f'job_{job_id}')
    
    def emit_job_error(job_id: str, error: str):
        """Emit job error to all subscribers."""
        socketio.emit('job_error', {
            'job_id': job_id,
            'error': error
        }, room=f'job_{job_id}')
    
    # Store utility functions on socketio for external use
    socketio.emit_job_log = emit_job_log
    socketio.emit_job_progress = emit_job_progress
    socketio.emit_job_status = emit_job_status
    socketio.emit_job_complete = emit_job_complete
    socketio.emit_job_error = emit_job_error
    
    logger.info("WebSocket handlers registered")

