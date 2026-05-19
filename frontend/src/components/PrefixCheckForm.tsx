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

  const onSubmit = async () => {
    setError(null)
    setResult(null)
    setLoading(true)

    try {
      const response = await checkPrefix(prefix, originAs || undefined)
      setResult(response)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err)
      } else {
        setError(new ApiError('Unbekannter Fehler bei der Prefix-Prüfung.'))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='p-4 border rounded bg-white'>
      <h2 className='font-bold mb-2'>Prefix Check</h2>
      <input className='border p-2 w-full mb-2' placeholder='193.0.22.0/23' value={prefix} onChange={e => setPrefix(e.target.value)} />
      <input className='border p-2 w-full' placeholder='Optional: AS3333' value={originAs} onChange={e => setOriginAs(e.target.value)} />
      <button disabled={loading} className='mt-2 px-3 py-2 bg-blue-600 text-white rounded' onClick={onSubmit}>
        Prüfen
      </button>

      {loading && <p className='mt-3 text-sm text-slate-700'>Prüfung läuft ...</p>}

      {error && (
        <div className='mt-3 p-3 rounded border border-red-300 bg-red-50 text-red-800'>
          <p className='font-semibold'>Die Prüfung konnte nicht ausgeführt werden.</p>
          <p className='text-sm mt-1'>{error.message}</p>
          <details className='mt-2'>
            <summary className='cursor-pointer text-sm'>Technische Details</summary>
            <pre className='text-xs whitespace-pre-wrap mt-1'>
              {JSON.stringify(
                {
                  status: error.status,
                  responseBody: error.responseBody,
                },
                null,
                2,
              )}
            </pre>
          </details>
        </div>
      )}

      {result && <div className='mt-4'><ReportView report={result} /></div>}
    </div>
  )
}
