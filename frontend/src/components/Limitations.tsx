import { api } from '../api'
import { useApiData } from '../useApiData'
import { Card, SectionHeading, StateMessage } from './Common'

export function Limitations() {
  const { data, loading, error } = useApiData(api.getLimitations)

  if (loading) return <StateMessage>Loading limitations…</StateMessage>
  if (error || !data) return <StateMessage error>Failed to load limitations: {error}</StateMessage>

  return (
    <div className="section">
      <SectionHeading
        title="Limitations"
        subtitle="What this project cannot establish, stated plainly rather than buried in a footnote."
      />
      <Card>
        {data.limitations.map((l) => (
          <div className="limitation-item" key={l.title}>
            <div className="limitation-title">{l.title}</div>
            <div className="limitation-detail">{l.detail}</div>
          </div>
        ))}
      </Card>
    </div>
  )
}
