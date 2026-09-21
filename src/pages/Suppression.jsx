/**
 * Feature 7: Alert Suppression Rules — whitelist IPs or regex patterns.
 */
import { useState, useEffect } from 'react'
import { getRules, createRule, toggleRule, deleteRule } from '../services/suppressionService'
import { MdAdd, MdDelete, MdToggleOn, MdToggleOff, MdBlock } from 'react-icons/md'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

export default function Suppression() {
  const [rules,   setRules]   = useState([])
  const [loading, setLoading] = useState(false)
  const [form,    setForm]    = useState({ rule_type: 'ip', value: '', reason: '' })

  const load = async () => {
    setLoading(true)
    try { const { data } = await getRules(); setRules(data) }
    catch { toast.error('Failed to load rules') }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await createRule(form)
      toast.success('Rule created')
      setForm({ rule_type: 'ip', value: '', reason: '' })
      load()
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed') }
  }

  const handleToggle = async (id, active) => {
    try { await toggleRule(id, !active); load() }
    catch { toast.error('Failed') }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this suppression rule?')) return
    try { await deleteRule(id); toast.success('Deleted'); load() }
    catch { toast.error('Failed') }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
        <MdBlock className="text-orange-400" /> Suppression Rules
      </h1>
      <p className="text-sm text-slate-400">
        Suppress false positives by whitelisting IPs or matching regex patterns.
        Suppressed events are still stored but will not generate alerts.
      </p>

      {/* Add form */}
      <form onSubmit={handleCreate} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <h2 className="font-semibold text-slate-200">Add Rule</h2>
        <div className="flex gap-3 flex-wrap">
          <select value={form.rule_type} onChange={e => setForm(f => ({ ...f, rule_type: e.target.value }))}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-300">
            <option value="ip">IP Address</option>
            <option value="pattern">Regex Pattern</option>
          </select>
          <input
            value={form.value} onChange={e => setForm(f => ({ ...f, value: e.target.value }))}
            placeholder={form.rule_type === 'ip' ? '192.168.1.1' : 'test.*ping'}
            required
            className="flex-1 min-w-48 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
          <input
            value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))}
            placeholder="Reason (optional)"
            className="flex-1 min-w-48 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
          />
          <button type="submit"
            className="flex items-center gap-1 px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg text-sm text-white">
            <MdAdd /> Add
          </button>
        </div>
      </form>

      {/* Rules list */}
      {loading ? <LoadingSpinner /> : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-800 text-slate-400 text-xs uppercase">
              <tr>
                <th className="px-4 py-3 text-left">Type</th>
                <th className="px-4 py-3 text-left">Value</th>
                <th className="px-4 py-3 text-left">Reason</th>
                <th className="px-4 py-3 text-left">Created</th>
                <th className="px-4 py-3 text-left">Active</th>
                <th className="px-4 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {rules.map(r => (
                <tr key={r.id} className="hover:bg-slate-800/50">
                  <td className="px-4 py-3">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                      r.rule_type === 'ip' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-purple-500/20 text-purple-400'
                    }`}>{r.rule_type.toUpperCase()}</span>
                  </td>
                  <td className="px-4 py-3 font-mono text-slate-300">{r.value}</td>
                  <td className="px-4 py-3 text-slate-500">{r.reason || '—'}</td>
                  <td className="px-4 py-3 text-slate-500">
                    {format(new Date(r.created_at), 'MM/dd HH:mm')}
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => handleToggle(r.id, r.is_active)}
                      className={r.is_active ? 'text-green-400' : 'text-slate-600'}>
                      {r.is_active ? <MdToggleOn className="text-2xl" /> : <MdToggleOff className="text-2xl" />}
                    </button>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => handleDelete(r.id)} className="text-red-500 hover:text-red-400">
                      <MdDelete />
                    </button>
                  </td>
                </tr>
              ))}
              {rules.length === 0 && (
                <tr><td colSpan={6} className="text-center py-10 text-slate-500">No suppression rules</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
