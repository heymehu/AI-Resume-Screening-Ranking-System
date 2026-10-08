from src.eligibility import evaluate_eligibility
from src.models import Candidate


def test_python_plus_ai_is_eligible():
    candidate = Candidate(
        candidate_name="Ada Lovelace",
        resume_text="Python developer building LangGraph multi-agent RAG pipeline with FastAPI backend.",
        skills=["Python", "FastAPI", "LangGraph", "RAG"],
    )
    eligible, reasons = evaluate_eligibility(candidate)
    assert eligible is True
    assert reasons == []


def test_python_without_ai_is_rejected():
    candidate = Candidate(
        candidate_name="Python Developer",
        resume_text="Worked in Flask and PostgreSQL building internal dashboards.",
        skills=["Python", "Flask", "PostgreSQL"],
    )
    eligible, reasons = evaluate_eligibility(candidate)
    assert eligible is False
    assert any("Python evidence" in reason for reason in reasons)


def test_ai_without_python_is_rejected():
    candidate = Candidate(
        candidate_name="AI Engineer",
        resume_text="Designed LangChain and RAG retrieval system for enterprise search use cases.",
        skills=["LangChain", "RAG", "Vector DB"],
    )
    eligible, reasons = evaluate_eligibility(candidate)
    assert eligible is False
    assert any("Python evidence" in reason for reason in reasons)


def test_js_react_only_is_rejected():
    candidate = Candidate(
        candidate_name="Frontend Engineer",
        resume_text="React and Next.js specialist building UI and dashboards.",
        skills=["JavaScript", "React", "Next.js"],
    )
    eligible, reasons = evaluate_eligibility(candidate)
    assert eligible is False
    assert any("Python evidence" in reason for reason in reasons)
