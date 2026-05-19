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
  input?: { prefix?: string; origin_as?: string | null; asn?: string; limit?: number }
  checks?: { rpki?: CheckSection } | null
  details: {
    rpki_explanation?: string
    extracted_prefixes?: string[]
    rpki_summary?: Record<string, number>
    results?: RpkiBatchResult[]
    [key: string]: unknown
  }
  markdown: string
  html: string
}
