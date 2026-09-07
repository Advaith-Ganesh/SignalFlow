import type { ReactNode } from 'react'

export function StatCard({
  label,
  value,
  sub,
  valueClassName,
}: {
  label: string
  value: ReactNode
  sub?: ReactNode
  valueClassName?: string
}) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className={`stat-value ${valueClassName ?? ''}`}>{value}</div>
      {sub ? <div className="stat-sub">{sub}</div> : null}
    </div>
  )
}

export function Card({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <div className="card">
      {title ? <div className="card-title">{title}</div> : null}
      {children}
    </div>
  )
}

export function SectionHeading({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="section-heading">
      <h2 className="section-title">{title}</h2>
      <p className="section-subtitle">{subtitle}</p>
    </div>
  )
}

export function StateMessage({ children, error }: { children: ReactNode; error?: boolean }) {
  return <div className={`state-message ${error ? 'error' : ''}`}>{children}</div>
}

export function Badge({ label, tone }: { label: string; tone: 'positive' | 'negative' | 'neutral' }) {
  return <span className={`badge badge-${tone}`}>{label}</span>
}
