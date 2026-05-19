const STYLES: Record<string, string> = {
  OK: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  WARNING: 'border-amber-200 bg-amber-50 text-amber-700',
  CRITICAL: 'border-rose-200 bg-rose-50 text-rose-700',
  UNKNOWN: 'border-slate-200 bg-slate-100 text-slate-700',
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = (status || 'UNKNOWN').toUpperCase()
  const safeStatus = STYLES[normalized] ? normalized : 'UNKNOWN'
  return <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${STYLES[safeStatus]}`}>{safeStatus}</span>
}
