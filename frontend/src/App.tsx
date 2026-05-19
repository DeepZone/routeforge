import { useState } from 'react'
import { checkAsn, checkPrefix } from './api'
import { Layout } from './components/Layout'
import { AsnCheckForm } from './components/AsnCheckForm'
import { PrefixCheckForm } from './components/PrefixCheckForm'
import { ReportView } from './components/ReportView'
import type { CheckResponse } from './types'

export default function App(){ const [report,setReport]=useState<CheckResponse|null>(null); const [loading,setLoading]=useState(false); const run=async(fn:()=>Promise<CheckResponse>)=>{setLoading(true); try{setReport(await fn())}finally{setLoading(false)}}; return <Layout><h1 className='text-3xl font-bold mb-2'>RouteForge</h1><p className='mb-6 text-slate-700'>RouteForge performs read-only checks and does not modify registry, ROA or router configuration.</p><div className='grid md:grid-cols-2 gap-4'><AsnCheckForm loading={loading} onSubmit={(asn)=>run(()=>checkAsn(asn))}/><PrefixCheckForm loading={loading} onSubmit={(p,o)=>run(()=>checkPrefix(p,o))}/></div>{loading && <p className='mt-4'>Lade...</p>}{report && <ReportView report={report}/>}</Layout> }
