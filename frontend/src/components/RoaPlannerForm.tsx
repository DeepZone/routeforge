import { useState } from 'react'
import { ApiError, runRoaPreflightCheck } from '../api'
import type { CheckResponse, UserRole } from '../types'
import { ReportView } from './ReportView'

export function RoaPlannerForm({ role }: { role: UserRole }) {
  const [prefix, setPrefix] = useState('')
  const [originAs, setOriginAs] = useState('')
  const [maxLength, setMaxLength] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<CheckResponse | null>(null)
  const canRun = role === 'admin' || role === 'operator'

  const onSubmit = async () => {
    setLoading(true); setError(null)
    try { setResult(await runRoaPreflightCheck(prefix, originAs, maxLength ? Number(maxLength) : undefined)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) }
  }

  return <section className='space-y-4'><article className='rf-card p-5 space-y-3'>
    <h3 className='text-lg font-semibold'>ROA Planner / ROA Preflight</h3>
    <p className='rf-alert border-blue-200 bg-blue-50 text-blue-700'>Read-only: RouteForge erstellt, ändert oder löscht keine ROAs.</p>
    <div><label className='mb-1 block text-sm font-medium'>Prefix</label><input className='rf-input' value={prefix} onChange={e => setPrefix(e.target.value)} placeholder='203.0.113.0/24' /></div>
    <div><label className='mb-1 block text-sm font-medium'>Origin AS</label><input className='rf-input' value={originAs} onChange={e => setOriginAs(e.target.value)} placeholder='AS64500' /></div>
    <div><label className='mb-1 block text-sm font-medium'>Max Length (optional)</label><input className='rf-input' value={maxLength} onChange={e => setMaxLength(e.target.value)} placeholder='24' /></div>
    <button onClick={onSubmit} disabled={loading || !canRun} className='rf-btn-primary'>Run ROA Preflight</button>
    {!canRun && <p className='text-sm text-amber-700'>Viewer können Checks nicht ausführen.</p>}
    {loading && <p className='text-sm text-blue-700'>Prüfung läuft…</p>}
    {error && <p className='rf-alert border-rose-200 bg-rose-50 text-rose-700'>{error.message}</p>}
  </article>{result && <ReportView report={result} />}</section>
}
