import type { CheckResponse, RpkiBatchResult } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'

const order = { CRITICAL: 0, WARNING: 1, UNKNOWN: 2, OK: 3 }

const RecommendationList = ({ items }: { items: string[] }) => items.length ? <ul className='list-disc pl-5 text-sm space-y-1'>{items.map((r, i) => <li key={`${r}-${i}`}>{r}</li>)}</ul> : <p className='text-sm text-slate-600'>Keine Empfehlungen verfügbar.</p>
const RawSection = ({ title, raw }: { title: string; raw: unknown }) => <details className='mt-2'><summary className='cursor-pointer text-sm font-medium'>{title}</summary><pre className='mt-2 text-xs overflow-auto bg-slate-950 text-slate-100 p-3 rounded'>{JSON.stringify(raw ?? {}, null, 2)}</pre></details>

export function ReportView({ report }: { report: CheckResponse }) {
  const rpki = report.checks?.rpki
  const registry = report.checks?.registry
  const recs = report.recommendations ?? []
  const details = report.details ?? {}
  const rpkiSummary = details.rpki_summary as Record<string, number> | undefined
  const sortedResults = ([...(Array.isArray(details.results) ? details.results : [])] as RpkiBatchResult[]).sort((a, b) => (order[a.status as keyof typeof order] ?? 99) - (order[b.status as keyof typeof order] ?? 99))

  return <div className='space-y-4'>
    {details.demo_mode && <div className='p-3 rounded-md border border-amber-300 bg-amber-50 text-amber-900 text-sm'><strong>Demo-Modus aktiv.</strong> Es werden feste Beispieldaten verwendet. Diese Ausgabe ist nicht für echte Routing-Bewertungen geeignet.</div>}
    <section className='bg-white border rounded-lg p-4'>
      <div className='flex items-center gap-2 mb-2'><h3 className='font-semibold text-lg'>Gesamtbewertung</h3><StatusBadge status={report.status} /></div>
      <p className='font-medium'>{report.summary}</p><p className='text-sm mt-2'><strong>Erklärung:</strong> {report.explanation || '-'}</p><p className='text-sm mt-1'><strong>Risiko:</strong> {report.risk || '-'}</p>
      <h4 className='font-semibold mt-3'>Empfehlungen</h4><RecommendationList items={recs} />
    </section>

    {(rpki || registry) && <section className='grid md:grid-cols-2 gap-4'>
      {rpki && <article className='bg-white border rounded-lg p-4'><div className='flex items-center gap-2'><h4 className='font-semibold'>RPKI</h4><StatusBadge status={rpki.status || 'UNKNOWN'} /></div><p className='text-sm mt-2'><strong>Kurzfassung:</strong> {rpki.summary || '-'}</p><p className='text-sm mt-1'><strong>Erklärung:</strong> {rpki.explanation || '-'}</p><p className='text-sm mt-1'><strong>Risiko:</strong> {rpki.risk || '-'}</p><RecommendationList items={rpki.recommendations || []} /><RawSection title='RPKI Rohdaten' raw={rpki.raw} /></article>}
      {registry && <article className='bg-white border rounded-lg p-4'><div className='flex items-center gap-2'><h4 className='font-semibold'>Registry/IRR</h4><StatusBadge status={registry.status || 'UNKNOWN'} /></div><p className='text-sm mt-2'><strong>Kurzfassung:</strong> {registry.summary || '-'}</p><p className='text-sm mt-1'><strong>Erklärung:</strong> {registry.explanation || '-'}</p><p className='text-sm mt-1'><strong>Risiko:</strong> {registry.risk || '-'}</p><RecommendationList items={registry.recommendations || []} /><RawSection title='Registry/IRR Rohdaten' raw={registry.raw} /></article>}
    </section>}

    <section className='bg-white border rounded-lg p-4 text-sm'><h4 className='font-semibold mb-2'>Technische Details</h4><p><strong>input:</strong> {JSON.stringify(report.input ?? {})}</p><p><strong>warnings:</strong> {JSON.stringify(details.warnings ?? [])}</p><p><strong>source_errors:</strong> {JSON.stringify(details.source_errors ?? [])}</p><p><strong>demo_mode:</strong> {String(Boolean(details.demo_mode))}</p></section>

    {rpkiSummary && <section className='bg-white border rounded-lg p-4 text-sm'><h4 className='font-semibold mb-2'>ASN-RPKI Batch Summary</h4><div className='grid grid-cols-2 md:grid-cols-4 gap-2'>{['checked_prefixes','total_prefixes_seen','limited','valid','invalid_asn','invalid_length','unknown','errors'].map((k) => <div key={k} className='p-2 rounded bg-slate-50 border'><div className='text-xs text-slate-500'>{k}</div><div className='font-semibold'>{String((details as Record<string, unknown>)[k] ?? rpkiSummary[k] ?? 0)}</div></div>)}</div></section>}

    {sortedResults.length > 0 && <section className='bg-white border rounded-lg p-4'><h4 className='font-semibold mb-2'>ASN-RPKI Ergebnisse</h4><div className='space-y-2'>{sortedResults.map((item, idx) => <div key={`${item.prefix}-${idx}`} className='p-2 border rounded'><div className='flex items-center gap-2'><StatusBadge status={item.status || 'UNKNOWN'} /><span className='font-mono text-xs'>{item.prefix}</span></div><p className='text-sm mt-1'>{item.summary || '-'}</p></div>)}</div></section>}

    <button className='px-3 py-2 border rounded-md text-sm hover:bg-slate-50' onClick={() => navigator.clipboard.writeText(report.markdown)}>Markdown-Report kopieren</button>
    <RawDataPanel data={report.details} />
  </div>
}
