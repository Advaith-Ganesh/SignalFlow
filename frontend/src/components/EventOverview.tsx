import { api } from '../api'
import { formatPctPoints, formatUsdBillion, signClass } from '../format'
import { useApiData } from '../useApiData'
import { Badge, Card, SectionHeading, StatCard, StateMessage } from './Common'

export function EventOverview() {
  const { data, loading, error } = useApiData(api.getEventOverview)

  if (loading) return <StateMessage>Loading event overview…</StateMessage>
  if (error || !data) return <StateMessage error>Failed to load event overview: {error}</StateMessage>

  const { event, earnings_surprise: surprise } = data

  return (
    <div className="section">
      <SectionHeading
        title="Event Overview"
        subtitle="The single historical earnings event this entire project investigates."
      />

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>
              {event.company_name} ({event.ticker})
            </div>
            <div className="muted" style={{ marginTop: 4 }}>
              {event.fiscal_quarter} earnings release
            </div>
          </div>
          <Badge
            label={surprise.direction === 'miss' ? 'EPS MISS' : surprise.direction === 'beat' ? 'EPS BEAT' : 'IN-LINE'}
            tone={surprise.direction === 'miss' ? 'negative' : surprise.direction === 'beat' ? 'positive' : 'neutral'}
          />
        </div>
        <p style={{ marginTop: 14, fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
          Announced <strong className="mono">{event.announcement_date}</strong> ({event.announcement_time}).{' '}
          {event.announcement_context} Event day (t = 0) for the study is{' '}
          <strong className="mono">{event.event_day}</strong>.
        </p>
      </Card>

      <div className="grid grid-4">
        <StatCard
          label="EPS actual vs. estimate"
          value={`$${surprise.eps_actual.toFixed(2)}`}
          sub={`vs. $${surprise.eps_estimate.toFixed(2)} est. (${formatPctPoints(surprise.eps_surprise_pct)})`}
          valueClassName={signClass(surprise.eps_surprise_pct)}
        />
        <StatCard
          label="Revenue actual vs. estimate"
          value={formatUsdBillion(surprise.revenue_actual_usd_billion)}
          sub={`vs. ${formatUsdBillion(surprise.revenue_estimate_usd_billion)} est. (${formatPctPoints(surprise.revenue_surprise_pct)})`}
          valueClassName={signClass(surprise.revenue_surprise_pct)}
        />
        <StatCard
          label="Daily active users"
          value={`${event.dau_billion.toFixed(2)}B`}
          sub={`vs. ${event.dau_estimate_billion.toFixed(2)}B est. — ${event.dau_qoq_change}`}
        />
        <StatCard
          label="1-day stock reaction"
          value={`${event.one_day_return_2022_02_03_pct.toFixed(1)}%`}
          sub={`$${event.close_2022_02_02.toFixed(2)} → $${event.close_2022_02_03.toFixed(2)}`}
          valueClassName="negative"
        />
      </div>

      <div className="grid grid-2">
        <Card title="Q1 2022 guidance (given alongside this report)">
          <p style={{ fontSize: 13, lineHeight: 1.6 }}>
            Revenue guided to{' '}
            <strong className="mono">
              ${event.q1_2022_revenue_guidance_low_usd_billion}B–${event.q1_2022_revenue_guidance_high_usd_billion}B
            </strong>
            , versus a Street consensus of roughly{' '}
            <strong className="mono">${event.q1_2022_revenue_consensus_usd_billion}B</strong>. This guidance
            miss is widely credited as a larger driver of the stock reaction than the Q4 EPS/revenue
            figures themselves.
          </p>
        </Card>
        <Card title="Stated headwinds (per the earnings call)">
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, lineHeight: 1.7 }}>
            {event.stated_headwinds.map((h) => (
              <li key={h}>{h}</li>
            ))}
          </ul>
        </Card>
      </div>

      <Card title="Why this event">
        <p style={{ fontSize: 13, lineHeight: 1.65, color: 'var(--text-muted)' }}>{event.reason_for_selecting_event}</p>
      </Card>

      <Card title="Sources (real, publicly accessible)">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Publisher</th>
                <th>Title</th>
              </tr>
            </thead>
            <tbody>
              {event.sources.map((s) => (
                <tr key={s.url}>
                  <td className="mono">{s.date}</td>
                  <td>{s.publisher}</td>
                  <td>
                    <a href={s.url} target="_blank" rel="noreferrer">
                      {s.title}
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
