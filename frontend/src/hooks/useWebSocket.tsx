import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage } from '../types';
import apiService from '../services/api';

interface UseWebSocketOptions {
  userId: number;
  onMessage?: (message: WebSocketMessage) => void;
  onAdaptation?: (adaptation: any) => void;
  onError?: (error: Event) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export const useWebSocket = ({
  userId,
  onMessage,
  onAdaptation,
  onError,
  reconnectAttempts = 5,
  reconnectInterval = 3000,
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    
    try {
      wsRef.current = apiService.createWebSocketConnection(userId);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectCountRef.current = 0;
        console.log('WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (onMessage) {
            onMessage(message);
          }

          // Handle specific message types
          if (message.type === 'adaptation_response' && onAdaptation) {
            onAdaptation(message.data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        console.log('WebSocket disconnected');

        // Attempt to reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect... (${reconnectCountRef.current}/${reconnectAttempts})`);
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        setConnectionStatus('error');
        console.error('WebSocket error:', error);
        if (onError) {
          onError(error);
        }
      };
    } catch (error) {
      setConnectionStatus('error');
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [userId, onMessage, onAdaptation, onError, reconnectAttempts, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const sendMessage = useCallback((message: Partial<WebSocketMessage>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const fullMessage: WebSocketMessage = {
        timestamp: new Date().toISOString(),
        ...message,
      } as WebSocketMessage;
      
      wsRef.current.send(JSON.stringify(fullMessage));
      return true;
    }
    return false;
  }, []);

  const sendPerformanceUpdate = useCallback((sessionId: string, performanceData: any) => {
    return sendMessage({
      type: 'performance_update',
      session_id: sessionId,
      data: performanceData,
    });
  }, [sendMessage]);

  const sendHeartbeat = useCallback(() => {
    return sendMessage({
      type: 'heartbeat',
    });
  }, [sendMessage]);

  useEffect(() => {
    connect();

    // Set up heartbeat
    const heartbeatInterval = setInterval(() => {
      if (isConnected) {
        sendHeartbeat();
      }
    }, 30000); // Send heartbeat every 30 seconds

    return () => {
      clearInterval(heartbeatInterval);
      disconnect();
    };
  }, [connect, disconnect, isConnected, sendHeartbeat]);

  return {
    isConnected,
    connectionStatus,
    sendMessage,
    sendPerformanceUpdate,
    sendHeartbeat,
    connect,
    disconnect,
  };
};