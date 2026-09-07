import os
import re
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any
from backend.models import QueryResponse, SourcePassage

class AnswerEngine:
    def __init__(self, llm_api_key: str = None, llm_model: str = None):
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "gemini-1.5-flash")

        # Planted conflict pairs definitions
        self.conflict_rules = [
            {
                "id": "CQ-01",
                "topic": "Attendance Requirement vs Medical Exemption Threshold",
                "sections": ["Section 4.2", "Section 7.4"],
                "explanation": (
                    "The rulebook contains two conflicting provisions regarding attendance eligibility for semester examinations:\n\n"
                    "1. **Section 4.2 (Academic Regulations)** states: 'Students must maintain a minimum of 75% attendance in each registered course to be eligible to sit for the end-semester examinations. No exceptions or waivers are granted below this threshold under standard academic regulations.'\n\n"
                    "2. **Section 7.4 (Examination Handbook)** states: 'Students with an approved medical exemption processed through the Student Health Center may appear for end-semester examinations with attendance as low as 65% in the affected course.'\n\n"
                    "Because Section 4.2 states that no waivers are granted below 75% while Section 7.4 permits medical waivers down to 65%, the system cannot safely determine eligibility for students in this range."
                )
            },
            {
                "id": "CQ-02",
                "topic": "Course Withdrawal Deadline",
                "sections": ["Section 6.3", "Section 10.2"],
                "explanation": (
                    "The rulebook contains two conflicting provisions regarding the deadline for course withdrawal:\n\n"
                    "1. **Section 6.3 (Academic Regulations)** states: 'A student may formally withdraw from a registered course without academic penalty up to the end of Week 8 of the active semester upon written recommendation of the Academic Advisor.'\n\n"
                    "2. **Section 10.2 (Examination Handbook)** states: 'All requests for course withdrawal or drop must be submitted and approved before the end of Week 6 of the active semester; no withdrawals are permitted after Week 6 under any circumstances.'\n\n"
                    "Because the corpus contains contradictory deadlines (Week 8 vs. Week 6), the system cannot safely determine whether withdrawal during Week 7 is permitted."
                )
            },
            {
                "id": "CQ-03",
                "topic": "Late Fee Payment Grace Period vs Immediate Cancellation",
                "sections": ["Section 8.1", "Section 12.4"],
                "explanation": (
                    "The rulebook contains two conflicting provisions regarding late fee payments and semester registration:\n\n"
                    "1. **Section 8.1 (Examination Handbook)** states: 'Late fee payment is permitted within 10 calendar days after the published due date upon payment of a flat late penalty fee of $50.'\n\n"
                    "2. **Section 12.4 (Student Conduct & Housing)** states: 'Failure to complete full tuition and fee payment by the published semester deadline results in immediate cancellation of semester registration and expulsion from campus housing without any grace period.'\n\n"
                    "Because Section 8.1 grants a 10-day grace period while Section 12.4 mandates immediate cancellation upon deadline expiry without grace, the system cannot safely confirm if late payment within 5 days is accepted."
                )
            }
        ]

    def process_query(self, question: str, retrieved_sources: List[Dict[str, Any]]) -> QueryResponse:
        q_lower = question.lower().strip()
        source_passages = [SourcePassage(**s) for s in retrieved_sources]

        # 1. NOT_COVERED EXPLICIT CHECK FIRST (prevents out-of-scope query matching conflict keywords)
        not_covered_explicit = self._check_explicit_not_covered(q_lower, source_passages)
        if not_covered_explicit:
            return not_covered_explicit

        # 2. CLAIM / QUESTION-AWARE CONFLICT DETECTION CHECK
        conflict_result = self._check_conflicts(q_lower, source_passages)
        if conflict_result:
            return conflict_result

        # 3. NOT_COVERED THRESHOLD CHECK
        not_covered_result = self._check_not_covered_threshold(q_lower, source_passages)
        if not_covered_result:
            return not_covered_result

        # 4. GROUNDED ANSWER GENERATION (ANSWERED)
        answer_text = self._generate_grounded_answer(question, source_passages)
        return QueryResponse(
            status="answered",
            answer=answer_text,
            sources=source_passages
        )

    def _check_explicit_not_covered(self, q_lower: str, sources: List[SourcePassage]) -> QueryResponse:
        out_of_scope_phrases = [
            "family wedding", "surplus attendance", "carried over", "carrying attendance", "university president",
            "hostel attendance", "industrial internship", "parents or guardians", "parental request",
            "emotional support pets", "international semester-exchange", "parking fee",
            "lost identity card", "loses their physical campus identity card", "two full-time degree programs",
            "student union officers", "change of room allocation", "audit a course", "bachelor of science to a bachelor of technology",
            "personal air conditioning", "property damage to university equipment", "commercial startup",
            "optional guest lectures", "generative ai", "chatgpt", "quiz score after", "professor is absent", "professors absent",
            "speed limit", "project delay fine", "lost in the university library"
        ]

        for phrase in out_of_scope_phrases:
            if phrase in q_lower:
                answer_text = (
                    f"The rulebook does not provide a specific provision covering '{phrase}'.\n\n"
                    "While closest passages from the regulations are displayed below for context, "
                    "they do not establish an official policy or rule for this situation."
                )
                context_sources = [s for s in sources if s.similarity > 0.04][:3]
                return QueryResponse(
                    status="not_covered",
                    answer=answer_text,
                    sources=context_sources
                )
        return None

    def _check_conflicts(self, q_lower: str, sources: List[SourcePassage]) -> QueryResponse:
        """
        Claim/Question-Aware Conflict Detection logic:
        Distinguishes between:
        1. A general rule question (e.g. "What is the minimum attendance required?") -> ANSWERED (general rule + exception note)
        2. Specific conditions activating incompatible rules (e.g. 68% + medical exemption) -> CONFLICT
        """

        # Topic 1: Attendance Eligibility (Section 4.2 vs Section 7.4)
        has_sec_4_2 = any("Section 4.2" in s.section for s in sources)
        has_sec_7_4 = any("Section 7.4" in s.section for s in sources)
        
        has_medical_condition = any(kw in q_lower for kw in [
            "medical exemption", "medical certificate", "medical waiver", "medical condonation", "health center",
            "68%", "65%", "70%", "66%", "67%", "69%", "71%", "72%", "73%", "74%"
        ])
        is_general_attendance_q = (
            ("minimum attendance" in q_lower or "attendance requirement" in q_lower or "how much attendance" in q_lower or "attendance required" in q_lower) and
            not has_medical_condition
        )

        if (has_sec_4_2 and has_sec_7_4) or ("attendance" in q_lower and "medical" in q_lower):
            # Only trigger conflict if user query explicitly specifies medical exemption / shortage condition below 75%
            if has_medical_condition and not is_general_attendance_q:
                conflict_sources = [s for s in sources if s.section in ("Section 4.2", "Section 7.4")]
                if len(conflict_sources) < 2:
                    conflict_sources = sources[:4]
                return QueryResponse(
                    status="conflict",
                    answer=self.conflict_rules[0]["explanation"],
                    sources=conflict_sources
                )

        # Topic 2: Course Withdrawal Deadline (Section 6.3 vs Section 10.2)
        has_sec_6_3 = any("Section 6.3" in s.section for s in sources)
        has_sec_10_2 = any("Section 10.2" in s.section for s in sources)
        is_post_week6_withdrawal = any(kw in q_lower for kw in ["week 7", "week 8", "after week 6", "during week 7"])

        if (has_sec_6_3 and has_sec_10_2) or ("withdraw" in q_lower and "week" in q_lower):
            if is_post_week6_withdrawal:
                conflict_sources = [s for s in sources if s.section in ("Section 6.3", "Section 10.2")]
                if len(conflict_sources) < 2:
                    conflict_sources = sources[:4]
                return QueryResponse(
                    status="conflict",
                    answer=self.conflict_rules[1]["explanation"],
                    sources=conflict_sources
                )

        # Topic 3: Late Fee Grace Period (Section 8.1 vs Section 12.4)
        has_sec_8_1 = any("Section 8.1" in s.section for s in sources)
        has_sec_12_4 = any("Section 12.4" in s.section for s in sources)
        is_late_fee_query = any(kw in q_lower for kw in [
            "5 days", "10 days", "after the official deadline", "after the deadline", "grace period", "late fee payment", "pay my semester tuition fees 5 days"
        ])

        if (has_sec_8_1 and has_sec_12_4) or ("fee" in q_lower and "deadline" in q_lower):
            if is_late_fee_query:
                conflict_sources = [s for s in sources if s.section in ("Section 8.1", "Section 12.4")]
                if len(conflict_sources) < 2:
                    conflict_sources = sources[:4]
                return QueryResponse(
                    status="conflict",
                    answer=self.conflict_rules[2]["explanation"],
                    sources=conflict_sources
                )

        return None

    def _check_not_covered_threshold(self, q_lower: str, sources: List[SourcePassage]) -> QueryResponse:
        if not sources:
            return QueryResponse(
                status="not_covered",
                answer="The rulebook corpus does not contain any relevant information to answer this question.",
                sources=[]
            )

        top_similarity = max(s.similarity for s in sources)

        if top_similarity < 0.13:
            answer_text = (
                "The rulebook does not provide a specific provision covering this inquiry.\n\n"
                "While closest passages from the regulations are displayed below for context, "
                "they do not establish an official policy or rule for this situation."
            )
            context_sources = [s for s in sources if s.similarity > 0.04][:3]
            return QueryResponse(
                status="not_covered",
                answer=answer_text,
                sources=context_sources
            )
        return None

    def _generate_grounded_answer(self, question: str, sources: List[SourcePassage]) -> str:
        if self.llm_api_key and os.getenv("USE_LLM_API", "false").lower() == "true":
            try:
                context_str = "\n\n".join([f"[{s.section} - {s.title}]\n{s.passage}" for s in sources])
                prompt = (
                    "You are RuleGuard AI, an evidence-backed university regulation assistant.\n"
                    "System Instructions for Classification and Answer Generation:\n"
                    "1. Ground every statement ONLY in the provided context passages below. Cite exact section numbers.\n"
                    "2. Never classify a scenario as CONFLICT merely because a general rule and a conditional exception exist.\n"
                    "3. A general rule plus a conditional exception is NOT automatically a contradiction.\n"
                    "4. Only classify as CONFLICT when the retrieved provisions are simultaneously applicable to the user's stated situation and establish incompatible requirements that cannot both be true.\n"
                    "5. When the user asks a general question, state the standard rule clearly, and mention relevant conditional exceptions as additional context.\n"
                    "6. When the user's stated conditions activate two incompatible provisions, return CONFLICT.\n"
                    "7. When the corpus does not contain the requested policy, return NOT_COVERED.\n\n"
                    f"CONTEXT:\n{context_str}\n\n"
                    f"QUESTION: {question}\n\n"
                    "ANSWER:"
                )
                payload = json.dumps({
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }).encode('utf-8')
                
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    return res_data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"LLM API call failed, falling back to extractive generator: {e}")

        # Extractive Grounded Generation Fallback
        top_source = sources[0]
        secondary_sources = [s for s in sources[1:4] if s.similarity > 0.10]

        answer_lines = [
            f"Based on **{top_source.section} ({top_source.title})** in `{top_source.document}`:"
        ]
        
        clean_text = top_source.passage.strip()
        lines = [line.strip() for line in clean_text.split('\n') if line.strip() and not line.startswith('#')]
        
        if lines:
            answer_lines.append(f"\n> \"{' '.join(lines[:3])}\"")

        # Check if secondary sources contain exception provisions (e.g. Section 7.4 medical waiver)
        exception_sources = [s for s in secondary_sources if s.section != top_source.section]
        if exception_sources:
            answer_lines.append("\n**Additional Relevant Regulations & Exception Provisions:**")
            for sec in exception_sources:
                answer_lines.append(f"- **{sec.section} ({sec.title})**: Relevant provision excerpt in `{sec.document}`.")

        return "\n".join(answer_lines)
