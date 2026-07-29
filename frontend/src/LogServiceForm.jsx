import { useState, useEffect } from 'react'

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

function LogServiceForm({ scheduleItems, currentMileage, onServiceLogged }) {
  const [scheduleItemId, setScheduleItemId] = useState('')
  const [serviceDate, setServiceDate] = useState(todayISO)
  const [mileage, setMileage] = useState('')
  const [mileageTouched, setMileageTouched] = useState(false)
  const [cost, setCost] = useState('')
  const [performedBy, setPerformedBy] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (currentMileage != null && !mileageTouched) {
      setMileage(String(currentMileage))
    }
  }, [currentMileage, mileageTouched])

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setSuccess(false)
    try {
      const res = await fetch('/api/services', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          schedule_item_id: scheduleItemId === '' ? null : Number(scheduleItemId),
          service_date: serviceDate,
          mileage_at_service: Number(mileage),
          cost: cost === '' ? null : Number(cost),
          performed_by: performedBy || null,
          notes: notes || null,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg).join(', ')
          : data.detail
        throw new Error(detail || 'Failed to log service')
      }
      setScheduleItemId('')
      setCost('')
      setPerformedBy('')
      setNotes('')
      setMileageTouched(false)
      setSuccess(true)
      onServiceLogged()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card">
      <h2>Log a Service</h2>
      <form onSubmit={handleSubmit} className="stacked-form">
        <label>
          Service type
          <select value={scheduleItemId} onChange={(e) => setScheduleItemId(e.target.value)}>
            <option value="">Other / Repair</option>
            {scheduleItems.map((item) => (
              <option key={item.id} value={item.id}>
                {item.service_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Date
          <input
            type="date"
            value={serviceDate}
            onChange={(e) => setServiceDate(e.target.value)}
            required
          />
        </label>
        <label>
          Mileage
          <input
            type="number"
            value={mileage}
            onChange={(e) => {
              setMileage(e.target.value)
              setMileageTouched(true)
            }}
            required
          />
        </label>
        <label>
          Cost
          <input type="number" step="0.01" value={cost} onChange={(e) => setCost(e.target.value)} />
        </label>
        <label>
          Performed by
          <input type="text" value={performedBy} onChange={(e) => setPerformedBy(e.target.value)} />
        </label>
        <label>
          Notes
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Saving...' : 'Log service'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {success && <p className="success">Service logged.</p>}
    </section>
  )
}

export default LogServiceForm
