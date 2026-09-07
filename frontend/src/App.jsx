import React, { useState } from 'react';
import { StatusBadge } from './components/StatusBadge';
import { SourceCard } from './components/SourceCard';
import { QuestionExamples } from './components/QuestionExamples';
import './index.css';

export default function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAsk = async (queryToSubmit) => {
    const q = queryToSubmit || question;
    if (!q || !q.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned status ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to connect to RuleGuard AI backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleAsk();
  };

  const handleSelectExample = (text) => {
    setQuestion(text);
    handleAsk(text);
  };

  return (
    <div className="app-container">
      {/* Header Banner */}
      <header className="app-header">
        <div className="header-brand">
          <div className="brand-logo">🛡️</div>
          <div>
            <h1 className="brand-title">RuleGuard AI</h1>
            <p className="brand-subtitle">Evidence-Based University Regulation Assistant</p>
          </div>
        </div>
        <div className="corpus-tag">
          🏛️ Northbridge Institute of Technology Corpus
        </div>
      </header>

      {/* Main Content Card */}
      <main className="main-content">
        {/* Question Form */}
        <section className="search-section">
          <form onSubmit={handleSubmit} className="search-form">
            <label htmlFor="question-input" className="form-label">
              Ask a Regulation Question:
            </label>
            <div className="input-row">
              <input
                id="question-input"
                type="text"
                className="question-input"
                placeholder="e.g. Can I sit for the exam with 68% attendance?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={loading}
              />
              <button
                type="submit"
                className="submit-btn"
                disabled={loading || !question.trim()}
              >
                {loading ? (
                  <span className="spinner-label">Analyzing...</span>
                ) : (
                  <span>Ask RuleGuard</span>
                )}
              </button>
            </div>
          </form>

          {/* Quick Demo Examples */}
          <QuestionExamples onSelectQuestion={handleSelectExample} />
        </section>

        {/* Error Alert */}
        {error && (
          <div className="error-alert">
            <span className="error-icon">⚠️</span>
            <div className="error-body">
              <strong>Backend Connection Error:</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="loading-card">
            <div className="spinner"></div>
            <p>Scanning university regulation index & evaluating evidence...</p>
          </div>
        )}

        {/* Results Container */}
        {response && !loading && (
          <section className={`results-section status-${response.status}`}>
            {/* Status Header */}
            <div className="response-status-bar">
              <StatusBadge status={response.status} />
              <span className="source-count-label">
                {response.sources.length} {response.sources.length === 1 ? 'Source Cited' : 'Sources Cited'}
              </span>
            </div>

            {/* Grounded Answer Panel */}
            <div className="answer-panel">
              <h2 className="answer-heading">Official Guidance Response</h2>
              <div className="answer-text">
                {response.answer.split('\n').map((line, idx) => (
                  <p key={idx}>{line}</p>
                ))}
              </div>
            </div>

            {/* Sources & Citations Display (MUST BE VISIBLE DIRECTLY) */}
            <div className="sources-section">
              <div className="sources-header-bar">
                <h3 className="sources-heading">
                  Retrieved Passages & Section Citations
                </h3>
                <p className="sources-subtext">
                  Direct evidence extracted from official NIT regulations, sorted by similarity relevance.
                </p>
              </div>

              {response.sources.length > 0 ? (
                <div className="sources-grid">
                  {response.sources.map((src, index) => (
                    <SourceCard key={index} source={src} index={index} />
                  ))}
                </div>
              ) : (
                <div className="no-sources-card">
                  No relevant passage evidence found in the university rulebook corpus.
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>RuleGuard AI — University Academic Regulation Verification Engine</p>
      </footer>
    </div>
  );
}
