import { useEffect, useMemo, useState } from 'react'
import { getReportHtml, getReportMarkdown, getReportSummary, getReports, getSystemInfo, getSystemStatus } from './api'
import { AsnCheckForm } from './components/AsnCheckForm'
import { Layout } from './components/Layout'
import { PrefixCheckForm } from './components/PrefixCheckForm'
import { PreflightCheckForm } from './components/PreflightCheckForm'
import { StatusBadge } from './components/StatusBadge'
import type { ReportListItem, SystemInfo, SystemStatus } from './types'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'preflight' | 'reports' | 'system' | 'about'

export default function App() {
  const [active, setActive] = useState<NavKey>('dashboard')
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [system, setSystem] = useState<SystemInfo | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [systemStatusError, setSystemStatusError] = useState('')

  useEffect(() => {
    getReports().then(setReports).catch(() => setReports([]))
    getSystemInfo().then(setSystem).catch(() => null)
    getSystemStatus().then((payload) => { setSystemStatus(payload); setSystemStatusError('') }).catch(() => setSystemStatusError('System status could not be loaded.'))
  }, [])

  const systemLine = useMemo(() => system ? `${system.name} ${system.version} · mode=${system.demo_mode ? 'DEMO' : 'LIVE'} · read_only=${String(system.read_only)}` : 'RouteForge v0.5.2-beta · read-only preflight checks', [system])
  const title = { dashboard: 'Dashboard', asn: 'ASN Check', prefix: 'Prefix Check', preflight: 'Preflight Check', reports: 'Reports', system: 'System Status', about: 'About RouteForge' }[active]
  const proxyStatus = systemStatusError ? 'ERROR' : 'OK'

  return <Layout active={active} onNav={setActive} systemLine={systemLine} title={title} demoMode={Boolean(system?.demo_mode)}>
    {active === 'dashboard' && <section className='space-y-4'>
      <article className='rf-card p-6'><h1 className='text-2xl font-bold'>RouteForge v0.5.2-beta</h1><p className='mt-2 text-slate-600'>Modernes read-only Operator-Tool für Preflight Checks von ASN, Prefix, RPKI und Registry/IRR.</p></article>
      <article className='rf-card p-4'><h3 className='font-semibold'>System Health</h3>{systemStatusError ? <p className='text-sm text-rose-700 mt-2'>{systemStatusError}</p> : <div className='mt-2 grid gap-2 text-sm md:grid-cols-4'><div>Status: <b>{systemStatus?.status || 'unknown'}</b></div><div>Mode: <b>{systemStatus?.mode || 'unknown'}</b></div><div>Database: <b>{systemStatus?.database?.status || 'unknown'}</b></div><div>Version: <b>{systemStatus?.version || 'unknown'}</b></div></div>}</article>
    </section>}
    {active === 'asn' && <AsnCheckForm />}
    {active === 'prefix' && <PrefixCheckForm />}
    {active === 'preflight' && <PreflightCheckForm />}
    {active === 'reports' && <section className='rf-card p-4'><h2 className='mb-3 text-xl font-semibold'>Reports</h2>{reports.length===0 ? <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>Noch keine Reports vorhanden.</div> : <div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th>Zeitpunkt</th><th>Typ</th><th>Resource</th><th>Origin-AS</th><th>Holder</th><th>Status</th><th>Kurzfassung</th><th>Actions</th></tr></thead><tbody>{reports.map(r=><tr key={r.report_id} className='border-b border-slate-100'><td className='py-2'>{new Date(r.created_at).toLocaleString()}</td><td>{r.check_type === 'preflight' ? 'Preflight' : r.check_type}</td><td>{r.input_resource}</td><td>{r.origin_as || '-'}</td><td>{r.holder || 'Unknown'}</td><td><StatusBadge status={r.status} /></td><td>{r.summary}</td><td><div className='flex flex-wrap gap-1'><button className='rf-btn-secondary' onClick={() => window.open(`/api/reports/${r.report_id}`, '_blank')}>Open</button><button className='rf-btn-secondary' onClick={async ()=>navigator.clipboard?.writeText(await getReportSummary(r.report_id))}>Copy Summary</button><button className='rf-btn-secondary' onClick={async ()=>{const t=await getReportMarkdown(r.report_id);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/markdown'}));a.download=`routeforge-report-${r.report_id}.md`;a.click()}}>Download Markdown</button><button className='rf-btn-secondary' onClick={async ()=>{const t=await getReportHtml(r.report_id);const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/html'}));a.download=`routeforge-report-${r.report_id}.html`;a.click()}}>Download HTML</button></div></td></tr>)}</tbody></table></div>}</section>}
    {active === 'system' && <section className='space-y-3'>
      {systemStatusError && <article className='rf-card p-4 text-rose-700'>{systemStatusError}</article>}
      {systemStatus && <>
        <article className='rf-card p-4'><h3 className='font-semibold'>Overall Status</h3><p className='text-sm mt-1'>{systemStatus.status}</p></article>
        <article className='rf-card p-4 grid gap-2 md:grid-cols-2 text-sm'>
          <div>Version: <b>{systemStatus.version}</b></div><div>Mode: <b>{systemStatus.mode}</b></div><div>Read-only: <b>{String(systemStatus.read_only)}</b></div><div>Demo mode: <b>{String(systemStatus.demo_mode)}</b></div>
          <div>API Proxy: <b>{proxyStatus}</b></div><div>Database: <b>{systemStatus.database?.status || 'unknown'}</b></div>
        </article>
        <article className='rf-card p-4 text-sm'><h3 className='font-semibold mb-2'>RIPEstat Settings</h3><pre>{JSON.stringify(systemStatus.ripestat, null, 2)}</pre></article>
        <article className='rf-card p-4 text-sm'><h3 className='font-semibold mb-2'>Features</h3><pre>{JSON.stringify(systemStatus.features, null, 2)}</pre></article>
      </>}
    </section>}
    {active === 'about' && <section className='rf-card p-5 space-y-2 text-sm text-slate-700'><p>RouteForge liefert nachvollziehbare Routing-Preflightchecks für technische Operator-Workflows.</p><p><b>Version:</b> v0.5.2-beta</p></section>}
  </Layout>
}
