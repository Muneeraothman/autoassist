import { useState } from 'react'

function VehicleCard({ vehicle, loading, onMileageUpdated }) {
  const [mileageInput, setMileageInput] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  if (loading) {
    return (
      <section className="card">
        <p className="muted">Loading vehicle...</p>
      </section>
    )
  }

  if (!vehicle) {
    return (
      <section className="card">
        <p className="muted">No vehicle found.</p>
      </section>
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await fetch('/api/vehicle/mileage', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mileage: Number(mileageInput) }),
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to update mileage')
      }
      setMileageInput('')
      await onMileageUpdated()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card">
      <h2>
        {vehicle.year} {vehicle.make} {vehicle.model}
      </h2>
      <p>Current mileage: {vehicle.current_mileage.toLocaleString()} mi</p>
      <p className="muted">~{vehicle.avg_miles_per_day} mi/day average</p>
      <form onSubmit={handleSubmit} className="inline-form">
        <input
          type="number"
          placeholder="New mileage"
          value={mileageInput}
          onChange={(e) => setMileageInput(e.target.value)}
          required
        />
        <button type="submit" disabled={submitting}>
          {submitting ? 'Updating...' : 'Update mileage'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  )
}

export default VehicleCard
