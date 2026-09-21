import { useState } from 'react'
import { useDashboard } from '../hooks/useDashboard'
import { useWebSocket } from '../hooks/useWebSocket'
import StatCard          from '../components/StatCard'
import LoadingSpinner    from '../components/LoadingSpinner'
import SeverityPie       from '../charts/SeverityPie'
import HourlyEvents      from '../charts/HourlyEvents'
import TopIPs            from '../charts/TopIPs'
import AttackCategories  from '../charts/AttackCategories'
import {
  MdRefresh, MdWarning, MdErrorOutline,
  MdInfoOutline, MdCalendarToday, MdFormatListBulleted,
} from 'react-icons/md'
import { format } from 'date-fns'

export default function Dashboard() {
  const { stats, hourly, topIPs, categories, alertSum, loading, refresh } = useDashboard()
  const [liveAlerts, setLiveAlerts] = useState([])

  useWebSocket((alert) => {
    setLiveAlerts(prev => [alert, ...prev].slice(0, 20))
  })

  if (loading) return <LoadingSpinner size="lg" />

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
        <button
          onClick={refresh}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm text-slate-300 transition-colors"
        >
          <MdRefresh /> Refresh
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <StatCard label="Total"    value={stats?.total}    color="blue"   icon={MdFormatListBulleted} />
        <StatCard label="Critical" value={stats?.CRITICAL} color="red"    icon={MdErrorOutline} />
        <StatCard label="High"     value={stats?.HIGH}     color="orange" icon={MdWarning} />
        <StatCard label="Medium"   value={stats?.MEDIUM}   color="yellow" icon={MdWarning} />
        <StatCard label="Low"      value={stats?.LOW}      color="green"  icon={MdWarning} />
        <StatCard label="Info"     value={stats?.INFO}     color="slate"  icon={MdInfoOutline} />
        <StatCard label="Today"    value={stats?.today}    color="blue"   icon={MdCalendarToday} />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Severity Distribution</h3>
          <SeverityPie data={stats} />
        </div>
        <div className="lg:col-span-2 bg-slate-900 rounded-xl border border-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Events per Hour (last 24h)</h3>
          <HourlyEvents data={hourly} />
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Top Attacker IPs</h3>
          <TopIPs data={topIPs} />
        </div>
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Attack Categories</h3>
          <AttackCategories data={categories} />
        </div>
      </div>

      {/* Live alert feed */}
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">
          Live Alert Feed <span className="ml-2 inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        </h3>
        {liveAlerts.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-4">Listening for alerts…</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {liveAlerts.map((a, i) => (
              <div key={i} className="flex items-center gap-3 text-sm bg-slate-800 rounded-lg px-3 py-2">
                <span className={`text-xs font-bold w-16 text-center rounded px-1 py-0.5 ${
                  a.severity === 'CRITICAL' ? 'bg-red-600 text-white' :
                  a.severity === 'HIGH'     ? 'bg-orange-500 text-white' :
                  'bg-yellow-500 text-black'
                }`}>{a.severity}</span>
                <span className="text-slate-400 flex-shrink-0">
                  {a.timestamp ? format(new Date(a.timestamp), 'HH:mm:ss') : '--:--:--'}
                </span>
                <span className="text-slate-200 truncate">{a.message}</span>
                {a.source_ip && (
                  <span className="text-slate-500 text-xs flex-shrink-0">{a.source_ip}</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
