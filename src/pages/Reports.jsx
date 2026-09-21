/**
 * Reports page — Feature 5: trigger scheduled email send button.
 */
import { useState, useEffect } from 'react'
import { getReport, exportCsv, exportJson, exportPdf, sendReportEmail } from '../services/reportService'
import LoadingSpinner from '../components/LoadingSpinner'
import { MdDownload, MdEmail, MdBarChart } from 'react-icons/md'
import toast from 'react-hot-toast'

const PERIODS = ['daily', 'weekly', 'monthly']

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

export default function Reports() {
  const [period,  setPeriod]  = useState('daily')
  const [report,  setReport]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    setLoading(true)
    getReport(period)
      .then(r => setReport(r.data))
      .catch(() => toast.error('Failed to load report'))
      .finally(() => setLoading(false))
  }, [period])

  const handleExport = async (type) => {
    try {
      let res, filename
      if (type === 'csv')  { res = await exportCsv(period);  filename = `report_${period}.csv` }
      if (type === 'json') { res = await exportJson(period); filename = `report_${period}.json` }
      if (type === 'pdf')  { res = await exportPdf(period);  filename = `report_${period}.pdf` }
      downloadBlob(res.data, filename)
    } catch { toast.error('Export failed') }
  }

  const handleEmail = async () => {
    setSending(true)
    try {
      await sendReportEmail(period)
      toast.success('Report emailed!')
    } catch { toast.error('Email failed — check EMAIL_HOST config') }
    finally { setSending(false) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-100">Reports</h1>
        <div className="flex gap-2">
          {PERIODS.map(p => (
            <button key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                period === p ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Export buttons */}
      <div className="flex gap-3 flex-wrap">
        {['csv', 'json', 'pdf'].map(t => (
          <button key={t} onClick={() => handleExport(t)}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-sm text-slate-300 transition-colors">
            <MdDownload /> Export {t.toUpperCase()}
          </button>
        ))}
        {/* Feature 5 */}
        <button onClick={handleEmail} disabled={sending}
          className="flex items-center gap-2 px-4 py-2 bg-blue-700 hover:bg-blue-600 disabled:opacity-50 rounded-lg text-sm text-white transition-colors">
          <MdEmail /> {sending ? 'Sending…' : 'Email Report'}
        </button>
      </div>

      {/* Report data */}
      {loading ? <LoadingSpinner /> : report && (
        <div className="space-y-4">
          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Logs',   value: report.total_logs,   color: 'text-blue-400' },
              { label: 'Total Alerts', value: report.total_alerts, color: 'text-orange-400' },
              { label: 'Critical',     value: report.severity?.CRITICAL, color: 'text-red-400' },
              { label: 'High',         value: report.severity?.HIGH,     color: 'text-orange-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <p className="text-xs text-slate-500 mb-1">{label}</p>
                <p className={`text-3xl font-bold ${color}`}>{value ?? 0}</p>
              </div>
            ))}
          </div>

          {/* Top event types + IPs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                <MdBarChart /> Top Event Types
              </h3>
              <div className="space-y-2">
                {report.top_event_types?.map(item => (
                  <div key={item.type} className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">{item.type}</span>
                    <span className="text-slate-200 font-mono">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Top Source IPs</h3>
              <div className="space-y-2">
                {report.top_source_ips?.map(item => (
                  <div key={item.ip} className="flex items-center justify-between text-sm">
                    <span className="text-yellow-400 font-mono">{item.ip}</span>
                    <span className="text-slate-200 font-mono">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
