const MAP = {
  CRITICAL: 'bg-red-600 text-white',
  HIGH:     'bg-orange-500 text-white',
  MEDIUM:   'bg-yellow-500 text-black',
  LOW:      'bg-green-600 text-white',
  INFO:     'bg-slate-600 text-slate-100',
}

export default function SeverityBadge({ severity }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${MAP[severity] ?? MAP.INFO}`}>
      {severity}
    </span>
  )
}
