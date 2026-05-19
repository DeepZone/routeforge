import type { CheckResponse } from './types'

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
  let response: Response

  try {
    response = await fetch(url, options)
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unbekannter Netzwerkfehler'
    throw new ApiError(`Netzwerkfehler beim Aufruf von ${url}: ${message}`)
  }

  const rawText = await response.text()
  let parsedBody: unknown = rawText

  if (rawText) {
    try {
      parsedBody = JSON.parse(rawText)
    } catch {
      parsedBody = rawText
    }
  }

  if (!response.ok) {
    const detail =
      typeof parsedBody === 'object' && parsedBody !== null && 'detail' in parsedBody
        ? String((parsedBody as { detail: unknown }).detail)
        : response.statusText || 'Unbekannter API-Fehler'

    throw new ApiError(`HTTP ${response.status}: ${detail}`, response.status, parsedBody)
  }

  return parsedBody as T
}

function apiUrl(path: string): string {
  if (!API_BASE_URL) {
    return path
  }

  return `${API_BASE_URL}${path}`
}

export async function checkAsn(asn: string): Promise<CheckResponse> {
  return requestJson<CheckResponse>(apiUrl('/api/check/asn'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asn }),
  })
}

export async function checkPrefix(prefix: string, origin_as?: string): Promise<CheckResponse> {
  return requestJson<CheckResponse>(apiUrl('/api/check/prefix'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prefix, origin_as: origin_as || null }),
  })
}
