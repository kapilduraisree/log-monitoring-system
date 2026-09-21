/**
 * Feature 9: Threat Timeline — visual per-IP attack timeline.
 */
import { useState, useEffect } from 'react'
import { getTimeline } from '../services/logService'
import SeverityBadge  from '../components/SeverityBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import { MdSearch, MdTimeline, MdPublic } from 'react-icons/md'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

const SEV_COLOR = {
  CRITICAL: 'bg-red-500',
  HIGH:     'bg-orange-500',
  MEDIUM:   'bg-yellow-500',
  LOW:      'bg-green-500',
  INFO:     'bg-slate-500',
}

export default function Timeline() {
  const [events,  setEvents]  = useState([])
  const [ip,      setIp]      = useState('')
  const [search,  setSearch]  = useState('')
  const [loading, setLoading] = useState(false)

  const load = async (filterIp = '') => {
    setLoading(true)
    try {
      const { data } = await getTimeline(filterIp)
      setEvents(data)
    } catch { toast.error('Failed to load timeline') }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const handleSearch = () => { setIp(search); load(search) }

  // Group by IP for display
  const grouped = events.reduce((acc, ev) => {
    const key = ev.source_ip || 'Unknown'
    if (!acc[key]) acc[key] = []
    acc[key].push(ev)
    return acc
  }, {})

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <MdTimeline className="text-blue-400" /> Threat Timeline
        </h1>
        <div className="flex gap-2">
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Filter by IP…"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
          <button onClick={handleSearch}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm text-white">
            <MdSearch />
          </button>
          {ip && (
            <button onClick={() => { setSearch(''); setIp(''); load('') }}
              className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-300">
              Clear
            </button>
          )}
        </div>
      </div>

      {loading ? <LoadingSpinner /> : (
        <div className="space-y-8">
          {Object.entries(grouped).map(([srcIp, ipEvents]) => (
            <div key={srcIp} className="bg-slate-900 rounded-xl border border-slate-800 p-5">
              {/* IP header */}
              <div className="flex items-center gap-3 mb-4">
                <span className="text-yellow-400 font-mono font-bold">{srcIp}</span>
                {ipEvents[0]?.geo_country && (
                  <span className="flex items-center gap-1 text-xs text-slate-400">
                    <MdPublic className="text-blue-400" />
                    {ipEvents[0].geo_city ? `${ipEvents[0].geo_city}, ` : ''}
                    {ipEvents[0].geo_country}
                  </span>
                )}
                <span className="text-xs text-slate-500">{ipEvents.length} events</span>
              </div>

              {/* Timeline track */}
              <div className="relative pl-6">
                <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-slate-700" />
                <div className="space-y-3">
                  {ipEvents.map((ev, idx) => (
                    <div key={ev.id} className="relative flex gap-4 items-start">
                      {/* Dot */}
                      <div className={`absolute -left-4 mt-1.5 w-3 h-3 rounded-full border-2 border-slate-900 ${SEV_COLOR[ev.severity]}`} />
                      {/* Content */}
                      <div className="flex-1 bg-slate-800 rounded-lg px-3 py-2">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-slate-500 font-mono">
                            {format(new Date(ev.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                          </span>
                          <SeverityBadge severity={ev.severity} />
                          {ev.event_type && (
                            <span className="text-xs text-slate-500">{ev.event_type}</span>
                          )}
                        </div>
                        <p className="text-sm text-slate-300">{ev.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}

          {Object.keys(grouped).length === 0 && (
            <div className="text-center py-20 text-slate-500">
              <MdTimeline className="text-5xl mx-auto mb-3 opacity-30" />
              No security events found{ip ? ` for IP ${ip}` : ''}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
