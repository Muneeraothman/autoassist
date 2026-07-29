import { useState, useEffect, useCallback } from 'react'
import VehicleCard from './VehicleCard'
import LogServiceForm from './LogServiceForm'
import ServiceHistory from './ServiceHistory'
import './App.css'

function App() {
  const [vehicle, setVehicle] = useState(null)
  const [vehicleLoading, setVehicleLoading] = useState(true)
  const [scheduleItems, setScheduleItems] = useState([])
  const [historyRefreshKey, setHistoryRefreshKey] = useState(0)

  const fetchVehicle = useCallback(() => {
    setVehicleLoading(true)
    return fetch('/api/vehicle')
      .then((res) => res.json())
      .then(setVehicle)
      .finally(() => setVehicleLoading(false))
  }, [])

  useEffect(() => {
    fetchVehicle()
    fetch('/api/schedule')
      .then((res) => res.json())
      .then(setScheduleItems)
  }, [fetchVehicle])

  return (
    <div className="app">
      <h1>AutoAssist</h1>
      <VehicleCard vehicle={vehicle} loading={vehicleLoading} onMileageUpdated={fetchVehicle} />
      <LogServiceForm
        scheduleItems={scheduleItems}
        currentMileage={vehicle?.current_mileage}
        onServiceLogged={() => setHistoryRefreshKey((key) => key + 1)}
      />
      <ServiceHistory scheduleItems={scheduleItems} refreshKey={historyRefreshKey} />
    </div>
  )
}

export default App
