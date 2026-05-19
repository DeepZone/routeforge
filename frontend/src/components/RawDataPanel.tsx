export function RawDataPanel({ data }: { data: unknown }) {
  return <details className='rf-card p-4'>
    <summary className='cursor-pointer text-sm font-semibold text-slate-700'>API-Rohdaten</summary>
    <pre className='mt-3 overflow-auto rounded-xl bg-slate-900 p-3 text-xs text-slate-100'>{JSON.stringify(data, null, 2)}</pre>
  </details>
}
