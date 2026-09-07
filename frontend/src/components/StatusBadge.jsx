import React from 'react';

export function StatusBadge({ status }) {
  let badgeStyle = "badge-answered";
  let statusText = "ANSWERED WITH CITATIONS";
  let icon = "🟢";

  if (status === "not_covered") {
    badgeStyle = "badge-not-covered";
    statusText = "NOT COVERED IN RULEBOOK";
    icon = "🟡";
  } else if (status === "conflict") {
    badgeStyle = "badge-conflict";
    statusText = "CONFLICTING PROVISIONS DETECTED";
    icon = "🔴";
  }

  return (
    <div className={`status-badge ${badgeStyle}`}>
      <span className="badge-icon">{icon}</span>
      <span className="badge-text">{statusText}</span>
    </div>
  );
}
