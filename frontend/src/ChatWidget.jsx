import { useState } from 'react'

function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    const nextMessages = [...messages, { role: 'user', content: text }]
    setMessages(nextMessages)
    setInput('')
    setSending(true)
    setError('')

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ messages: nextMessages }),
      })
      if (!res.ok) throw new Error('Chat request failed')
      const data = await res.json()
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setError('Something went wrong - try again.')
    } finally {
      setSending(false)
    }
  }

  if (!open) {
    return (
      <button type="button" className="chat-fab" onClick={() => setOpen(true)}>
        Ask AutoAssist
      </button>
    )
  }

  return (
    <div className="chat-widget card">
      <div className="chat-widget-header">
        <h2>Ask AutoAssist</h2>
        <button type="button" className="link-button" onClick={() => setOpen(false)}>
          Close
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="muted">
            Ask about your vehicle's upcoming maintenance, service history, or spending.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-message chat-message-${m.role}`}>
            {m.content}
          </div>
        ))}
        {sending && <p className="muted">Thinking...</p>}
      </div>

      {error && <p className="error">{error}</p>}

      <form className="inline-form" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. What's overdue on my Lexus?"
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

export default ChatWidget
