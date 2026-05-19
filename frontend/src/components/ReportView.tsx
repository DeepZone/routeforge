import type { CheckResponse, RpkiBatchResult } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'

const order = { CRITICAL: 0, WARNING: 1, UNKNOWN: 2, OK: 3 }

export function ReportView({ report }: { report: CheckResponse }) {
  const details = report.details ?? {}
  const rpki = report.checks?.rpki
  const registry = report.checks?.registry
  const routingVisibility = report.checks?.routing_visibility
  const sortedResults = ([...(Array.isArray(details.results) ? details.results : [])] as RpkiBatchResult[]).sort((a, b) => (order[a.status as keyof typeof order] ?? 99) - (order[b.status as keyof typeof order] ?? 99))

  return <div className='space-y-4'>
    {details.demo_mode && <div className='rf-alert border-amber-300 bg-amber-50 text-amber-800'>Demo-Modus aktiv: Ausgabe kann simulierte Beispieldaten enthalten.</div>}
    <section className='rf-card p-5 space-y-3'>
      <div className='flex items-center gap-2'><h3 className='text-lg font-semibold'>Gesamtbewertung</h3><StatusBadge status={report.status} /></div>
      <p className='font-medium'>{report.summary}</p><p className='text-sm'><b>Erklärung:</b> {report.explanation || '-'}</p><p className='text-sm'><b>Risiko:</b> {report.risk || '-'}</p>
      <div><h4 className='font-semibold text-sm mb-1'>Empfehlungen</h4><ul className='list-disc pl-5 text-sm'>{(report.recommendations || []).map((r, i) => <li key={`${r}-${i}`}>{r}</li>)}</ul></div>
    </section>
    <section className='grid gap-4 md:grid-cols-2'>
      {[['RPKI', rpki], ['Registry/IRR', registry], ['Routing Visibility', routingVisibility] as const].map(([title, item]) => item && <article key={title} className='rf-card p-4'><div className='mb-2 flex items-center gap-2'><h4 className='font-semibold'>{title}</h4><StatusBadge status={item.status || 'UNKNOWN'} /></div><p className='text-sm'>{item.summary || '-'}</p></article>)}
    </section>
    <details className='rf-card p-4'><summary className='cursor-pointer text-sm font-semibold'>Technische Details</summary><pre className='mt-3 overflow-auto rounded-xl bg-slate-50 p-3 text-xs'>{JSON.stringify({ input: report.input, warnings: details.warnings, source_errors: details.source_errors }, null, 2)}</pre></details>
    {sortedResults.length > 0 && <section className='rf-card p-4'><h4 className='mb-2 font-semibold'>Batch Results</h4><div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th className='py-2'>Status</th><th>Prefix</th><th>Summary</th></tr></thead><tbody>{sortedResults.map((item, idx) => <tr key={`${item.prefix}-${idx}`} className='border-b border-slate-100'><td className='py-2'><StatusBadge status={item.status || 'UNKNOWN'} /></td><td className='font-mono'>{item.prefix}</td><td>{item.summary || '-'}</td></tr>)}</tbody></table></div></section>}
    <button className='rf-btn-secondary' onClick={() => navigator.clipboard.writeText(report.markdown)}>Markdown-Report kopieren</button>
    <RawDataPanel data={report.details} />
  </div>
}
