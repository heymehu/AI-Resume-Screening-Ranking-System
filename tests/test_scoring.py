from src.models import Candidate
from src.scorer import score_candidate


def test_scores_stay_in_range():
    candidate = Candidate(
        candidate_name="Test Candidate",
        resume_text="Python engineer building LangGraph agentic AI project with FastAPI, Docker, and PostgreSQL.",
        skills=["Python", "FastAPI", "LangGraph", "Docker", "PostgreSQL"],
    )
    result = score_candidate(candidate, github_points=4)
    assert 0 <= result["total_score"] <= 100
    assert sum(result["score_breakdown"].values()) == result["total_score"]


def test_ai_depth_has_highest_weight():
    candidate = Candidate(
        candidate_name="AI Engineer",
        resume_text="Python developer using LangChain, LangGraph, RAG, embeddings, and tool calling in production AI workflows.",
        skills=["Python", "LangChain", "LangGraph", "RAG", "Embeddings"],
    )
    result = score_candidate(candidate, github_points=5)
    assert result["score_breakdown"]["ai_project_depth"] >= result["score_breakdown"]["python_backend"]
    assert result["score_breakdown"]["ai_project_depth"] >= result["score_breakdown"]["cloud_fullstack"]


def test_missing_github_does_not_fail_scoring():
    candidate = Candidate(
        candidate_name="Candidate",
        resume_text="Python backend engineer with FastAPI and LangChain project experience.",
        skills=["Python", "FastAPI", "LangChain"],
    )
    result = score_candidate(candidate)
    assert 0 <= result["total_score"] <= 100


def test_ranking_sort_is_descending():
    high = Candidate(candidate_name="High", resume_text="Python engineer building LangGraph AI agent pipeline with FastAPI and Docker.")
    low = Candidate(candidate_name="Low", resume_text="Python developer with backend dashboards but no AI system work.")
    high_result = score_candidate(high, github_points=7)
    low_result = score_candidate(low, github_points=0)
    assert high_result["total_score"] > low_result["total_score"]


def test_rejected_candidate_can_receive_evidence_based_screening_score():
    candidate = Candidate(
        candidate_name="Backend Candidate",
        resume_text="Python FastAPI PostgreSQL Redis Docker pytest microservices.",
        skills=["Python", "FastAPI", "PostgreSQL"],
        projects=["Built a Python FastAPI backend with tests."],
    )
    result = score_candidate(candidate)
    assert 0 <= result["screening_score"] <= 100
    assert result["screening_score"] == sum(result["score_breakdown"].values())
