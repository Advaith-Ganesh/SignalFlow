import Plot from 'react-plotly.js'
import { api } from '../api'
import { useApiData } from '../useApiData'
import { Badge, Card, SectionHeading, StateMessage } from './Common'
import type { HeadlineRecord } from '../api'

const PHASE_LABELS: Record<string, string> = {
  pre_announcement: 'Pre-announcement',
  announcement: 'Announcement',
  immediate_reaction: 'Immediate reaction',
  post_announcement: 'Post-announcement',
  follow_up: 'Follow-up',
}

function sentimentTone(label: HeadlineRecord['sentiment_label']): 'positive' | 'negative' | 'neutral' {
  if (label === 'positive') return 'positive'
  if (label === 'negative') return 'negative'
  return 'neutral'
}

export function NewsTimeline() {
  const { data, loading, error } = useApiData(api.getNews)

  if (loading) return <StateMessage>Loading news timeline…</StateMessage>
  if (error || !data) return <StateMessage error>Failed to load news: {error}</StateMessage>

  const intensity = [...data.daily_intensity].sort((a, b) => a.date_str.localeCompare(b.date_str))
  const headlines = [...data.headlines].sort((a, b) => a.date.localeCompare(b.date))

  return (
    <div className="section">
      <SectionHeading
        title="News Timeline"
        subtitle="A small, manually curated set of real, publicly published headlines spanning before, during, and after the announcement — metadata only, no copyrighted article bodies reproduced."
      />

      <Card title="Daily information intensity (article count) and mean headline sentiment">
        <Plot
          data={[
            {
              x: intensity.map((i) => i.date_str),
              y: intensity.map((i) => i.article_count),
              type: 'bar',
              name: 'Article count',
              marker: { color: '#4f8cff' },
              yaxis: 'y',
            },
            {
              x: intensity.map((i) => i.date_str),
              y: intensity.map((i) => i.mean_sentiment),
              type: 'scatter',
              mode: 'lines+markers',
              name: 'Mean sentiment (compound)',
              line: { color: '#e3b341' },
              yaxis: 'y2',
            },
          ]}
          layout={{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#8b93a1', family: 'ui-monospace, monospace', size: 11 },
            margin: { l: 50, r: 50, t: 10, b: 60 },
            height: 280,
            xaxis: { gridcolor: '#1a2029', tickangle: -35 },
            yaxis: { title: { text: 'Article count' }, gridcolor: '#1a2029' },
            yaxis2: { title: { text: 'Sentiment' }, overlaying: 'y', side: 'right', range: [-1, 1], gridcolor: 'transparent' },
            legend: { orientation: 'h', y: -0.35 },
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: '100%' }}
        />
      </Card>

      <Card title="Headlines (chronological)">
        <div className="timeline">
          {headlines.map((h) => (
            <div className="timeline-item" key={h.url}>
              <div className="timeline-date">
                {h.date}
                {h.time_et ? ` ${h.time_et}` : ''}
              </div>
              <div>
                <Badge label={PHASE_LABELS[h.phase] ?? h.phase} tone="neutral" />
              </div>
              <div className="timeline-headline">
                <a href={h.url} target="_blank" rel="noreferrer">
                  {h.headline}
                </a>
                <div className="timeline-source">{h.source}</div>
              </div>
              <div>
                <Badge
                  label={`${h.sentiment_label} (${h.sentiment_compound.toFixed(2)})`}
                  tone={sentimentTone(h.sentiment_label)}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
