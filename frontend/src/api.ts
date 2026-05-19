import type { CheckResponse, ReportListItem, SystemInfo } from './types'

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
  const response = await fetch(url, options)
  const rawText = await response.text()
  let parsedBody: unknown = rawText
  if (rawText) {
    try { parsedBody = JSON.parse(rawText) } catch { parsedBody = rawText }
  }
  if (!response.ok) {
    const detail = typeof parsedBody === 'object' && parsedBody !== null && 'detail' in parsedBody
      ? String((parsedBody as { detail: unknown }).detail)
      : response.statusText || 'Unbekannter API-Fehler'
    throw new ApiError(`HTTP ${response.status}: ${detail}`, response.status, parsedBody)
  }
  return parsedBody as T
}

const apiUrl = (path: string) => (API_BASE_URL ? `${API_BASE_URL}${path}` : path)

export const checkAsn = (asn: string) => requestJson<CheckResponse>(apiUrl('/api/check/asn'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asn }) })
export const checkPrefix = (prefix: string, origin_as?: string) => requestJson<CheckResponse>(apiUrl('/api/check/prefix'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prefix, origin_as: origin_as || null }) })
export const checkAsnRpki = (asn: string, limit = 25) => requestJson<CheckResponse>(apiUrl('/api/check/asn-rpki'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asn, limit }) })
export const getReports = () => requestJson<ReportListItem[]>(apiUrl('/api/reports'), { method: 'GET' })
export const getSystemInfo = () => requestJson<SystemInfo>(apiUrl('/api/system/info'), { method: 'GET' })
