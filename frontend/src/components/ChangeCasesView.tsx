import { useEffect, useState } from 'react'
import { ApiError, createChangeCase, deleteChangeCase, getChangeCaseReports, getReportHtml, getReportMarkdown, getReportSummary, listChangeCases, runAsnCheck, runBgpVisibilityCheck, runChangeCasePostChangeVerification, runChangeCasePreflight, runPrefixCheck, runPreflightCheck, runRoaPreflightCheck, updateChangeCase } from '../api'
import type { ChangeCaseItem, UserRole } from '../types'
import { StatusBadge } from './StatusBadge'

type ChangeCaseReport = { report_id:number; check_id:number; check_type:string; summary:string; status:string; created_at:string }

const statusActions: Record<string, Array<{label:string; to:string}>> = {
  draft: [{ label: 'To Review', to: 'in_review' }, { label: 'Close', to: 'closed' }],
  in_review: [{ label: 'Approve', to: 'approved' }, { label: 'Back to Draft', to: 'draft' }, { label: 'Close', to: 'closed' }],
  approved: [{ label: 'Back to Review', to: 'in_review' }, { label: 'Close', to: 'closed' }],
  closed: []
}

export function ChangeCasesView({ role }: { role: UserRole }) {
  const canEdit = role === 'admin' || role === 'operator'
  const [items, setItems] = useState<ChangeCaseItem[]>([])
  const [selected, setSelected] = useState<ChangeCaseItem | null>(null)
  const [reports, setReports] = useState<ChangeCaseReport[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [editing, setEditing] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [asn, setAsn] = useState('')
  const [prefix, setPrefix] = useState('')
  const [originAs, setOriginAs] = useState('')
  const [preflightPrefix, setPreflightPrefix] = useState('')
  const [plannedOriginAs, setPlannedOriginAs] = useState('')
  const [bgpPrefix, setBgpPrefix] = useState('')
  const [bgpExpectedOriginAs, setBgpExpectedOriginAs] = useState('')
  const [roaPrefix, setRoaPrefix] = useState('')
  const [roaOriginAs, setRoaOriginAs] = useState('')
  const [roaMaxLength, setRoaMaxLength] = useState('')

  const load = async () => { setLoading(true); setError(null); try { const next = await listChangeCases(); setItems(next); if (selected) { const found = next.find(i => i.id === selected.id) || null; setSelected(found) } } catch (e) { setError((e as Error).message) } finally { setLoading(false) } }
  const loadReports = async (id: number) => { try { setReports(await getChangeCaseReports(id)) } catch { setReports([]) } }

  useEffect(() => { load() }, [])
  useEffect(() => { if (selected) { setEditTitle(selected.title); setEditDescription(selected.description || ''); loadReports(selected.id) } else { setReports([]) } }, [selected?.id])

  const runAction = async (work:()=>Promise<void>, ok:string) => {
    setError(null); setSuccess(null)
    try { await work(); setSuccess(ok) } catch (e) { setError((e as Error).message) }
  }

  return <section className='rf-card p-4 space-y-3'>
    <div className='flex justify-between items-center'><h2 className='text-xl font-semibold'>Change Cases</h2>{canEdit && <button className='rf-btn-secondary' onClick={()=>setCreating(v=>!v)}>{creating ? 'Cancel' : 'New Change Case'}</button>}</div>
    {error && <p className='rf-alert border-rose-200 bg-rose-50 text-rose-700'>{error}</p>}
    {success && <p className='rf-alert border-emerald-200 bg-emerald-50 text-emerald-700'>{success}</p>}

    {canEdit && creating && <article className='border rounded p-3 space-y-2'>
      <h3 className='font-semibold'>Create Change Case</h3>
      <input className='rf-input' placeholder='Title' value={newTitle} onChange={e=>setNewTitle(e.target.value)} />
      <textarea className='rf-input min-h-20' placeholder='Description' value={newDescription} onChange={e=>setNewDescription(e.target.value)} />
      <div className='flex gap-2'>
        <button className='rf-btn-primary' onClick={()=>runAction(async()=>{await createChangeCase({title:newTitle, description:newDescription}); setNewTitle(''); setNewDescription(''); setCreating(false); await load()}, 'Change Case created.')} disabled={loading || !newTitle.trim()}>Create</button>
        <button className='rf-btn-secondary' onClick={()=>setCreating(false)}>Cancel</button>
      </div>
    </article>}

    {loading ? <div className='text-sm text-slate-500'>Loading change cases…</div> : items.length===0 ? <div className='rounded border border-dashed p-3 text-sm text-slate-500'>No change cases yet.</div> : <table className='w-full text-sm'><thead><tr><th>Title</th><th>Status</th><th>Owner</th><th>Created</th><th>Updated</th></tr></thead><tbody>{items.map(i=><tr key={i.id} className='border-t cursor-pointer' onClick={()=>setSelected(i)}><td>{i.title}</td><td><StatusBadge status={i.status === 'approved' ? 'OK' : i.status === 'in_review' ? 'WARNING' : i.status === 'closed' ? 'UNKNOWN' : 'UNKNOWN'} /></td><td>{i.created_by_user_id ?? '—'}</td><td>{new Date(i.created_at).toLocaleString()}</td><td>{new Date(i.updated_at).toLocaleString()}</td></tr>)}</tbody></table>}

    {selected && <article className='border rounded p-3 space-y-3'>
      <div className='flex justify-between items-center'>
        <div>
          <h3 className='font-semibold'>{selected.title}</h3>
          <span className='inline-block text-xs px-2 py-1 rounded bg-slate-100'>{selected.status}</span>
        </div>
        {canEdit && <button className='rf-btn-secondary' onClick={()=>setEditing(v=>!v)}>{editing ? 'Cancel' : 'Edit'}</button>}
      </div>
      <p>{selected.description || '—'}</p>
      <div className='rounded border bg-slate-50 p-3 text-sm space-y-1'>
        <div><b>Preflight Decision:</b> {selected.decision || 'UNKNOWN'}</div>
        <div><b>Risk Summary:</b> {selected.risk_summary || 'Not available yet.'}</div>
        <div><b>Post-Change Verification:</b> {selected.post_change_status || 'Not run yet.'}</div>
        <div><b>Required Actions:</b> {(selected.required_actions && selected.required_actions.length > 0) ? selected.required_actions.join(' · ') : 'None recorded.'}</div>
      </div>

      {canEdit && editing && <div className='space-y-2'>
        <input className='rf-input' value={editTitle} onChange={e=>setEditTitle(e.target.value)} />
        <textarea className='rf-input min-h-20' value={editDescription} onChange={e=>setEditDescription(e.target.value)} />
        <div className='flex gap-2'><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await updateChangeCase(selected.id,{title:editTitle,description:editDescription}); setEditing(false); await load();}, 'Change Case updated.')}>Save</button><button className='rf-btn-secondary' onClick={()=>setEditing(false)}>Cancel</button></div>
        <div className='space-y-2'><h4 className='font-medium'>Run ROA Preflight</h4><input className='rf-input' placeholder='203.0.113.0/24' value={roaPrefix} onChange={e=>setRoaPrefix(e.target.value)} /><input className='rf-input' placeholder='Origin AS' value={roaOriginAs} onChange={e=>setRoaOriginAs(e.target.value)} /><input className='rf-input' placeholder='Max Length (optional)' value={roaMaxLength} onChange={e=>setRoaMaxLength(e.target.value)} /><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runRoaPreflightCheck(roaPrefix, roaOriginAs, roaMaxLength ? Number(roaMaxLength) : undefined, selected.id); await loadReports(selected.id)}, 'ROA preflight check started.')}>Run ROA Preflight</button></div>
      </div>}

      {canEdit && <div className='flex flex-wrap gap-2'>
        <button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runChangeCasePreflight(selected.id); await load();}, 'Change case preflight completed.')}>Run Case Preflight</button>
        <button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runChangeCasePostChangeVerification(selected.id); await load();}, 'Post-change verification completed.')}>Run Post-Change Verification</button>
        {(statusActions[selected.status] || []).map((action)=><button key={action.to} className='rf-btn-secondary' onClick={()=>runAction(async()=>{await updateChangeCase(selected.id,{status:action.to}); await load();}, `Status changed to ${action.to}.`)}>{action.label}</button>)}
        {selected.status === 'closed' && <p className='text-sm text-slate-500'>Case is closed (read-only workflow state).</p>}
      </div>}

      {canEdit && <div className='grid md:grid-cols-3 gap-3 border-t pt-3'>
        <div className='space-y-2'><h4 className='font-medium'>Run ASN Check</h4><input className='rf-input' placeholder='AS3320' value={asn} onChange={e=>setAsn(e.target.value)} /><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runAsnCheck(asn, selected.id); await loadReports(selected.id)}, 'ASN check started.')}>Run ASN Check</button></div>
        <div className='space-y-2'><h4 className='font-medium'>Run Prefix Check</h4><input className='rf-input' placeholder='203.0.113.0/24' value={prefix} onChange={e=>setPrefix(e.target.value)} /><input className='rf-input' placeholder='Origin AS (optional)' value={originAs} onChange={e=>setOriginAs(e.target.value)} /><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runPrefixCheck(prefix, originAs || undefined, selected.id); await loadReports(selected.id)}, 'Prefix check started.')}>Run Prefix Check</button></div>
        <div className='space-y-2'><h4 className='font-medium'>Run BGP Visibility Check</h4><input className='rf-input' placeholder='203.0.113.0/24' value={bgpPrefix} onChange={e=>setBgpPrefix(e.target.value)} /><input className='rf-input' placeholder='Expected Origin AS (optional)' value={bgpExpectedOriginAs} onChange={e=>setBgpExpectedOriginAs(e.target.value)} /><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runBgpVisibilityCheck(bgpPrefix, bgpExpectedOriginAs || undefined, selected.id); await loadReports(selected.id)}, 'BGP visibility check started.')}>Run BGP Visibility Check</button></div>
        <div className='space-y-2'><h4 className='font-medium'>Run Preflight Check</h4><input className='rf-input' placeholder='203.0.113.0/24' value={preflightPrefix} onChange={e=>setPreflightPrefix(e.target.value)} /><input className='rf-input' placeholder='Planned Origin AS' value={plannedOriginAs} onChange={e=>setPlannedOriginAs(e.target.value)} /><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runPreflightCheck(preflightPrefix, plannedOriginAs, selected.id); await loadReports(selected.id)}, 'Preflight check started.')}>Run Preflight Check</button></div>
        <div className='space-y-2'><h4 className='font-medium'>Run ROA Preflight</h4><input className='rf-input' placeholder='203.0.113.0/24' value={roaPrefix} onChange={e=>setRoaPrefix(e.target.value)} /><input className='rf-input' placeholder='Origin AS' value={roaOriginAs} onChange={e=>setRoaOriginAs(e.target.value)} /><input className='rf-input' placeholder='Max Length (optional)' value={roaMaxLength} onChange={e=>setRoaMaxLength(e.target.value)} /><button className='rf-btn-primary' onClick={()=>runAction(async()=>{await runRoaPreflightCheck(roaPrefix, roaOriginAs, roaMaxLength ? Number(roaMaxLength) : undefined, selected.id); await loadReports(selected.id)}, 'ROA preflight check started.')}>Run ROA Preflight</button></div>
      </div>}

      <div className='border-t pt-3'>
        <h4 className='font-medium mb-2'>Reports</h4>
        {reports.length === 0 ? <p className='text-sm text-slate-500'>No reports yet.</p> : <table className='w-full text-sm'><thead><tr><th>Type</th><th>Status</th><th>Summary</th><th>Created</th><th>Open</th></tr></thead><tbody>{reports.map(r=><tr key={r.report_id} className='border-t'><td>{r.check_type}</td><td>{r.status}</td><td>{r.summary}</td><td>{new Date(r.created_at).toLocaleString()}</td><td className='space-x-1'><button className='rf-btn-secondary' onClick={()=>runAction(async()=>{await getReportSummary(r.report_id)}, 'Summary loaded.')}>Summary</button><button className='rf-btn-secondary' onClick={()=>runAction(async()=>{await getReportMarkdown(r.report_id)}, 'Markdown loaded.')}>Markdown</button><button className='rf-btn-secondary' onClick={()=>runAction(async()=>{await getReportHtml(r.report_id)}, 'HTML loaded.')}>HTML</button></td></tr>)}</tbody></table>}
      </div>

      {canEdit && <div className='border-t pt-3'>
        <button className='rf-btn-secondary' onClick={()=>runAction(async()=>{await deleteChangeCase(selected.id); setSelected(null); await load()}, 'Change case deleted.')}>Delete Change Case</button>
      </div>}
    </article>}
  </section>
}
