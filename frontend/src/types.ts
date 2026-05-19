export type CheckSection = {
  status?: string
  summary?: string
  explanation?: string
  risk?: string
  recommendations?: string[]
  raw?: Record<string, unknown>
}

export type CheckResponse = {
  report_id: number
  status: string
  summary: string
  explanation?: string
  risk?: string
  recommendations: string[]
  input?: { prefix?: string; origin_as?: string | null }
  checks?: { rpki?: CheckSection }
  details: Record<string, unknown>
  markdown: string
  html: string
}
