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

  const onSubmit = async () => { setError(null); setLoading(true); try { setResult(await checkAsn(asn)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) } }
  const onBatch = async () => { setError(null); setBatchLoading(true); try { setBatchResult(await checkAsnRpki(asn, 25)) } catch (e) { setError(e as ApiError) } finally { setBatchLoading(false) } }
  const extracted = Array.isArray(result?.details?.extracted_prefixes) ? result?.details?.extracted_prefixes : []

  return <section className='bg-white border rounded-lg p-4'>
    <h2 className='text-xl font-semibold'>ASN Check</h2>
    <p className='text-sm text-slate-600 mt-1'>Eine ASN allein kann nicht RPKI-valid oder invalid sein. RPKI bewertet Prefix-Origin-Paare.</p>
    <input className='border p-2 w-full mt-3 rounded' placeholder='AS3320' value={asn} onChange={e => setAsn(e.target.value)} />
    <button onClick={onSubmit} disabled={loading} className='mt-2 px-3 py-2 bg-blue-700 text-white rounded-md'>ASN prüfen</button>
    {result && <div className='text-sm mt-3 p-3 rounded border bg-slate-50'><p><strong>ASN:</strong> {asn}</p><p><strong>Anzahl extrahierter Prefixe:</strong> {extracted.length}</p><p><strong>Datenquellen/Warnungen:</strong> {JSON.stringify(result.details?.warnings ?? [])}</p>{extracted.length > 0 && <button onClick={onBatch} disabled={batchLoading} className='mt-2 px-3 py-2 bg-indigo-700 text-white rounded-md'>RPKI-Batch für sichtbare Prefixe starten</button>}</div>}
    {(loading || batchLoading) && <p className='mt-2 text-sm'>Ladezustand aktiv ...</p>}
    {error && <p className='mt-2 text-sm text-rose-700'>{error.message}</p>}
    {result && <div className='mt-4'><ReportView report={result} /></div>}
    {batchResult && <div className='mt-4'><ReportView report={batchResult} /></div>}
  </section>
}
