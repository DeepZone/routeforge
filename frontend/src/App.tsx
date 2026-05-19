import { useEffect, useMemo, useState } from 'react'
import { getReports, getSystemInfo } from './api'
import { AsnCheckForm } from './components/AsnCheckForm'
import { Layout } from './components/Layout'
import { PrefixCheckForm } from './components/PrefixCheckForm'
import { StatusBadge } from './components/StatusBadge'
import type { ReportListItem, SystemInfo } from './types'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'reports' | 'about'

export default function App() {
  const [active, setActive] = useState<NavKey>('dashboard')
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [system, setSystem] = useState<SystemInfo | null>(null)

  useEffect(() => { getReports().then(setReports).catch(() => setReports([])); getSystemInfo().then(setSystem).catch(() => null) }, [])

  const systemLine = useMemo(() => system ? `${system.name} ${system.version} · mode=${system.demo_mode ? 'DEMO' : 'LIVE'} · read_only=${String(system.read_only)}` : 'RouteForge v0.1.0-alpha · read-only preflight checks', [system])

  return <Layout active={active} onNav={setActive} systemLine={systemLine}>
    {active === 'dashboard' && <section className='space-y-4'>
      <div className='bg-white border rounded-lg p-4'><h1 className='text-2xl font-bold'>RouteForge v0.1.0-alpha</h1><p className='mt-2 text-slate-700'>Read-only preflight checks for BGP, RPKI and Registry/IRR data.</p>{system?.demo_mode && <p className='mt-3 p-2 rounded border border-amber-300 bg-amber-50 text-amber-900 text-sm'>Demo-Modus aktiv. Feste Beispieldaten können enthalten sein.</p>}<p className='mt-3 text-sm'>Sicherheitsmodell: ausschließlich read-only. Keine Writes, keine Deployments.</p></div>
      <div className='grid md:grid-cols-3 gap-3'>{['ASN prüfen','Prefix prüfen','Demo Flow'].map((x,i)=><button key={x} onClick={()=>setActive(i===0?'asn':i===1?'prefix':'reports')} className='bg-white border rounded-lg p-4 text-left hover:bg-slate-50'><h3 className='font-semibold'>{x}</h3></button>)}</div>
      <div className='bg-white border rounded-lg p-4'><h2 className='font-semibold mb-2'>Letzte Reports</h2>{reports.length===0 ? <p className='text-sm text-slate-600'>Report history will appear here after checks.</p> : <ul className='space-y-2'>{reports.slice(0,5).map(r=><li key={r.report_id} className='text-sm border rounded p-2 flex items-center justify-between'><span>{r.input_resource} ({r.check_type})</span><StatusBadge status={r.status} /></li>)}</ul>}</div>
    </section>}
    {active === 'asn' && <AsnCheckForm />}
    {active === 'prefix' && <PrefixCheckForm />}
    {active === 'reports' && <section className='bg-white border rounded-lg p-4'><h2 className='text-xl font-semibold mb-3'>Reports</h2>{reports.length===0 ? <p>Noch keine Reports vorhanden.</p> : <div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='text-left border-b'><th>Zeitpunkt</th><th>Typ</th><th>Resource</th><th>Origin-AS</th><th>Status</th><th>Kurzfassung</th></tr></thead><tbody>{reports.map(r=><tr key={r.report_id} className='border-b'><td>{new Date(r.created_at).toLocaleString()}</td><td>{r.check_type}</td><td>{r.input_resource}</td><td>{r.origin_as || '-'}</td><td><StatusBadge status={r.status} /></td><td>{r.summary}</td></tr>)}</tbody></table></div>}</section>}
    {active === 'about' && <section className='bg-white border rounded-lg p-4'><h2 className='text-xl font-semibold'>About</h2><p className='mt-2 text-sm'>RouteForge unterstützt nachvollziehbare Routing-Preflightchecks für Operator-Workflows.</p></section>}
  </Layout>
}
