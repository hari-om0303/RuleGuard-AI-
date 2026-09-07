# RuleGuard AI — Project Presentation & Evaluation Defense

This document provides a natural, conversational 3–4 minute speech designed for presenting and defending **RuleGuard AI** during technical evaluations and interview presentations, followed by a concise 30-second elevator pitch.

---

## 3–4 Minute Main Presentation Speech

"Hello everyone. Today I'm excited to present **RuleGuard AI**, an evidence-based AI assistant built to solve a critical flaw in standard AI chatbots: **hallucination and ungrounded confidence when answering strict regulations**.

In academic institutions, universities, and compliance-heavy environments, students and faculty often ask questions about complex rulebooks. Generic chatbots like standard ChatGPT have two huge dangers:
1. They confidently invent policies that don't exist in the rulebook, leading to wrong student decisions.
2. When rules in a multi-part regulation contradict each other, chatbots arbitrarily pick one rule as truth without informing the user.

We call this challenge **'The Rulebook That Argues With Itself'**. To solve this, I built **RuleGuard AI** from scratch using a strict, evidence-backed Retrieval-Augmented Generation (RAG) architecture.

### How RuleGuard AI Works

RuleGuard AI ingests a synthetic 6,500+ word university regulation corpus from the *Northbridge Institute of Technology*. The corpus spans mixed document formats: Markdown manuals, fee deadline tables in CSV format, and emergency provision PDF handbooks.

Every single document passage is split into metadata-aware chunks preserving section numbers (like Section 4.2 or Section 7.4), document titles, and page numbers. We generate local vector embeddings and store them in a lightweight JSON vector index.

When a user asks a question, RuleGuard AI executes a multi-stage evaluation pipeline:

1. **Cosine Similarity Retrieval**: It embeds the user query and retrieves top candidate passages based on semantic vector similarity.
2. **NOT_COVERED Detection**: If the query asks about a topic outside the corpus—such as missing an exam due to a family wedding or transferring attendance across semesters—the system evaluates relevance thresholds and keyword boundaries. Rather than inventing a rule, it returns a clear `NOT_COVERED` status, stating: *"The rulebook does not provide a specific provision covering this topic."*
3. **Conflict Detection**: This is the core innovation. We intentionally planted three genuine contradictions in the university corpus—such as Section 4.2 requiring 75% attendance for exams versus Section 7.4 allowing medical exemptions down to 65%. When a query triggers conflicting provisions, RuleGuard AI flags a `CONFLICT` status. Instead of choosing a winner, it displays BOTH conflicting sections side-by-side and explains why the rulebook argues with itself.
4. **Grounded Answer Generation**: If sufficient, consistent evidence exists, it returns an `ANSWERED` status with an answer strictly grounded in the retrieved passages.

### The User Experience

In the React frontend, every answer displays:
- A prominent status badge: 🟢 **ANSWERED**, 🟡 **NOT COVERED**, or 🔴 **CONFLICT**.
- The grounded response.
- **Visible Citations**: Right next to and below the answer—never hidden behind a button or modal—every retrieved source is displayed in a card with section numbers, document titles, exact similarity percentage match scores, and raw passage excerpts.

### Tech Stack & Engineering Decisions

For the tech stack:
- **Backend**: Python, FastAPI, Pydantic, Uvicorn, and Scikit-Learn for cosine similarity vector search.
- **Frontend**: React, Vite, and clean responsive CSS.
- **Local Fallback**: Built with a zero-dependency TF-IDF/cosine similarity fallback so the entire RAG pipeline, conflict engine, and 38-question evaluation suite run 100% locally out-of-the-box without requiring external API keys.

In summary, RuleGuard AI transforms passive rulebooks into trustworthy, transparent, and evidence-grounded AI compliance assistants. Thank you!"

---

## 30-Second Elevator Pitch

"RuleGuard AI is an evidence-backed QA engine over university regulations that prevents AI hallucination. Unlike standard chatbots that guess policies or pick sides when rules clash, RuleGuard AI categorizes every query into three strict response types: **ANSWERED WITH CITATIONS**, **NOT COVERED IN RULEBOOK**, or **CONFLICTING PROVISIONS DETECTED**. Every answer visibly displays the exact section references, similarity match percentages, and passage excerpts right below the answer. It's built with Python, FastAPI, Scikit-Learn, and React."

---

## Demo Questions Matrix for Live Presentation

| Demo Category | Sample Question | Expected Status | Key Citations / Behavior |
| :--- | :--- | :--- | :--- |
| **1. Normal Answered** | *"What is the minimum overall CGPA required to graduate from an undergraduate program?"* | 🟢 `ANSWERED` | Section 3.2 (Graduation CGPA Threshold) |
| **2. Contradiction / Conflict** | *"I have 68% attendance and an approved medical exemption. Am I eligible to sit for the semester examination?"* | 🔴 `CONFLICT` | Highlights clash between Section 4.2 (75% min) & Section 7.4 (65% medical waiver) |
| **3. Not Covered** | *"What happens if I miss an end-semester examination because I had to attend a family wedding?"* | 🟡 `NOT_COVERED` | Explicitly states rulebook is silent; displays closest passages without inventing policies |
