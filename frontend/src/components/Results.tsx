import { api } from '../api'
import { useApiData } from '../useApiData'
import { Card, SectionHeading, StateMessage } from './Common'

function formatVariables(variables: Record<string, unknown>): string {
  return Object.entries(variables)
    .map(([k, v]) => `${k} = ${typeof v === 'number' ? v.toFixed(4) : String(v)}`)
    .join('  ·  ')
}

function formatStatistic(statistic: Record<string, unknown>): string {
  return Object.entries(statistic)
    .map(([k, v]) => `${k}: ${typeof v === 'number' ? v.toFixed(4) : String(v)}`)
    .join('  ·  ')
}

export function Results() {
  const { data, loading, error } = useApiData(api.getHypotheses)

  if (loading) return <StateMessage>Loading hypothesis results…</StateMessage>
  if (error || !data) return <StateMessage error>Failed to load hypotheses: {error}</StateMessage>

  return (
    <div className="section">
      <SectionHeading
        title="Results"
        subtitle="Four pre-defined hypotheses, each tested with a method valid for a single-event study, with the honest result — supported or not."
      />

      {data.hypotheses.map((h) => (
        <Card key={h.hypothesis}>
          <div className={`hypothesis-card ${h.supported ? 'supported' : 'not-supported'}`}>
            <div className="hypothesis-header">
              <span className="hypothesis-id">{h.hypothesis}</span>
              <span className={`badge ${h.supported ? 'badge-positive' : 'badge-negative'}`}>
                {h.supported ? 'SUPPORTED' : 'NOT SUPPORTED'}
              </span>
            </div>
            <div className="hypothesis-statement">{h.statement}</div>
            <div className="hypothesis-meta">
              <strong>Method:</strong> {h.method}
            </div>
            <div className="hypothesis-meta">
              <strong>Variables:</strong> {formatVariables(h.variables)}
            </div>
            <div className="hypothesis-meta">
              <strong>Statistic:</strong> {formatStatistic(h.statistic)}
            </div>
            <div className="hypothesis-conclusion">{h.conclusion}</div>
          </div>
        </Card>
      ))}
    </div>
  )
}
