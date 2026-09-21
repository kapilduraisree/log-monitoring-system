import { useState, useEffect, useCallback } from 'react'
import { getAlerts, getSummary } from '../services/alertService'

export function useAlerts(initialFilters = {}) {
  const [alerts,  setAlerts]  = useState([])
  const [summary, setSummary] = useState(null)
  const [total,   setTotal]   = useState(0)
  const [page,    setPage]    = useState(1)
  const [filters, setFilters] = useState(initialFilters)
  const [loading, setLoading] = useState(false)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const [a, s] = await Promise.all([
        getAlerts({ page, page_size: 50, ...filters }),
        getSummary(),
      ])
      setAlerts(a.data.items)
      setTotal(a.data.total)
      setSummary(s.data)
    } finally {
      setLoading(false)
    }
  }, [page, filters])

  useEffect(() => { fetch() }, [fetch])

  return { alerts, summary, total, page, setPage, filters, setFilters, loading, refresh: fetch }
}
