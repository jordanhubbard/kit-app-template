#!/usr/bin/env python3
"""
Job Management API Routes.

Provides REST API endpoints for job management:
- Submit jobs
- Get job status
- List jobs
- Cancel jobs
- Get job logs
"""

from flask import Blueprint, jsonify, request
import logging

from kit_playground.backend.source.job_manager import get_job_manager, JobStatus

logger = logging.getLogger(__name__)


def create_job_routes() -> Blueprint:
    """Create and configure job management routes."""
    
    job_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')
    job_manager = get_job_manager()
    
    @job_bp.route('', methods=['GET'])
    def list_jobs():
        """
        List all jobs with optional filtering.
        
        Query params:
            status: Filter by status (pending, running, completed, failed, cancelled)
            type: Filter by job type
            limit: Maximum number of jobs to return (default: 50)
        """
        try:
            # Parse query params
            status_str = request.args.get('status')
            job_type = request.args.get('type')
            limit = int(request.args.get('limit', 50))
            
            # Parse status
            status = None
            if status_str:
                try:
                    status = JobStatus(status_str)
                except ValueError:
                    return jsonify({'error': f'Invalid status: {status_str}'}), 400
            
            # Get jobs
            jobs = job_manager.list_jobs(status=status, job_type=job_type, limit=limit)
            
            return jsonify({
                'jobs': [job.to_dict() for job in jobs],
                'count': len(jobs)
            })
            
        except Exception as e:
            logger.error(f"Error listing jobs: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @job_bp.route('/<job_id>', methods=['GET'])
    def get_job(job_id: str):
        """
        Get job details by ID.
        
        Returns job information including status, progress, and metadata.
        """
        try:
            job = job_manager.get_job(job_id)
            
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            
            return jsonify(job.to_dict())
            
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @job_bp.route('/<job_id>/logs', methods=['GET'])
    def get_job_logs(job_id: str):
        """
        Get job logs.
        
        Query params:
            limit: Maximum number of log lines (default: 1000)
        """
        try:
            limit = int(request.args.get('limit', 1000))
            logs = job_manager.get_job_logs(job_id, limit=limit)
            
            if logs is None:
                return jsonify({'error': 'Job not found'}), 404
            
            return jsonify({
                'job_id': job_id,
                'logs': logs,
                'count': len(logs)
            })
            
        except Exception as e:
            logger.error(f"Error getting logs for job {job_id}: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @job_bp.route('/<job_id>/cancel', methods=['POST'])
    def cancel_job(job_id: str):
        """
        Cancel a running or pending job.
        
        Returns success if job was cancelled, error otherwise.
        """
        try:
            success = job_manager.cancel_job(job_id)
            
            if not success:
                return jsonify({'error': 'Job not found or cannot be cancelled'}), 400
            
            return jsonify({
                'message': 'Job cancelled successfully',
                'job_id': job_id
            })
            
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @job_bp.route('/<job_id>', methods=['DELETE'])
    def delete_job(job_id: str):
        """
        Delete a job from history.
        
        Only completed, failed, or cancelled jobs can be deleted.
        """
        try:
            success = job_manager.delete_job(job_id)
            
            if not success:
                return jsonify({'error': 'Job not found'}), 404
            
            return jsonify({
                'message': 'Job deleted successfully',
                'job_id': job_id
            })
            
        except Exception as e:
            logger.error(f"Error deleting job {job_id}: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    @job_bp.route('/stats', methods=['GET'])
    def get_stats():
        """
        Get job statistics.
        
        Returns counts by status and other metrics.
        """
        try:
            all_jobs = job_manager.list_jobs(limit=1000)
            
            stats = {
                'total': len(all_jobs),
                'by_status': {
                    'pending': len([j for j in all_jobs if j.status == JobStatus.PENDING]),
                    'running': len([j for j in all_jobs if j.status == JobStatus.RUNNING]),
                    'completed': len([j for j in all_jobs if j.status == JobStatus.COMPLETED]),
                    'failed': len([j for j in all_jobs if j.status == JobStatus.FAILED]),
                    'cancelled': len([j for j in all_jobs if j.status == JobStatus.CANCELLED]),
                }
            }
            
            return jsonify(stats)
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    return job_bp

