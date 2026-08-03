import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function formatCurrency(value) {
  return Number(value).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}

const tooltipStyle = {
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  color: 'var(--text-h)',
}

function SpendingDashboard({ vehicleId, refreshKey }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/vehicles/${vehicleId}/stats`, { credentials: 'include' })
      .then((res) => res.json())
      .then(setStats)
      .finally(() => setLoading(false))
  }, [vehicleId, refreshKey])

  if (loading) {
    return (
      <section className="card">
        <h2>Spending Dashboard</h2>
        <p className="muted">Loading...</p>
      </section>
    )
  }

  if (!stats || stats.spend_by_category.length === 0) {
    return (
      <section className="card">
        <h2>Spending Dashboard</h2>
        <p className="muted">No service history yet — log a service to see spending data.</p>
      </section>
    )
  }

  return (
    <section className="card">
      <h2>Spending Dashboard</h2>
      <p>
        Total spend: <strong>{formatCurrency(stats.total_spend)}</strong>
        {stats.cost_per_mile !== null && (
          <span className="muted"> ({formatCurrency(stats.cost_per_mile)}/mi since first record)</span>
        )}
      </p>

      <p className="chart-label">Spend by category</p>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={Math.max(200, stats.spend_by_category.length * 36)}>
          <BarChart data={stats.spend_by_category} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid stroke="var(--border)" horizontal={false} />
            <XAxis type="number" stroke="var(--text)" tickFormatter={formatCurrency} />
            <YAxis type="category" dataKey="category" stroke="var(--text)" width={180} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => formatCurrency(value)} contentStyle={tooltipStyle} />
            <Bar dataKey="total" fill="var(--accent)" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="chart-label">Spend by year</p>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={stats.spend_by_year} margin={{ left: 8, right: 16 }}>
            <CartesianGrid stroke="var(--border)" />
            <XAxis dataKey="year" stroke="var(--text)" />
            <YAxis stroke="var(--text)" tickFormatter={formatCurrency} width={70} />
            <Tooltip formatter={(value) => formatCurrency(value)} contentStyle={tooltipStyle} />
            <Line type="monotone" dataKey="total" stroke="var(--accent)" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}

export default SpendingDashboard
