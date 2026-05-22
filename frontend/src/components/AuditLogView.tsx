import { useEffect, useState } from 'react'
import { getAuditLog } from '../api'
import type { AuditLogEntry } from '../types'

export function AuditLogView() {
  const [items, setItems] = useState<AuditLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [action, setAction] = useState('')
  const [targetType, setTargetType] = useState('')
  const hasFilters = action.trim().length > 0 || targetType.trim().length > 0

  useEffect(() => {
    const run = async () => {
      setLoading(true); setError('')
      try {
        const payload = await getAuditLog({ action: action || undefined, target_type: targetType || undefined, limit: 200 })
        setItems(payload.items || [])
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Audit log could not be loaded')
      } finally { setLoading(false) }
    }
    run()
  }, [action, targetType])

  return <section className='rf-card p-4 space-y-3'>
    <h2 className='text-xl font-semibold'>Audit Log</h2>
    <div className='flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 p-2'>
      <input className='rf-input w-48' placeholder='Filter action' value={action} onChange={(e)=>setAction(e.target.value)} />
      <input className='rf-input w-56' placeholder='Filter target type' value={targetType} onChange={(e)=>setTargetType(e.target.value)} />
      <button className='rf-btn-secondary' onClick={() => { setAction(''); setTargetType('') }} disabled={!hasFilters}>Clear Filters</button>
    </div>
    {loading && <div className='text-sm text-slate-500'>Loading audit log…</div>}
    {error && <div className='text-sm text-rose-700'>{error}</div>}
    {!loading && !error && items.length === 0 && <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>No audit entries found.</div>}
    {!loading && !error && items.length > 0 && <div className='overflow-x-auto'><table className='w-full text-xs'><thead className='text-left text-slate-600'><tr><th className='pb-2'>Time</th><th className='pb-2'>User</th><th className='pb-2'>Action</th><th className='pb-2'>Target</th><th className='pb-2'>IP</th><th className='pb-2'>Details</th></tr></thead><tbody>{items.map((a) => { const target = a.target_type && a.target_id ? `${a.target_type} · ${a.target_id}` : a.target_type || a.target_id || '-'; const detailsPayload = { ...(a.details_json || {}), ...(a.user_agent ? { user_agent: a.user_agent } : {}) }; return <tr key={a.id} className='border-t align-top hover:bg-slate-50'><td className='py-2 pr-3'>{a.created_at}</td><td className='py-2 pr-3'>{a.username || a.user_id || '-'}</td><td className='py-2 pr-3'><span className='rounded-full border border-slate-300 bg-slate-100 px-2 py-1 font-mono text-[11px] text-slate-700'>{a.action}</span></td><td className='py-2 pr-3'>{target}</td><td className='py-2 pr-3'>{a.ip_address || '-'}</td><td className='py-2'><details><summary className='cursor-pointer text-blue-700 hover:text-blue-900'>View</summary><pre className='mt-2 max-w-md whitespace-pre-wrap rounded-lg bg-slate-50 p-2 text-xs text-slate-600'>{JSON.stringify(detailsPayload, null, 2)}</pre></details></td></tr>})}</tbody></table></div>}
  </section>
}
