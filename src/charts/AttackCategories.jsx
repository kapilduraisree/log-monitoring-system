import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

const CAT_COLORS = {
  sql_injection:      '#ef4444',
  brute_force:        '#dc2626',
  malware:            '#b91c1c',
  ssh_auth_failure:   '#f97316',
  xss:                '#eab308',
  suspicious_ip:      '#f59e0b',
  unauthorized_access:'#84cc16',
  port_scan:          '#22c55e',
  failed_login:       '#3b82f6',
}

export default function AttackCategories({ data = [] }) {
  if (!data.length) return <p className="text-center text-slate-500 py-8">No data</p>

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="type" tick={{ fill: '#64748b', fontSize: 10 }}
          angle={-35} textAnchor="end" interval={0} />
        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
          labelStyle={{ color: '#f8fafc' }}
          itemStyle={{ color: '#94a3b8' }}
        />
        <Bar dataKey="count" name="Count" radius={[4, 4, 0, 0]}>
          {data.map((entry, i) => (
            <Cell key={i} fill={CAT_COLORS[entry.type] || '#3b82f6'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
