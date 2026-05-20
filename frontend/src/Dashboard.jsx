import React, { useEffect, useState } from 'react'
import { analyzeText, getModelInfo } from './api'

export default function Dashboard() {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [modelInfo, setModelInfo] = useState(null)

  useEffect(() => {
    let ignore = false

    async function loadModelInfo() {
      try {
        const data = await getModelInfo()
        if (!ignore) {
          setModelInfo(data)
        }
      } catch (err) {
        console.error(err)
      }
    }

    loadModelInfo()
    return () => {
      ignore = true
    }
  }, [])

  const loadExample = () => {
    setSubject('Urgent: verify your payroll account today')
    setBody(
      'Hello team member, your payroll profile has been suspended. Click the secure link below to verify your password and avoid delayed salary processing.'
    )
    setResult(null)
    setError('')
  }

  const clearForm = () => {
    setSubject('')
    setBody('')
    setResult(null)
    setError('')
  }

  const analyzeEmail = async () => {
    if (!subject || !body) return

    try {
      setLoading(true)
      setError('')
      const data = await analyzeText(subject, body)
      setResult(data)
    } catch (err) {
      console.error(err)
      setError('Analysis failed. Make sure the backend server is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  const percentage = result
    ? Math.round(result.spam_probability * 100)
    : 0

  return (
    <div className="dashboard-grid">
      <section className="panel panel-input">
        <div className="card-header">
          <div>
            <p className="section-kicker">Input</p>
            <h2>Email content</h2>
          </div>
          <span className="status-live">Manual review</span>
        </div>

        <label htmlFor="subject">Email subject</label>
        <input
          id="subject"
          type="text"
          placeholder="Quarterly bonus update"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />

        <label htmlFor="body">Email body</label>
        <textarea
          id="body"
          rows="10"
          placeholder="Paste the email body here for review."
          value={body}
          onChange={(e) => setBody(e.target.value)}
        />

        <div className="button-row">
          <button className="primary-button" onClick={analyzeEmail} disabled={loading}>
            {loading ? 'Reviewing message...' : 'Analyze message'}
          </button>
          <button className="secondary-button" onClick={loadExample} type="button">
            Load example
          </button>
          <button className="tertiary-button" onClick={clearForm} type="button">
            Clear
          </button>
        </div>

        {error ? <p className="error-text">{error}</p> : null}

        {modelInfo?.dataset_name && typeof modelInfo?.best_accuracy === 'number' ? (
          <div className="analysis-section">
            <h3>Training setup</h3>
            <div className="reason-chip neutral-chip">
              Dataset: {modelInfo.dataset_name}
            </div>
            <div className="reason-chip neutral-chip">
              Best model: {modelInfo.best_model} ({(modelInfo.best_accuracy * 100).toFixed(2)}% accuracy)
            </div>
          </div>
        ) : null}
      </section>

      <section className="panel panel-result">
        <div className="card-header">
          <div>
            <p className="section-kicker">Output</p>
            <h2>Analysis summary</h2>
          </div>
        </div>

        {!result ? (
          <div className="empty-state">
            <div className="empty-state-mark">S</div>
            <h3>Ready for a first pass</h3>
            <p>
              Run an analysis to see the spam probability, confidence level,
              and the reasons behind the model's decision.
            </p>
          </div>
        ) : (
          <>
            <div className="result-banner">
              <div>
                <p className="mini-label">Classification</p>
                <h1 className="result-title">
                  {result.is_spam
                    ? 'Likely spam'
                    : 'Looks safe'}
                </h1>
                <p className="result-summary">
                  {result.is_spam
                    ? 'This message contains language patterns that closely match spam samples.'
                    : 'The wording and structure look closer to a normal inbox message.'}
                </p>
              </div>

              <div className={`risk-score ${result.is_spam ? 'risk-high' : 'risk-low'}`}>
                <span>{percentage}%</span>
                <p>Spam score</p>
              </div>
            </div>

            <div className="progress-wrapper">
              <div
                className="progress-bar"
                style={{ width: `${percentage}%` }}
              ></div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card">
                <p className="mini-label">Spam probability</p>
                <p className="metric">
                  {(result.spam_probability * 100).toFixed(2)}%
                </p>
              </div>
              <div className="metric-card">
                <p className="mini-label">Confidence</p>
                <p className="metric">
                  {(result.confidence * 100).toFixed(2)}%
                </p>
              </div>
              <div className="metric-card">
                <p className="mini-label">Model used</p>
                <p className="metric metric-small">
                  {result.model_name || 'Saved classifier'}
                </p>
              </div>
            </div>

            <div className="analysis-section">
              <h3>Why the model said that</h3>

              {result.reasons?.map((reason, index) => (
                <div key={index} className="reason-chip">
                  {reason}
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  )
}
