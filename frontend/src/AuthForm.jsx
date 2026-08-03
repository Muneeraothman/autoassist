import { useState } from 'react'

function AuthForm({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [forgotSent, setForgotSent] = useState(false)

  function switchMode(newMode) {
    setMode(newMode)
    setError(null)
    setForgotSent(false)
  }

  async function handleForgotSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email }),
      })
      if (!res.ok) {
        throw new Error('Failed to request password reset')
      }
      setForgotSent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleSubmit(e) {
    if (mode === 'forgot') {
      return handleForgotSubmit(e)
    }

    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const res = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg).join(', ')
          : data.detail
        throw new Error(detail || `Failed to ${mode === 'login' ? 'log in' : 'sign up'}`)
      }
      onAuthenticated(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (mode === 'forgot' && forgotSent) {
    return (
      <section className="card">
        <h2>Check your email</h2>
        <p className="muted">If that email is registered, a reset link has been sent.</p>
        <button type="button" className="link-button" onClick={() => switchMode('login')}>
          Back to login
        </button>
      </section>
    )
  }

  return (
    <section className="card">
      <h2>
        {mode === 'login' && 'Log in'}
        {mode === 'register' && 'Create an account'}
        {mode === 'forgot' && 'Reset your password'}
      </h2>
      <form onSubmit={handleSubmit} className="stacked-form">
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>
        {mode !== 'forgot' && (
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={mode === 'register' ? 8 : undefined}
              required
            />
          </label>
        )}
        <button type="submit" disabled={submitting}>
          {submitting
            ? 'Please wait...'
            : mode === 'login'
              ? 'Log in'
              : mode === 'register'
                ? 'Sign up'
                : 'Send reset link'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}

      {mode === 'login' && (
        <p className="muted">
          <button type="button" className="link-button" onClick={() => switchMode('forgot')}>
            Forgot password?
          </button>
        </p>
      )}

      {mode !== 'forgot' && (
        <p className="muted">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            type="button"
            className="link-button"
            onClick={() => switchMode(mode === 'login' ? 'register' : 'login')}
          >
            {mode === 'login' ? 'Sign up' : 'Log in'}
          </button>
        </p>
      )}

      {mode === 'forgot' && (
        <p className="muted">
          <button type="button" className="link-button" onClick={() => switchMode('login')}>
            Back to login
          </button>
        </p>
      )}
    </section>
  )
}

export default AuthForm
