/**
 * Alerts page — Feature 3: Acknowledge/unacknowledge with notes.
 */
import { useState } from 'react'
import { useAlerts }      from '../hooks/useAlerts'
import { acknowledge, unacknowledge } from '../services/alertService'
import SeverityBadge  from '../components/SeverityBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import Pagination     from '../components/Pagination'
import StatCard       from '../components/StatCard'
import { MdExpandMore, MdExpandLess, MdCheck, MdUndo } from 'react-icons/md'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Alerts() {
  const { alerts, summary, total, page, setPage, filters, setFilters, loading, refresh } = useAlerts()
  const [expanded, setExpanded] = useState(null)
  const [ackNote,  setAckNote]  = useState('')
  const [acking,   setAcking]   = useState(null)

  const handleAck = async (id) => {
    setAcking(id)
    try {
      await acknowledge(id, ackNote)
      toast.success('Alert acknowledged')
      setAckNote('')
      setExpanded(null)
      refresh()
    } catch { toast.error('Failed') }
    finally { setAcking(null) }
  }

  const handleUnack = async (id) => {
    try {
      await unacknowledge(id)
      toast.success('Unacknowledged')
      refresh()
    } catch { toast.error('Failed') }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-100">Alerts</h1>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-3 md:grid-cols-7 gap-3">
          <StatCard label="Total"       value={summary.total}          color="blue" />
          <StatCard label="Critical"    value={summary.CRITICAL}       color="red" />
          <StatCard label="High"        value={summary.HIGH}           color="orange" />
          <StatCard label="Medium"      value={summary.MEDIUM}         color="yellow" />
          <StatCard label="Low"         value={summary.LOW}            color="green" />
          <StatCard label="Info"        value={summary.INFO}           color="slate" />
          <StatCard label="Unacked"     value={summary.unacknowledged} color="red" />
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <select
          value={filters.severity || ''}
          onChange={e => { setFilters(f => ({ ...f, severity: e.target.value })); setPage(1) }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300"
        >
          {['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].map(s =>
            <option key={s} value={s}>{s || 'All Severities'}</option>
          )}
        </select>
        <select
          value={filters.acknowledged ?? ''}
          onChange={e => {
            const v = e.target.value === '' ? undefined : e.target.value === 'true'
            setFilters(f => ({ ...f, acknowledged: v })); setPage(1)
          }}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300"
        >
          <option value="">All Status</option>
          <option value="false">Unacknowledged</option>
          <option value="true">Acknowledged</option>
        </select>
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
                <th className="px-4 py-3 text-left">Message</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {alerts.map(alert => (
                <>
                  <tr key={alert.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3 text-slate-400 whitespace-nowrap">
                      {format(new Date(alert.created_at), 'MM/dd HH:mm:ss')}
                    </td>
                    <td className="px-4 py-3"><SeverityBadge severity={alert.severity} /></td>
                    <td className="px-4 py-3 text-slate-400 text-xs">{alert.alert_type}</td>
                    <td className="px-4 py-3 text-yellow-400 font-mono text-xs">{alert.source_ip || '—'}</td>
                    <td className="px-4 py-3 text-slate-300 max-w-xs truncate">{alert.message}</td>
                    <td className="px-4 py-3">
                      {alert.acknowledged ? (
                        <span className="text-xs text-green-400 flex items-center gap-1">
                          <MdCheck /> Acked
                        </span>
                      ) : (
                        <span className="text-xs text-slate-500">Pending</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button onClick={() => setExpanded(expanded === alert.id ? null : alert.id)}
                          className="text-slate-500 hover:text-slate-200">
                          {expanded === alert.id ? <MdExpandLess /> : <MdExpandMore />}
                        </button>
                        {!alert.acknowledged ? (
                          <button onClick={() => setExpanded(alert.id)}
                            className="text-green-500 hover:text-green-400" title="Acknowledge">
                            <MdCheck />
                          </button>
                        ) : (
                          <button onClick={() => handleUnack(alert.id)}
                            className="text-slate-500 hover:text-orange-400" title="Unacknowledge">
                            <MdUndo />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>

                  {expanded === alert.id && (
                    <tr key={`exp-${alert.id}`} className="bg-slate-800/30">
                      <td colSpan={7} className="px-6 py-4">
                        <div className="space-y-3 text-xs">
                          <p className="text-slate-300">{alert.message}</p>
                          {alert.ack_note && (
                            <p className="text-green-400">Note: {alert.ack_note}</p>
                          )}
                          {!alert.acknowledged && (
                            <div className="flex gap-2 mt-2">
                              <input
                                value={ackNote}
                                onChange={e => setAckNote(e.target.value)}
                                placeholder="Optional note…"
                                className="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-1.5 text-slate-100 text-xs focus:outline-none"
                              />
                              <button
                                onClick={() => handleAck(alert.id)}
                                disabled={acking === alert.id}
                                className="px-4 py-1.5 bg-green-600 hover:bg-green-700 rounded text-white text-xs disabled:opacity-50"
                              >
                                {acking === alert.id ? 'Saving…' : 'Acknowledge'}
                              </button>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
              {alerts.length === 0 && (
                <tr><td colSpan={7} className="text-center py-12 text-slate-500">No alerts found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} total={total} pageSize={50} onPage={setPage} />
    </div>
  )
}
