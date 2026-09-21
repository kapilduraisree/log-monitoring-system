import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = {
  CRITICAL: '#ef4444',
  HIGH:     '#f97316',
  MEDIUM:   '#eab308',
  LOW:      '#22c55e',
  INFO:     '#64748b',
}

export default function SeverityPie({ data }) {
  if (!data) return null
  const items = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
    .map(k => ({ name: k, value: data[k] || 0 }))
    .filter(d => d.value > 0)

  if (items.length === 0) return (
    <p className="text-center text-slate-500 py-8">No data</p>
  )

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={items} dataKey="value" nameKey="name" cx="50%" cy="50%"
          innerRadius={55} outerRadius={85} paddingAngle={3}>
          {items.map(entry => (
            <Cell key={entry.name} fill={COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
          labelStyle={{ color: '#f8fafc' }}
          itemStyle={{ color: '#94a3b8' }}
        />
        <Legend formatter={v => <span style={{ color: '#94a3b8', fontSize: 12 }}>{v}</span>} />
      </PieChart>
    </ResponsiveContainer>
  )
}
