/**
 * Feature 4: User Activity Audit Log — admin only.
 */
import { useState, useEffect, useCallback } from 'react'
import { getAuditLogs } from '../services/auditService'
import LoadingSpinner from '../components/LoadingSpinner'
import Pagination     from '../components/Pagination'
import { MdManageSearch } from 'react-icons/md'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

const ACTION_COLORS = {
  LOGIN:          'text-green-400',
  LOGIN_FAILED:   'text-red-400',
  LOGOUT:         'text-slate-400',
  REGISTER:       'text-blue-400',
  DELETE_LOG:     'text-red-400',
  ACK_ALERT:      'text-green-400',
  UNACK_ALERT:    'text-yellow-400',
  MONITOR_START:  'text-green-400',
  MONITOR_STOP:   'text-orange-400',
  UPLOAD_LOG:     'text-blue-400',
  CREATE_SUPPRESSION: 'text-orange-400',
  DELETE_SUPPRESSION: 'text-red-400',
}

export default function AuditLog() {
  const [logs,    setLogs]    = useState([])
  const [total,   setTotal]   = useState(0)
  const [page,    setPage]    = useState(1)
  const [loading, setLoading] = useState(false)
  const [username,setUsername]= useState('')
  const [action,  setAction]  = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await getAuditLogs({ page, page_size: 50, username: username || undefined, action: action || undefined })
      setLogs(data.items)
      setTotal(data.total)
    } catch { toast.error('Failed to load audit logs') }
    finally { setLoading(false) }
  }, [page, username, action])

  useEffect(() => { load() }, [load])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
        <MdManageSearch className="text-blue-400" /> Audit Log
      </h1>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <div className="flex gap-2">
          <input value={username} onChange={e => { setUsername(e.target.value); setPage(1) }}
            placeholder="Filter by username…"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500" />
          <input value={action} onChange={e => { setAction(e.target.value); setPage(1) }}
            placeholder="Filter by action…"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500" />
        </div>
      </div>

      {loading ? <LoadingSpinner /> : (
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3 text-left">Time</th>
                <th className="px-4 py-3 text-left">User</th>
                <th className="px-4 py-3 text-left">Action</th>
                <th className="px-4 py-3 text-left">Resource</th>
                <th className="px-4 py-3 text-left">Detail</th>
                <th className="px-4 py-3 text-left">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {logs.map(log => (
                <tr key={log.id} className="hover:bg-slate-800/50">
                  <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                    {format(new Date(log.created_at), 'MM/dd HH:mm:ss')}
                  </td>
                  <td className="px-4 py-3 text-slate-300">{log.username || '—'}</td>
                  <td className={`px-4 py-3 font-semibold text-xs ${ACTION_COLORS[log.action] || 'text-slate-400'}`}>
                    {log.action}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs font-mono">{log.resource || '—'}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs max-w-xs truncate">{log.detail || '—'}</td>
                  <td className="px-4 py-3 text-slate-500 font-mono text-xs">{log.ip_address || '—'}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={6} className="text-center py-12 text-slate-500">No audit entries</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      <Pagination page={page} total={total} pageSize={50} onPage={setPage} />
    </div>
  )
}
