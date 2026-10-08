from __future__ import annotations

import json
from typing import Any

from src.config import settings


class LLMProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model

    def _fallback_analysis(self, resume_text: str) -> dict[str, Any]:
        lower = resume_text.lower()
        strengths: list[str] = []
        if "python" in lower:
            strengths.append("Python-first engineering background")
        if "fastapi" in lower or "django" in lower:
            strengths.append("Backend/API implementation experience")
        if any(token in lower for token in ["langchain", "langgraph", "rag", "agent", "llm", "vector"]):
            strengths.append("AI and agentic system experience")
        if "docker" in lower or "gcp" in lower or "aws" in lower or "azure" in lower:
            strengths.append("Deployment or cloud exposure")
        if not strengths:
            strengths = ["Relevant engineering work is present but shallow in detail"]

        concerns = []
        if "python" not in lower:
            concerns.append("Limited Python evidence")
        if not any(token in lower for token in ["langchain", "langgraph", "rag", "agent", "llm", "vector"]):
            concerns.append("AI/agentic evidence is limited")
        if len(resume_text.split()) < 200:
            concerns.append("Resume is shorter than expected for a senior engineering profile")

        summary = "Candidate demonstrates engineering work with evidence across product delivery and technical execution."
        if "python" in lower and any(token in lower for token in ["langchain", "langgraph", "rag", "agent", "llm", "vector"]):
            summary = "Candidate shows strong Python + AI engineering evidence with applied system-building and backend delivery."
        return {
            "project_summary": summary,
            "strengths": strengths[:5],
            "concerns": concerns[:5],
            "error": "",
        }

    def analyze_resume(self, resume_text: str) -> dict[str, Any]:
        if not self.api_key:
            return self._fallback_analysis(resume_text)

        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            prompt = (
                "Extract a concise project summary, top strengths, and concerns for this resume. "
                "Use only evidence from the resume. Return JSON with keys: "
                "project_summary (string), strengths (array of strings), concerns (array of strings)."
            )
            response = client.models.generate_content(
                model=self.model,
                contents=prompt + "\n\nResume:\n" + resume_text[:12000],
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                },
            )
            content = response.text
            if not content:
                raise ValueError("Gemini returned an empty response.")
            payload = json.loads(content)
            if not isinstance(payload, dict):
                raise ValueError("Gemini response must be a JSON object.")
            strengths = payload.get("strengths", [])
            concerns = payload.get("concerns", [])
            if not isinstance(strengths, list) or not isinstance(concerns, list):
                raise ValueError("Gemini strengths and concerns must be JSON arrays.")
            return {
                "project_summary": str(payload.get("project_summary", "Candidate shows meaningful technical delivery.")),
                "strengths": [str(item) for item in strengths[:5]],
                "concerns": [str(item) for item in concerns[:5]],
                "error": "",
            }
        except Exception as exc:  # pragma: no cover - network failures handled gracefully
            fallback = self._fallback_analysis(resume_text)
            fallback["error"] = str(exc)
            return fallback
