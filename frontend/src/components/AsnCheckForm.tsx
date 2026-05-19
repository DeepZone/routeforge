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
  const extracted = Array.isArray(result?.details?.extracted_prefixes) ? result?.details?.extracted_prefixes : []
  const onSubmit = async () => { setError(null); setLoading(true); try { setResult(await checkAsn(asn)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) } }
  const onBatch = async () => { setError(null); setBatchLoading(true); try { setBatchResult(await checkAsnRpki(asn, 25)) } catch (e) { setError(e as ApiError) } finally { setBatchLoading(false) } }
  return <section className='space-y-4'>
    <article className='rf-card p-5 space-y-3'><h3 className='text-lg font-semibold'>ASN Check</h3><p className='text-sm text-slate-600'>RPKI bewertet Prefix-Origin-Paare, nicht die ASN isoliert.</p><label className='text-sm font-medium'>ASN</label><input className='rf-input' placeholder='AS3320' value={asn} onChange={e => setAsn(e.target.value)} /><div className='flex gap-2'><button onClick={onSubmit} disabled={loading} className='rf-btn-primary'>ASN prüfen</button>{extracted.length > 0 && <button onClick={onBatch} disabled={batchLoading} className='rf-btn-secondary'>RPKI-Batch starten</button>}</div>{(loading || batchLoading) && <p className='text-sm text-blue-700'>Prüfung läuft…</p>}{error && <p className='rf-alert border-rose-200 bg-rose-50 text-rose-700'>{error.message}</p>}</article>
    {result && <ReportView report={result} />}
    {batchResult && <ReportView report={batchResult} />}
  </section>
}
