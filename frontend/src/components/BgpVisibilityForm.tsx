import { useMemo, useState } from 'react'
import { ApiError, runBgpVisibilityCheck } from '../api'
import type { CheckResponse, UserRole } from '../types'
import { StatusBadge } from './StatusBadge'

export function BgpVisibilityForm({ role }: { role: UserRole }) {
  const [prefix, setPrefix] = useState('')
  const [expectedOriginAs, setExpectedOriginAs] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<CheckResponse | null>(null)
  const canRun = role === 'admin' || role === 'operator'
  const details = useMemo(()=> (result?.details || {}) as Record<string, unknown>, [result])

  const onSubmit = async () => {
    if (!canRun) return
    setLoading(true); setError(null)
    try { setResult(await runBgpVisibilityCheck(prefix, expectedOriginAs || undefined)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) }
  }

  return <section className='rf-card p-4 space-y-3'>
    <h3 className='text-lg font-semibold'>BGP Visibility</h3>
    {!canRun && <p className='rf-alert border-amber-200 bg-amber-50 text-amber-800'>Viewer role: Seite ist sichtbar, aber Checks dürfen nicht ausgeführt werden.</p>}
    <input className='rf-input' placeholder='203.0.113.0/24' value={prefix} onChange={e=>setPrefix(e.target.value)} />
    <input className='rf-input' placeholder='Expected Origin AS (optional)' value={expectedOriginAs} onChange={e=>setExpectedOriginAs(e.target.value)} />
    <button className='rf-btn-primary' disabled={loading || !prefix.trim() || !canRun} onClick={onSubmit}>{loading ? 'Checking…' : 'Run BGP Visibility Check'}</button>
    {error && <p className='text-rose-700 text-sm'>{error.message}</p>}
    {result && <div className='space-y-2 text-sm'>
      <div className='flex items-center gap-2'><StatusBadge status={result.status} /><span>{result.summary}</span></div>
      <div><b>Origins:</b> {String((details.origins as string[] | undefined)?.join(', ') || '-')}</div>
      <div><b>Expected Origin Seen:</b> {String(details.expected_origin_seen ?? '-')}</div>
      <div><b>Multiple Origins:</b> {String(details.multiple_origins ?? '-')}</div>
      <div><b>Recommendations:</b><ul>{(result.recommendations||[]).map((r,i)=><li key={i}>- {r}</li>)}</ul></div>
      <details><summary>Details</summary><pre>{JSON.stringify(details, null, 2)}</pre></details>
    </div>}
  </section>
}
