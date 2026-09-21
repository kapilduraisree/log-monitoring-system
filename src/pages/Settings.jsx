/**
 * Settings page:
 * - Monitor control (F8: multi-target)
 * - Log file upload
 * - Feature 10: TOTP 2FA setup/disable
 * - Feature 1: Email config info
 * - Feature 5: Scheduled report info
 */
import { useState } from 'react'
import { useMonitor } from '../hooks/useMonitor'
import { useAuth }    from '../context/AuthContext'
import {
  startMonitor, stopMonitor, uploadLog, addTarget, removeTarget,
} from '../services/monitorService'
import { setupTotp, verifyTotp, disableTotp } from '../services/authService'
import { MdPlay, MdStop, MdUpload, MdDelete, MdAdd, MdQrCode, MdShield } from 'react-icons/md'
import toast from 'react-hot-toast'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Settings() {
  const { user, fetchMe } = useAuth()
  const { status, targets, loading, refresh } = useMonitor()

  // Monitor
  const [watchPath,  setWatchPath]  = useState('')
  const [targetLabel,setTargetLabel]= useState('')
  const [newPath,    setNewPath]    = useState('')

  // Upload
  const [file,       setFile]       = useState(null)
  const [uploading,  setUploading]  = useState(false)

  // TOTP
  const [totpSetup,  setTotpSetup]  = useState(null)   // { secret, qr_code }
  const [totpCode,   setTotpCode]   = useState('')
  const [disableCode,setDisableCode]= useState('')
  const [totpLoading,setTotpLoading]= useState(false)

  const handleStart = async () => {
    try { await startMonitor({ watch_path: watchPath }); toast.success('Monitoring started'); refresh() }
    catch { toast.error('Failed to start') }
  }
  const handleStop = async () => {
    try { await stopMonitor(); toast.success('All monitors stopped'); refresh() }
    catch { toast.error('Failed to stop') }
  }
  const handleAddTarget = async () => {
    if (!newPath.trim()) return
    try { await addTarget({ path: newPath, label: targetLabel }); toast.success('Target added'); setNewPath(''); setTargetLabel(''); refresh() }
    catch (e) { toast.error(e.response?.data?.detail || 'Failed') }
  }
  const handleRemoveTarget = async (id) => {
    try { await removeTarget(id); toast.success('Target removed'); refresh() }
    catch { toast.error('Failed') }
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    try {
      const { data } = await uploadLog(file)
      toast.success(`Processed ${data.lines_processed} lines`)
      setFile(null)
    } catch (e) { toast.error(e.response?.data?.detail || 'Upload failed') }
    finally { setUploading(false) }
  }

  // TOTP handlers
  const handleTotpSetup = async () => {
    setTotpLoading(true)
    try { const { data } = await setupTotp(); setTotpSetup(data) }
    catch { toast.error('Setup failed') }
    finally { setTotpLoading(false) }
  }
  const handleTotpVerify = async () => {
    try { await verifyTotp(totpCode); toast.success('2FA enabled!'); setTotpSetup(null); setTotpCode(''); fetchMe() }
    catch { toast.error('Invalid code') }
  }
  const handleTotpDisable = async () => {
    try { await disableTotp(disableCode); toast.success('2FA disabled'); setDisableCode(''); fetchMe() }
    catch { toast.error('Invalid code') }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-bold text-slate-100">Settings</h1>

      {/* ── Monitor ─────────────────────────────────────────────────────── */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="font-semibold text-slate-200">File Monitoring</h2>
        <div className="flex items-center gap-2 text-sm">
          <span className={`w-2 h-2 rounded-full ${status?.active ? 'bg-green-500' : 'bg-slate-600'}`} />
          <span className="text-slate-400">{status?.active ? `Active (${status.count} target${status.count !== 1 ? 's' : ''})` : 'Inactive'}</span>
        </div>
        {/* Quick start */}
        <div className="flex gap-2">
          <input value={watchPath} onChange={e => setWatchPath(e.target.value)}
            placeholder="Path to watch (e.g. C:\logs)"
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500" />
          <button onClick={handleStart} className="flex items-center gap-1 px-3 py-2 bg-green-700 hover:bg-green-600 rounded-lg text-sm text-white"><MdPlay /> Start</button>
          <button onClick={handleStop}  className="flex items-center gap-1 px-3 py-2 bg-red-700 hover:bg-red-600 rounded-lg text-sm text-white"><MdStop /> Stop All</button>
        </div>
        {/* Feature 8: Multi-target list */}
        <div className="space-y-2">
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Watch Targets</p>
          {targets.map(t => (
            <div key={t.id} className="flex items-center justify-between bg-slate-800 rounded-lg px-3 py-2 text-sm">
              <span className="text-slate-300">{t.label ? `${t.label}: ` : ''}<span className="font-mono text-slate-400">{t.path}</span></span>
              <button onClick={() => handleRemoveTarget(t.id)} className="text-red-500 hover:text-red-400"><MdDelete /></button>
            </div>
          ))}
          <div className="flex gap-2">
            <input value={newPath} onChange={e => setNewPath(e.target.value)} placeholder="Add new path…"
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500" />
            <input value={targetLabel} onChange={e => setTargetLabel(e.target.value)} placeholder="Label (optional)"
              className="w-32 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500" />
            <button onClick={handleAddTarget} className="flex items-center gap-1 px-3 py-1.5 bg-blue-700 hover:bg-blue-600 rounded-lg text-sm text-white"><MdAdd /></button>
          </div>
        </div>
      </section>

      {/* ── Upload ──────────────────────────────────────────────────────── */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
        <h2 className="font-semibold text-slate-200">Upload Log File</h2>
        <div className="border-2 border-dashed border-slate-700 rounded-xl p-6 text-center"
          onDrop={e => { e.preventDefault(); setFile(e.dataTransfer.files[0]) }}
          onDragOver={e => e.preventDefault()}>
          {file ? (
            <p className="text-sm text-slate-300">{file.name}</p>
          ) : (
            <p className="text-sm text-slate-500">Drag & drop or click to select</p>
          )}
          <input type="file" className="hidden" id="file-upload" onChange={e => setFile(e.target.files[0])} />
          <label htmlFor="file-upload" className="mt-3 inline-block px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-300 cursor-pointer">
            Browse
          </label>
        </div>
        <button onClick={handleUpload} disabled={!file || uploading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm text-white">
          <MdUpload /> {uploading ? 'Processing…' : 'Upload & Process'}
        </button>
      </section>

      {/* ── Feature 10: TOTP 2FA ─────────────────────────────────────────── */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="font-semibold text-slate-200 flex items-center gap-2">
          <MdShield className="text-blue-400" /> Two-Factor Authentication (2FA)
        </h2>
        <p className="text-sm text-slate-400">
          Status: <span className={user?.totp_enabled ? 'text-green-400' : 'text-slate-500'}>
            {user?.totp_enabled ? '✓ Enabled' : 'Disabled'}
          </span>
        </p>

        {!user?.totp_enabled ? (
          <div className="space-y-3">
            {!totpSetup ? (
              <button onClick={handleTotpSetup} disabled={totpLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-700 hover:bg-blue-600 disabled:opacity-50 rounded-lg text-sm text-white">
                <MdQrCode /> {totpLoading ? 'Generating…' : 'Setup 2FA'}
              </button>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-slate-400">Scan this QR code with your authenticator app:</p>
                <img src={`data:image/png;base64,${totpSetup.qr_code}`} alt="TOTP QR" className="w-40 h-40 rounded" />
                <p className="text-xs text-slate-500 font-mono">Secret: {totpSetup.secret}</p>
                <div className="flex gap-2">
                  <input value={totpCode} onChange={e => setTotpCode(e.target.value)}
                    placeholder="Enter 6-digit code" maxLength={6}
                    className="w-40 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 tracking-widest text-center focus:outline-none focus:border-blue-500" />
                  <button onClick={handleTotpVerify}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm text-white">
                    Confirm
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex gap-2">
            <input value={disableCode} onChange={e => setDisableCode(e.target.value)}
              placeholder="Enter code to disable" maxLength={6}
              className="w-44 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 tracking-widest text-center focus:outline-none focus:border-red-500" />
            <button onClick={handleTotpDisable}
              className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded-lg text-sm text-white">
              Disable 2FA
            </button>
          </div>
        )}
      </section>

      {/* ── Email / Schedule info ────────────────────────────────────────── */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="font-semibold text-slate-200 mb-2">Email & Scheduled Reports</h2>
        <p className="text-sm text-slate-400">
          Configure <code className="text-blue-400">EMAIL_HOST</code>, <code className="text-blue-400">EMAIL_USER</code>,
          and <code className="text-blue-400">EMAIL_TO</code> in your <code className="text-slate-300">.env</code> file to
          enable alert emails (Feature 1). Set <code className="text-blue-400">REPORT_SCHEDULE_ENABLED=true</code> and
          <code className="text-blue-400"> REPORT_SCHEDULE_HOUR</code> for daily auto-reports (Feature 5).
        </p>
      </section>
    </div>
  )
}
