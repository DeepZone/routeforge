import type { AuditLogEntry, ChangeCaseItem, CheckResponse, ReportListItem, SystemInfo, SystemStatus, User, UserCreatePayload, UserUpdatePayload } from './types'

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  status?: number
  responseBody?: unknown

  constructor(message: string, status?: number, responseBody?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.responseBody = responseBody
  }
}

async function requestJson<T>(url: string, options: RequestInit): Promise<T> {
  const response = await fetch(url, { ...options, credentials: 'include' })
  const rawText = await response.text()
  let parsedBody: unknown = rawText
  if (rawText) {
    try { parsedBody = JSON.parse(rawText) } catch { parsedBody = rawText }
  }
  if (!response.ok) {
    const detail = typeof parsedBody === 'object' && parsedBody !== null && 'detail' in parsedBody
      ? String((parsedBody as { detail: unknown }).detail)
      : response.statusText || 'Unbekannter API-Fehler'
    const friendly = detail.includes('Database schema is not up to date') ? 'Database migration required. Please run alembic upgrade head.' : detail
    throw new ApiError(`HTTP ${response.status}: ${friendly}`, response.status, parsedBody)
  }
  return parsedBody as T
}

async function requestText(url: string, options: RequestInit): Promise<string> {
  const response = await fetch(url, { ...options, credentials: 'include' })
  const text = await response.text()
  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}: ${text || response.statusText || 'Request failed'}`, response.status, text)
  }
  return text
}

const apiUrl = (path: string) => (API_BASE_URL ? `${API_BASE_URL}${path}` : path)

export const checkAsn = (asn: string) => requestJson<CheckResponse>(apiUrl('/api/check/asn'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asn }) })
export const checkPrefix = (prefix: string, origin_as?: string, change_case_id?: number) => requestJson<CheckResponse>(apiUrl('/api/check/prefix'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, origin_as: origin_as || null, change_case_id: change_case_id ?? null }) })
export const checkAsnRpki = (asn: string, limit = 25) => requestJson<CheckResponse>(apiUrl('/api/check/asn-rpki'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asn, limit }) })
export const getReports = () => requestJson<ReportListItem[]>(apiUrl('/api/reports'), { method: 'GET' })
export const getSystemInfo = () => requestJson<SystemInfo>(apiUrl('/api/system/info'), { method: 'GET' })
export const getReportMarkdown = (reportId: number) => requestText(apiUrl(`/api/reports/${reportId}/markdown`), { method: 'GET' })
export const getReportHtml = (reportId: number) => requestText(apiUrl(`/api/reports/${reportId}/html`), { method: 'GET' })
export const getReportSummary = (reportId: number) => requestText(apiUrl(`/api/reports/${reportId}/summary`), { method: 'GET' })

export const checkPreflight = (prefix: string, planned_origin_as: string, change_case_id?: number) => requestJson<CheckResponse>(apiUrl('/api/check/preflight'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, planned_origin_as, change_case_id: change_case_id ?? null }) })

export const getSystemStatus = () => requestJson<SystemStatus>(apiUrl('/api/system/status'), { method: 'GET' })
export const getSetupRequired = () => requestJson<{ setup_required: boolean }>(apiUrl('/api/auth/setup-required'), { method: 'GET' })
export const getMe = () => requestJson<{ user: User }>(apiUrl('/api/auth/me'), { method: 'GET' })
export const setupAdmin = (payload: { username: string; email?: string; password: string; password_confirm: string }) => requestJson<{ user?: { id: number; username: string } }>(apiUrl('/api/auth/setup'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const login = (payload: { username: string; password: string }) => requestJson<{ user?: { id: number; username: string } }>(apiUrl('/api/auth/login'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const logout = () => requestJson<{ ok: boolean }>(apiUrl('/api/auth/logout'), { method: 'POST' })
export const listUsers = () => requestJson<User[]>(apiUrl('/api/users'), { method: 'GET' })
export const createUser = (payload: UserCreatePayload) => requestJson<User>(apiUrl('/api/users'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const updateUser = (userId: number, payload: UserUpdatePayload) => requestJson<User>(apiUrl(`/api/users/${userId}`), { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })


export const getAuditLog = (params: { action?: string; user_id?: number; target_type?: string; limit?: number; offset?: number }) => {
  const search = new URLSearchParams()
  if (params.action) search.set('action', params.action)
  if (params.user_id !== undefined) search.set('user_id', String(params.user_id))
  if (params.target_type) search.set('target_type', params.target_type)
  if (params.limit !== undefined) search.set('limit', String(params.limit))
  if (params.offset !== undefined) search.set('offset', String(params.offset))
  const suffix = search.toString()
  return requestJson<{ items: AuditLogEntry[]; limit: number; offset: number }>(apiUrl('/api/audit-log' + (suffix ? `?${suffix}` : '')), { method: 'GET' })
}

export const listChangeCases = () => requestJson<ChangeCaseItem[]>(apiUrl('/api/change-cases'), { method: 'GET' })
export const createChangeCase = (payload: { title: string; description?: string }) => requestJson<ChangeCaseItem>(apiUrl('/api/change-cases'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const updateChangeCase = (id: number, payload: { title?: string; description?: string; status?: string }) => requestJson<ChangeCaseItem>(apiUrl(`/api/change-cases/${id}`), { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const getChangeCaseReports = (id: number) => requestJson<any[]>(apiUrl(`/api/change-cases/${id}/reports`), { method: 'GET' })
export const runAsnCheck = (asn: string, change_case_id?: number) => requestJson<CheckResponse>(apiUrl('/api/check/asn'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asn, change_case_id: change_case_id ?? null }) })

export const deleteChangeCase = (id: number) => requestJson<{ ok: boolean; detached_checks: number }>(apiUrl(`/api/change-cases/${id}`), { method: 'DELETE' })
export const runPrefixCheck = (prefix: string, origin_as?: string, change_case_id?: number) => checkPrefix(prefix, origin_as, change_case_id)
export const runPreflightCheck = (prefix: string, planned_origin_as: string, change_case_id?: number) => checkPreflight(prefix, planned_origin_as, change_case_id)

export const runBgpVisibilityCheck = (prefix: string, expected_origin_as?: string, change_case_id?: number) => requestJson<CheckResponse>(apiUrl('/api/check/bgp-visibility'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, expected_origin_as: expected_origin_as || null, change_case_id: change_case_id ?? null }) })

export const runRoaPreflightCheck = (prefix: string, origin_as: string, max_length?: number, change_case_id?: number) => requestJson<CheckResponse>(apiUrl('/api/check/roa-preflight'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, origin_as, max_length: max_length ?? null, change_case_id: change_case_id ?? null }) })
