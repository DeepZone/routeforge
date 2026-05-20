import { useState } from 'react'
import { ApiError, checkPreflight } from '../api'
import { ReportView } from './ReportView'
import type { CheckResponse } from '../types'

export function PreflightCheckForm() {
  const [prefix, setPrefix] = useState('')
  const [plannedOriginAs, setPlannedOriginAs] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<CheckResponse | null>(null)

  const onSubmit = async () => {
    setLoading(true); setError(null)
    try { setResult(await checkPreflight(prefix, plannedOriginAs)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) }
  }

  return <section className='space-y-4'>
    <article className='rf-card p-5 space-y-3'>
      <h3 className='text-lg font-semibold'>Preflight Check</h3>
      <p className='rf-alert border-blue-200 bg-blue-50 text-blue-700'>This is a read-only preflight check. RouteForge does not create ROAs, update RIPE DB objects or deploy router configuration.</p>
      <div><label className='mb-1 block text-sm font-medium'>Prefix</label><input className='rf-input' placeholder='203.0.113.0/24' value={prefix} onChange={e => setPrefix(e.target.value)} /></div>
      <div><label className='mb-1 block text-sm font-medium'>Planned Origin-AS</label><input className='rf-input' placeholder='AS64500' value={plannedOriginAs} onChange={e => setPlannedOriginAs(e.target.value)} /></div>
      <button onClick={onSubmit} disabled={loading} className='rf-btn-primary'>Run Preflight Check</button>
      {loading && <p className='text-sm text-blue-700'>Prüfung läuft…</p>}
      {error && <p className='rf-alert border-rose-200 bg-rose-50 text-rose-700'>{error.message}</p>}
    </article>
    {result && <ReportView report={result} />}
  </section>
}
