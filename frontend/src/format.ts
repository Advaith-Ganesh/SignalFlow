export function formatPct(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return `${(value * 100).toFixed(decimals)}%`
}

export function formatPctPoints(value: number | null | undefined, decimals = 2): string {
  // For values already expressed in percentage points (e.g. earnings surprise %).
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return `${value.toFixed(decimals)}%`
}

export function formatNumber(value: number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return value.toFixed(decimals)
}

export function formatUsdBillion(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  return `$${value.toFixed(2)}B`
}

export function formatVolume(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`
  return String(value)
}

export function signClass(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return 'neutral'
  return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral'
}
