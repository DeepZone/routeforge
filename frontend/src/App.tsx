import { Layout } from './components/Layout'
import { AsnCheckForm } from './components/AsnCheckForm'
import { PrefixCheckForm } from './components/PrefixCheckForm'

export default function App() {
  return (
    <Layout>
      <h1 className='text-3xl font-bold mb-2'>RouteForge</h1>
      <p className='mb-6 text-slate-700'>
        RouteForge performs read-only checks and does not modify registry, ROA or router configuration.
      </p>
      <div className='grid md:grid-cols-2 gap-4'>
        <AsnCheckForm />
        <PrefixCheckForm />
      </div>
    </Layout>
  )
}
