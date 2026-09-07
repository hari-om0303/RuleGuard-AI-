import React from 'react';

export function QuestionExamples({ onSelectQuestion }) {
  const examples = [
    {
      label: "Answered Question",
      type: "normal",
      icon: "🟢",
      text: "What is the minimum overall CGPA required to graduate from an undergraduate program?"
    },
    {
      label: "Conflict Question",
      type: "conflict",
      icon: "🔴",
      text: "I have 68% attendance and an approved medical exemption. Am I eligible to sit for the semester examination?"
    },
    {
      label: "Not Covered Question",
      type: "not_covered",
      icon: "🟡",
      text: "What happens if I miss an end-semester examination because I had to attend a family wedding?"
    }
  ];

  return (
    <div className="examples-container">
      <span className="examples-title">Try Demo Questions:</span>
      <div className="examples-grid">
        {examples.map((item, idx) => (
          <button
            key={idx}
            type="button"
            className={`example-btn btn-${item.type}`}
            onClick={() => onSelectQuestion(item.text)}
          >
            <span className="example-icon">{item.icon}</span>
            <div className="example-text-wrapper">
              <span className="example-badge-label">{item.label}</span>
              <span className="example-query">"{item.text}"</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
