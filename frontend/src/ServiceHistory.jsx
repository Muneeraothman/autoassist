import { useState, useEffect } from 'react'

function ServiceHistory({ vehicleId, scheduleItems, refreshKey }) {
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    setLoading(true)
    const base = `/api/vehicles/${vehicleId}/services`
    const url = filter ? `${base}?schedule_item_id=${filter}` : base
    fetch(url, { credentials: 'include' })
      .then((res) => res.json())
      .then(setServices)
      .finally(() => setLoading(false))
  }, [vehicleId, filter, refreshKey])

  function nameForScheduleItem(id) {
    const item = scheduleItems.find((i) => i.id === id)
    return item ? item.service_name : 'Other / Repair'
  }

  return (
    <section className="card">
      <h2>Service History</h2>
      <label>
        Filter by type
        <select value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">All</option>
          {scheduleItems.map((item) => (
            <option key={item.id} value={item.id}>
              {item.service_name}
            </option>
          ))}
        </select>
      </label>
      {loading ? (
        <p className="muted">Loading history...</p>
      ) : services.length === 0 ? (
        <p className="muted">No service records yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Mileage</th>
              <th>Cost</th>
              <th>Performed by</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {services.map((service) => (
              <tr key={service.id}>
                <td>{service.service_date}</td>
                <td>{nameForScheduleItem(service.schedule_item_id)}</td>
                <td>{service.mileage_at_service.toLocaleString()}</td>
                <td>{service.cost != null ? `$${service.cost.toFixed(2)}` : '—'}</td>
                <td>{service.performed_by || '—'}</td>
                <td>{service.notes || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

export default ServiceHistory
