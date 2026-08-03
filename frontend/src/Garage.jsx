import { useState } from 'react'

function Garage({ vehicles, selectedVehicleId, onSelectVehicle, onVehicleAdded }) {
  const [showAddForm, setShowAddForm] = useState(false)
  const [make, setMake] = useState('')
  const [model, setModel] = useState('')
  const [year, setYear] = useState('')
  const [vin, setVin] = useState('')
  const [currentMileage, setCurrentMileage] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await fetch('/api/vehicles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          make,
          model,
          year: Number(year),
          vin: vin || null,
          current_mileage: Number(currentMileage),
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg).join(', ')
          : data.detail
        throw new Error(detail || 'Failed to add vehicle')
      }
      setMake('')
      setModel('')
      setYear('')
      setVin('')
      setCurrentMileage('')
      setShowAddForm(false)
      onVehicleAdded(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="card">
      <h2>My Garage</h2>
      <label>
        Vehicle
        <select
          value={selectedVehicleId ?? ''}
          onChange={(e) => onSelectVehicle(Number(e.target.value))}
        >
          {vehicles.map((v) => (
            <option key={v.id} value={v.id}>
              {v.year} {v.make} {v.model}
            </option>
          ))}
        </select>
      </label>

      {!showAddForm && (
        <button type="button" onClick={() => setShowAddForm(true)} style={{ marginTop: 12 }}>
          Add a vehicle
        </button>
      )}

      {showAddForm && (
        <form onSubmit={handleSubmit} className="stacked-form">
          <label>
            Make
            <input type="text" value={make} onChange={(e) => setMake(e.target.value)} required />
          </label>
          <label>
            Model
            <input type="text" value={model} onChange={(e) => setModel(e.target.value)} required />
          </label>
          <label>
            Year
            <input type="number" value={year} onChange={(e) => setYear(e.target.value)} required />
          </label>
          <label>
            VIN (optional)
            <input type="text" value={vin} onChange={(e) => setVin(e.target.value)} />
          </label>
          <label>
            Current mileage
            <input
              type="number"
              value={currentMileage}
              onChange={(e) => setCurrentMileage(e.target.value)}
              required
            />
          </label>
          <div className="inline-form">
            <button type="submit" disabled={submitting}>
              {submitting ? 'Adding...' : 'Add vehicle'}
            </button>
            <button type="button" onClick={() => setShowAddForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  )
}

export default Garage
