import { FormEvent, useState } from 'react'

type SetupPayload = { username: string; email?: string; password: string; password_confirm: string }

export function SetupView({ onSubmit, error }: { onSubmit: (payload: SetupPayload) => Promise<void>; error: string }) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    try {
      await onSubmit({ username, email: email || undefined, password, password_confirm: passwordConfirm })
    } finally { setBusy(false) }
  }

  return <section className='mx-auto mt-16 max-w-md rf-card p-6'>
    <h1 className='text-2xl font-bold'>Initial Admin Setup</h1>
    <p className='mt-2 text-sm text-slate-600'>Create the first administrator account.</p>
    <form className='mt-4 space-y-3' onSubmit={submit}>
      <input className='w-full rounded border p-2' placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)} required />
      <input className='w-full rounded border p-2' placeholder='Email (optional)' value={email} onChange={(e) => setEmail(e.target.value)} />
      <input className='w-full rounded border p-2' type='password' placeholder='Password' value={password} onChange={(e) => setPassword(e.target.value)} required />
      <input className='w-full rounded border p-2' type='password' placeholder='Confirm password' value={passwordConfirm} onChange={(e) => setPasswordConfirm(e.target.value)} required />
      {error && <p className='text-sm text-rose-700'>{error}</p>}
      <button className='rf-btn-primary w-full' disabled={busy}>{busy ? 'Saving...' : 'Create admin user'}</button>
    </form>
  </section>
}
