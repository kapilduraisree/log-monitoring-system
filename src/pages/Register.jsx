import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register as apiRegister } from '../services/authService'
import { MdShield } from 'react-icons/md'
import toast from 'react-hot-toast'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm]     = useState({ username: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiRegister(form)
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-3 mb-8">
          <MdShield className="text-red-500 text-4xl" />
          <h1 className="text-xl font-bold text-slate-100">Create Account</h1>
        </div>

        <form onSubmit={submit} className="bg-slate-900 rounded-2xl border border-slate-800 p-6 space-y-4">
          {[
            { name: 'username', label: 'Username', type: 'text',     placeholder: 'johndoe' },
            { name: 'email',    label: 'Email',    type: 'email',    placeholder: 'john@example.com' },
            { name: 'password', label: 'Password', type: 'password', placeholder: '••••••••' },
          ].map(({ name, label, type, placeholder }) => (
            <div key={name}>
              <label className="block text-xs text-slate-400 mb-1">{label}</label>
              <input
                name={name} type={type} value={form[name]} onChange={handle}
                placeholder={placeholder} required
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              />
            </div>
          ))}

          <button
            type="submit" disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2 rounded-lg transition-colors"
          >
            {loading ? 'Creating…' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:text-blue-300">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
