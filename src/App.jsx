import { useState, useEffect } from 'react'
import TickerBar from './components/TickerBar'
import FilterBar from './components/FilterBar'
import CompanyCard from './components/CompanyCard'
import './App.css'

const COMPANY_ORDER = [
  'OpenAI', 'Anthropic', 'Google', 'Microsoft',
  'Apple', 'Perplexity', 'Meta', 'Amazon',
]

function groupByCompany(signals) {
  const map = {}
  for (const signal of signals) {
    if (!map[signal.company]) map[signal.company] = []
    map[signal.company].push(signal)
  }
  return COMPANY_ORDER
    .filter(c => map[c])
    .map(c => ({ company: c, signals: map[c] }))
}

export default function App() {
  const [signals, setSignals] = useState([])
  const [updated, setUpdated] = useState(null)
  const [filter,  setFilter]  = useState('all')
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    fetch('/signals.json')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(data => {
        setSignals(data.signals ?? [])
        setUpdated(data.updated ?? null)
        setLoading(false)
      })
      .catch(() => {
        setError('Could not load signals.json — run python3 ingest.py first.')
        setLoading(false)
      })
  }, [])

  const companies = groupByCompany(signals)
  const visible   = filter === 'all'
    ? companies
    : companies.filter(c => c.signals[0]?.badge === filter)

  return (
    <div className="app">
      <header className="header">
        <h1>AI Signal Tracker</h1>
        <p className="subtitle">Live intelligence from the AI frontier</p>
      </header>

      <TickerBar signals={signals} />

      <main className="main">
        <div className="controls">
          <FilterBar filter={filter} setFilter={setFilter} />
          {updated && (
            <span className="updated">
              Updated {new Date(updated).toLocaleString()}
            </span>
          )}
        </div>

        {loading && <p className="status">Loading signals…</p>}
        {error   && <p className="status error">{error}</p>}

        {!loading && !error && (
          <div className="grid">
            {visible.map(c => (
              <CompanyCard key={c.company} data={c} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
