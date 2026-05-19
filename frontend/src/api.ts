import type { CheckResponse } from './types'
const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export async function checkAsn(asn: string): Promise<CheckResponse> { const r = await fetch(`${BASE}/api/check/asn`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({asn})}); if(!r.ok) throw new Error('ASN check failed'); return r.json() }
export async function checkPrefix(prefix: string, origin_as?: string): Promise<CheckResponse> { const r = await fetch(`${BASE}/api/check/prefix`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({prefix, origin_as: origin_as || null})}); if(!r.ok) throw new Error('Prefix check failed'); return r.json() }
