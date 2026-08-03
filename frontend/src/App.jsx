import { useState, useEffect, useCallback } from 'react'
import AuthForm from './AuthForm'
import ResetPasswordForm from './ResetPasswordForm'
import Garage from './Garage'
import VehicleCard from './VehicleCard'
import LogServiceForm from './LogServiceForm'
import ServiceHistory from './ServiceHistory'
import UpcomingMaintenance from './UpcomingMaintenance'
import SpendingDashboard from './SpendingDashboard'
import './App.css'

function App() {
  const [resetToken] = useState(() => new URLSearchParams(window.location.search).get('reset_token'))
  const [resetDone, setResetDone] = useState(false)

  const [authChecked, setAuthChecked] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  const [vehicles, setVehicles] = useState([])
  const [selectedVehicleId, setSelectedVehicleId] = useState(null)

  const [vehicle, setVehicle] = useState(null)
  const [vehicleLoading, setVehicleLoading] = useState(true)
  const [scheduleItems, setScheduleItems] = useState([])
  const [historyRefreshKey, setHistoryRefreshKey] = useState(0)

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : null))
      .then(setCurrentUser)
      .finally(() => setAuthChecked(true))
  }, [])

  const fetchVehicles = useCallback(() => {
    return fetch('/api/vehicles', { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => {
        setVehicles(data)
        setSelectedVehicleId((current) => current ?? (data.length > 0 ? data[0].id : null))
        return data
      })
  }, [])

  useEffect(() => {
    if (currentUser) {
      fetchVehicles()
    }
  }, [currentUser, fetchVehicles])

  const fetchVehicle = useCallback(() => {
    if (!selectedVehicleId) return Promise.resolve()
    setVehicleLoading(true)
    return fetch(`/api/vehicles/${selectedVehicleId}`, { credentials: 'include' })
      .then((res) => res.json())
      .then(setVehicle)
      .finally(() => setVehicleLoading(false))
  }, [selectedVehicleId])

  const handleMileageUpdated = useCallback(async () => {
    await fetchVehicle()
    setHistoryRefreshKey((key) => key + 1)
  }, [fetchVehicle])

  useEffect(() => {
    if (!selectedVehicleId) return
    fetchVehicle()
    fetch(`/api/vehicles/${selectedVehicleId}/schedule`, { credentials: 'include' })
      .then((res) => res.json())
      .then(setScheduleItems)
  }, [selectedVehicleId, fetchVehicle])

  async function handleLogout() {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    setCurrentUser(null)
    setVehicles([])
    setSelectedVehicleId(null)
    setVehicle(null)
  }

  if (resetToken && !resetDone) {
    return (
      <div className="app">
        <h1>AutoAssist</h1>
        <ResetPasswordForm
          token={resetToken}
          onDone={() => {
            setResetDone(true)
            window.history.replaceState({}, '', window.location.pathname)
          }}
        />
      </div>
    )
  }

  if (!authChecked) {
    return (
      <div className="app">
        <h1>AutoAssist</h1>
        <p className="muted">Loading...</p>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="app">
        <h1>AutoAssist</h1>
        <AuthForm onAuthenticated={setCurrentUser} />
      </div>
    )
  }

  return (
    <div className="app">
      <div className="app-header">
        <h1>AutoAssist</h1>
        <div className="app-header-right">
          <span className="muted">{currentUser.email}</span>
          <button type="button" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </div>

      <Garage
        vehicles={vehicles}
        selectedVehicleId={selectedVehicleId}
        onSelectVehicle={setSelectedVehicleId}
        onVehicleAdded={(newVehicle) => {
          setVehicles((prev) => [...prev, newVehicle])
          setSelectedVehicleId(newVehicle.id)
        }}
      />

      {selectedVehicleId && (
        <>
          <VehicleCard
            vehicle={vehicle}
            vehicleId={selectedVehicleId}
            loading={vehicleLoading}
            onMileageUpdated={handleMileageUpdated}
          />
          <UpcomingMaintenance vehicleId={selectedVehicleId} refreshKey={historyRefreshKey} />
          <LogServiceForm
            vehicleId={selectedVehicleId}
            scheduleItems={scheduleItems}
            currentMileage={vehicle?.current_mileage}
            onServiceLogged={() => setHistoryRefreshKey((key) => key + 1)}
          />
          <ServiceHistory
            vehicleId={selectedVehicleId}
            scheduleItems={scheduleItems}
            refreshKey={historyRefreshKey}
          />
          <SpendingDashboard vehicleId={selectedVehicleId} refreshKey={historyRefreshKey} />
        </>
      )}
    </div>
  )
}

export default App
