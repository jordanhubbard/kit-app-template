import { useEffect, useState } from 'react';
import { websocketService } from '../services/websocket';

interface UseWebSocketOptions {
  onJobStatus?: (data: any) => void;
  onJobProgress?: (data: any) => void;
  onLogMessage?: (data: any) => void;
  onStreamingReady?: (data: any) => void;
  onJobLog?: (data: any) => void;
}

interface UseWebSocketResult {
  connected: boolean;
}

/**
 * useWebSocket
 * 
 * Custom hook for WebSocket connections and real-time updates.
 * Manages connection lifecycle and event subscriptions.
 */
export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketResult => {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();
    
    // Update connected state
    setConnected(websocketService.isConnected());

    // Set up event listeners and get unsubscribe functions
    const unsubscribeFns: Array<() => void> = [];

    if (options.onJobStatus) {
      const unsub = websocketService.onJobStatus(options.onJobStatus);
      unsubscribeFns.push(unsub);
    }
    if (options.onJobProgress) {
      const unsub = websocketService.onJobProgress(options.onJobProgress);
      unsubscribeFns.push(unsub);
    }
    if (options.onLogMessage) {
      const unsub = websocketService.onLogMessage(options.onLogMessage);
      unsubscribeFns.push(unsub);
    }
    if (options.onStreamingReady) {
      const unsub = websocketService.onStreamingReady(options.onStreamingReady);
      unsubscribeFns.push(unsub);
    }
    if (options.onJobLog) {
      const unsub = websocketService.onJobLog(options.onJobLog);
      unsubscribeFns.push(unsub);
    }

    // Cleanup on unmount
    return () => {
      // Call all unsubscribe functions
      unsubscribeFns.forEach(unsub => unsub());
      
      // Note: We don't disconnect here as other components may be using the socket
      // websocketService.disconnect();
    };
  }, [options.onJobStatus, options.onJobProgress, options.onLogMessage, options.onStreamingReady, options.onJobLog]);

  return {
    connected,
  };
};

