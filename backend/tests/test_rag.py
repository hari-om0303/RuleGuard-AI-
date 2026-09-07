import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.rag.retriever import Retriever
from backend.rag.answer_engine import AnswerEngine

@pytest.fixture
def rag_components():
    retriever = Retriever()
    answer_engine = AnswerEngine()
    return retriever, answer_engine

def test_question_1_general_attendance_rule(rag_components):
    """
    Question 1: "What is the minimum attendance required to appear for the semester examination?"
    Expected Status: ANSWERED (General rule = 75%, mentions 65% medical waiver as exception context)
    """
    retriever, answer_engine = rag_components
    question = "What is the minimum attendance required to appear for the semester examination?"
    sources = retriever.retrieve(question, top_k=6)
    res = answer_engine.process_query(question, sources)
    
    assert res.status == "answered"
    assert len(res.sources) > 0
    assert any("Section 4.2" in s.section for s in res.sources)

def test_question_2_medical_exemption_conflict(rag_components):
    """
    Question 2: "I have 68% attendance and an approved medical exemption. Can I appear for the semester examination?"
    Expected Status: CONFLICT (User's specific condition triggers clash between Section 4.2 and Section 7.4)
    """
    retriever, answer_engine = rag_components
    question = "I have 68% attendance and an approved medical exemption. Can I appear for the semester examination?"
    sources = retriever.retrieve(question, top_k=6)
    res = answer_engine.process_query(question, sources)
    
    assert res.status == "conflict"
    assert any("Section 4.2" in s.section for s in res.sources)
    assert any("Section 7.4" in s.section for s in res.sources)
    assert "Section 4.2" in res.answer and "Section 7.4" in res.answer

def test_question_3_family_wedding_not_covered(rag_components):
    """
    Question 3: "Can I miss my examination because I had to attend a family wedding?"
    Expected Status: NOT_COVERED (Corpus is silent on family weddings)
    """
    retriever, answer_engine = rag_components
    question = "Can I miss my examination because I had to attend a family wedding?"
    sources = retriever.retrieve(question, top_k=6)
    res = answer_engine.process_query(question, sources)
    
    assert res.status == "not_covered"
    assert "family wedding" in res.answer.lower()
