import { useState } from 'react'
import axios from 'axios'

export default function Dashboard() {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const analyzeEmail = async () => {
    if (!subject || !body) return

    try {
      setLoading(true)

      const response = await axios.post('http://127.0.0.1:8000/analyze', {
        subject,
        body,
      })

      setResult(response.data)
    } catch (err) {
      console.error(err)
      alert('Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const percentage = result
    ? Math.round(result.spam_probability * 100)
    : 0

  return (
    <div className="dashboard-grid">
      <div className="glass-card input-card">
        <div className="card-header">
          <h2>Email Scanner</h2>
          <span className="status-live">LIVE</span>
        </div>

        <label>Email Subject</label>
        <input
          type="text"
          placeholder="Enter suspicious email subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />

        <label>Email Body</label>
        <textarea
          rows="10"
          placeholder="Paste email content here"
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />

        <button onClick={analyzeEmail} disabled={loading}>
          {loading ? 'Analyzing Threat...' : 'Analyze Email'}
        </button>
      </div>

      <div className="glass-card result-card">
        <div className="card-header">
          <h2>Threat Analysis</h2>
        </div>

        {!result ? (
          <div className="empty-state">
            <div className="scanner-circle"></div>
            <p>No email analyzed yet.</p>
          </div>
        ) : (
          <>
            <div className="threat-banner">
              <div>
                <p className="mini-label">Classification</p>

                <h1>
                  {result.is_spam
                    ? '⚠ Spam Detected'
                    : '✔ Safe Email'}
                </h1>
              </div>

              <div className="risk-score">
                <span>{percentage}%</span>
                <p>Threat Score</p>
              </div>
            </div>

            <div className="progress-wrapper">
              <div
                className="progress-bar"
                style={{ width: `${percentage}%` }}
              ></div>
            </div>

            <div className="analysis-section">
              <h3>AI Reasoning</h3>

              {result.reasons?.map((reason, index) => (
                <div key={index} className="reason-chip">
                  {reason}
                </div>
              ))}
            </div>

            <div className="analysis-section">
              <h3>Spam Probability</h3>
              <p className="metric">
                {(result.spam_probability * 100).toFixed(2)}%
              </p>
            </div>

            <div className="analysis-section">
              <h3>Confidence Level</h3>
              <p className="metric">
                {(result.confidence * 100).toFixed(2)}%
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}