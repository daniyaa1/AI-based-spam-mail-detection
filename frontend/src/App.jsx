import Dashboard from "./Dashboard";
import './index.css'

function App() {
  return (
    <div className="app-shell">
      <div className="background-glow"></div>

      <header className="hero">
        <div>
          <p className="tag">AI Powered Cybersecurity</p>
          <h1>MailShield AI</h1>
          <p className="subtitle">
            Intelligent spam and phishing detection using Machine Learning and NLP.
          </p>
        </div>

        <div className="hero-badge">
          <span className="pulse"></span>
          Real-Time Threat Analysis
        </div>
      </header>

      <Dashboard />
    </div>
  )
}

export default App