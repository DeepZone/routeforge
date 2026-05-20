import { ReactNode } from 'react'
import type { UserRole } from '../types'

type NavKey = 'dashboard' | 'asn' | 'prefix' | 'preflight' | 'reports' | 'system' | 'users' | 'audit' | 'about'

const nav: { key: NavKey; label: string; desc: string }[] = [
  { key: 'dashboard', label: 'Dashboard', desc: 'Overview & quick actions' },
  { key: 'asn', label: 'ASN Check', desc: 'Read-only ASN preflight' },
  { key: 'prefix', label: 'Prefix Check', desc: 'Prefix + origin validation' },
  { key: 'preflight', label: 'Preflight', desc: 'Planned prefix-origin validation' },
  { key: 'reports', label: 'Reports', desc: 'History and outcomes' },
  { key: 'system', label: 'System', desc: 'Operational checks' },
  { key: 'users', label: 'Users', desc: 'Admin user management' },
  { key: 'audit', label: 'Audit Log', desc: 'Admin audit trail' },
  { key: 'about', label: 'About', desc: 'Data sources and limits' },
]

export function Layout({ children, active, onNav, systemLine, title, demoMode, currentUser, onLogout }: { children: ReactNode; active: NavKey; onNav: (key: NavKey) => void; systemLine: string; title: string; demoMode: boolean; currentUser?: { username: string; role: UserRole } | null; onLogout: () => void }) {
  const visibleNav = nav.filter((item) => {
    if (!currentUser) return ['dashboard', 'about'].includes(item.key)
    if (currentUser.role === 'admin') return true
    if (currentUser.role === 'operator') return !['users', 'audit'].includes(item.key)
    return ['dashboard', 'reports', 'about'].includes(item.key)
  })
  return <div className='min-h-screen bg-slate-100 text-slate-900'>
    <div className='mx-auto flex max-w-7xl flex-col gap-4 p-4 lg:grid lg:grid-cols-[260px_1fr]'>
      <aside className='rf-card p-4'>
        <div className='mb-4 flex items-center gap-3'>
          <img src='/routeforge.png' alt='RouteForge' className='h-11 w-11 rounded-xl object-contain' />
          <div>
            <p className='text-xs font-semibold uppercase tracking-wider text-blue-700'>RouteForge</p>
            <h1 className='text-xl font-bold'>Operator Console</h1>
          </div>
        </div>
        <nav className='flex gap-2 overflow-auto lg:flex-col'>
          {visibleNav.map((n) => <button key={n.key} onClick={() => onNav(n.key)} className={`min-w-fit rounded-xl px-3 py-2 text-left text-sm transition lg:w-full ${active === n.key ? 'bg-slate-900 text-white' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'}`}><div className='font-semibold'>{n.label}</div><div className={`text-xs ${active === n.key ? 'text-slate-300' : 'text-slate-500'}`}>{n.desc}</div></button>)}
        </nav>
      </aside>

      <div className='space-y-4'>
        <header className='rf-card flex flex-wrap items-center justify-between gap-3 p-4'>
          <h2 className='text-xl font-semibold'>{title}</h2>
          <div className='flex flex-wrap items-center gap-2 text-xs font-semibold'>
            {currentUser && <span className='rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-violet-700'>Angemeldet als {currentUser.username} · {currentUser.role}</span>}
            <span className={`rounded-full border px-3 py-1 ${demoMode ? 'border-amber-300 bg-amber-50 text-amber-700' : 'border-emerald-300 bg-emerald-50 text-emerald-700'}`}>{demoMode ? 'DEMO' : 'LIVE'}</span>
            <span className='rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-blue-700'>READ-ONLY</span>
            <span className='rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-slate-700'>v0.6.6-beta</span>
            <button className='rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-rose-700 hover:bg-rose-100' onClick={onLogout}>Logout</button>
          </div>
        </header>
        <main className='space-y-4'>{children}</main>
        <footer className='px-1 text-xs text-slate-500'>{systemLine}</footer>
      </div>
    </div>
  </div>
}
