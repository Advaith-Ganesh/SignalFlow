import { useState } from 'react'
import { EventOverview } from './components/EventOverview'
import { MarketReaction } from './components/MarketReaction'
import { NewsTimeline } from './components/NewsTimeline'
import { InformationDiffusion } from './components/InformationDiffusion'
import { Results } from './components/Results'
import { Limitations } from './components/Limitations'

const TABS = [
  { id: 'overview', label: 'Event Overview', component: EventOverview },
  { id: 'market', label: 'Market Reaction', component: MarketReaction },
  { id: 'news', label: 'News Timeline', component: NewsTimeline },
  { id: 'diffusion', label: 'Information Diffusion', component: InformationDiffusion },
  { id: 'results', label: 'Results', component: Results },
  { id: 'limitations', label: 'Limitations', component: Limitations },
] as const

function App() {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]['id']>('overview')
  const ActiveComponent = TABS.find((t) => t.id === activeTab)?.component ?? EventOverview

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-name">SIGNALFLOW</span>
          <span className="brand-tagline">Information Diffusion &amp; Market Reaction Research</span>
          <span className="ticker-badge">META · Q4 FY2021</span>
        </div>
        <nav className="nav-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="app-main">
        <ActiveComponent />
      </main>

      <footer className="app-footer">
        Historical research project. Not investment advice. Every figure is either sourced from a
        cited public record, computed deterministically from that data, or a fitted model explicitly
        labeled as such — see the Limitations tab and docs/research_report.md.
      </footer>
    </div>
  )
}

export default App
