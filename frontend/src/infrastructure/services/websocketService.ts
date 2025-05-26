import { performanceMonitoringService } from './performanceMonitoringService';

export interface WebSocketMessage {
  type: 'execution_update' | 'resource_update' | 'error' | 'status';
  payload: any;
  timestamp: number;
}

export interface ExecutionUpdate {
  nodeId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  startTime?: number;
  endTime?: number;
  error?: string;
}

export interface ResourceUpdate {
  cpu: number;
  memory: number;
  network: {
    bytesIn: number;
    bytesOut: number;
  };
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000;
  private messageHandlers: ((message: WebSocketMessage) => void)[] = [];
  private isConnected = false;

  constructor() {
    this.connect();
  }

  private connect() {
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/execution`;
    
    try {
      this.socket = new WebSocket(wsUrl);
      
      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        performanceMonitoringService.trackEvent('websocket_connected');
      };

      this.socket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.messageHandlers.forEach(handler => handler(message));
          performanceMonitoringService.trackEvent('websocket_message_received');
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          performanceMonitoringService.trackError('websocket_message_parse_error', error);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.handleReconnect();
        performanceMonitoringService.trackEvent('websocket_disconnected');
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        performanceMonitoringService.trackError('websocket_error', error);
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      performanceMonitoringService.trackError('websocket_connection_error', error);
      this.handleReconnect();
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, this.reconnectTimeout * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
      performanceMonitoringService.trackError('websocket_max_reconnect_attempts');
    }
  }

  public subscribe(handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }

  public send(message: WebSocketMessage) {
    if (this.socket && this.isConnected) {
      try {
        this.socket.send(JSON.stringify(message));
        performanceMonitoringService.trackEvent('websocket_message_sent');
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        performanceMonitoringService.trackError('websocket_message_send_error', error);
      }
    } else {
      console.warn('WebSocket is not connected');
      performanceMonitoringService.trackError('websocket_not_connected');
    }
  }

  public disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
      performanceMonitoringService.trackEvent('websocket_disconnected');
    }
  }
}

export const websocketService = new WebSocketService(); 