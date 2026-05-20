import React from 'react'
import Dashboard from "./Dashboard";
import './index.css'

function App() {
  return (
    <div className="app-shell">
      <div className="page-orb page-orb-left"></div>
      <div className="page-orb page-orb-right"></div>

      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Inbox Risk Review</p>
          <h1>Spot suspicious emails without the security-theater UI.</h1>
          <p className="subtitle">
            Paste a subject line and email body, then review the spam score,
            supporting signals, and the model's confidence in plain language.
          </p>
        </div>

        <div className="hero-stats">
          <div className="stat-card">
            <span className="stat-label">Model</span>
            <strong>Naive Bayes + TF-IDF</strong>
          </div>
          <div className="stat-card">
            <span className="stat-label">Response</span>
            <strong>Real-time analysis</strong>
          </div>
        </div>
      </header>

      <Dashboard />
    </div>
  )
}

export default App
