import { useState } from 'react'
import { getReportHtml, getReportMarkdown, getReportSummary } from '../api'
import type { CheckResponse, RpkiBatchResult } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'

const order = { CRITICAL: 0, WARNING: 1, UNKNOWN: 2, OK: 3 }
const decisionByStatus: Record<string, string> = { OK: 'GO', WARNING: 'CAUTION', CRITICAL: 'NO-GO', UNKNOWN: 'UNKNOWN' }

export function ReportView({ report }: { report: CheckResponse }) {
  const [copyMessage, setCopyMessage] = useState<string>('')
  const details = report.details ?? {}
  const holder = (details.resource_holder as { holder?: string } | undefined)?.holder || 'Unknown'
  const checkType = report.input?.planned_origin_as ? 'Preflight' : report.input?.asn ? 'ASN Check' : 'Prefix Check'
  const preflightDecision = (details.preflight_decision as string | undefined) || decisionByStatus[report.status] || 'UNKNOWN'
  const rpki = report.checks?.rpki
  const registry = report.checks?.registry
  const routingVisibility = report.checks?.routing_visibility
  const sortedResults = ([...(Array.isArray(details.results) ? details.results : [])] as RpkiBatchResult[]).sort((a, b) => (order[a.status as keyof typeof order] ?? 99) - (order[b.status as keyof typeof order] ?? 99))
  const recommendationsTitle = report.status === 'CRITICAL' ? 'Sofort prüfen' : report.status === 'WARNING' ? 'Empfohlen' : report.status === 'OK' ? 'Hinweis' : 'Datenlage prüfen'
  const reportId = report.report_id

  const notify = (message: string) => {
    setCopyMessage(message)
    window.setTimeout(() => setCopyMessage(''), 2000)
  }
  const copyText = async (text: string, success: string) => {
    if (!navigator.clipboard?.writeText) return notify('Copy failed')
    try { await navigator.clipboard.writeText(text); notify(success) } catch { notify('Copy failed') }
  }
  const downloadText = (filename: string, text: string, mimeType: string) => {
    const blob = new Blob([text], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  }

  return <div className='space-y-4'>
    <section className='rf-card p-5 space-y-2 border-l-4 border-l-blue-500'>
      <div className='flex items-center gap-2'><h3 className='text-lg font-semibold'>Ergebnis</h3><StatusBadge status={report.status} /></div>
      <div className='grid gap-1 text-sm md:grid-cols-2'>
        <p><b>Check-Typ:</b> {checkType}</p><p><b>Resource:</b> {report.input?.prefix || report.input?.asn || '-'}</p>
        <p><b>Origin-AS:</b> {report.input?.origin_as || report.input?.planned_origin_as || '-'}</p><p><b>Holder:</b> {holder}</p>
      </div>
      {report.input?.planned_origin_as && <p className='text-sm'><b>Preflight Decision:</b> {preflightDecision}</p>}
      <p className='font-medium'>{report.summary}</p>
    </section>

    <section className='rf-card p-5 space-y-3'>
      <div className='flex items-center gap-2'><h3 className='text-lg font-semibold'>Gesamtbewertung</h3><StatusBadge status={report.status} /></div>
      <p className='text-sm'><b>Erklärung:</b> {report.explanation || '-'}</p><p className='text-sm'><b>Risiko:</b> {report.risk || '-'}</p>
      <div><h4 className='font-semibold text-sm mb-1'>{recommendationsTitle}</h4><ul className='list-disc pl-5 text-sm'>{(report.recommendations || []).map((r, i) => <li key={`${r}-${i}`}>{r}</li>)}</ul></div>
    </section>

    <section className='grid gap-4 md:grid-cols-2'>
      {[['RPKI', rpki], ['Registry/IRR', registry], ['Routing Visibility', routingVisibility] as const].map(([title, item]) => item && <article key={title} className='rf-card p-4'><div className='mb-2 flex items-center gap-2'><h4 className='font-semibold'>{title}</h4><StatusBadge status={item.status || 'UNKNOWN'} /></div><p className='text-sm'>{item.summary || '-'}</p></article>)}
    </section>

    <details className='rf-card p-4'><summary className='cursor-pointer text-sm font-semibold'>Technische Details</summary><pre className='mt-3 overflow-auto rounded-xl bg-slate-50 p-3 text-xs'>{JSON.stringify({ input: report.input, holder: details.resource_holder, warnings: details.warnings, source_errors: details.source_errors }, null, 2)}</pre></details>
    {sortedResults.length > 0 && <section className='rf-card p-4'><h4 className='mb-2 font-semibold'>Batch Results</h4><div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th className='py-2'>Status</th><th>Prefix</th><th>Summary</th></tr></thead><tbody>{sortedResults.map((item, idx) => <tr key={`${item.prefix}-${idx}`} className='border-b border-slate-100'><td className='py-2'><StatusBadge status={item.status || 'UNKNOWN'} /></td><td className='font-mono'>{item.prefix}</td><td>{item.summary || '-'}</td></tr>)}</tbody></table></div></section>}
    <section className='rf-card p-4 space-y-2'>
      <h4 className='font-semibold'>Export</h4>
      <div className='flex flex-wrap gap-2'>
        <button className='rf-btn-secondary' disabled={!reportId} onClick={async () => reportId && copyText(await getReportSummary(reportId), 'Summary copied')}>Copy Summary</button>
        <button className='rf-btn-secondary' disabled={!reportId} onClick={async () => reportId && copyText(await getReportMarkdown(reportId), 'Markdown copied')}>Copy Markdown</button>
        <button className='rf-btn-secondary' disabled={!reportId} onClick={async () => reportId && downloadText(`routeforge-report-${reportId}.md`, await getReportMarkdown(reportId), 'text/markdown;charset=utf-8')}>Download Markdown</button>
        <button className='rf-btn-secondary' disabled={!reportId} onClick={async () => reportId && downloadText(`routeforge-report-${reportId}.html`, await getReportHtml(reportId), 'text/html;charset=utf-8')}>Download HTML</button>
      </div>
      {copyMessage && <p className='text-sm text-slate-600'>{copyMessage}</p>}
    </section>
    <RawDataPanel data={report.details} />
  </div>
}
