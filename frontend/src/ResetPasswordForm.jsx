import { useState } from 'react'

function ResetPasswordForm({ token, onDone }) {
  const [newPassword, setNewPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ token, new_password: newPassword }),
      })
      const data = await res.json()
      if (!res.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg).join(', ')
          : data.detail
        throw new Error(detail || 'Failed to reset password')
      }
      setSuccess(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <section className="card">
        <h2>Password reset</h2>
        <p className="success">Your password has been reset. You can now log in.</p>
        <button type="button" onClick={onDone}>
          Go to login
        </button>
      </section>
    )
  }

  return (
    <section className="card">
      <h2>Set a new password</h2>
      <form onSubmit={handleSubmit} className="stacked-form">
        <label>
          New password
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength={8}
            required
          />
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Resetting...' : 'Reset password'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  )
}

export default ResetPasswordForm
