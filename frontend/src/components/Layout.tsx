import { ReactNode } from 'react'
export function Layout({children}:{children:ReactNode}) { return <div className='min-h-screen bg-slate-50 p-6'><div className='max-w-5xl mx-auto'>{children}</div></div> }
