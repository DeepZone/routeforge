import type { CheckResponse } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'

export function ReportView({ report }: { report: CheckResponse }) {
  const recs = report.recommendations ?? []
  const rpki = report.checks?.rpki

  return <div className='mt-6 p-4 border rounded bg-white'>
    <div className='flex gap-2 items-center'><h3 className='text-lg font-bold'>Ergebnis</h3><StatusBadge status={report.status} /></div>

    <p className='mt-3 font-semibold'>{report.summary || 'Keine Kurzfassung verfügbar.'}</p>
    <p className='mt-2'><strong>Erklärung:</strong> {report.explanation || 'Keine Erklärung verfügbar.'}</p>
    <p className='mt-2'><strong>Risiko:</strong> {report.risk || 'Keine Risikobewertung verfügbar.'}</p>

    <h4 className='font-semibold mt-4'>Empfehlungen</h4>
    {recs.length > 0 ? <ul className='list-disc pl-5'>{recs.map((r, i) => <li key={`${r}-${i}`}>{r}</li>)}</ul> : <p>Keine Empfehlungen verfügbar.</p>}

    <h4 className='font-semibold mt-4'>Einzelprüfungen</h4>
    <div className='border rounded p-3 mt-2'>
      <div className='flex items-center gap-2'><span className='font-semibold'>RPKI</span><StatusBadge status={rpki?.status || 'UNKNOWN'} /></div>
      <p className='mt-2'><strong>Summary:</strong> {rpki?.summary || '-'}</p>
      <p className='mt-1'><strong>Erklärung:</strong> {rpki?.explanation || '-'}</p>
      <p className='mt-1'><strong>Risiko:</strong> {rpki?.risk || '-'}</p>
      <details className='mt-2'>
        <summary>RPKI Rohdaten</summary>
        <pre className='mt-2 text-xs overflow-auto'>{JSON.stringify(rpki?.raw ?? {}, null, 2)}</pre>
      </details>
    </div>

    <button className='mt-4 px-3 py-2 border rounded' onClick={() => navigator.clipboard.writeText(report.markdown)}>Markdown kopieren</button>
    <RawDataPanel data={report.details} />
  </div>
}
