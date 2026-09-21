import { Routes, Route, Navigate } from 'react-router-dom'

import Layout       from './components/Layout'
import PrivateRoute from './components/PrivateRoute'

import Login       from './pages/Login'
import Register    from './pages/Register'
import Dashboard   from './pages/Dashboard'
import Logs        from './pages/Logs'
import Alerts      from './pages/Alerts'
import Reports     from './pages/Reports'
import Settings    from './pages/Settings'
import Timeline    from './pages/Timeline'
import Suppression from './pages/Suppression'
import AuditLog    from './pages/AuditLog'

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login"    element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected layout */}
      <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index                element={<Dashboard />} />
        <Route path="logs"          element={<Logs />} />
        <Route path="alerts"        element={<Alerts />} />
        <Route path="reports"       element={<Reports />} />
        <Route path="timeline"      element={<Timeline />} />
        <Route path="suppression"   element={<PrivateRoute adminOnly><Suppression /></PrivateRoute>} />
        <Route path="audit"         element={<PrivateRoute adminOnly><AuditLog /></PrivateRoute>} />
        <Route path="settings"      element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
