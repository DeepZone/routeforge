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
  const rpkiBatch = result?.details?.rpki_batch as { available?: boolean; message?: string; reason_code?: string; prefix_count?: number } | undefined
  const batchAvailable = rpkiBatch?.available ?? extracted.length > 0
  const onSubmit = async () => { setError(null); setLoading(true); try { setResult(await checkAsn(asn)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) } }
  const onBatch = async () => { setError(null); setBatchLoading(true); try { setBatchResult(await checkAsnRpki(asn, 25)) } catch (e) { setError(e as ApiError) } finally { setBatchLoading(false) } }
  return <section className='space-y-4'>
    <article className='rf-card p-5 space-y-3'><h3 className='text-lg font-semibold'>ASN Check</h3><p className='text-sm text-slate-600'>RPKI evaluates prefix-origin pairs, not an ASN in isolation.</p><label className='text-sm font-medium'>ASN</label><input className='rf-input' placeholder='AS3320' value={asn} onChange={e => setAsn(e.target.value)} /><div className='flex gap-2'><button onClick={onSubmit} disabled={loading} className='rf-btn-primary'>Run ASN Check</button>{result && <button onClick={onBatch} disabled={batchLoading || !batchAvailable} className='rf-btn-secondary' title={!batchAvailable ? 'RPKI batch unavailable: no evaluable prefixes found.' : ''}>Run RPKI Batch</button>}</div>{result && <p className='text-sm text-slate-700'>Extracted prefixes: <b>{extracted.length}</b></p>}{result && !batchAvailable && <div className='rf-alert border-amber-200 bg-amber-50 text-amber-800'><p className='font-medium'>RPKI batch unavailable</p><p>{rpkiBatch?.message || 'No evaluable prefixes were found for this ASN.'}</p><p className='text-xs mt-1'>Reason: {rpkiBatch?.reason_code || 'unknown'} · Prefix count: {rpkiBatch?.prefix_count ?? 0}</p></div>}{(loading || batchLoading) && <p className='text-sm text-blue-700'>Running check…</p>}{error && <p className='rf-alert border-rose-200 bg-rose-50 text-rose-700'>{error.message}</p>}</article>
    {result && <ReportView report={result} />}
    {batchResult && <ReportView report={batchResult} />}
  </section>
}
