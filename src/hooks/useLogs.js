import { useState, useEffect, useCallback } from 'react'
import { getLogs } from '../services/logService'

export function useLogs(initialFilters = {}) {
  const [logs,    setLogs]    = useState([])
  const [total,   setTotal]   = useState(0)
  const [page,    setPage]    = useState(1)
  const [filters, setFilters] = useState(initialFilters)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await getLogs({ page, page_size: 50, ...filters })
      setLogs(data.items)
      setTotal(data.total)
    } catch (e) {
      setError(e)
    } finally {
      setLoading(false)
    }
  }, [page, filters])

  useEffect(() => { fetch() }, [fetch])

  return { logs, total, page, setPage, filters, setFilters, loading, error, refresh: fetch }
}
