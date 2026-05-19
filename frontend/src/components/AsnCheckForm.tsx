import { useState } from 'react'

import { ApiError, checkAsn, checkAsnRpki } from '../api'
import { ReportView } from './ReportView'
import type { CheckResponse } from '../types'

export function AsnCheckForm() {
  const [asn, setAsn] = useState('')
  const [loading, setLoading] = useState(false)
  const [batchLoading, setBatchLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<CheckResponse | null>(null)
  const [batchResult, setBatchResult] = useState<CheckResponse | null>(null)

  const onSubmit = async () => {
    setError(null)
    setResult(null)
    setBatchResult(null)
    setLoading(true)
    try {
      const response = await checkAsn(asn)
      setResult(response)
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError('Unbekannter Fehler bei der ASN-Prüfung.'))
    } finally { setLoading(false) }
  }

  const onBatchRpki = async () => {
    const sourceAsn = String(result?.details?.resource || asn)
    setError(null)
    setBatchLoading(true)
    try {
      const response = await checkAsnRpki(sourceAsn, 25)
      setBatchResult(response)
    } catch (err) {
      setError(err instanceof ApiError ? err : new ApiError('Unbekannter Fehler bei der ASN-RPKI-Prüfung.'))
    } finally { setBatchLoading(false) }
  }

  const extractedPrefixes = Array.isArray(result?.details?.extracted_prefixes) ? result?.details?.extracted_prefixes : []

  return (
    <div className='p-4 border rounded bg-white'>
      <h2 className='font-bold mb-2'>ASN Check</h2>
      <input className='border p-2 w-full' placeholder='AS3320' value={asn} onChange={e => setAsn(e.target.value)} />
      <button disabled={loading} className='mt-2 px-3 py-2 bg-blue-600 text-white rounded' onClick={onSubmit}>Prüfen</button>
      {loading && <p className='mt-3 text-sm text-slate-700'>Prüfung läuft ...</p>}
      {result && <p className='mt-2 text-sm text-slate-700'>ASN wurde geprüft. Für ASN allein ist RPKI nicht direkt anwendbar.</p>}
      {result && <p className='mt-1 text-sm text-slate-700'>Extrahierte Prefixe: {extractedPrefixes.length}</p>}
      {result && extractedPrefixes.length > 0 && (
        <button disabled={batchLoading} className='mt-2 ml-2 px-3 py-2 bg-indigo-600 text-white rounded' onClick={onBatchRpki}>RPKI für sichtbare Prefixe prüfen</button>
      )}
      {batchLoading && <p className='mt-2 text-sm text-slate-700'>ASN-RPKI-Batchprüfung läuft ...</p>}
      {error && <div className='mt-3 p-3 rounded border border-red-300 bg-red-50 text-red-800'><p className='font-semibold'>Die Prüfung konnte nicht ausgeführt werden.</p><p className='text-sm mt-1'>{error.message}</p></div>}
      {result && <div className='mt-4'><ReportView report={result} /></div>}
      {batchResult && <div className='mt-4'>
        <h3 className='text-md font-bold mb-2'>Batchprüfungsergebnis</h3>
        <ReportView report={batchResult} />
      </div>}
    </div>
  )
}
