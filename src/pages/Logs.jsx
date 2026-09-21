import { useState, useCallback } from 'react'
import { useLogs }       from '../hooks/useLogs'
import { useAuth }       from '../context/AuthContext'
import { deleteLog }     from '../services/logService'
import SeverityBadge     from '../components/SeverityBadge'
import LoadingSpinner    from '../components/LoadingSpinner'
import Pagination        from '../components/Pagination'
import { MdSearch, MdDelete, MdExpandMore, MdExpandLess, MdLanguage } from 'react-icons/md'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

const SEVERITIES  = ['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
const EVENT_TYPES = ['', 'sql_injection', 'brute_force', 'malware', 'ssh_auth_failure',
                     'xss', 'suspicious_ip', 'unauthorized_access', 'port_scan', 'failed_login']

export default function Logs() {
  const { user } = useAuth()
  const { logs, total, page, setPage, filters, setFilters, loading, refresh } = useLogs()
  const [expanded, setExpanded] = useState(null)
  const [search, setSearch]     = useState('')

  const applySearch = useCallback(() => {
    setFilters(f => ({ ...f, search }))
    setPage(1)
  }, [search, setFilters, setPage])

  const handleDelete = async (id) => {
    if (!confirm('Delete this log entry?')) return
    try {
      await deleteLog(id)
      toast.success('Deleted')
      refresh()
    } catch { toast.error('Delete failed') }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-100">Log Viewer</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="flex gap-2 flex-1 min-w-64">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && applySearch()}
            placeholder="Search logs…"
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
          <button onClick={applySearch} className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white">
            <MdSearch />
          </button>
        </div>

        <select
          value={filters.severity || ''}
          onChange={e => { setFilters(f => ({ ...f, severity: e.target.value })); setPage(1) }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300"
        >
          {SEVERITIES.map(s => <option key={s} value={s}>{s || 'All Severities'}</option>)}
        </select>

        <select
          value={filters.event_type || ''}
          onChange={e => { setFilters(f => ({ ...f, event_type: e.target.value })); setPage(1) }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300"
        >
          {EVENT_TYPES.map(t => <option key={t} value={t}>{t || 'All Types'}</option>)}
        </select>

        <button
          onClick={() => { setFilters(f => ({ ...f, sort_desc: !f.sort_desc })); setPage(1) }}
          className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700"
        >
          {filters.sort_desc === false ? '↑ Oldest' : '↓ Newest'}
        </button>
      </div>

      {/* Table */}
      {loading ? <LoadingSpinner /> : (
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3 text-left">Time</th>
                <th className="px-4 py-3 text-left">Severity</th>
                <th className="px-4 py-3 text-left">Type</th>
                <th className="px-4 py-3 text-left">IP</th>
                <th className="px-4 py-3 text-left">Location</th>
                <th className="px-4 py-3 text-left">Message</th>
                <th className="px-4 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {logs.map(log => (
                <>
                  <tr key={log.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                      {format(new Date(log.timestamp), 'MM/dd HH:mm:ss')}
                    </td>
                    <td className="px-4 py-3"><SeverityBadge severity={log.severity} /></td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{log.event_type || '—'}</td>
                    <td className="px-4 py-3 text-yellow-400 font-mono text-xs">{log.source_ip || '—'}</td>
                    <td className="px-4 py-3 text-slate-400 text-xs">
                      {/* Feature 2: show geo */}
                      {log.geo_country ? (
                        <span className="flex items-center gap-1">
                          <MdLanguage className="text-blue-400" />
                          {log.geo_city ? `${log.geo_city}, ` : ''}{log.geo_country}
                        </span>
                      ) : '—'}
                    </td>
                    <td className="px-4 py-3 text-slate-300 max-w-xs truncate">{log.message}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setExpanded(expanded === log.id ? null : log.id)}
                          className="text-slate-500 hover:text-slate-200"
                        >
                          {expanded === log.id ? <MdExpandLess /> : <MdExpandMore />}
                        </button>
                        {user?.role === 'admin' && (
                          <button onClick={() => handleDelete(log.id)} className="text-red-500 hover:text-red-400">
                            <MdDelete />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                  {expanded === log.id && (
                    <tr key={`exp-${log.id}`} className="bg-slate-800/30">
                      <td colSpan={7} className="px-6 py-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                          <div>
                            <p className="text-slate-500 mb-1">Full Message</p>
                            <p className="text-slate-300 break-all">{log.message}</p>
                          </div>
                          <div>
                            <p className="text-slate-500 mb-1">Raw Line</p>
                            <pre className="text-slate-400 break-all whitespace-pre-wrap font-mono">{log.raw_line}</pre>
                          </div>
                          <div>
                            <p className="text-slate-500 mb-1">Source File</p>
                            <p className="text-slate-300">{log.source_file || '—'}</p>
                          </div>
                          {log.geo_lat && (
                            <div>
                              <p className="text-slate-500 mb-1">Coordinates</p>
                              <p className="text-slate-300">{log.geo_lat}, {log.geo_lon}</p>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={7} className="text-center py-12 text-slate-500">No logs found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} total={total} pageSize={50} onPage={setPage} />
    </div>
  )
}
