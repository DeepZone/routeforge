import type { CheckResponse, ReportListItem, SystemInfo, SystemStatus } from './types'

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
export const checkPrefix = (prefix: string, origin_as?: string) => requestJson<CheckResponse>(apiUrl('/api/check/prefix'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, origin_as: origin_as || null }) })
export const checkAsnRpki = (asn: string, limit = 25) => requestJson<CheckResponse>(apiUrl('/api/check/asn-rpki'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asn, limit }) })
export const getReports = () => requestJson<ReportListItem[]>(apiUrl('/api/reports'), { method: 'GET' })
export const getSystemInfo = () => requestJson<SystemInfo>(apiUrl('/api/system/info'), { method: 'GET' })
export const getReportMarkdown = (reportId: number) => requestText(apiUrl(`/api/reports/${reportId}/markdown`), { method: 'GET' })
export const getReportHtml = (reportId: number) => requestText(apiUrl(`/api/reports/${reportId}/html`), { method: 'GET' })
export const getReportSummary = (reportId: number) => requestText(apiUrl(`/api/reports/${reportId}/summary`), { method: 'GET' })

export const checkPreflight = (prefix: string, planned_origin_as: string) => requestJson<CheckResponse>(apiUrl('/api/check/preflight'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, planned_origin_as }) })

export const getSystemStatus = () => requestJson<SystemStatus>(apiUrl('/api/system/status'), { method: 'GET' })
export const getSetupRequired = () => requestJson<{ setup_required: boolean }>(apiUrl('/api/auth/setup-required'), { method: 'GET' })
export const getMe = () => requestJson<{ user: { id: number; username: string; email?: string; role: string } }>(apiUrl('/api/auth/me'), { method: 'GET' })
export const setupAdmin = (payload: { username: string; email?: string; password: string; password_confirm: string }) => requestJson<{ user?: { id: number; username: string } }>(apiUrl('/api/auth/setup'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const login = (payload: { username: string; password: string }) => requestJson<{ user?: { id: number; username: string } }>(apiUrl('/api/auth/login'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const logout = () => requestJson<{ ok: boolean }>(apiUrl('/api/auth/logout'), { method: 'POST' })
