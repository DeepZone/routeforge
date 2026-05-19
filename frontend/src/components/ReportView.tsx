import type { CheckResponse, RpkiBatchResult } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'

const order = { CRITICAL: 0, WARNING: 1, UNKNOWN: 2, OK: 3 }

export function ReportView({ report }: { report: CheckResponse }) {
  const recs = report.recommendations ?? []
  const rpki = report.checks?.rpki
  const hasRpkiCheck = Boolean(rpki)
  const rpkiExplanation = report.details?.rpki_explanation
  const extractedPrefixes = Array.isArray(report.details?.extracted_prefixes) ? report.details.extracted_prefixes : []
  const rpkiSummary = report.details?.rpki_summary
  const results = (Array.isArray(report.details?.results) ? report.details.results : []) as RpkiBatchResult[]
  const checkedPrefixes = Number(report.details?.checked_prefixes ?? 0)
  const totalPrefixesSeen = Number(report.details?.total_prefixes_seen ?? 0)
  const limited = Boolean(report.details?.limited)
  const sortedResults = [...results].sort((a, b) => (order[a.status as keyof typeof order] ?? 99) - (order[b.status as keyof typeof order] ?? 99))

  return <div className='mt-6 p-4 border rounded bg-white'>
    <div className='flex gap-2 items-center'><h3 className='text-lg font-bold'>Ergebnis</h3><StatusBadge status={report.status} /></div>
    <p className='mt-3 font-semibold'>{report.summary || 'Keine Kurzfassung verfügbar.'}</p>
    <p className='mt-2'><strong>Erklärung:</strong> {report.explanation || 'Keine Erklärung verfügbar.'}</p>
    <p className='mt-2'><strong>Risiko:</strong> {report.risk || 'Keine Risikobewertung verfügbar.'}</p>
    {rpkiExplanation && <p className='mt-2 p-2 rounded bg-amber-50 border border-amber-200'><strong>RPKI-Hinweis:</strong> {String(rpkiExplanation)}</p>}
    {extractedPrefixes.length > 0 && <p className='mt-2 text-sm'><strong>Sichtbare Prefixe:</strong> {extractedPrefixes.length}</p>}
    {report.details?.demo_mode && <p className='mt-2 text-sm p-3 rounded border border-blue-300 bg-blue-50 text-blue-900'><strong>Demo-Modus aktiv.</strong> Es werden feste Beispieldaten verwendet. Diese Ausgabe ist nicht für echte Routing-Bewertungen geeignet.</p>}

    <h4 className='font-semibold mt-4'>Empfehlungen</h4>
    {recs.length > 0 ? <ul className='list-disc pl-5'>{recs.map((r, i) => <li key={`${r}-${i}`}>{r}</li>)}</ul> : <p>Keine Empfehlungen verfügbar.</p>}

    <h4 className='font-semibold mt-4'>Einzelprüfungen</h4>
    {hasRpkiCheck ? <div className='border rounded p-3 mt-2'>
      <div className='flex items-center gap-2'><span className='font-semibold'>RPKI</span><StatusBadge status={rpki?.status || 'UNKNOWN'} /></div>
      <p className='mt-2'><strong>Summary:</strong> {rpki?.summary || '-'}</p>
      <p className='mt-1'><strong>Erklärung:</strong> {rpki?.explanation || '-'}</p>
      <p className='mt-1'><strong>Risiko:</strong> {rpki?.risk || '-'}</p>
      <details className='mt-2'>
        <summary>RPKI Rohdaten</summary>
        <pre className='mt-2 text-xs overflow-auto'>{JSON.stringify(rpki?.raw ?? {}, null, 2)}</pre>
      </details>
    </div> : <p className='mt-2'>Für diesen Check-Typ sind keine Einzelprüfungen verfügbar.</p>}

    {rpkiSummary && <div className='mt-4 border rounded p-3'><h4 className='font-semibold'>ASN-RPKI Summary</h4>
      <p className='text-sm mt-1'>geprüft: {checkedPrefixes} / gesehen: {totalPrefixesSeen}</p>
      {limited && <p className='text-sm text-amber-700'>Hinweis: Ergebnis wurde durch das gesetzte Limit begrenzt.</p>}
      <ul className='list-disc pl-5 text-sm'>
        <li>valid: {Number((rpkiSummary as Record<string, unknown>).valid ?? 0)}</li>
        <li>invalid_asn: {Number((rpkiSummary as Record<string, unknown>).invalid_asn ?? 0)}</li>
        <li>invalid_length: {Number((rpkiSummary as Record<string, unknown>).invalid_length ?? 0)}</li>
        <li>unknown: {Number((rpkiSummary as Record<string, unknown>).unknown ?? 0)}</li>
        <li>errors: {Number((rpkiSummary as Record<string, unknown>).errors ?? 0)}</li>
      </ul>
    </div>}

    {sortedResults.length > 0 && <div className='mt-4'><h4 className='font-semibold'>ASN-RPKI Ergebnisse</h4>
      <ul className='mt-2 space-y-2'>
        {sortedResults.map((item, idx) => <li key={`${item.prefix}-${idx}`} className='border rounded p-2'>
          <div className='flex items-center gap-2'><StatusBadge status={item.status || 'UNKNOWN'} /><span className='font-mono text-sm'>{item.prefix}</span></div>
          <p className='text-sm mt-1'>{item.summary || '-'}</p>
        </li>)}
      </ul>
    </div>}

    <button className='mt-4 px-3 py-2 border rounded' onClick={() => navigator.clipboard.writeText(report.markdown)}>Markdown kopieren</button>
    <RawDataPanel data={report.details} />
  </div>
}
