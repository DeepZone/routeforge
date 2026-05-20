export type StatusValue = 'OK' | 'WARNING' | 'CRITICAL' | 'UNKNOWN'

export type CheckSection = {
  status?: string
  summary?: string
  explanation?: string
  risk?: string
  recommendations?: string[]
  raw?: Record<string, unknown>
}

export type RpkiBatchResult = {
  prefix?: string
  origin_as?: string
  rpki_raw_status?: string | null
  status?: string
  summary?: string
  raw?: Record<string, unknown>
}

export type CheckResponse = {
  report_id: number
  status: string
  summary: string
  explanation?: string
  risk?: string
  recommendations: string[]
  input?: { prefix?: string; origin_as?: string | null; planned_origin_as?: string | null; asn?: string; limit?: number }
  checks?: { rpki?: CheckSection; registry?: CheckSection; routing_visibility?: CheckSection } | null
  details?: {
    rpki_explanation?: string
    extracted_prefixes?: string[]
    rpki_summary?: Record<string, number>
    results?: RpkiBatchResult[]
    checked_prefixes?: number
    total_prefixes_seen?: number
    rpki_batch?: {
      available?: boolean
      reason_code?: string
      message?: string
      prefix_count?: number
      can_retry?: boolean
    }
    limited?: boolean
    demo_mode?: boolean
    source_errors?: unknown
    warnings?: unknown
    [key: string]: unknown
  }
  markdown: string
  html: string
}

export type ReportListItem = {
  report_id: number
  check_id: number
  check_type: string
  input_resource: string
  origin_as?: string | null
  status: string
  summary: string
  holder?: string | null
  created_at: string
}

export type SystemInfo = {
  name: string
  version: string
  demo_mode: boolean
  read_only: boolean
  data_sources: string[]
}
