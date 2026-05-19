const STYLES: Record<string, string> = {
  OK: 'bg-green-100 text-green-800',
  WARNING: 'bg-yellow-100 text-yellow-800',
  CRITICAL: 'bg-red-100 text-red-800',
  UNKNOWN: 'bg-gray-100 text-gray-800',
}

export function StatusBadge({ status }: { status: string }) {
  const normalized = (status || 'UNKNOWN').toUpperCase()
  const safeStatus = STYLES[normalized] ? normalized : 'UNKNOWN'
  return <span className={`px-2 py-1 rounded font-semibold ${STYLES[safeStatus]}`}>{safeStatus}</span>
}
