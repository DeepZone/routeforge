import { useEffect, useState } from 'react'
import { getAuditLog } from '../api'
import type { AuditLogEntry } from '../types'

export function AuditLogView() {
  const [items, setItems] = useState<AuditLogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [action, setAction] = useState('')
  const [targetType, setTargetType] = useState('')

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
    <div className='flex gap-2'>
      <input className='rf-input' placeholder='Filter action' value={action} onChange={(e)=>setAction(e.target.value)} />
      <input className='rf-input' placeholder='Filter target type' value={targetType} onChange={(e)=>setTargetType(e.target.value)} />
    </div>
    {loading && <div className='text-sm text-slate-500'>Loading audit log…</div>}
    {error && <div className='text-sm text-rose-700'>{error}</div>}
    {!loading && !error && items.length === 0 && <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>No audit events yet.</div>}
    {!loading && !error && items.length > 0 && <div className='overflow-x-auto'><table className='w-full text-xs'><thead><tr><th>Time</th><th>User</th><th>Action</th><th>Target</th><th>IP</th><th>User Agent</th><th>Details</th></tr></thead><tbody>{items.map((a)=><tr key={a.id}><td>{a.created_at}</td><td>{a.username || a.user_id || '-'}</td><td>{a.action}</td><td>{a.target_type || '-'}:{a.target_id || '-'}</td><td>{a.ip_address || '-'}</td><td>{a.user_agent || '-'}</td><td><pre className='whitespace-pre-wrap'>{JSON.stringify(a.details_json || {}, null, 2)}</pre></td></tr>)}</tbody></table></div>}
  </section>
}
