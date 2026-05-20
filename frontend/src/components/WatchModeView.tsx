import { useEffect, useState } from 'react'
import { createWatchTarget, deleteWatchTarget, getWatchTargetRuns, listWatchTargets, runWatchTarget, updateWatchTarget } from '../api'
import type { UserRole, WatchRun, WatchTarget } from '../types'

export function WatchModeView({ role }: { role: UserRole }) {
  const [targets, setTargets] = useState<WatchTarget[]>([])
  const [selected, setSelected] = useState<WatchTarget | null>(null)
  const [runs, setRuns] = useState<WatchRun[]>([])
  const canEdit = role !== 'viewer'
  const load = () => listWatchTargets().then(setTargets)
  useEffect(() => { load() }, [])
  useEffect(() => { if (selected) getWatchTargetRuns(selected.id).then(setRuns) }, [selected?.id])
  return <section className='rf-card p-4 space-y-3'><h2 className='text-xl font-semibold'>Watch Mode</h2><div className='grid md:grid-cols-2 gap-3'><div>{targets.map(t => <button key={t.id} className='block w-full text-left border rounded p-2' onClick={()=>setSelected(t)}>{t.name} · {t.watch_type} · {t.last_status || 'n/a'}</button>)}</div><div>{selected && <div className='space-y-2'><div>{selected.name}</div>{canEdit && <button className='rf-btn-secondary' onClick={async()=>{await runWatchTarget(selected.id); await load(); const nt=await listWatchTargets(); setSelected(nt.find(x=>x.id===selected.id)||null)}}>Run Now</button>}{canEdit && <button className='rf-btn-secondary' onClick={async()=>{await updateWatchTarget(selected.id,{is_active:!selected.is_active}); await load()}}>Toggle Active</button>}{canEdit && <button className='rf-btn-secondary' onClick={async()=>{await deleteWatchTarget(selected.id); setSelected(null); await load()}}>Delete</button>}<table className='w-full text-xs'><tbody>{runs.map(r=><tr key={r.id}><td>{r.created_at}</td><td>{r.previous_status}</td><td>{r.status}</td><td>{String(r.changed)}</td></tr>)}</tbody></table></div>}</div></div>{canEdit && <button className='rf-btn-primary' onClick={async()=>{await createWatchTarget({name:'New Watch Target',watch_type:'prefix',prefix:'192.0.2.0/24',interval_minutes:60,is_active:true});await load()}}>New Watch Target</button>}</section>
}
