import { NavLink } from 'react-router-dom'
import {
  MdDashboard, MdList, MdWarning, MdAssessment,
  MdSettings, MdTimeline, MdBlock, MdHistory, MdShield,
} from 'react-icons/md'

const links = [
  { to: '/',           label: 'Dashboard',  icon: MdDashboard },
  { to: '/logs',       label: 'Logs',       icon: MdList },
  { to: '/alerts',     label: 'Alerts',     icon: MdWarning },
  { to: '/timeline',   label: 'Timeline',   icon: MdTimeline },
  { to: '/reports',    label: 'Reports',    icon: MdAssessment },
  { to: '/suppression',label: 'Suppression',icon: MdBlock },
  { to: '/audit',      label: 'Audit Log',  icon: MdHistory },
  { to: '/settings',   label: 'Settings',   icon: MdSettings },
]

export default function Sidebar() {
  return (
    <aside className="w-56 bg-slate-900 border-r border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-800">
        <MdShield className="text-red-500 text-2xl" />
        <span className="font-bold text-sm text-slate-100 leading-tight">
          Log Security<br />Monitor
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
               ${isActive
                 ? 'bg-blue-600 text-white'
                 : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'}`
            }
          >
            <Icon className="text-lg flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
