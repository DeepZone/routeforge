import { useEffect, useMemo, useState } from 'react'
import { createWatchTarget, deleteWatchTarget, getWatchTargetRuns, listWatchTargets, runDueWatchTargets, runWatchTarget, updateWatchTarget } from '../api'
import type { UserRole, WatchRun, WatchTarget } from '../types'

type WatchType = 'asn' | 'prefix' | 'bgp_visibility' | 'roa_preflight'
type WatchTargetForm = {
  name: string
  watch_type: WatchType
  prefix: string
  asn: string
  origin_as: string
  expected_origin_as: string
  max_length: string
  interval_minutes: string
  is_active: boolean
  change_case_id: string
}

const emptyForm = (): WatchTargetForm => ({
  name: '', watch_type: 'prefix', prefix: '', asn: '', origin_as: '', expected_origin_as: '', max_length: '', interval_minutes: '60', is_active: true, change_case_id: ''
})

const parseOptionalNumber = (value: string): number | undefined => {
  if (!value.trim()) return undefined
  return Number(value)
}

const buildPayload = (form: WatchTargetForm) => ({
  name: form.name.trim(),
  watch_type: form.watch_type,
  prefix: form.prefix.trim() || undefined,
  asn: form.asn.trim() || undefined,
  origin_as: form.origin_as.trim() || undefined,
  expected_origin_as: form.expected_origin_as.trim() || undefined,
  max_length: parseOptionalNumber(form.max_length),
  interval_minutes: Number(form.interval_minutes),
  is_active: form.is_active,
  change_case_id: parseOptionalNumber(form.change_case_id)
})

export function WatchModeView({ role }: { role: UserRole }) {
  const [targets, setTargets] = useState<WatchTarget[]>([])
  const [selected, setSelected] = useState<WatchTarget | null>(null)
  const [runs, setRuns] = useState<WatchRun[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState<WatchTargetForm>(emptyForm)
  const [editForm, setEditForm] = useState<WatchTargetForm | null>(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [runDueSummary, setRunDueSummary] = useState<string | null>(null)

  const canEdit = role !== 'viewer'

  const loadTargets = async (selectedId?: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await listWatchTargets()
      setTargets(data)
      const nextId = selectedId ?? selected?.id
      if (nextId) setSelected(data.find((t) => t.id === nextId) ?? null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load watch targets')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadTargets() }, [])
  useEffect(() => {
    if (!selected) return
    getWatchTargetRuns(selected.id).then((data)=>setRuns([...data].sort((a,b)=>new Date(b.created_at).getTime()-new Date(a.created_at).getTime()))).catch((e) => setError(e instanceof Error ? e.message : 'Failed to load runs'))
  }, [selected?.id])

  const typeHints = useMemo(() => ({
    asn: ['asn'],
    prefix: ['prefix', 'origin_as'],
    bgp_visibility: ['prefix', 'expected_origin_as'],
    roa_preflight: ['prefix', 'origin_as', 'max_length']
  }), [])

  const renderCommonFields = (form: WatchTargetForm, setForm: (next: WatchTargetForm) => void) => (
    <>
      <label className='block text-sm'>Name<input className='w-full border rounded p-2' value={form.name} onChange={(e)=>setForm({ ...form, name: e.target.value })} /></label>
      <label className='block text-sm'>Watch Type<select className='w-full border rounded p-2' value={form.watch_type} onChange={(e)=>setForm({ ...form, watch_type: e.target.value as WatchType })}><option value='asn'>asn</option><option value='prefix'>prefix</option><option value='bgp_visibility'>bgp_visibility</option><option value='roa_preflight'>roa_preflight</option></select></label>
      {(form.watch_type === 'prefix' || form.watch_type === 'bgp_visibility' || form.watch_type === 'roa_preflight') && <label className='block text-sm'>Prefix<input className='w-full border rounded p-2' value={form.prefix} onChange={(e)=>setForm({ ...form, prefix: e.target.value })} /></label>}
      {form.watch_type === 'asn' && <label className='block text-sm'>ASN<input className='w-full border rounded p-2' value={form.asn} onChange={(e)=>setForm({ ...form, asn: e.target.value })} /></label>}
      {(form.watch_type === 'prefix' || form.watch_type === 'roa_preflight') && <label className='block text-sm'>Origin AS<input className='w-full border rounded p-2' value={form.origin_as} onChange={(e)=>setForm({ ...form, origin_as: e.target.value })} /></label>}
      {form.watch_type === 'bgp_visibility' && <label className='block text-sm'>Expected Origin AS<input className='w-full border rounded p-2' value={form.expected_origin_as} onChange={(e)=>setForm({ ...form, expected_origin_as: e.target.value })} /></label>}
      {form.watch_type === 'roa_preflight' && <label className='block text-sm'>Max Length<input type='number' className='w-full border rounded p-2' value={form.max_length} onChange={(e)=>setForm({ ...form, max_length: e.target.value })} /></label>}
      <label className='block text-sm'>Interval Minutes<input type='number' min={1} className='w-full border rounded p-2' value={form.interval_minutes} onChange={(e)=>setForm({ ...form, interval_minutes: e.target.value })} /></label>
      <label className='block text-sm'>Change Case ID (optional)<input type='number' className='w-full border rounded p-2' value={form.change_case_id} onChange={(e)=>setForm({ ...form, change_case_id: e.target.value })} /></label>
      <label className='inline-flex items-center gap-2 text-sm'><input type='checkbox' checked={form.is_active} onChange={(e)=>setForm({ ...form, is_active: e.target.checked })} /> Active</label>
      <p className='text-xs text-gray-500'>Type fields: {typeHints[form.watch_type].join(', ')}</p>
    </>
  )

  const startEdit = () => {
    if (!selected) return
    setEditForm({
      name: selected.name,
      watch_type: selected.watch_type as WatchType,
      prefix: selected.prefix ?? '',
      asn: selected.asn ?? '',
      origin_as: selected.origin_as ?? '',
      expected_origin_as: selected.expected_origin_as ?? '',
      max_length: selected.max_length != null ? String(selected.max_length) : '',
      interval_minutes: String(selected.interval_minutes),
      is_active: selected.is_active,
      change_case_id: selected.change_case_id != null ? String(selected.change_case_id) : ''
    })
  }

  return <section className='rf-card p-4 space-y-3'>
    <h2 className='text-xl font-semibold'>Watch Mode</h2>
    {!canEdit && <div className='rounded border border-amber-300 bg-amber-50 p-2 text-sm'>Viewer role: read-only access. Create/Edit/Delete/Run actions are disabled.</div>}
    {canEdit && <button className='rf-btn-secondary' disabled={submitting} onClick={async()=>{setSubmitting(true); setError(null); setRunDueSummary(null); try { const r=await runDueWatchTargets(); setRunDueSummary(`Executed: ${r.executed}, Changed: ${r.changed}, Failed: ${r.failed}`); await loadTargets(selected?.id) } catch (e) { setError(e instanceof Error ? e.message : 'Run due failed') } finally { setSubmitting(false) }}}>Run Due Watches</button>}
    {runDueSummary && <div className='text-sm text-emerald-700'>{runDueSummary}</div>}
    {loading && <div className='text-sm'>Loading targets…</div>}
    {error && <div className='text-sm text-red-700'>{error}</div>}
    {success && <div className='text-sm text-green-700'>{success}</div>}

    <div className='grid md:grid-cols-2 gap-3'>
      <div className='space-y-2'>
        {targets.length === 0 && <div className='rounded border border-dashed p-3 text-sm text-slate-500'>No watch targets yet. Create one to start scheduled monitoring.</div>}
        {targets.map(t => <button key={t.id} className='block w-full text-left border rounded p-2' onClick={()=>setSelected(t)}>{t.name} · {t.watch_type} · {t.last_status || 'n/a'}</button>)}
      </div>
      <div>{selected && <div className='space-y-2 border rounded p-3'>
        <h3 className='font-semibold'>{selected.name}</h3>
        <div className='text-sm'>Watch Type: {selected.watch_type}</div>
        <div className='text-sm'>Resource: {selected.asn ?? selected.prefix ?? 'n/a'}</div>
        <div className='text-sm'>Interval: {selected.interval_minutes} min</div>
        <div className='text-sm'>Active: {String(selected.is_active)}</div>
        <div className='text-sm'>Last Status: {selected.last_status ?? 'n/a'}</div>
        <div className='text-sm'>Last Run: {selected.last_run_at ?? 'n/a'}</div>
        <div className='text-sm'>Next Run: {selected.next_run_at ?? 'n/a'}</div>
        <div className='text-sm'>Prefix: {selected.prefix ?? 'n/a'} | ASN: {selected.asn ?? 'n/a'} | Origin AS: {selected.origin_as ?? 'n/a'} | Expected Origin AS: {selected.expected_origin_as ?? 'n/a'} | Max Length: {selected.max_length ?? 'n/a'}</div>

        {canEdit && <div className='flex gap-2 flex-wrap'>
          <button className='rf-btn-secondary' disabled={submitting} onClick={async()=>{ setSubmitting(true); setError(null); await runWatchTarget(selected.id); await loadTargets(selected.id); const nt = await listWatchTargets(); setSelected(nt.find(x=>x.id===selected.id)||null); setSuccess('Run started successfully.'); setSubmitting(false) }}>Run Now</button>
          <button className='rf-btn-secondary' onClick={startEdit}>Edit</button>
          <button className='rf-btn-secondary' disabled={submitting} onClick={async()=>{ setSubmitting(true); await deleteWatchTarget(selected.id); setSelected(null); setRuns([]); await loadTargets(); setSuccess('Watch target deleted.'); setSubmitting(false) }}>Delete</button>
        </div>}

        {editForm && canEdit && <div className='space-y-2 border-t pt-3'>
          <h4 className='font-medium'>Edit Watch Target</h4>
          {renderCommonFields(editForm, setEditForm)}
          <div className='flex gap-2'>
            <button className='rf-btn-primary' disabled={submitting} onClick={async()=>{ if(!selected) return; setSubmitting(true); setError(null); try { await updateWatchTarget(selected.id, buildPayload(editForm)); await loadTargets(selected.id); setSuccess('Watch target updated.'); setEditForm(null) } catch (e) { setError(e instanceof Error ? e.message : 'Update failed') } finally { setSubmitting(false) } }}>Save</button>
            <button className='rf-btn-secondary' disabled={submitting} onClick={()=>setEditForm(null)}>Cancel</button>
          </div>
        </div>}

        <h4 className='font-medium pt-2'>Runs History</h4>
        {runs.length === 0 ? <div className='text-xs text-slate-500'>No runs yet.</div> : <table className='w-full text-xs'><thead><tr><th>created_at</th><th>previous_status</th><th>status</th><th>changed</th><th>summary</th><th>report_id</th></tr></thead><tbody>{runs.map(r=><tr key={r.id} className={r.changed ? 'bg-amber-50' : ''}><td>{r.created_at}</td><td>{r.previous_status ?? 'n/a'}</td><td>{r.status}</td><td>{String(r.changed)}</td><td>{r.summary}</td><td>{r.report_id ? <a className='text-blue-700 underline' href={`/api/reports/${r.report_id}/summary`} target='_blank' rel='noreferrer'>{r.report_id}</a> : 'n/a'}</td></tr>)}</tbody></table>}
      </div>}</div>
    </div>

    {canEdit && <div className='border rounded p-3 space-y-2'>
      <button className='rf-btn-secondary' onClick={()=>{setShowCreate(!showCreate); setSuccess(null); setError(null)}}>{showCreate ? 'Hide Create Form' : 'New Watch Target'}</button>
      {showCreate && <div className='space-y-2'>
        <h3 className='font-medium'>Create Watch Target</h3>
        {renderCommonFields(createForm, setCreateForm)}
        <div className='flex gap-2'>
          <button className='rf-btn-primary' disabled={submitting} onClick={async()=>{ setSubmitting(true); setError(null); try { const created=await createWatchTarget(buildPayload(createForm)); await loadTargets(created.id); setSelected(created); setCreateForm(emptyForm()); setShowCreate(false); setSuccess('Watch target created.') } catch (e) { setError(e instanceof Error ? e.message : 'Create failed') } finally { setSubmitting(false) } }}>Create</button>
          <button className='rf-btn-secondary' disabled={submitting} onClick={()=>{ setCreateForm(emptyForm()); setShowCreate(false) }}>Cancel</button>
        </div>
      </div>}
    </div>}
  </section>
}
