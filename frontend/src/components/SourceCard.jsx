import React from 'react';

export function SourceCard({ source, index }) {
  const similarityPct = Math.round(source.similarity * 100);
  
  return (
    <div className="source-card">
      <div className="source-header">
        <div className="source-title-group">
          <span className="source-number">#{index + 1}</span>
          <span className="source-section">{source.section}</span>
          <span className="source-title">{source.title}</span>
        </div>
        <div className="source-metrics">
          <span className="similarity-badge" title="Cosine Similarity Score">
            {similarityPct}% Match
          </span>
          <span className={`type-tag type-${source.source_type}`}>
            {source.source_type.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="source-meta">
        <span className="doc-name">📄 {source.document}</span>
        {source.page && <span className="page-number">Page {source.page}</span>}
      </div>

      <div className="source-passage">
        <blockquote className="passage-quote">
          "{source.passage}"
        </blockquote>
      </div>
    </div>
  );
}
