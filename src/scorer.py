from __future__ import annotations

from src.models import Candidate

AI_KEYWORDS = (
    "langchain",
    "langgraph",
    "llamaindex",
    "rag",
    "retrieval",
    "vector",
    "embeddings",
    "agent",
    "agents",
    "tool calling",
    "multi-agent",
    "llm",
    "openai",
    "gemini",
    "generative ai",
    "prompt engineering",
    "pydantic",
    "nvidia nim",
    "computer vision",
    "nlp",
)

PYTHON_KEYWORDS = (
    "python",
    "fastapi",
    "django",
    "flask",
    "asyncio",
    "postgres",
    "redis",
    "sql",
    "pandas",
    "numpy",
    "pytest",
)

CLOUD_KEYWORDS = ("docker", "kubernetes", "gcp", "aws", "azure", "next.js", "react")
ENGINEERING_KEYWORDS = ("testing", "pytest", "observability", "caching", "microservices", "kafka", "system design")


def _count_evidence(text: str, keywords: tuple[str, ...]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def score_candidate(candidate: Candidate, github_points: int = 0) -> dict[str, int]:
    text = (candidate.resume_text or "").lower()
    ai_hits = _count_evidence(text, AI_KEYWORDS)
    python_hits = _count_evidence(text, PYTHON_KEYWORDS)
    cloud_hits = _count_evidence(text, CLOUD_KEYWORDS)
    eng_hits = _count_evidence(text, ENGINEERING_KEYWORDS)

    project_text = " ".join(candidate.projects).lower()
    experience_text = candidate.experience.lower()
    demonstrated_text = f"{project_text} {experience_text}"
    demonstrated_ai_hits = _count_evidence(demonstrated_text, AI_KEYWORDS)
    demonstrated_python_hits = _count_evidence(demonstrated_text, PYTHON_KEYWORDS)
    demonstrated_cloud_hits = _count_evidence(demonstrated_text, CLOUD_KEYWORDS)
    demonstrated_eng_hits = _count_evidence(demonstrated_text, ENGINEERING_KEYWORDS)

    ai_score = min(40, demonstrated_ai_hits * 7 + max(0, ai_hits - demonstrated_ai_hits) * 2)
    python_score = min(30, demonstrated_python_hits * 5 + max(0, python_hits - demonstrated_python_hits) * 2)
    cloud_score = min(15, demonstrated_cloud_hits * 3 + max(0, cloud_hits - demonstrated_cloud_hits))
    engineering_score = min(5, demonstrated_eng_hits * 2 + max(0, eng_hits - demonstrated_eng_hits))
    github_score = min(10, max(0, github_points))

    total = ai_score + python_score + cloud_score + github_score + engineering_score

    total = max(0, min(100, total))
    breakdown = {
        "ai_project_depth": ai_score,
        "python_backend": python_score,
        "cloud_fullstack": cloud_score,
        "github": github_score,
        "engineering_depth": engineering_score,
    }
    return {"score_breakdown": breakdown, "total_score": total, "screening_score": total}
