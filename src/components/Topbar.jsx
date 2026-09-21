import { useAuth }  from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { MdLightMode, MdDarkMode, MdLogout, MdPerson } from 'react-icons/md'

export default function Topbar() {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()

  return (
    <header className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-6">
      <span className="text-sm text-slate-400">
        Real-time Security Monitoring
      </span>

      <div className="flex items-center gap-4">
        {/* Feature 6: Theme toggle */}
        <button
          onClick={toggle}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <MdLightMode className="text-xl" /> : <MdDarkMode className="text-xl" />}
        </button>

        {user && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <MdPerson className="text-slate-400" />
              <span className="text-sm text-slate-300">{user.username}</span>
              <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                {user.role}
              </span>
            </div>
            <button
              onClick={logout}
              className="flex items-center gap-1 text-sm text-slate-400 hover:text-red-400 transition-colors"
            >
              <MdLogout />
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
