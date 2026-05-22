import { useEffect, useState } from 'react'
import { ApiError, getMe, getReportHtml, getReportMarkdown, getReportSummary, getReports, getSetupRequired, getSystemInfo, getSystemStatus, login, logout, setupAdmin } from './api'
import { AuditLogView } from './components/AuditLogView'
import { AsnCheckForm } from './components/AsnCheckForm'
import { Layout } from './components/Layout'
import { LoginView } from './components/LoginView'
import { PrefixCheckForm } from './components/PrefixCheckForm'
import { PreflightCheckForm } from './components/PreflightCheckForm'
import { BgpVisibilityForm } from './components/BgpVisibilityForm'
import { RoaPlannerForm } from './components/RoaPlannerForm'
import { SetupView } from './components/SetupView'
import { StatusBadge } from './components/StatusBadge'
import type { ReportListItem, SystemInfo, SystemStatus, User, UserRole } from './types'
import { UsersView } from './components/UsersView'
import { ChangeCasesView } from './components/ChangeCasesView'
import { WatchModeView } from './components/WatchModeView'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'preflight' | 'roa-planner' | 'bgp-visibility' | 'reports' | 'watch-mode' | 'change-cases' | 'system' | 'users' | 'audit' | 'about'
type AuthMode = 'loading' | 'setup' | 'login' | 'app' | 'error'

export default function App() {
  const [authMode, setAuthMode] = useState<AuthMode>('loading')
  const [authError, setAuthError] = useState('')
  const [active, setActive] = useState<NavKey>('dashboard')
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [system, setSystem] = useState<SystemInfo | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [systemStatusError, setSystemStatusError] = useState('')
  const [currentUser, setCurrentUser] = useState<User | null>(null)

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
        setCurrentUser(me.user)
        setAuthMode('app'); loadAppData()
      } catch (err: unknown) {
        if (err instanceof ApiError && err.status === 401) { setAuthMode('login'); setCurrentUser(null); return }
        setAuthMode('error'); setAuthError('Authentication state could not be loaded.')
      }
    } catch { setAuthMode('error'); setAuthError('Setup state could not be loaded.') }
  }

  useEffect(() => { bootstrapAuth() }, [])
  const handleLogout = async () => {
    try { await logout() } catch { setAuthError('Logout request failed, but local session was cleared.') }
    setCurrentUser(null); setAuthMode('login'); setActive('dashboard'); setReports([]); setSystemStatus(null)
  }

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

  const systemLine = system ? `${system.name} ${system.version} · mode=${system.demo_mode ? 'DEMO' : 'LIVE'} · read_only=${String(system.read_only)}` : 'RouteForge v0.9.2-rc · read-only preflight checks'
  const title = { dashboard: 'Dashboard', asn: 'ASN Check', prefix: 'Prefix Check', preflight: 'Preflight', 'roa-planner': 'ROA Planner', 'bgp-visibility': 'BGP Visibility', reports: 'Reports', 'watch-mode': 'Watch Mode', 'change-cases': 'Change Cases', system: 'System', users: 'Users', audit: 'Audit Log', about: 'About' }[active]
  const proxyStatus = systemStatusError ? 'ERROR' : 'OK'
  const migrationStatus = systemStatus?.database?.migration_status || 'unknown'
  const migrationsBlocked = migrationStatus === 'behind' || migrationStatus === 'error'

  const role = (currentUser?.role || 'viewer') as UserRole
  const canAccess = (view: NavKey) => {
    if (role === 'admin') return true
    if (role === 'operator') return !['users', 'audit'].includes(view)
    return ['dashboard', 'reports', 'watch-mode', 'change-cases', 'bgp-visibility', 'roa-planner', 'about'].includes(view)
  }
  const readOnlyLabel = system?.read_only ? 'Enabled' : 'Disabled'

  return <Layout active={active} onNav={setActive} systemLine={systemLine} title={title} demoMode={Boolean(system?.demo_mode)} currentUser={currentUser} onLogout={handleLogout}>
    {active === 'dashboard' && <section className='space-y-4'><article className='rf-card p-6 space-y-2'><h1 className='text-2xl font-bold'>{system?.name || 'RouteForge'} {system?.version || 'v0.9.2-rc'}</h1><div className='grid gap-1 text-sm md:grid-cols-2'><p><b>Current user:</b> {currentUser?.username || '-'}</p><p><b>Role:</b> {currentUser?.role || '-'}</p><p><b>Read-only:</b> {readOnlyLabel}</p><p><b>Mode:</b> {system?.demo_mode ? 'DEMO' : 'LIVE'}</p></div>{system?.demo_mode && <p className='rf-alert border-amber-200 bg-amber-50 text-amber-800'>Demo mode is active.</p>}</article><article className='rf-card p-4'><h3 className='mb-2 text-sm font-semibold'>Quick Actions</h3><div className='flex flex-wrap gap-2'><button className='rf-btn-secondary' onClick={() => setActive('preflight')}>Preflight</button><button className='rf-btn-secondary' onClick={() => setActive('reports')}>Reports</button>{role === 'admin' && <button className='rf-btn-secondary' onClick={() => setActive('system')}>System</button>}</div></article>{migrationsBlocked && <article className='rf-card border border-amber-300 bg-amber-50 p-4 text-amber-900'>Database migrations are required before using RouteForge. Run: <code>alembic current</code>, <code>alembic heads</code>, <code>alembic upgrade head</code>.</article>}</section>}
    {!canAccess(active) && <article className='rf-card p-4 text-amber-800 bg-amber-50 border border-amber-200'>You do not have permission to access this section.</article>}
    {active === 'asn' && canAccess('asn') && <AsnCheckForm />}
    {active === 'prefix' && canAccess('prefix') && <PrefixCheckForm />}
    {active === 'preflight' && canAccess('preflight') && <PreflightCheckForm />}
    {active === 'bgp-visibility' && canAccess('bgp-visibility') && <BgpVisibilityForm role={role} />}
    {active === 'roa-planner' && canAccess('roa-planner') && <RoaPlannerForm role={role} />}
    {active === 'reports' && <section className='rf-card p-4'><h2 className='mb-3 text-xl font-semibold'>Reports</h2>{reports.length===0 ? <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>No reports yet.</div> : <div className='overflow-x-auto'><table className='w-full text-sm'><tbody>{reports.map(r=><tr key={r.report_id}><td>{r.summary}</td><td><button className='rf-btn-secondary' onClick={async ()=>navigator.clipboard?.writeText(await getReportSummary(r.report_id))}>Copy Summary</button><button className='rf-btn-secondary' onClick={async ()=>{const t=await getReportMarkdown(r.report_id);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/markdown'}));a.download=`routeforge-report-${r.report_id}.md`;a.click()}}>Download Markdown</button><button className='rf-btn-secondary' onClick={async ()=>{const t=await getReportHtml(r.report_id);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/html'}));a.download=`routeforge-report-${r.report_id}.html`;a.click()}}>Download HTML</button></td></tr>)}</tbody></table></div>}</section>}
    {active === 'watch-mode' && canAccess('watch-mode') && <WatchModeView role={role} />}
    {active === 'change-cases' && canAccess('change-cases') && <ChangeCasesView role={role} />}
    {active === 'system' && canAccess('system') && <section className='space-y-3'>{systemStatusError && <article className='rf-card p-4 text-rose-700'>{systemStatusError}</article>}{migrationsBlocked && <article className='rf-card border border-amber-300 bg-amber-50 p-4 text-amber-900'>Database migrations are required before using RouteForge. Run: <code>alembic current</code>, <code>alembic heads</code>, <code>alembic upgrade head</code>.</article>}{systemStatus && <article className='rf-card p-4 grid gap-2 md:grid-cols-2 text-sm'><div>Version: <b>{systemStatus.version}</b></div><div>Mode: <b>{systemStatus.mode}</b></div><div>API Proxy: <b>{proxyStatus}</b></div><div>Migration Status: <b>{migrationStatus}</b> <StatusBadge status={migrationStatus === 'up_to_date' ? 'OK' : migrationStatus === 'behind' ? 'WARNING' : migrationStatus === 'error' ? 'CRITICAL' : 'UNKNOWN'} /></div><div>DB Current Revision: <b>{systemStatus.database?.schema_version || 'unknown'}</b></div><div>DB Head Revision: <b>{systemStatus.database?.migration_head || 'unknown'}</b></div></article>}</section>}
    {active === 'users' && canAccess('users') && <UsersView />}
    {active === 'audit' && canAccess('audit') && <AuditLogView />}
    {active === 'about' && <section className='rf-card p-5 space-y-2 text-sm text-slate-700'><p>RouteForge is a read-only routing operations console for validation workflows.</p><p><b>Read-only:</b> All checks are non-destructive.</p><p><b>Version:</b> v0.9.2-rc</p></section>}
  </Layout>
}
