import { useEffect, useState } from 'react'
import { ApiError, createUser, listUsers, updateUser } from '../api'
import type { User, UserRole } from '../types'

const ROLES: UserRole[] = ['admin', 'operator', 'viewer']
const formatRole = (role: UserRole) => role.charAt(0).toUpperCase() + role.slice(1)

export function UsersView() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [createForm, setCreateForm] = useState({ username: '', email: '', password: '', role: 'viewer' as UserRole })

  const load = async () => {
    setLoading(true)
    setError('')
    try { setUsers(await listUsers()) } catch (e: unknown) { setError(e instanceof Error ? e.message : 'Failed to load users') } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const onCreate = async () => {
    if (!createForm.username.trim() || !createForm.password) { setError('Username and password are required.'); return }
    setError(''); setSuccess('')
    try {
      await createUser({ username: createForm.username.trim(), email: createForm.email || undefined, password: createForm.password, role: createForm.role })
      setCreateForm({ username: '', email: '', password: '', role: 'viewer' })
      setSuccess('User created.')
      await load()
    } catch (e: unknown) { setError(e instanceof Error ? e.message : 'Create failed') }
  }

  const onPatch = async (user: User, patch: Partial<User> & { password?: string }) => {
    setError(''); setSuccess('')
    try {
      await updateUser(user.id, { email: patch.email ?? user.email ?? null, role: (patch.role as UserRole) ?? user.role, is_active: patch.is_active ?? user.is_active, password: patch.password || undefined })
      setSuccess(`Updated ${user.username}.`)
      await load()
    } catch (e: unknown) { setError(e instanceof Error ? e.message : 'Update failed') }
  }

  return <section className='rf-card p-4 space-y-4'>
    <h2 className='text-xl font-semibold'>User Management</h2>
    {error && <div className='rounded border border-rose-200 bg-rose-50 p-2 text-sm text-rose-700'>{error}</div>}
    {success && <div className='rounded border border-emerald-200 bg-emerald-50 p-2 text-sm text-emerald-700'>{success}</div>}
    <div className='grid gap-2 md:grid-cols-4'>
      <input className='rf-input' placeholder='Username' value={createForm.username} onChange={e => setCreateForm({ ...createForm, username: e.target.value })} />
      <input className='rf-input' placeholder='Email (optional)' value={createForm.email} onChange={e => setCreateForm({ ...createForm, email: e.target.value })} />
      <input className='rf-input' placeholder='Password' type='password' value={createForm.password} onChange={e => setCreateForm({ ...createForm, password: e.target.value })} />
      <div className='flex gap-2'>
        <select className='rf-input' value={createForm.role} onChange={e => setCreateForm({ ...createForm, role: e.target.value as UserRole })}>{ROLES.map(r => <option key={r} value={r}>{formatRole(r)}</option>)}</select>
        <button className='rf-btn-primary' onClick={onCreate}>Create</button>
      </div>
    </div>
    {loading ? <div className='text-sm text-slate-500'>Loading users…</div> : users.length === 0 ? <div className='rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-500'>No users found.</div> : <div className='overflow-x-auto'><table className='w-full text-sm'><thead><tr className='text-left'><th>User</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead><tbody>{users.map(u => <tr key={u.id} className='border-t align-top'><td className='py-2'>{u.username}<div className='text-xs text-slate-500'>{u.email || '—'}</div></td><td className='py-2'><span className='rounded-full border border-violet-200 bg-violet-50 px-2 py-1 text-xs font-semibold text-violet-700'>{formatRole(u.role)}</span></td><td className='py-2'><span className={`rounded-full px-2 py-1 text-xs font-semibold ${u.is_active ? 'border border-emerald-200 bg-emerald-50 text-emerald-700' : 'border border-slate-200 bg-slate-100 text-slate-700'}`}>{u.is_active ? 'Active' : 'Inactive'}</span></td><td className='py-2'><div className='flex items-center gap-2 whitespace-nowrap'><select className='rf-input w-32 min-w-32' value={u.role} onChange={e => onPatch(u, { role: e.target.value as UserRole })}>{ROLES.map(r => <option key={r} value={r}>{formatRole(r)}</option>)}</select><button className='rf-btn-secondary' onClick={() => onPatch(u, { is_active: !u.is_active })}>{u.is_active ? 'Deactivate' : 'Activate'}</button></div><p className='mt-1 text-xs text-slate-500'>Password resets via API/admin procedure only.</p></td></tr>)}</tbody></table></div>}
  </section>
}
