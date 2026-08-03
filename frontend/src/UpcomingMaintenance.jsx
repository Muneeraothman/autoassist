import { useEffect, useState } from 'react'

const STATUS_LABELS = {
  OVERDUE: 'Overdue',
  DUE_SOON: 'Due soon',
  OK: 'OK',
}

function formatDueText(entry) {
  const parts = []

  if (entry.miles_remaining !== null) {
    const miles = Math.round(Math.abs(entry.miles_remaining))
    parts.push(
      entry.miles_remaining >= 0
        ? `due in ~${miles.toLocaleString()} mi`
        : `${miles.toLocaleString()} mi overdue`
    )
  }

  if (entry.due_date) {
    parts.push(`by ${entry.due_date}`)
  }

  return parts.length > 0 ? parts.join(' / ') : 'No projection available'
}

function UpcomingMaintenance({ vehicleId, refreshKey }) {
  const [items, setItems] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`/api/vehicles/${vehicleId}/upcoming`, { credentials: 'include' })
      .then((res) => res.json())
      .then(setItems)
      .finally(() => setLoading(false))
  }, [vehicleId, refreshKey])

  return (
    <section className="card">
      <h2>Upcoming Maintenance</h2>
      {loading && <p className="muted">Loading...</p>}
      {!loading && (!items || items.length === 0) && (
        <p className="muted">No schedule items found.</p>
      )}
      {!loading && items && items.length > 0 && (
        <div className="upcoming-list">
          {items.map((entry) => (
            <div
              key={entry.schedule_item.id}
              className={`upcoming-item status-${entry.status.toLowerCase()}`}
            >
              <div className="upcoming-item-header">
                <span className="upcoming-item-name">{entry.schedule_item.service_name}</span>
                <span className="status-badge">{STATUS_LABELS[entry.status]}</span>
              </div>
              <p className="muted">{formatDueText(entry)}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

export default UpcomingMaintenance
