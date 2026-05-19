import { useState } from 'react'
import { ApiError, checkPrefix } from '../api'
import { ReportView } from './ReportView'
import type { CheckResponse } from '../types'

export function PrefixCheckForm() {
  const [prefix, setPrefix] = useState('')
  const [originAs, setOriginAs] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [result, setResult] = useState<CheckResponse | null>(null)

  const onSubmit = async () => { setLoading(true); setError(null); try { setResult(await checkPrefix(prefix, originAs || undefined)) } catch (e) { setError(e as ApiError) } finally { setLoading(false) } }

  return <section className='bg-white border rounded-lg p-4'>
    <h2 className='text-xl font-semibold'>Prefix Check</h2>
    <p className='text-sm text-slate-600'>Origin-AS empfohlen für vollständige RPKI- und Registry/IRR-Bewertung.</p>
    <input className='border p-2 w-full rounded mt-3' placeholder='193.0.22.0/23' value={prefix} onChange={e => setPrefix(e.target.value)} />
    <input className='border p-2 w-full rounded mt-2' placeholder='AS3333 (optional)' value={originAs} onChange={e => setOriginAs(e.target.value)} />
    <button onClick={onSubmit} disabled={loading} className='mt-2 px-3 py-2 bg-blue-700 text-white rounded-md'>Prefix prüfen</button>
    {loading && <p className='text-sm mt-2'>Prüfung läuft ...</p>}
    {error && <p className='text-sm mt-2 text-rose-700'>{error.message}</p>}
    {result && <div className='mt-4'><ReportView report={result} /></div>}
  </section>
}
