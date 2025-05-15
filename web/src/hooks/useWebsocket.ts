import { useState, useEffect, useCallback, useRef } from 'react'

interface WebSocketOptions {
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket(url: string | null, options: WebSocketOptions = {}) {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [events, setEvents] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const {
    reconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options

  const connect = useCallback(() => {
    if (!url) return

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        setIsConnected(true)
        setReconnectAttempts(0)
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('WebSocket message received:', data)
          setEvents(prev => [...prev, data])
        } catch (error) {
          console.error('Error parsing WebSocket message:', error, event.data)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        setIsConnected(false)
        setSocket(null)

        if (reconnect && reconnectAttempts < maxReconnectAttempts) {
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
          }
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1)
            connect()
          }, reconnectInterval)
        }
      }

      setSocket(ws)
    } catch (error) {
      console.error('Error creating WebSocket:', error)
    }
  }, [url, reconnect, reconnectInterval, maxReconnectAttempts, reconnectAttempts])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socket) {
        socket.close()
      }
    }
  }, [url])

  const sendMessage = useCallback((message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log('Sending WebSocket message:', message)
      socket.send(JSON.stringify(message))
    } else {
      console.error('WebSocket not connected or not ready')
    }
  }, [socket])

  const disconnect = useCallback(() => {
    if (socket) {
      socket.close()
    }
  }, [socket])

  return {
    sendMessage,
    events,
    isConnected,
    disconnect
  }
}