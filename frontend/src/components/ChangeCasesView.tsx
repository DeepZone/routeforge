import { useEffect, useState } from 'react'
import { createChangeCase, getChangeCaseReports, listChangeCases, runAsnCheck, updateChangeCase } from '../api'
import type { ChangeCaseItem, UserRole } from '../types'

export function ChangeCasesView({ role }: { role: UserRole }) {
  const [items, setItems] = useState<ChangeCaseItem[]>([])
  const [selected, setSelected] = useState<ChangeCaseItem | null>(null)
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const canEdit = role === 'admin' || role === 'operator'
  const load = async () => { setLoading(true); try { setItems(await listChangeCases()) } finally { setLoading(false) } }
  useEffect(() => { load() }, [])
  useEffect(() => { if (selected) getChangeCaseReports(selected.id).then(setReports).catch(()=>setReports([])) }, [selected])
  return <section className='rf-card p-4 space-y-3'>
    <div className='flex justify-between'><h2 className='text-xl font-semibold'>Change Cases</h2>{canEdit && <button className='rf-btn-secondary' onClick={async()=>{const title=prompt('Title?'); if(!title) return; await createChangeCase({title, description:''}); await load()}}>New Change Case</button>}</div>
    {loading ? <div>Loading…</div> : items.length===0 ? <div className='text-sm text-slate-500'>No change cases yet.</div> : <table className='w-full text-sm'><thead><tr><th>Title</th><th>Status</th><th>Owner</th><th>Created</th><th>Updated</th></tr></thead><tbody>{items.map(i=><tr key={i.id} className='border-t cursor-pointer' onClick={()=>setSelected(i)}><td>{i.title}</td><td>{i.status}</td><td>{i.created_by_user_id ?? '—'}</td><td>{new Date(i.created_at).toLocaleString()}</td><td>{new Date(i.updated_at).toLocaleString()}</td></tr>)}</tbody></table>}
    {selected && <article className='border rounded p-3 space-y-2'><h3 className='font-semibold'>{selected.title}</h3><p>{selected.description || '—'}</p><div>Status: {selected.status}</div>{canEdit && <div className='flex gap-2'><button className='rf-btn-secondary' onClick={async()=>{await updateChangeCase(selected.id,{status:'in_review'}); await load()}}>To Review</button><button className='rf-btn-secondary' onClick={async()=>{await runAsnCheck('AS3320', selected.id); await getChangeCaseReports(selected.id).then(setReports)}}>Run ASN Check</button></div>}<div className='text-sm'>Reports: {reports.length}</div></article>}
  </section>
}
