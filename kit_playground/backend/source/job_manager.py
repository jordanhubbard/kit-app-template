#!/usr/bin/env python3
"""
Job Management System for Kit Playground.

Handles asynchronous execution of long-running operations like builds and launches.
"""

import threading
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """Represents a job in the system."""
    id: str
    type: str  # 'build', 'launch', 'template_create', etc.
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0  # 0-100
    message: str = ""
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for API responses."""
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
            'message': self.message,
            'error': self.error,
            'metadata': self.metadata,
            'result': self.result,
            'log_count': len(self.logs)
        }


class JobManager:
    """
    Manages asynchronous job execution.
    
    Features:
    - Job submission and tracking
    - Status updates
    - Progress reporting
    - Log collection
    - Job cancellation
    """
    
    def __init__(self, max_concurrent_jobs: int = 3, max_history: int = 100):
        """
        Initialize job manager.
        
        Args:
            max_concurrent_jobs: Maximum number of jobs running simultaneously
            max_history: Maximum number of completed jobs to keep in history
        """
        self.jobs: Dict[str, Job] = {}
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_history = max_history
        self.lock = threading.Lock()
        self.executor_thread: Optional[threading.Thread] = None
        self.running = False
        
    def start(self):
        """Start the job executor thread."""
        if not self.running:
            self.running = True
            self.executor_thread = threading.Thread(target=self._executor_loop, daemon=True)
            self.executor_thread.start()
            logger.info("Job manager started")
    
    def stop(self):
        """Stop the job executor thread."""
        self.running = False
        if self.executor_thread:
            self.executor_thread.join(timeout=5)
        logger.info("Job manager stopped")
    
    def submit_job(
        self,
        job_type: str,
        func: Callable,
        *args,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Submit a new job for execution.
        
        Args:
            job_type: Type of job (e.g., 'build', 'launch')
            func: Function to execute
            *args: Positional arguments for function
            metadata: Optional metadata dictionary
            **kwargs: Keyword arguments for function
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        with self.lock:
            job = Job(
                id=job_id,
                type=job_type,
                status=JobStatus.PENDING,
                created_at=datetime.now(),
                metadata=metadata or {}
            )
            
            # Store function and args for execution
            job.metadata['_func'] = func
            job.metadata['_args'] = args
            job.metadata['_kwargs'] = kwargs
            
            self.jobs[job_id] = job
            logger.info(f"Job {job_id} submitted: {job_type}")
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        with self.lock:
            return self.jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Job]:
        """
        List jobs with optional filtering.
        
        Args:
            status: Filter by status
            job_type: Filter by type
            limit: Maximum number of jobs to return
            
        Returns:
            List of jobs (newest first)
        """
        with self.lock:
            jobs = list(self.jobs.values())
        
        # Filter
        if status:
            jobs = [j for j in jobs if j.status == status]
        if job_type:
            jobs = [j for j in jobs if j.type == job_type]
        
        # Sort by created_at (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        return jobs[:limit]
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if job was cancelled, False otherwise
        """
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
            
            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now()
                job.message = "Job cancelled by user"
                logger.info(f"Job {job_id} cancelled")
                return True
            
            return False
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from history.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if job was deleted, False otherwise
        """
        with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                logger.info(f"Job {job_id} deleted")
                return True
            return False
    
    def get_job_logs(self, job_id: str, limit: int = 1000) -> List[str]:
        """
        Get job logs.
        
        Args:
            job_id: Job ID
            limit: Maximum number of log lines to return
            
        Returns:
            List of log lines (newest first)
        """
        job = self.get_job(job_id)
        if not job:
            return []
        
        return job.logs[-limit:]
    
    def update_progress(self, job_id: str, progress: int, message: str = ""):
        """Update job progress."""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.progress = max(0, min(100, progress))
                if message:
                    job.message = message
    
    def add_log(self, job_id: str, log_line: str):
        """Add a log line to job."""
        with self.lock:
            job = self.jobs.get(job_id)
            if job:
                job.logs.append(log_line)
    
    def _executor_loop(self):
        """Main executor loop (runs in separate thread)."""
        while self.running:
            try:
                # Find pending jobs
                pending_jobs = self.list_jobs(status=JobStatus.PENDING)
                running_jobs = self.list_jobs(status=JobStatus.RUNNING)
                
                # Execute jobs if we have capacity
                if len(running_jobs) < self.max_concurrent_jobs and pending_jobs:
                    job = pending_jobs[0]
                    self._execute_job(job)
                
                # Cleanup old jobs
                self._cleanup_history()
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                logger.error(f"Error in executor loop: {e}", exc_info=True)
    
    def _execute_job(self, job: Job):
        """Execute a single job in a new thread."""
        def run():
            try:
                with self.lock:
                    job.status = JobStatus.RUNNING
                    job.started_at = datetime.now()
                    logger.info(f"Job {job.id} started")
                
                # Get function and args
                func = job.metadata.get('_func')
                args = job.metadata.get('_args', ())
                kwargs = job.metadata.get('_kwargs', {})
                
                # Execute function
                result = func(*args, **kwargs)
                
                with self.lock:
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.now()
                    job.progress = 100
                    job.message = "Job completed successfully"
                    job.result = result
                    logger.info(f"Job {job.id} completed")
                    
            except Exception as e:
                with self.lock:
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now()
                    job.error = str(e)
                    job.message = f"Job failed: {e}"
                    logger.error(f"Job {job.id} failed: {e}", exc_info=True)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def _cleanup_history(self):
        """Clean up old completed jobs."""
        with self.lock:
            completed = [
                j for j in self.jobs.values()
                if j.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
            ]
            
            if len(completed) > self.max_history:
                # Sort by completion time and remove oldest
                completed.sort(key=lambda j: j.completed_at or j.created_at)
                to_remove = completed[:-self.max_history]
                
                for job in to_remove:
                    del self.jobs[job.id]
                    logger.debug(f"Cleaned up old job {job.id}")


# Global job manager instance
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get the global job manager instance."""
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
        _job_manager.start()
    return _job_manager

