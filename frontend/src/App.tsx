import { useEffect, useState } from 'react'
import { ApiError, getMe, getReportHtml, getReportMarkdown, getReportSummary, getReports, getSetupRequired, getSystemInfo, getSystemStatus, login, logout, setupAdmin } from './api'
import { AsnCheckForm } from './components/AsnCheckForm'
import { Layout } from './components/Layout'
import { LoginView } from './components/LoginView'
import { PrefixCheckForm } from './components/PrefixCheckForm'
import { PreflightCheckForm } from './components/PreflightCheckForm'
import { SetupView } from './components/SetupView'
import { StatusBadge } from './components/StatusBadge'
import type { ReportListItem, SystemInfo, SystemStatus } from './types'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'preflight' | 'reports' | 'system' | 'about'
type AuthMode = 'loading' | 'setup' | 'login' | 'app' | 'error'

export default function App() {
  const [authMode, setAuthMode] = useState<AuthMode>('loading')
  const [authError, setAuthError] = useState('')
  const [active, setActive] = useState<NavKey>('dashboard')
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [system, setSystem] = useState<SystemInfo | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [systemStatusError, setSystemStatusError] = useState('')
  const [currentUser, setCurrentUser] = useState<{ username: string; role: string } | null>(null)

  const loadAppData = () => {
    getReports().then(setReports).catch(() => setReports([]))
    getSystemInfo().then(setSystem).catch(() => null)
    getSystemStatus().then((payload) => { setSystemStatus(payload); setSystemStatusError('') }).catch((err: unknown) => {
      if (err instanceof ApiError && err.status === 401) { setAuthMode('login'); setAuthError('Your session has expired. Please log in again.'); return }
      if (err instanceof ApiError && err.status === 403) { setSystemStatusError('You do not have permission to perform this action.'); return }
      setSystemStatusError('System status could not be loaded.')
    })
  }

  const bootstrapAuth = async () => {
    setAuthMode('loading'); setAuthError('')
    try {
      const setup = await getSetupRequired()
      if (setup.setup_required) { setAuthMode('setup'); setCurrentUser(null); return }
      try {
        const me = await getMe()
        setCurrentUser({ username: me.user.username, role: me.user.role })
        setAuthMode('app'); loadAppData()
      } catch (err: unknown) {
        if (err instanceof ApiError && err.status === 401) { setAuthMode('login'); setCurrentUser(null); return }
        setAuthMode('error'); setAuthError('Authentication state could not be loaded.')
      }
    } catch { setAuthMode('error'); setAuthError('Setup state could not be loaded.') }
  }

  useEffect(() => { bootstrapAuth() }, [])
  const handleLogout = async () => { await logout(); setCurrentUser(null); setAuthMode('login') }

  const onSetupSubmit = async (payload: { username: string; email?: string; password: string; password_confirm: string }) => {
    setAuthError('')
    try { const res = await setupAdmin(payload); if (res.user) { await bootstrapAuth(); return }; setAuthMode('login') } catch (err: unknown) { setAuthError(err instanceof Error ? err.message : 'Setup failed') }
  }
  const onLoginSubmit = async (username: string, password: string) => {
    setAuthError('')
    try { await login({ username, password }); await bootstrapAuth() } catch (err: unknown) { setAuthError(err instanceof Error ? err.message : 'Login failed') }
  }

  if (authMode === 'loading') return <div className='p-8 text-center text-slate-600'>Loading authentication state...</div>
  if (authMode === 'setup') return <SetupView onSubmit={onSetupSubmit} error={authError} />
  if (authMode === 'login') return <LoginView onSubmit={onLoginSubmit} error={authError} />
  if (authMode === 'error') return <div className='p-8 text-center text-rose-700'>{authError}</div>

  const systemLine = system ? `${system.name} ${system.version} · mode=${system.demo_mode ? 'DEMO' : 'LIVE'} · read_only=${String(system.read_only)}` : 'RouteForge v0.6.4-beta · read-only preflight checks'
  const title = { dashboard: 'Dashboard', asn: 'ASN Check', prefix: 'Prefix Check', preflight: 'Preflight Check', reports: 'Reports', system: 'System Status', about: 'About RouteForge' }[active]
  const proxyStatus = systemStatusError ? 'ERROR' : 'OK'
  const migrationStatus = systemStatus?.database?.migration_status || 'unknown'
  const migrationsBlocked = migrationStatus === 'behind' || migrationStatus === 'error'

  return <Layout active={active} onNav={setActive} systemLine={systemLine} title={title} demoMode={Boolean(system?.demo_mode)} currentUser={currentUser} onLogout={handleLogout}>
    {active === 'dashboard' && <section className='space-y-4'><article className='rf-card p-6'><h1 className='text-2xl font-bold'>RouteForge v0.6.4-beta</h1><p className='mt-2 text-slate-600'>Modernes read-only Operator-Tool für Preflight Checks von ASN, Prefix, RPKI und Registry/IRR.</p></article>{migrationsBlocked && <article className='rf-card border border-amber-300 bg-amber-50 p-4 text-amber-900'>Database migrations are required before using RouteForge.</article>}</section>}
    {active === 'asn' && <AsnCheckForm />}
    {active === 'prefix' && <PrefixCheckForm />}
    {active === 'preflight' && <PreflightCheckForm />}
    {active === 'reports' && <section className='rf-card p-4'><h2 className='mb-3 text-xl font-semibold'>Reports</h2>{reports.length===0 ? <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>Noch keine Reports vorhanden.</div> : <div className='overflow-x-auto'><table className='w-full text-sm'><tbody>{reports.map(r=><tr key={r.report_id}><td>{r.summary}</td><td><button className='rf-btn-secondary' onClick={async ()=>navigator.clipboard?.writeText(await getReportSummary(r.report_id))}>Copy Summary</button><button className='rf-btn-secondary' onClick={async ()=>{const t=await getReportMarkdown(r.report_id);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/markdown'}));a.download=`routeforge-report-${r.report_id}.md`;a.click()}}>Download Markdown</button><button className='rf-btn-secondary' onClick={async ()=>{const t=await getReportHtml(r.report_id);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/html'}));a.download=`routeforge-report-${r.report_id}.html`;a.click()}}>Download HTML</button></td></tr>)}</tbody></table></div>}</section>}
    {active === 'system' && <section className='space-y-3'>{systemStatusError && <article className='rf-card p-4 text-rose-700'>{systemStatusError}</article>}{migrationsBlocked && <article className='rf-card border border-amber-300 bg-amber-50 p-4 text-amber-900'>Database migrations are required before using RouteForge.</article>}{systemStatus && <article className='rf-card p-4 grid gap-2 md:grid-cols-2 text-sm'><div>Version: <b>{systemStatus.version}</b></div><div>Mode: <b>{systemStatus.mode}</b></div><div>API Proxy: <b>{proxyStatus}</b></div><div>Migration Status: <b>{migrationStatus}</b> <StatusBadge status={migrationStatus === 'up_to_date' ? 'OK' : migrationStatus === 'behind' ? 'WARNING' : migrationStatus === 'error' ? 'CRITICAL' : 'UNKNOWN'} /></div></article>}</section>}
    {active === 'about' && <section className='rf-card p-5 space-y-2 text-sm text-slate-700'><p><b>Version:</b> v0.6.4-beta</p></section>}
  </Layout>
}
