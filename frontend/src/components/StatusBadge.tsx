const STYLES: Record<string, string> = {
  OK: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  WARNING: 'bg-amber-100 text-amber-800 border-amber-200',
  CRITICAL: 'bg-rose-100 text-rose-800 border-rose-200',
  UNKNOWN: 'bg-slate-100 text-slate-800 border-slate-200',
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = (status || 'UNKNOWN').toUpperCase()
  const safeStatus = STYLES[normalized] ? normalized : 'UNKNOWN'
  return <span className={`inline-flex px-2 py-1 rounded-md border text-xs font-semibold tracking-wide ${STYLES[safeStatus]}`}>{safeStatus}</span>
}
