import { useState, useEffect, useCallback } from 'react'
import { getStatus, getTargets } from '../services/monitorService'

export function useMonitor() {
  const [status,  setStatus]  = useState(null)
  const [targets, setTargets] = useState([])
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const [s, t] = await Promise.all([getStatus(), getTargets()])
      setStatus(s.data)
      setTargets(t.data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { refresh() }, [refresh])

  return { status, targets, loading, refresh }
}
