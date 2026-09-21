import { useEffect, useRef, useCallback } from 'react'
import toast from 'react-hot-toast'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export function useWebSocket(onAlert) {
  const ws      = useRef(null)
  const retry   = useRef(null)
  const stopped = useRef(false)

  const connect = useCallback(() => {
    if (stopped.current) return
    const socket = new WebSocket(WS_URL)
    ws.current = socket

    socket.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data)
        if (data.severity === 'CRITICAL') {
          toast.error(`🚨 CRITICAL: ${data.event_type} — ${data.source_ip || 'N/A'}`, {
            duration: 6000,
          })
        }
        onAlert?.(data)
      } catch {}
    }

    socket.onclose = () => {
      if (!stopped.current) {
        retry.current = setTimeout(connect, 3000)
      }
    }

    socket.onerror = () => socket.close()
  }, [onAlert])

  useEffect(() => {
    connect()
    return () => {
      stopped.current = true
      clearTimeout(retry.current)
      ws.current?.close()
    }
  }, [connect])
}
