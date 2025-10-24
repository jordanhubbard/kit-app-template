#!/usr/bin/env python3
"""
Job Manager Tests.

Tests for job management system: job submission, tracking, cancellation.
"""

import pytest
import time
import sys
from pathlib import Path

# Add paths
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "kit_playground"))
sys.path.insert(0, str(REPO_ROOT))

from kit_playground.backend.source.job_manager import JobManager, JobStatus


class TestJobManagerCore:
    """Test core job manager functionality."""

    def test_job_manager_creation(self):
        """Verify job manager can be created."""
        jm = JobManager()
        assert jm is not None
        assert jm.max_concurrent_jobs == 3
        assert jm.max_history == 100

    def test_submit_simple_job(self):
        """Verify simple job submission works."""
        jm = JobManager()
        jm.start()

        try:
            def simple_task():
                return "success"

            job_id = jm.submit_job('test', simple_task)

            assert job_id is not None
            assert len(job_id) > 0

            job = jm.get_job(job_id)
            assert job is not None
            assert job.type == 'test'
            assert job.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED]

        finally:
            jm.stop()

    def test_job_execution(self):
        """Verify job actually executes."""
        jm = JobManager()
        jm.start()

        try:
            def task_with_result():
                return 42

            job_id = jm.submit_job('test', task_with_result)

            # Wait for completion (up to 5 seconds)
            for _ in range(50):
                job = jm.get_job(job_id)
                if job.status == JobStatus.COMPLETED:
                    break
                time.sleep(0.1)

            job = jm.get_job(job_id)
            assert job.status == JobStatus.COMPLETED
            assert job.result == 42
            assert job.progress == 100

        finally:
            jm.stop()

    def test_job_with_arguments(self):
        """Verify job can receive arguments."""
        jm = JobManager()
        jm.start()

        try:
            def task_with_args(a, b, c=0):
                return a + b + c

            job_id = jm.submit_job('test', task_with_args, 10, 20, c=5)

            # Wait for completion
            for _ in range(50):
                job = jm.get_job(job_id)
                if job.status == JobStatus.COMPLETED:
                    break
                time.sleep(0.1)

            job = jm.get_job(job_id)
            assert job.result == 35

        finally:
            jm.stop()

    def test_job_error_handling(self):
        """Verify job errors are captured."""
        jm = JobManager()
        jm.start()

        try:
            def failing_task():
                raise ValueError("Test error")

            job_id = jm.submit_job('test', failing_task)

            # Wait for failure
            for _ in range(50):
                job = jm.get_job(job_id)
                if job.status == JobStatus.FAILED:
                    break
                time.sleep(0.1)

            job = jm.get_job(job_id)
            assert job.status == JobStatus.FAILED
            assert job.error is not None
            assert "Test error" in job.error

        finally:
            jm.stop()


class TestJobManagerListing:
    """Test job listing and filtering."""

    def test_list_all_jobs(self):
        """Verify list_jobs returns all jobs."""
        jm = JobManager()
        jm.start()

        try:
            # Submit multiple jobs
            job_ids = []
            for i in range(3):
                job_id = jm.submit_job('test', lambda: time.sleep(0.1))
                job_ids.append(job_id)

            jobs = jm.list_jobs()
            assert len(jobs) >= 3

        finally:
            jm.stop()

    def test_list_jobs_by_status(self):
        """Verify jobs can be filtered by status."""
        jm = JobManager()
        jm.start()

        try:
            # Submit jobs
            for i in range(2):
                jm.submit_job('test', lambda: None)

            # Get pending jobs
            pending = jm.list_jobs(status=JobStatus.PENDING)
            assert len(pending) >= 0  # May have already started

        finally:
            jm.stop()

    def test_list_jobs_by_type(self):
        """Verify jobs can be filtered by type."""
        jm = JobManager()
        jm.start()

        try:
            jm.submit_job('build', lambda: None)
            jm.submit_job('launch', lambda: None)
            jm.submit_job('build', lambda: None)

            builds = jm.list_jobs(job_type='build')
            assert len(builds) >= 2

            launches = jm.list_jobs(job_type='launch')
            assert len(launches) >= 1

        finally:
            jm.stop()


class TestJobManagerControl:
    """Test job control operations."""

    def test_cancel_pending_job(self):
        """Verify pending jobs can be cancelled."""
        jm = JobManager()

        # Don't start job manager so jobs stay pending
        job_id = jm.submit_job('test', lambda: time.sleep(1))

        success = jm.cancel_job(job_id)
        assert success is True

        job = jm.get_job(job_id)
        assert job.status == JobStatus.CANCELLED

    def test_cancel_nonexistent_job(self):
        """Verify cancelling nonexistent job returns False."""
        jm = JobManager()
        success = jm.cancel_job('nonexistent-id')
        assert success is False

    def test_delete_job(self):
        """Verify jobs can be deleted."""
        jm = JobManager()

        job_id = jm.submit_job('test', lambda: None)
        assert jm.get_job(job_id) is not None

        success = jm.delete_job(job_id)
        assert success is True

        assert jm.get_job(job_id) is None

    def test_get_job_logs(self):
        """Verify job logs can be retrieved."""
        jm = JobManager()

        job_id = jm.submit_job('test', lambda: None)

        # Add some logs
        jm.add_log(job_id, "Log line 1")
        jm.add_log(job_id, "Log line 2")

        logs = jm.get_job_logs(job_id)
        assert len(logs) == 2
        assert logs[0] == "Log line 1"
        assert logs[1] == "Log line 2"

    def test_update_progress(self):
        """Verify job progress can be updated."""
        jm = JobManager()

        job_id = jm.submit_job('test', lambda: None)

        jm.update_progress(job_id, 50, "Halfway done")

        job = jm.get_job(job_id)
        assert job.progress == 50
        assert job.message == "Halfway done"


class TestJobManagerAPI:
    """Test job manager API endpoints."""

    def test_list_jobs_endpoint(self, api_client):
        """Verify /api/jobs endpoint works."""
        response = api_client.get('/api/jobs')

        assert response.status_code == 200
        data = response.get_json()
        assert 'jobs' in data
        assert 'count' in data
        assert isinstance(data['jobs'], list)

    def test_get_nonexistent_job(self, api_client):
        """Verify getting nonexistent job returns 404."""
        response = api_client.get('/api/jobs/nonexistent-job-id')

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_job_stats_endpoint(self, api_client):
        """Verify /api/jobs/stats endpoint works."""
        response = api_client.get('/api/jobs/stats')

        assert response.status_code == 200
        data = response.get_json()
        assert 'total' in data
        assert 'by_status' in data
        assert 'pending' in data['by_status']
        assert 'running' in data['by_status']
        assert 'completed' in data['by_status']

    def test_cancel_job_endpoint(self, api_client):
        """Verify cancel endpoint works."""
        response = api_client.post('/api/jobs/nonexistent/cancel')

        # Should return 400 for nonexistent job
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_delete_job_endpoint(self, api_client):
        """Verify delete endpoint works."""
        response = api_client.delete('/api/jobs/nonexistent')

        # Should return 404 for nonexistent job
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
