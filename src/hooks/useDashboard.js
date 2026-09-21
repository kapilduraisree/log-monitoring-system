import { useState, useEffect, useCallback } from 'react'
import { getStats, getHourly, getTopIPs, getAttackCats } from '../services/logService'
import { getSummary } from '../services/alertService'

export function useDashboard() {
  const [stats,      setStats]      = useState(null)
  const [hourly,     setHourly]     = useState([])
  const [topIPs,     setTopIPs]     = useState([])
  const [categories, setCategories] = useState([])
  const [alertSum,   setAlertSum]   = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)

  const refresh = useCallback(async () => {
    try {
      const [s, h, t, c, a] = await Promise.all([
        getStats(), getHourly(), getTopIPs(10), getAttackCats(), getSummary(),
      ])
      setStats(s.data)
      setHourly(h.data)
      setTopIPs(t.data)
      setCategories(c.data)
      setAlertSum(a.data)
    } catch (e) {
      setError(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 30_000)
    return () => clearInterval(id)
  }, [refresh])

  return { stats, hourly, topIPs, categories, alertSum, loading, error, refresh }
}
