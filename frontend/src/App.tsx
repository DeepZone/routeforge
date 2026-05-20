import { useEffect, useMemo, useState } from 'react'
import { getReports, getSystemInfo } from './api'
import { AsnCheckForm } from './components/AsnCheckForm'
import { Layout } from './components/Layout'
import { PrefixCheckForm } from './components/PrefixCheckForm'
import { PreflightCheckForm } from './components/PreflightCheckForm'
import { StatusBadge } from './components/StatusBadge'
import type { ReportListItem, SystemInfo } from './types'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'preflight' | 'reports' | 'about'

export default function App() {
  const [active, setActive] = useState<NavKey>('dashboard')
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [system, setSystem] = useState<SystemInfo | null>(null)
  useEffect(() => { getReports().then(setReports).catch(() => setReports([])); getSystemInfo().then(setSystem).catch(() => null) }, [])
  const systemLine = useMemo(() => system ? `${system.name} ${system.version} · mode=${system.demo_mode ? 'DEMO' : 'LIVE'} · read_only=${String(system.read_only)}` : 'RouteForge v0.2.0-alpha · read-only preflight checks', [system])
  const title = { dashboard: 'Dashboard', asn: 'ASN Check', prefix: 'Prefix Check', preflight: 'Preflight Check', reports: 'Reports', about: 'About RouteForge' }[active]

  return <Layout active={active} onNav={setActive} systemLine={systemLine} title={title} demoMode={Boolean(system?.demo_mode)}>
    {active === 'dashboard' && <section className='space-y-4'>
      <article className='rf-card p-6'><h1 className='text-2xl font-bold'>RouteForge v0.2.0-alpha</h1><p className='mt-2 text-slate-600'>Modernes read-only Operator-Tool für Preflight Checks von ASN, Prefix, RPKI und Registry/IRR.</p><p className='mt-3 rf-alert border-slate-200 bg-slate-50 text-slate-700'>Security-Modell: ausschließlich read-only, keine writes/deployments.</p></article>
      <div className='grid gap-3 md:grid-cols-3'>{[['ASN Check', 'asn'], ['Prefix Check', 'prefix'], ['Preflight Check', 'preflight'], ['Reports', 'reports']].map(([x, key]) => <button key={x} onClick={() => setActive(key as NavKey)} className='rf-card p-4 text-left hover:border-blue-300'><h3 className='font-semibold'>{x}</h3></button>)}</div>
      <article className='rf-card p-4'><h2 className='mb-2 font-semibold'>Letzte Reports</h2>{reports.length === 0 ? <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>Noch keine Reports vorhanden.</div> : <div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th className='py-2'>Zeit</th><th>Typ</th><th>Resource</th><th>Holder</th><th>Status</th></tr></thead><tbody>{reports.slice(0, 8).map(r => <tr key={r.report_id} className='border-b border-slate-100'><td className='py-2'>{new Date(r.created_at).toLocaleString()}</td><td>{r.check_type === 'preflight' ? 'Preflight' : r.check_type}</td><td>{r.input_resource}</td><td>{r.holder || 'Unknown'}</td><td><StatusBadge status={r.status} /></td></tr>)}</tbody></table></div>}</article>
    </section>}
    {active === 'asn' && <AsnCheckForm />}
    {active === 'prefix' && <PrefixCheckForm />}
    {active === 'preflight' && <PreflightCheckForm />}
    {active === 'reports' && <section className='rf-card p-4'><h2 className='mb-3 text-xl font-semibold'>Reports</h2>{reports.length===0 ? <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>Noch keine Reports vorhanden.</div> : <div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th>Zeitpunkt</th><th>Typ</th><th>Resource</th><th>Origin-AS</th><th>Holder</th><th>Status</th><th>Kurzfassung</th></tr></thead><tbody>{reports.map(r=><tr key={r.report_id} className='border-b border-slate-100'><td className='py-2'>{new Date(r.created_at).toLocaleString()}</td><td>{r.check_type === 'preflight' ? 'Preflight' : r.check_type}</td><td>{r.input_resource}</td><td>{r.origin_as || '-'}</td><td>{r.holder || 'Unknown'}</td><td><StatusBadge status={r.status} /></td><td>{r.summary}</td></tr>)}</tbody></table></div>}</section>}
    {active === 'about' && <section className='rf-card p-5 space-y-2 text-sm text-slate-700'><p>RouteForge liefert nachvollziehbare Routing-Preflightchecks für technische Operator-Workflows.</p><p><b>Datenquellen:</b> RPKI Validator APIs und Registry/IRR Quellen.</p><p><b>Modell:</b> read-only Betrieb.</p><p><b>Limitations:</b> Externe Datenquellen können unvollständig oder verzögert sein.</p><p><b>Version:</b> v0.2.0-alpha</p></section>}
  </Layout>
}
