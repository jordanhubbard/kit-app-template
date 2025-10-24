import React, { useEffect, useState } from 'react';
import { Card, Button, ProgressBar, LoadingSpinner } from '../components/common';
import { apiService } from '../services/api';
import { websocketService } from '../services/websocket';
import type { Job, JobStatus } from '../services/types';

const statusColors: Record<JobStatus, string> = {
  pending: 'bg-gray-500',
  running: 'bg-blue-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
  cancelled: 'bg-yellow-500',
};

const statusIcons: Record<JobStatus, string> = {
  pending: '⏳',
  running: '▶️',
  completed: '✓',
  failed: '✗',
  cancelled: '⊘',
};

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [filter, setFilter] = useState<JobStatus | 'all'>('all');

  useEffect(() => {
    loadJobs();
    
    // Connect to WebSocket for real-time updates
    websocketService.connect();

    // Subscribe to job events
    const unsubLog = websocketService.onJobLog((data) => {
      console.log('[Job Log]', data);
      updateJobLogs(data.job_id, data.message);
    });

    const unsubProgress = websocketService.onJobProgress((data) => {
      console.log('[Job Progress]', data);
      updateJobProgress(data.job_id, data.progress);
    });

    const unsubStatus = websocketService.onJobStatus((data) => {
      console.log('[Job Status]', data);
      updateJobStatus(data.job_id, data.status);
    });

    return () => {
      unsubLog();
      unsubProgress();
      unsubStatus();
    };
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.listJobs();
      setJobs(response.jobs);
    } catch (err) {
      console.error('Failed to load jobs:', err);
      setError('Failed to load jobs. Please ensure the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const updateJobLogs = (jobId: string, message: string) => {
    setJobs(prev => prev.map(job => {
      if (job.id === jobId) {
        return {
          ...job,
          logs: [...(job.logs || []), message],
        };
      }
      return job;
    }));
    
    if (selectedJob?.id === jobId) {
      setSelectedJob(prev => prev ? {
        ...prev,
        logs: [...(prev.logs || []), message],
      } : null);
    }
  };

  const updateJobProgress = (jobId: string, progress: number) => {
    setJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, progress } : job
    ));
    
    if (selectedJob?.id === jobId) {
      setSelectedJob(prev => prev ? { ...prev, progress } : null);
    }
  };

  const updateJobStatus = (jobId: string, status: JobStatus) => {
    setJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, status } : job
    ));
    
    if (selectedJob?.id === jobId) {
      setSelectedJob(prev => prev ? { ...prev, status } : null);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await apiService.cancelJob(jobId);
      updateJobStatus(jobId, 'cancelled');
    } catch (err) {
      console.error('Failed to cancel job:', err);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    try {
      await apiService.deleteJob(jobId);
      setJobs(prev => prev.filter(job => job.id !== jobId));
      if (selectedJob?.id === jobId) {
        setSelectedJob(null);
      }
    } catch (err) {
      console.error('Failed to delete job:', err);
    }
  };

  const filteredJobs = filter === 'all' 
    ? jobs 
    : jobs.filter(job => job.status === filter);

  const activeJobs = jobs.filter(job => 
    job.status === 'pending' || job.status === 'running'
  );

  const completedJobs = jobs.filter(job => 
    job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled'
  );

  const formatTime = (dateString?: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'just now';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <LoadingSpinner size="lg" className="mx-auto text-nvidia-green" />
          <p className="text-gray-400">Loading jobs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="max-w-2xl mx-auto">
        <div className="text-center space-y-4">
          <div className="text-red-500 text-5xl">⚠️</div>
          <h2 className="text-2xl font-bold text-white">Error Loading Jobs</h2>
          <p className="text-gray-400">{error}</p>
          <Button onClick={loadJobs}>Retry</Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Jobs</h1>
          <p className="text-gray-400 mt-1">Monitor build and launch operations</p>
        </div>
        <Button onClick={loadJobs} variant="secondary" size="sm">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(['all', 'running', 'completed', 'failed'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`
              px-4 py-2 rounded-lg font-medium capitalize transition-all duration-200
              ${filter === status
                ? 'bg-nvidia-green text-white'
                : 'bg-dark-card text-gray-300 hover:bg-dark-hover border border-gray-700'
              }
            `}
          >
            {status}
            {status !== 'all' && (
              <span className="ml-2 text-sm opacity-75">
                ({jobs.filter(j => j.status === status).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Active Jobs */}
      {activeJobs.length > 0 && (filter === 'all' || filter === 'running' || filter === 'pending') && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">
            Active Jobs ({activeJobs.length})
          </h2>
          {activeJobs.map((job) => (
            <Card key={job.id} className="hover:border-nvidia-green transition-colors">
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${statusColors[job.status]}`}>
                      {statusIcons[job.status]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-white truncate">
                        {job.type === 'template_create' ? 'Creating Template' : 
                         job.type === 'build' ? 'Building' : 'Launching'}: {job.project_name || 'Unknown'}
                      </h3>
                      <p className="text-sm text-gray-400 capitalize">
                        Status: {job.status} • Started {formatTime(job.started_at || job.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setSelectedJob(job)}
                    >
                      View Logs
                    </Button>
                    {(job.status === 'pending' || job.status === 'running') && (
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleCancelJob(job.id)}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>
                <ProgressBar progress={job.progress} showLabel />
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Completed Jobs */}
      {completedJobs.length > 0 && (filter === 'all' || filter === 'completed' || filter === 'failed' || filter === 'cancelled') && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-white">
              Completed Jobs ({completedJobs.length})
            </h2>
            {completedJobs.length > 0 && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  completedJobs.forEach(job => handleDeleteJob(job.id));
                }}
              >
                Clear All
              </Button>
            )}
          </div>
          <div className="space-y-2">
            {completedJobs.map((job) => (
              <Card key={job.id} padding="sm" className="hover:bg-dark-hover transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm ${statusColors[job.status]}`}>
                      {statusIcons[job.status]}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-white truncate">
                        {job.type} • {job.project_name || 'Unknown'}
                      </p>
                      <p className="text-sm text-gray-400">
                        {formatTime(job.completed_at || job.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setSelectedJob(job)}
                    >
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteJob(job.id)}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredJobs.length === 0 && (
        <Card className="text-center py-12">
          <div className="text-gray-400 text-5xl mb-4">📋</div>
          <p className="text-gray-400">No jobs found</p>
          <p className="text-sm text-gray-500 mt-2">Jobs will appear here when you create projects or run builds</p>
        </Card>
      )}

      {/* Job Detail Modal */}
      {selectedJob && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl w-full max-h-[80vh] flex flex-col">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-white">Job Details</h2>
                <p className="text-gray-400 text-sm mt-1">ID: {selectedJob.id}</p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-400">Status</p>
                <p className="text-white font-semibold capitalize">{selectedJob.status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Type</p>
                <p className="text-white font-semibold capitalize">{selectedJob.type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Progress</p>
                <p className="text-white font-semibold">{selectedJob.progress}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Created</p>
                <p className="text-white font-semibold">{formatTime(selectedJob.created_at)}</p>
              </div>
            </div>

            {selectedJob.progress < 100 && selectedJob.status === 'running' && (
              <div className="mb-4">
                <ProgressBar progress={selectedJob.progress} />
              </div>
            )}

            <div className="flex-1 overflow-hidden flex flex-col">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold text-white">Logs</h3>
                <label className="flex items-center gap-2 text-sm text-gray-400">
                  <input type="checkbox" defaultChecked className="rounded" />
                  Auto-scroll
                </label>
              </div>
              <div className="flex-1 bg-dark-bg rounded-lg p-4 overflow-auto custom-scrollbar font-mono text-sm">
                {selectedJob.logs && selectedJob.logs.length > 0 ? (
                  selectedJob.logs.map((log, idx) => (
                    <div key={idx} className="text-gray-300">
                      {log}
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 italic">No logs available</p>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-4 mt-4">
              {(selectedJob.status === 'pending' || selectedJob.status === 'running') && (
                <Button
                  variant="danger"
                  onClick={() => {
                    handleCancelJob(selectedJob.id);
                    setSelectedJob(null);
                  }}
                >
                  Cancel Job
                </Button>
              )}
              <Button variant="secondary" onClick={() => setSelectedJob(null)}>
                Close
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default JobsPage;

