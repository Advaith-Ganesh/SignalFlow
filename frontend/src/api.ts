// Thin fetch wrapper + TypeScript types for the SignalFlow research API.
// Every type here mirrors the JSON shape returned by backend/app/routers/*.py.

export interface EarningsSurprise {
  eps_actual: number
  eps_estimate: number
  eps_surprise_pct: number
  revenue_actual_usd_billion: number
  revenue_estimate_usd_billion: number
  revenue_surprise_pct: number
  direction: 'beat' | 'miss' | 'in-line'
}

export interface EventFacts {
  ticker: string
  company_name: string
  fiscal_quarter: string
  announcement_date: string
  event_day: string
  announcement_time: string
  announcement_context: string
  dau_billion: number
  dau_estimate_billion: number
  dau_qoq_change: string
  mau_billion: number
  mau_estimate_billion: number
  q1_2022_revenue_guidance_low_usd_billion: number
  q1_2022_revenue_guidance_high_usd_billion: number
  q1_2022_revenue_consensus_usd_billion: number
  stated_headwinds: string[]
  close_2022_02_02: number
  close_2022_02_03: number
  one_day_return_2022_02_03_pct: number
  approx_market_cap_lost_usd_billion: number
  market_cap_loss_note: string
  reason_for_selecting_event: string
  sources: { publisher: string; title: string; url: string; date: string }[]
}

export interface EventOverviewResponse {
  event: EventFacts
  earnings_surprise: EarningsSurprise
}

export interface DailyEventRecord {
  date: string
  relative_day: number
  return_company: number
  return_benchmark: number
  expected_return: number
  abnormal_return: number
  cumulative_abnormal_return: number
  abnormal_volume_ratio: number
  ar_t_stat: number
  ar_p_value: number
  volume_company: number
}

export interface EventStudyResponse {
  market_model: {
    alpha: number
    beta: number
    resid_std: number
    n_obs: number
    r_squared: number
    estimation_window: [number, number]
  }
  event_window: [number, number]
  daily: DailyEventRecord[]
  summary: {
    car_full_window: number
    mean_pre_event_return: number | null
    mean_post_event_return: number | null
    volatility_pre_event: number | null
    volatility_post_event: number | null
    volatility_estimation_window: number
    max_abs_abnormal_return: { relative_day: number; date: string; value: number }
    max_abs_cumulative_abnormal_return: { relative_day: number; date: string; value: number }
    event_day_abnormal_return: number
    event_day_t_stat: number
    event_day_p_value: number
    event_day_abnormal_volume_ratio: number
  }
}

export interface HeadlineRecord {
  date: string
  time_et: string | null
  phase: string
  source: string
  headline: string
  url: string
  sentiment_compound: number
  sentiment_positive: number
  sentiment_negative: number
  sentiment_label: 'positive' | 'negative' | 'neutral'
}

export interface DailyIntensityRecord {
  date_str: string
  article_count: number
  mean_sentiment: number
}

export interface NewsResponse {
  headlines: HeadlineRecord[]
  daily_intensity: DailyIntensityRecord[]
}

export interface DiffusionModelFit {
  converged: boolean
  k?: number
  t0?: number
  rmse?: number
  mae?: number
  r_squared?: number
  error?: string
}

export interface DiffusionResponse {
  observed: {
    relative_day: number[]
    cumulative_abnormal_return: number[]
    eventual_car: number
    absorption_fraction: number[]
  }
  models: {
    exponential: DiffusionModelFit
    logistic: DiffusionModelFit
  }
  better_fit_model: 'exponential' | 'logistic' | null
  information_absorption_time_trading_days: Record<string, number | null>
}

export interface HypothesisResult {
  hypothesis: string
  statement: string
  variables: Record<string, unknown>
  method: string
  statistic: Record<string, unknown>
  supported: boolean
  conclusion: string
}

export interface HypothesesResponse {
  hypotheses: HypothesisResult[]
}

export interface Limitation {
  title: string
  detail: string
}

export interface LimitationsResponse {
  limitations: Limitation[]
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`)
  }
  return (await response.json()) as T
}

export const api = {
  getEventOverview: () => fetchJson<EventOverviewResponse>('/api/event'),
  getEventStudy: () => fetchJson<EventStudyResponse>('/api/market/event-study'),
  getNews: () => fetchJson<NewsResponse>('/api/news'),
  getDiffusion: () => fetchJson<DiffusionResponse>('/api/diffusion'),
  getHypotheses: () => fetchJson<HypothesesResponse>('/api/results/hypotheses'),
  getLimitations: () => fetchJson<LimitationsResponse>('/api/results/limitations'),
}
