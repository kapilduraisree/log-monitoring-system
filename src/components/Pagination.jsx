export default function Pagination({ page, total, pageSize, onPage }) {
  const pages = Math.ceil(total / pageSize)
  if (pages <= 1) return null
  return (
    <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
      <span>{total} total</span>
      <div className="flex gap-2">
        <button
          disabled={page <= 1}
          onClick={() => onPage(page - 1)}
          className="px-3 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700"
        >
          ← Prev
        </button>
        <span className="px-3 py-1">{page} / {pages}</span>
        <button
          disabled={page >= pages}
          onClick={() => onPage(page + 1)}
          className="px-3 py-1 rounded bg-slate-800 disabled:opacity-40 hover:bg-slate-700"
        >
          Next →
        </button>
      </div>
    </div>
  )
}
