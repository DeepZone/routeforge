import { ReactNode } from 'react'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'preflight' | 'reports' | 'system' | 'about'

const nav: { key: NavKey; label: string; desc: string }[] = [
  { key: 'dashboard', label: 'Dashboard', desc: 'Overview & quick actions' },
  { key: 'asn', label: 'ASN Check', desc: 'Read-only ASN preflight' },
  { key: 'prefix', label: 'Prefix Check', desc: 'Prefix + origin validation' },
  { key: 'preflight', label: 'Preflight', desc: 'Planned prefix-origin validation' },
  { key: 'reports', label: 'Reports', desc: 'History and outcomes' },
  { key: 'system', label: 'System', desc: 'Operational checks' },
  { key: 'about', label: 'About', desc: 'Data sources and limits' },
]

export function Layout({ children, active, onNav, systemLine, title, demoMode }: { children: ReactNode; active: NavKey; onNav: (key: NavKey) => void; systemLine: string; title: string; demoMode: boolean }) {
  return <div className='min-h-screen bg-slate-100 text-slate-900'>
    <div className='mx-auto flex max-w-7xl flex-col gap-4 p-4 lg:grid lg:grid-cols-[260px_1fr]'>
      <aside className='rf-card p-4'>
        <div className='mb-4'><p className='text-xs font-semibold uppercase tracking-wider text-blue-700'>RouteForge</p><h1 className='text-xl font-bold'>Operator Console</h1></div>
        <nav className='flex gap-2 overflow-auto lg:flex-col'>
          {nav.map((n) => <button key={n.key} onClick={() => onNav(n.key)} className={`min-w-fit rounded-xl px-3 py-2 text-left text-sm transition lg:w-full ${active === n.key ? 'bg-slate-900 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'}`}><div className='font-semibold'>{n.label}</div><div className={`text-xs ${active === n.key ? 'text-slate-300' : 'text-slate-500'}`}>{n.desc}</div></button>)}
        </nav>
      </aside>

      <div className='space-y-4'>
        <header className='rf-card flex flex-wrap items-center justify-between gap-3 p-4'>
          <h2 className='text-xl font-semibold'>{title}</h2>
          <div className='flex flex-wrap gap-2 text-xs font-semibold'>
            <span className={`rounded-full border px-3 py-1 ${demoMode ? 'border-amber-300 bg-amber-50 text-amber-700' : 'border-emerald-300 bg-emerald-50 text-emerald-700'}`}>{demoMode ? 'DEMO' : 'LIVE'}</span>
            <span className='rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-blue-700'>READ-ONLY</span>
            <span className='rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-slate-700'>v0.5.3-beta</span>
          </div>
        </header>
        <main className='space-y-4'>{children}</main>
        <footer className='px-1 text-xs text-slate-500'>{systemLine}</footer>
      </div>
    </div>
  </div>
}
