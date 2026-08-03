import { useState } from 'react'

const MAX_FILE_BYTES = 5 * 1024 * 1024

function ReceiptCell({ vehicleId, serviceId, hasReceipt, onUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [viewLoading, setViewLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleFileChange(e) {
    const file = e.target.files[0]
    e.target.value = ''
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setError('Only image files are allowed')
      return
    }
    if (file.size > MAX_FILE_BYTES) {
      setError('File must be under 5MB')
      return
    }

    setUploading(true)
    setError(null)
    try {
      const urlRes = await fetch(
        `/api/vehicles/${vehicleId}/services/${serviceId}/receipt-upload-url`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ content_type: file.type }),
        }
      )
      const urlData = await urlRes.json()
      if (!urlRes.ok) {
        const detail = Array.isArray(urlData.detail)
          ? urlData.detail.map((d) => d.msg).join(', ')
          : urlData.detail
        throw new Error(detail || 'Failed to get upload URL')
      }

      const putRes = await fetch(urlData.upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      })
      if (!putRes.ok) {
        throw new Error('Upload to S3 failed')
      }

      onUploaded()
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  async function handleView() {
    setViewLoading(true)
    setError(null)
    try {
      const res = await fetch(`/api/vehicles/${vehicleId}/services/${serviceId}/receipt-url`, {
        credentials: 'include',
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to get receipt link')
      }
      window.open(data.url, '_blank', 'noopener,noreferrer')
    } catch (err) {
      setError(err.message)
    } finally {
      setViewLoading(false)
    }
  }

  if (hasReceipt) {
    return (
      <div>
        <button type="button" onClick={handleView} disabled={viewLoading}>
          {viewLoading ? 'Loading...' : 'View'}
        </button>
        {error && <p className="error">{error}</p>}
      </div>
    )
  }

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleFileChange} disabled={uploading} />
      {uploading && <span className="muted"> Uploading...</span>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default ReceiptCell
