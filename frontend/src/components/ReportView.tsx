import type { CheckResponse } from '../types'
import { RawDataPanel } from './RawDataPanel'
import { StatusBadge } from './StatusBadge'
export function ReportView({report}:{report:CheckResponse}){ return <div className='mt-6 p-4 border rounded bg-white'><div className='flex gap-2 items-center'><h3 className='text-lg font-bold'>Ergebnis</h3><StatusBadge status={report.status}/></div><p className='mt-2'>{report.summary}</p><h4 className='font-semibold mt-4'>Empfehlungen</h4><ul className='list-disc pl-5'>{report.recommendations.map(r=><li key={r}>{r}</li>)}</ul><button className='mt-4 px-3 py-2 border rounded' onClick={()=>navigator.clipboard.writeText(report.markdown)}>Markdown kopieren</button><RawDataPanel data={report.details}/></div> }
