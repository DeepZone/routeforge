import { ReactNode } from 'react'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'reports' | 'about'

export function Layout({ children, active, onNav, systemLine }: { children: ReactNode; active: NavKey; onNav: (key: NavKey) => void; systemLine: string }) {
  const nav: { key: NavKey; label: string }[] = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'asn', label: 'ASN Check' },
    { key: 'prefix', label: 'Prefix Check' },
    { key: 'reports', label: 'Reports' },
    { key: 'about', label: 'About' },
  ]
  return <div className='min-h-screen bg-slate-100 text-slate-900'>
    <header className='bg-slate-900 text-white px-6 py-4 font-semibold'>RouteForge Operator Console</header>
    <div className='max-w-7xl mx-auto p-4 grid md:grid-cols-[220px_1fr] gap-4'>
      <aside className='bg-white border rounded-lg p-2 h-fit'>{nav.map(n => <button key={n.key} onClick={() => onNav(n.key)} className={`w-full text-left px-3 py-2 rounded-md text-sm ${active === n.key ? 'bg-slate-900 text-white' : 'hover:bg-slate-100'}`}>{n.label}</button>)}</aside>
      <main>{children}</main>
    </div>
    <footer className='border-t bg-white px-6 py-2 text-xs text-slate-600'>{systemLine}</footer>
  </div>
}
