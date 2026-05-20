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

export type SourceDiagnostic = {
  name?: string
  endpoint?: string
  status?: string
  message?: string
  duration_ms?: number | null
  cached?: boolean | null
  cache_age_seconds?: number | null
  cache_ttl_seconds?: number | null
  fetched_at?: string | null
  expires_at?: string | null
  freshness?: "LIVE" | "FRESH" | "EXPIRING_SOON" | "STALE" | "UNKNOWN" | string
  http_status?: number | null
  error_type?: string | null
  details?: Record<string, unknown>
  retry_count?: number | null
  attempts?: number | null
  fallback_used?: boolean | null
  fallback_reason?: string | null
  stale_cache_used?: boolean | null
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
  details?: Record<string, unknown>
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

export type DatabaseStatus = { status?: string; type?: string; url_safe?: string; error_message?: string; schema_version?: string; migration_status?: string; migration_head?: string }
export type ApiProxyStatus = { status?: string; mode?: string; frontend_proxy_expected?: boolean }
export type RipestatRuntimeSettings = { cache_ttl_seconds?: number; timeout_seconds?: number; max_retries?: number; retry_backoff_seconds?: number; use_stale_cache_on_error?: boolean }
export type SystemFeatures = { asn_check?: boolean; prefix_check?: boolean; preflight?: boolean; reports?: boolean; exports?: boolean; data_source_diagnostics?: boolean; cache_freshness?: boolean; retry_resilience?: boolean }
export type SystemStatus = {
  status?: string
  name?: string
  version?: string
  read_only?: boolean
  mode?: string
  demo_mode?: boolean
  database?: DatabaseStatus
  api_proxy?: ApiProxyStatus
  ripestat?: RipestatRuntimeSettings
  features?: SystemFeatures
  security_warnings?: string[]
}

export type UserRole = 'admin' | 'operator' | 'viewer'

export type User = {
  id: number
  username: string
  email?: string | null
  role: UserRole
  is_active?: boolean
  created_at?: string
  updated_at?: string
  last_login_at?: string | null
}

export type UserCreatePayload = {
  username: string
  email?: string
  password: string
  role: UserRole
}

export type UserUpdatePayload = {
  email?: string | null
  role?: UserRole
  is_active?: boolean
  password?: string
}


export type AuditLogEntry = {
  id: number
  created_at: string
  user_id?: number | null
  username?: string | null
  action: string
  target_type?: string | null
  target_id?: string | null
  ip_address?: string | null
  user_agent?: string | null
  details_json?: Record<string, unknown> | null
}

export type ChangeCaseStatus = 'draft' | 'in_review' | 'approved' | 'closed'
export type ChangeCaseItem = { id:number; title:string; description?:string|null; status:ChangeCaseStatus; created_by_user_id?:number|null; created_at:string; updated_at:string }
