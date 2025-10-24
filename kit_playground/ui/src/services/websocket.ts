import { io, Socket } from 'socket.io-client';
import type { JobLogEvent, JobProgressEvent, JobStatusEvent } from './types';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'http://localhost:5000';

export type WebSocketEventHandler<T> = (data: T) => void;

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(): void {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    console.log('Connecting to WebSocket:', WS_BASE_URL);
    
    this.socket = io(WS_BASE_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      console.log('Disconnecting WebSocket');
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // ===== Event Subscriptions =====

  onJobLog(handler: WebSocketEventHandler<JobLogEvent>): () => void {
    if (!this.socket) {
      console.warn('WebSocket not connected');
      return () => {};
    }

    this.socket.on('job_log', handler);
    
    // Return unsubscribe function
    return () => {
      this.socket?.off('job_log', handler);
    };
  }

  onJobProgress(handler: WebSocketEventHandler<JobProgressEvent>): () => void {
    if (!this.socket) {
      console.warn('WebSocket not connected');
      return () => {};
    }

    this.socket.on('job_progress', handler);
    
    return () => {
      this.socket?.off('job_progress', handler);
    };
  }

  onJobStatus(handler: WebSocketEventHandler<JobStatusEvent>): () => void {
    if (!this.socket) {
      console.warn('WebSocket not connected');
      return () => {};
    }

    this.socket.on('job_status', handler);
    
    return () => {
      this.socket?.off('job_status', handler);
    };
  }

  // ===== Status =====

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

// Export class for testing
export { WebSocketService };

