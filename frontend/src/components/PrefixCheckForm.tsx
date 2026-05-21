import { useState } from 'react'
import { ApiError, checkPrefix } from '../api'
import { ReportView } from './ReportView'
import type { CheckResponse } from '../types'

export function PrefixCheckForm() {
  const [prefix, setPrefix] = useState('')
  const [originAs, setOriginAs] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<CheckResponse | null>(null)
  const onSubmit = async () => { setLoading(true); setError(null); try { setResult(await checkPrefix(prefix, originAs || undefined)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) } }
  return <section className='space-y-4'>
    <article className='rf-card p-5 space-y-3'><h3 className='text-lg font-semibold'>Prefix Check</h3><p className='rf-alert border-blue-200 bg-blue-50 text-blue-700'>Provide Origin AS for a complete evaluation.</p><div><label className='mb-1 block text-sm font-medium'>Prefix</label><input className='rf-input' placeholder='193.0.22.0/23' value={prefix} onChange={e => setPrefix(e.target.value)} /></div><div><label className='mb-1 block text-sm font-medium'>Origin AS (optional)</label><input className='rf-input' placeholder='AS3333' value={originAs} onChange={e => setOriginAs(e.target.value)} /></div><button onClick={onSubmit} disabled={loading} className='rf-btn-primary'>Run Prefix Check</button>{loading && <p className='text-sm text-blue-700'>Running check…</p>}{error && <p className='rf-alert border-rose-200 bg-rose-50 text-rose-700'>{error.message}</p>}</article>
    {result && <ReportView report={result} />}
  </section>
}
