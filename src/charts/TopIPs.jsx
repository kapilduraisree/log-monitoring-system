import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

export default function TopIPs({ data = [] }) {
  if (!data.length) return <p className="text-center text-slate-500 py-8">No data</p>

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
        <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
        <YAxis type="category" dataKey="ip" width={110}
          tick={{ fill: '#fbbf24', fontSize: 11, fontFamily: 'monospace' }} />
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
          labelStyle={{ color: '#fbbf24' }}
          itemStyle={{ color: '#94a3b8' }}
        />
        <Bar dataKey="count" name="Events" radius={[0, 4, 4, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={`hsl(${200 + i * 15}, 70%, ${60 - i * 3}%)`} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
