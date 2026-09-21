export default function StatCard({ label, value, color = 'blue', icon: Icon }) {
  const colors = {
    red:    'border-red-500/30 bg-red-500/10 text-red-400',
    orange: 'border-orange-500/30 bg-orange-500/10 text-orange-400',
    yellow: 'border-yellow-500/30 bg-yellow-500/10 text-yellow-400',
    green:  'border-green-500/30 bg-green-500/10 text-green-400',
    blue:   'border-blue-500/30 bg-blue-500/10 text-blue-400',
    slate:  'border-slate-500/30 bg-slate-500/10 text-slate-400',
  }
  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium uppercase tracking-wide opacity-70">{label}</span>
        {Icon && <Icon className="text-xl opacity-70" />}
      </div>
      <p className="text-3xl font-bold">{value ?? '—'}</p>
    </div>
  )
}
