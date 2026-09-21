/**
 * Login page — handles standard login + Feature 10 TOTP second step.
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { login as apiLogin } from '../services/authService'
import { MdShield } from 'react-icons/md'
import toast from 'react-hot-toast'

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()

  const [form,        setForm]        = useState({ username: '', password: '', totp_code: '' })
  const [needsTotp,   setNeedsTotp]   = useState(false)
  const [pendingToken,setPendingToken] = useState('')
  const [loading,     setLoading]     = useState(false)

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = needsTotp
        ? { username: form.username, password: form.password, totp_code: form.totp_code }
        : { username: form.username, password: form.password }

      const { data } = await apiLogin(payload)

      if (data.requires_totp) {
        setPendingToken(data.access_token)
        setNeedsTotp(true)
        toast('Enter your 2FA code', { icon: '🔐' })
        setLoading(false)
        return
      }

      login(data.access_token)
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <MdShield className="text-red-500 text-4xl" />
          <div>
            <h1 className="text-xl font-bold text-slate-100">Log Security Monitor</h1>
            <p className="text-xs text-slate-500">v2.0 — 10 Enhanced Features</p>
          </div>
        </div>

        <form onSubmit={submit} className="bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-4">
          <h2 className="text-lg font-semibold text-slate-100">
            {needsTotp ? 'Two-Factor Authentication' : 'Sign In'}
          </h2>

          {!needsTotp ? (
            <>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Username</label>
                <input
                  name="username" value={form.username} onChange={handle}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  placeholder="admin" required autoFocus
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Password</label>
                <input
                  type="password" name="password" value={form.password} onChange={handle}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  placeholder="••••••••" required
                />
              </div>
            </>
          ) : (
            <div>
              <p className="text-sm text-slate-400 mb-3">
                Open your authenticator app and enter the 6-digit code.
              </p>
              <label className="block text-xs text-slate-400 mb-1">Authenticator Code</label>
              <input
                name="totp_code" value={form.totp_code} onChange={handle}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500 tracking-widest text-center text-lg"
                placeholder="000000" maxLength={6} required autoFocus
              />
            </div>
          )}

          <button
            type="submit" disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors"
          >
            {loading ? 'Signing in…' : needsTotp ? 'Verify' : 'Sign In'}
          </button>

          {needsTotp && (
            <button
              type="button" onClick={() => { setNeedsTotp(false); setPendingToken('') }}
              className="w-full text-sm text-slate-500 hover:text-slate-300 transition-colors"
            >
              ← Back to login
            </button>
          )}
        </form>

        <p className="text-center text-sm text-slate-500 mt-4">
          No account?{' '}
          <Link to="/register" className="text-blue-400 hover:text-blue-300">Register</Link>
        </p>
      </div>
    </div>
  )
}
