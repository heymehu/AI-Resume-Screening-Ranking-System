from __future__ import annotations

from src.models import Candidate

PYTHON_KEYWORDS = (
    "python",
    "fastapi",
    "django",
    "flask",
    "pandas",
    "numpy",
    "scikit",
    "sqlalchemy",
    "asyncio",
)

AI_KEYWORDS = (
    "langchain",
    "langgraph",
    "llamaindex",
    "rag",
    "retrieval",
    "vector db",
    "vector search",
    "embeddings",
    "agent",
    "agents",
    "tool calling",
    "multi-agent",
    "agentic",
    "llm",
    "gpt",
    "openai",
    "gemini",
    "generative ai",
    "artificial intelligence",
    "machine learning",
    "prompt engineering",
    "nvidia nim",
    "computer vision",
    "nlp",
)


def evaluate_eligibility(candidate: Candidate) -> tuple[bool, list[str]]:
    text = (candidate.resume_text or "").lower()
    python_present = any(keyword in text for keyword in PYTHON_KEYWORDS)
    ai_present = any(keyword in text for keyword in AI_KEYWORDS)
    reasons: list[str] = []

    if not python_present:
        reasons.append("Python evidence missing from skills, projects, or work experience.")
    if python_present and not ai_present:
        reasons.append("Python evidence present but meaningful AI/agentic evidence is missing.")
    if not ai_present and not python_present:
        reasons.append("Meaningful AI/agentic evidence missing (LangChain, LangGraph, RAG, embeddings, agents, LLM, etc.).")
    if not candidate.resume_text.strip():
        reasons.append("Resume content is empty or unreadable.")

    return (not reasons), reasons
