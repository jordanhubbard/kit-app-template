/**
 * DependencyPreparer - Modal component for preparing (pre-fetching) Kit extensions.
 *
 * Features:
 * - Shows download size and time estimate
 * - Real-time progress tracking via SSE
 * - Skip option with warning
 * - Success/error states
 */

import React, { useState, useEffect } from 'react';
import { Card, Button, ProgressBar, LoadingSpinner } from '../common';
import { useDependencies, PreparationProgress } from '../../hooks/useDependencies';

interface DependencyPreparerProps {
  isOpen: boolean;
  onClose: () => void;
  config?: string;
  autoStart?: boolean;
}

export const DependencyPreparer: React.FC<DependencyPreparerProps> = ({
  isOpen,
  onClose,
  config = 'release',
  autoStart = false,
}) => {
  const { getEstimate, startPreparation, estimateCache } = useDependencies();

  const [progress, setProgress] = useState<number>(0);
  const [status, setStatus] = useState<string>('');
  const [extensionCount, setExtensionCount] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showSkipWarning, setShowSkipWarning] = useState<boolean>(false);
  const [startTime, setStartTime] = useState<number>(0);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [estimate, setEstimate] = useState(estimateCache);
  const [runInBackground, setRunInBackground] = useState<boolean>(false);
  const [isMinimized, setIsMinimized] = useState<boolean>(false);

  // Load estimate on mount
  useEffect(() => {
    if (isOpen && !estimate) {
      getEstimate(50).then(setEstimate);
    }
  }, [isOpen, estimate, getEstimate]);

  // Auto-start if requested
  useEffect(() => {
    if (isOpen && autoStart && !isRunning && !isComplete) {
      handleStart();
    }
  }, [isOpen, autoStart]);

  // Update elapsed time
  useEffect(() => {
    if (isRunning && startTime > 0) {
      const timer = setInterval(() => {
        setElapsedTime(Date.now() - startTime);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isRunning, startTime]);

  const handleStart = () => {
    setIsRunning(true);
    setIsComplete(false);
    setError(null);
    setProgress(0);
    setStatus('Starting...');
    setExtensionCount(0);
    setStartTime(Date.now());
    setElapsedTime(0);

    startPreparation(
      config,
      (event: PreparationProgress) => {
        setStatus(event.message);

        if (event.progress !== undefined) {
          setProgress(event.progress);
        }

        if (event.count !== undefined) {
          setExtensionCount(event.count);
        }

        if (event.type === 'complete') {
          setIsComplete(true);
          setIsRunning(false);
          setProgress(100);
          setStatus(`✅ Complete! Prepared ${event.count || extensionCount} extensions in ${formatTime(elapsedTime)}`);
        }
      },
      () => {
        // Complete callback
        setIsComplete(true);
        setIsRunning(false);
      },
      (errorMsg: string) => {
        // Error callback
        setError(errorMsg);
        setIsRunning(false);
      }
    );
  };

  const handleSkip = () => {
    if (isRunning) {
      setShowSkipWarning(true);
    } else {
      onClose();
    }
  };

  const handleConfirmSkip = () => {
    setIsRunning(false);
    onClose();
  };

  const formatTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getRemainingTime = (): string => {
    if (!estimate || progress === 0) return 'Calculating...';

    const estimatedTotal = estimate.estimated_seconds * 1000;
    const elapsed = elapsedTime;
    const remaining = Math.max(0, estimatedTotal * (100 - progress) / 100);

    return formatTime(remaining);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="max-w-2xl w-full">
        {/* Header */}
        <div className="border-b border-gray-700 pb-4 mb-4">
          <h2 className="text-2xl font-bold text-white mb-2">
            {isComplete ? '✅ Dependencies Ready!' : '📦 Prepare Dependencies'}
          </h2>
          <p className="text-gray-400 text-sm">
            {isComplete
              ? 'Extensions are now cached for fast launching'
              : 'Download and cache Kit extensions for faster first launch'}
          </p>
        </div>

        {/* Skip Warning */}
        {showSkipWarning && (
          <div className="mb-4 p-4 bg-yellow-900 bg-opacity-30 border border-yellow-600 rounded">
            <h3 className="text-yellow-400 font-bold mb-2">⚠️ Skip Preparation?</h3>
            <p className="text-gray-300 text-sm mb-3">
              Skipping will cancel the download. Extensions will be downloaded during application launch instead, which may take 5-10 minutes and cause the app to appear frozen.
            </p>
            <div className="flex space-x-2">
              <Button
                variant="danger"
                onClick={handleConfirmSkip}
              >
                Skip Anyway
              </Button>
              <Button
                variant="secondary"
                onClick={() => setShowSkipWarning(false)}
              >
                Continue Preparing
              </Button>
            </div>
          </div>
        )}

        {/* Estimate Info */}
        {!isRunning && !isComplete && estimate && (
          <div className="mb-6 p-4 bg-blue-900 bg-opacity-30 border border-blue-600 rounded">
            <h3 className="text-blue-400 font-bold mb-2">📊 Download Estimate</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Size:</span>
                <span className="text-white ml-2 font-mono">{estimate.estimated_size}</span>
              </div>
              <div>
                <span className="text-gray-400">Time:</span>
                <span className="text-white ml-2 font-mono">{estimate.estimated_time}</span>
              </div>
              <div>
                <span className="text-gray-400">Extensions:</span>
                <span className="text-white ml-2 font-mono">~{estimate.extension_count}</span>
              </div>
              <div>
                <span className="text-gray-400">Bandwidth:</span>
                <span className="text-white ml-2 font-mono">{estimate.bandwidth_mbps} Mbps</span>
              </div>
            </div>
          </div>
        )}

        {/* Progress */}
        {(isRunning || isComplete) && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">
                {extensionCount > 0 && `${extensionCount} extensions`}
              </span>
              <span className="text-sm text-gray-400 font-mono">
                {isRunning && `${formatTime(elapsedTime)} / ~${getRemainingTime()}`}
                {isComplete && `Completed in ${formatTime(elapsedTime)}`}
              </span>
            </div>

            <ProgressBar value={progress} max={100} className="mb-2" />

            <div className="flex items-center space-x-2">
              {isRunning && <LoadingSpinner size="small" />}
              <p className="text-sm text-gray-300">{status}</p>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-900 bg-opacity-30 border border-red-600 rounded">
            <h3 className="text-red-400 font-bold mb-2">❌ Error</h3>
            <p className="text-gray-300 text-sm">{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-3">
          {!isRunning && !isComplete && (
            <>
              <Button
                variant="secondary"
                onClick={handleSkip}
              >
                Skip
              </Button>
              <Button
                variant="primary"
                onClick={handleStart}
              >
                Start Preparation
              </Button>
            </>
          )}

          {isRunning && (
            <Button
              variant="secondary"
              onClick={handleSkip}
            >
              Cancel
            </Button>
          )}

          {isComplete && (
            <Button
              variant="primary"
              onClick={onClose}
            >
              Done
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
};
