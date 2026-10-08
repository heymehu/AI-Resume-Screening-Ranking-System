from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from src.config import settings
from src.eligibility import evaluate_eligibility
from src.extractor import extract_candidate
from src.github import enrich_github
from src.llm import LLMProvider
from src.models import BatchSummary, Candidate, FailureRecord
from src.parser import find_resume_files, parse_resume
from src.scorer import score_candidate


class ResumePipeline:
    def __init__(self, input_dir: str | Path, output_path: str | Path) -> None:
        self.input_dir = Path(input_dir)
        self.output_path = Path(output_path)
        self.llm = LLMProvider()

    def _hash_resume(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def run(self) -> dict[str, Any]:
        resume_files = find_resume_files(self.input_dir)
        seen_hashes: dict[str, str] = {}
        eligible: list[Candidate] = []
        rejected: list[Candidate] = []
        failed: list[FailureRecord] = []
        successful_parsed = 0

        for path in resume_files:
            try:
                text = parse_resume(path)
                if not text.strip():
                    raise ValueError("Resume is empty or unreadable.")
                digest = self._hash_resume(text)
                if digest in seen_hashes:
                    duplicate_of = seen_hashes[digest]
                else:
                    seen_hashes[digest] = path.name
                    duplicate_of = None

                candidate = extract_candidate(path.name, text)
                candidate.duplicate_of = duplicate_of
                successful_parsed += 1
                candidate.eligible, candidate.rejection_reasons = evaluate_eligibility(candidate)

                llm_result = self.llm.analyze_resume(text)
                candidate.project_summary = llm_result.get("project_summary", "")
                candidate.strengths = llm_result.get("strengths", [])
                candidate.concerns = llm_result.get("concerns", [])

                github_data = enrich_github(candidate.github_url, settings.github_token)
                candidate.github_status = github_data.get("status", "missing")
                candidate.github_summary = github_data.get("summary", "")
                candidate.github_error = github_data.get("error", "")

                score_result = score_candidate(candidate, github_data.get("points", 0))
                candidate.score_breakdown = score_result["score_breakdown"]
                candidate.screening_score = score_result["screening_score"]
                candidate.total_score = score_result["total_score"]

                if candidate.eligible:
                    eligible.append(candidate)
                else:
                    rejected.append(candidate)
            except Exception as exc:  # pragma: no cover - environment-specific exceptions
                failed.append(FailureRecord(file=path.name, error=str(exc)))
                rejected.append(
                    Candidate(
                        candidate_name="Unknown Candidate",
                        source_file=path.name,
                        eligible=False,
                        rejection_reasons=[f"Resume could not be parsed: {exc}"],
                        score_breakdown={
                            "ai_project_depth": 0,
                            "python_backend": 0,
                            "cloud_fullstack": 0,
                            "github": 0,
                            "engineering_depth": 0,
                        },
                        parse_error=str(exc),
                        project_summary="Unavailable because the resume could not be parsed.",
                        concerns=["Resume content was unreadable; no evidence could be assessed."],
                    )
                )

        all_candidates = sorted(
            [*eligible, *rejected],
            key=lambda item: (
                -item.total_score,
                -item.score_breakdown.get("ai_project_depth", 0),
                -item.score_breakdown.get("python_backend", 0),
                -item.score_breakdown.get("engineering_depth", 0),
                item.candidate_name.casefold(),
                item.source_file.casefold(),
            ),
        )
        for index, candidate in enumerate(all_candidates, start=1):
            candidate.rank = index
            candidate.overall_position = index
            candidate.status = "ELIGIBLE" if candidate.eligible else "REJECTED"
            scores = candidate.score_breakdown
            candidate.score_display = (
                f"AI {scores.get('ai_project_depth', 0)}/40 | "
                f"Python {scores.get('python_backend', 0)}/30 | "
                f"Cloud {scores.get('cloud_fullstack', 0)}/15 | "
                f"GitHub {scores.get('github', 0)}/10 | "
                f"Engineering {scores.get('engineering_depth', 0)}/5"
            )

        output_payload = {
            "candidates": [
                candidate.model_dump(mode="json", exclude={"resume_text", "overall_position", "screening_score"})
                for candidate in all_candidates
            ],
            "batch_summary": BatchSummary(
                total_resumes=len(resume_files),
                successfully_parsed=successful_parsed,
                eligible=len(eligible),
                rejected=sum(1 for candidate in rejected if not candidate.parse_error),
                failed_or_unreadable=len(failed),
                duplicate_resumes=sum(1 for candidate in all_candidates if candidate.duplicate_of),
            ).model_dump(mode="json"),
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            __import__("json").dumps(output_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return output_payload
