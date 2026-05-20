import { FormEvent, useState } from 'react'

export function LoginView({ onSubmit, error }: { onSubmit: (username: string, password: string) => Promise<void>; error: string }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    try {
      await onSubmit(username, password)
    } finally { setBusy(false) }
  }

  return <section className='mx-auto mt-16 max-w-md rf-card p-6'>
    <h1 className='text-2xl font-bold'>Login</h1>
    <form className='mt-4 space-y-3' onSubmit={submit}>
      <input className='w-full rounded border p-2' placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)} required />
      <input className='w-full rounded border p-2' type='password' placeholder='Password' value={password} onChange={(e) => setPassword(e.target.value)} required />
      {error && <p className='text-sm text-rose-700'>{error}</p>}
      <button className='rf-btn-primary w-full' disabled={busy}>{busy ? 'Signing in...' : 'Login'}</button>
    </form>
  </section>
}
