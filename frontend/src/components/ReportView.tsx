import { useState } from 'react'
import { getReportHtml, getReportMarkdown, getReportSummary } from '../api'
import type { CheckResponse, RpkiBatchResult, SourceDiagnostic } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'

const order = { CRITICAL: 0, WARNING: 1, UNKNOWN: 2, OK: 3 }
const decisionByStatus: Record<string, string> = { OK: 'GO', WARNING: 'CAUTION', CRITICAL: 'NO-GO', UNKNOWN: 'UNKNOWN' }

const formatDurationSeconds = (seconds: number): string => {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`
  return `${Math.floor(seconds / 3600)}h`
}

const freshnessClass = (freshness?: string): string => {
  if (freshness === 'LIVE' || freshness === 'FRESH') return 'text-emerald-700'
  if (freshness === 'EXPIRING_SOON') return 'text-amber-700'
  if (freshness === 'STALE') return 'text-red-700'
  return 'text-slate-500'
}

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
  const reportId = Number((report as { report_id?: number; id?: number; details?: { report_id?: number } }).report_id ?? (report as { id?: number }).id ?? (report.details as { report_id?: number } | undefined)?.report_id)
  const hasReportId = Number.isFinite(reportId) && reportId > 0
  const rpkiBatch = details.rpki_batch as { message?: string } | undefined
  const sourceDiagnostics = (Array.isArray(details.source_diagnostics) ? details.source_diagnostics : []) as SourceDiagnostic[]

  const notify = (message: string) => {
    setCopyMessage(message)
    window.setTimeout(() => setCopyMessage(''), 2000)
  }
  const copyTextToClipboard = async (text: string): Promise<void> => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return
    }
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.setAttribute('readonly', '')
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(textarea)
    if (!ok) throw new Error('Clipboard fallback unavailable')
  }
  const downloadText = async (filename: string, text: string, mimeType: string) => {
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


    {sourceDiagnostics.length > 0 && <section className='rf-card p-4 space-y-2'><h4 className='font-semibold'>Data Source Diagnostics</h4><div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th className='py-2'>Source</th><th>Endpoint</th><th>Status</th><th>Freshness</th><th>Attempts</th><th>Retries</th><th>Fallback</th><th>Stale Cache</th><th>Duration</th><th>Cache</th><th>Age</th><th>TTL</th><th>Message</th></tr></thead><tbody>{sourceDiagnostics.map((d, idx) => <tr key={`${d.name}-${idx}`} className='border-b border-slate-100'><td>{d.name || '-'}</td><td className='font-mono'>{d.endpoint || '-'}</td><td><StatusBadge status={d.status || 'UNKNOWN'} /></td><td className={freshnessClass(d.freshness)}>{d.freshness || 'UNKNOWN'}</td><td>{typeof d.attempts === 'number' ? d.attempts : '-'}</td><td>{typeof d.retry_count === 'number' ? d.retry_count : '-'}</td><td>{d.fallback_used === true ? 'yes' : d.fallback_used === false ? 'no' : '-'}</td><td>{d.stale_cache_used === true ? 'yes' : d.stale_cache_used === false ? 'no' : '-'}</td><td>{typeof d.duration_ms === 'number' ? `${d.duration_ms} ms` : '-'}</td><td>{d.cached === true ? 'HIT' : d.cached === false ? 'MISS' : '-'}</td><td>{typeof d.cache_age_seconds === 'number' ? formatDurationSeconds(d.cache_age_seconds) : 'Unknown'}</td><td>{typeof d.cache_ttl_seconds === 'number' ? formatDurationSeconds(d.cache_ttl_seconds) : 'Unknown'}</td><td><div>{d.message || '-'}</div>{d.fallback_used === true && <div className='mt-1 rounded border border-amber-200 bg-amber-50 p-2 text-amber-800'>Live request failed. RouteForge used cached data. The result may be outdated.</div>}{d.status === 'RATE_LIMITED' && <div className='mt-1 text-amber-700'>Rate limited by data source.</div>}</td></tr>)}</tbody></table></div></section>}

    <details className='rf-card p-4'><summary className='cursor-pointer text-sm font-semibold'>Technische Details</summary><pre className='mt-3 overflow-auto rounded-xl bg-slate-50 p-3 text-xs'>{JSON.stringify({ input: report.input, holder: details.resource_holder, warnings: details.warnings, source_errors: details.source_errors }, null, 2)}</pre></details>
    {sortedResults.length > 0 && <section className='rf-card p-4'><h4 className='mb-2 font-semibold'>Batch Results</h4><div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='border-b text-left'><th className='py-2'>Status</th><th>Prefix</th><th>Summary</th></tr></thead><tbody>{sortedResults.map((item, idx) => <tr key={`${item.prefix}-${idx}`} className='border-b border-slate-100'><td className='py-2'><StatusBadge status={item.status || 'UNKNOWN'} /></td><td className='font-mono'>{item.prefix}</td><td>{item.summary || '-'}</td></tr>)}</tbody></table></div></section>}
    {sortedResults.length === 0 && ((details.checked_prefixes as number | undefined) === 0 || rpkiBatch?.message) && <section className='rf-card p-4'><h4 className='mb-2 font-semibold'>Keine Prefixe geprüft</h4><p className='text-sm text-slate-700'>{rpkiBatch?.message || report.explanation || 'Keine Daten verfügbar.'}</p></section>}
    {rpkiBatch?.message && <section className='rf-card p-4 border-l-4 border-l-amber-500'><h4 className='font-semibold'>RPKI-Batch Hinweis</h4><p className='text-sm'>{rpkiBatch.message}</p></section>}
    <section className='rf-card p-4 space-y-2'>
      <h4 className='font-semibold'>Export</h4>
      {!hasReportId && <p className='text-sm text-slate-600'>Export ist erst verfügbar, nachdem der Report gespeichert wurde.</p>}
      <div className='flex flex-wrap gap-2'>
        <button title={!hasReportId ? 'Export ist erst verfügbar, nachdem der Report gespeichert wurde.' : ''} className='rf-btn-secondary' disabled={!hasReportId} onClick={async () => { try { if (!hasReportId) return; await copyTextToClipboard(await getReportSummary(reportId)); notify('Summary copied') } catch (e) { notify(`Copy failed: ${e instanceof Error ? e.message : 'unknown error'}`) } }}>Copy Summary</button>
        <button title={!hasReportId ? 'Export ist erst verfügbar, nachdem der Report gespeichert wurde.' : ''} className='rf-btn-secondary' disabled={!hasReportId} onClick={async () => { try { if (!hasReportId) return; await copyTextToClipboard(await getReportMarkdown(reportId)); notify('Markdown copied') } catch (e) { notify(`Copy failed: ${e instanceof Error ? e.message : 'unknown error'}`) } }}>Copy Markdown</button>
        <button className='rf-btn-secondary' disabled={!hasReportId} onClick={async () => hasReportId && downloadText(`routeforge-report-${reportId}.md`, await getReportMarkdown(reportId), 'text/markdown;charset=utf-8')}>Download Markdown</button>
        <button className='rf-btn-secondary' disabled={!hasReportId} onClick={async () => hasReportId && downloadText(`routeforge-report-${reportId}.html`, await getReportHtml(reportId), 'text/html;charset=utf-8')}>Download HTML</button>
      </div>
      {copyMessage && <p className='text-sm text-slate-600'>{copyMessage}</p>}
    </section>
    <RawDataPanel data={report.details} />
  </div>
}
