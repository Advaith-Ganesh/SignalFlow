import Plot from 'react-plotly.js'
import { api } from '../api'
import { formatPct, formatVolume } from '../format'
import { useApiData } from '../useApiData'
import { Card, SectionHeading, StatCard, StateMessage } from './Common'

const PLOT_LAYOUT_BASE = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { color: '#8b93a1', family: 'ui-monospace, monospace', size: 11 },
  margin: { l: 50, r: 20, t: 10, b: 40 },
  xaxis: { gridcolor: '#1a2029', zerolinecolor: '#232a34' },
  yaxis: { gridcolor: '#1a2029', zerolinecolor: '#232a34' },
  legend: { orientation: 'h' as const, y: -0.2 },
}

export function MarketReaction() {
  const { data, loading, error } = useApiData(api.getEventStudy)

  if (loading) return <StateMessage>Loading market reaction data…</StateMessage>
  if (error || !data) return <StateMessage error>Failed to load event study: {error}</StateMessage>

  const daily = [...data.daily].sort((a, b) => a.relative_day - b.relative_day)
  const days = daily.map((d) => d.relative_day)
  const dates = daily.map((d) => d.date)
  const ar = daily.map((d) => d.abnormal_return * 100)
  const car = daily.map((d) => d.cumulative_abnormal_return * 100)
  const volumeRatio = daily.map((d) => d.abnormal_volume_ratio)
  const barColors = ar.map((v) => (v >= 0 ? '#3fb950' : '#e5484d'))

  const { summary, market_model: model } = data

  return (
    <div className="section">
      <SectionHeading
        title="Market Reaction"
        subtitle={`Market-model event study, event window [${data.event_window[0]}, +${data.event_window[1]}] trading days around t = 0 (${event_day(daily)}).`}
      />

      <div className="grid grid-4">
        <StatCard
          label="Event-day abnormal return"
          value={formatPct(summary.event_day_abnormal_return, 1)}
          sub={`t = ${summary.event_day_t_stat.toFixed(2)}, p ${summary.event_day_p_value < 0.0001 ? '< 0.0001' : `= ${summary.event_day_p_value.toFixed(4)}`}`}
          valueClassName={summary.event_day_abnormal_return >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="Cumulative AR (full window)"
          value={formatPct(summary.car_full_window, 1)}
          sub={`Max |CAR| on day ${summary.max_abs_cumulative_abnormal_return.relative_day} (${summary.max_abs_cumulative_abnormal_return.date})`}
          valueClassName={summary.car_full_window >= 0 ? 'positive' : 'negative'}
        />
        <StatCard
          label="Event-day abnormal volume"
          value={`${summary.event_day_abnormal_volume_ratio.toFixed(1)}×`}
          sub="vs. mean estimation-window volume"
        />
        <StatCard
          label="Market model fit"
          value={`β = ${model.beta.toFixed(2)}`}
          sub={`α = ${model.alpha.toFixed(4)}, R² = ${model.r_squared.toFixed(2)}, n = ${model.n_obs}`}
        />
      </div>

      <Card title="Daily abnormal return (market-model adjusted)">
        <Plot
          data={[
            {
              x: days,
              y: ar,
              type: 'bar',
              marker: { color: barColors },
              text: dates,
              hovertemplate: 'Day %{x}<br>%{text}<br>AR: %{y:.2f}%<extra></extra>',
            },
          ]}
          layout={{
            ...PLOT_LAYOUT_BASE,
            height: 260,
            xaxis: { ...PLOT_LAYOUT_BASE.xaxis, title: { text: 'Trading day relative to announcement (t=0)' } },
            yaxis: { ...PLOT_LAYOUT_BASE.yaxis, title: { text: 'Abnormal return (%)' } },
            shapes: [{ type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, yref: 'paper', line: { color: '#5b6472', dash: 'dot' } }],
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: '100%' }}
        />
      </Card>

      <Card title="Cumulative abnormal return (CAR)">
        <Plot
          data={[
            {
              x: days,
              y: car,
              type: 'scatter',
              mode: 'lines+markers',
              line: { color: '#4f8cff' },
              marker: { size: 5 },
              text: dates,
              hovertemplate: 'Day %{x}<br>%{text}<br>CAR: %{y:.2f}%<extra></extra>',
            },
          ]}
          layout={{
            ...PLOT_LAYOUT_BASE,
            height: 260,
            xaxis: { ...PLOT_LAYOUT_BASE.xaxis, title: { text: 'Trading day relative to announcement (t=0)' } },
            yaxis: { ...PLOT_LAYOUT_BASE.yaxis, title: { text: 'Cumulative abnormal return (%)' } },
            shapes: [{ type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, yref: 'paper', line: { color: '#5b6472', dash: 'dot' } }],
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: '100%' }}
        />
      </Card>

      <Card title="Abnormal trading volume (multiple of estimation-window average)">
        <Plot
          data={[
            {
              x: days,
              y: volumeRatio,
              type: 'bar',
              marker: { color: '#e3b341' },
              text: dates,
              hovertemplate: 'Day %{x}<br>%{text}<br>%{y:.1f}× normal volume<extra></extra>',
            },
          ]}
          layout={{
            ...PLOT_LAYOUT_BASE,
            height: 220,
            xaxis: { ...PLOT_LAYOUT_BASE.xaxis, title: { text: 'Trading day relative to announcement (t=0)' } },
            yaxis: { ...PLOT_LAYOUT_BASE.yaxis, title: { text: 'Volume multiple' } },
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: '100%' }}
        />
      </Card>

      <div className="grid grid-3">
        <StatCard
          label="Pre-event volatility"
          value={formatPct(summary.volatility_pre_event, 2)}
          sub="Std. dev. of daily returns, days < 0"
        />
        <StatCard
          label="Post-event volatility"
          value={formatPct(summary.volatility_post_event, 2)}
          sub="Std. dev. of daily returns, days > 0"
        />
        <StatCard
          label="Estimation-window volatility"
          value={formatPct(summary.volatility_estimation_window, 2)}
          sub="Baseline (non-event) daily volatility"
        />
      </div>

      <Card title="Daily event-window detail">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Day</th>
                <th>Date</th>
                <th className="num">Return</th>
                <th className="num">Abnormal return</th>
                <th className="num">CAR</th>
                <th className="num">Volume</th>
                <th className="num">Abn. volume</th>
              </tr>
            </thead>
            <tbody>
              {daily.map((d) => (
                <tr key={d.date}>
                  <td className="mono">{d.relative_day >= 0 ? `+${d.relative_day}` : d.relative_day}</td>
                  <td className="mono">{d.date}</td>
                  <td className={`num ${d.return_company >= 0 ? 'positive' : 'negative'}`}>{formatPct(d.return_company, 2)}</td>
                  <td className={`num ${d.abnormal_return >= 0 ? 'positive' : 'negative'}`}>{formatPct(d.abnormal_return, 2)}</td>
                  <td className={`num ${d.cumulative_abnormal_return >= 0 ? 'positive' : 'negative'}`}>
                    {formatPct(d.cumulative_abnormal_return, 2)}
                  </td>
                  <td className="num">{formatVolume(d.volume_company)}</td>
                  <td className="num">{d.abnormal_volume_ratio.toFixed(1)}×</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

function event_day(daily: { relative_day: number; date: string }[]): string {
  return daily.find((d) => d.relative_day === 0)?.date ?? 't=0'
}
