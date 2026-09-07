import Plot from 'react-plotly.js'
import type { Data } from 'plotly.js'
import { api } from '../api'
import { useApiData } from '../useApiData'
import { Card, SectionHeading, StatCard, StateMessage } from './Common'

function exponentialCurve(t: number[], k: number): number[] {
  return t.map((x) => 1 - Math.exp(-k * x))
}

function logisticCurve(t: number[], k: number, t0: number): number[] {
  return t.map((x) => 1 / (1 + Math.exp(-k * (x - t0))))
}

export function InformationDiffusion() {
  const { data, loading, error } = useApiData(api.getDiffusion)

  if (loading) return <StateMessage>Loading diffusion models…</StateMessage>
  if (error || !data) return <StateMessage error>Failed to load diffusion models: {error}</StateMessage>

  const { observed, models, better_fit_model: better, information_absorption_time_trading_days: absorptionTimes } = data
  const t = observed.relative_day
  const smoothT = Array.from({ length: 101 }, (_, i) => t[0] + (i / 100) * (t[t.length - 1] - t[0]))

  const traces: Data[] = [
    {
      x: t,
      y: observed.absorption_fraction,
      type: 'scatter',
      mode: 'markers',
      name: 'Observed (empirical)',
      marker: { color: '#e6e9ee', size: 8 },
    },
  ]

  if (models.exponential.converged && models.exponential.k !== undefined) {
    traces.push({
      x: smoothT,
      y: exponentialCurve(smoothT, models.exponential.k),
      type: 'scatter',
      mode: 'lines',
      name: `Exponential (R²=${models.exponential.r_squared?.toFixed(2)})`,
      line: { color: '#4f8cff', dash: 'solid' },
    })
  }

  if (models.logistic.converged && models.logistic.k !== undefined && models.logistic.t0 !== undefined) {
    traces.push({
      x: smoothT,
      y: logisticCurve(smoothT, models.logistic.k, models.logistic.t0),
      type: 'scatter',
      mode: 'lines',
      name: `Logistic (R²=${models.logistic.r_squared?.toFixed(2)})`,
      line: { color: '#e3b341', dash: 'solid' },
    })
  }

  return (
    <div className="section">
      <SectionHeading
        title="Information Diffusion"
        subtitle="Two candidate curves fit to the fraction of the eventual cumulative abnormal return absorbed by each post-announcement trading day."
      />

      <div className="grid grid-4">
        <StatCard label="Better-fitting model" value={better ?? '—'} />
        <StatCard
          label="Exponential R²"
          value={models.exponential.r_squared !== undefined ? models.exponential.r_squared.toFixed(3) : '—'}
          sub={models.exponential.k !== undefined ? `k = ${models.exponential.k.toFixed(3)}` : undefined}
        />
        <StatCard
          label="Logistic R²"
          value={models.logistic.r_squared !== undefined ? models.logistic.r_squared.toFixed(3) : '—'}
          sub={models.logistic.k !== undefined ? `k = ${models.logistic.k.toFixed(3)}, t0 = ${models.logistic.t0?.toFixed(2)}` : undefined}
        />
        <StatCard
          label="Information absorption time"
          value={absorptionTimes.p90 !== null && absorptionTimes.p90 !== undefined ? `${absorptionTimes.p90.toFixed(2)}d → 90%` : '—'}
          sub={absorptionTimes.p50 !== null && absorptionTimes.p50 !== undefined ? `${absorptionTimes.p50.toFixed(2)}d → 50%` : undefined}
        />
      </div>

      <Card title="Observed absorption fraction vs. fitted diffusion models">
        <Plot
          data={traces}
          layout={{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#8b93a1', family: 'ui-monospace, monospace', size: 11 },
            margin: { l: 55, r: 20, t: 10, b: 45 },
            height: 340,
            xaxis: { gridcolor: '#1a2029', title: { text: 'Trading days since announcement (t=0)' } },
            yaxis: { gridcolor: '#1a2029', title: { text: 'Fraction of eventual CAR absorbed' } },
            legend: { orientation: 'h', y: -0.25 },
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: '100%' }}
        />
      </Card>

      <Card title="Model comparison">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th className="num">Converged</th>
                <th className="num">RMSE</th>
                <th className="num">MAE</th>
                <th className="num">R²</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Exponential absorption</td>
                <td className="num">{models.exponential.converged ? 'yes' : 'no'}</td>
                <td className="num">{models.exponential.rmse?.toFixed(4) ?? '—'}</td>
                <td className="num">{models.exponential.mae?.toFixed(4) ?? '—'}</td>
                <td className="num">{models.exponential.r_squared?.toFixed(4) ?? '—'}</td>
              </tr>
              <tr>
                <td>Logistic diffusion</td>
                <td className="num">{models.logistic.converged ? 'yes' : 'no'}</td>
                <td className="num">{models.logistic.rmse?.toFixed(4) ?? '—'}</td>
                <td className="num">{models.logistic.mae?.toFixed(4) ?? '—'}</td>
                <td className="num">{models.logistic.r_squared?.toFixed(4) ?? '—'}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p style={{ marginTop: 12, fontSize: 12, color: 'var(--text-faint)', lineHeight: 1.6 }}>
          The exponential model assumes absorption starts at 0% on the event day; because roughly
          {' '}{(observed.absorption_fraction[0] * 100).toFixed(0)}% of the eventual move was already
          realized by the close of the announcement-reaction day itself, that assumption does not hold
          well here — which is itself informative about how fast this particular market absorbed the
          news.
        </p>
      </Card>
    </div>
  )
}
