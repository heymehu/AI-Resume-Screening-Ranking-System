import json
from pathlib import Path

from src.pipeline import ResumePipeline


class StubLLM:
    def analyze_resume(self, resume_text):
        return {
            "project_summary": "Summary based on resume text.",
            "strengths": [],
            "concerns": [],
        }


def test_pipeline_reports_all_candidates_and_scores_rejected(tmp_path: Path, monkeypatch):
    resumes = tmp_path / "resumes"
    resumes.mkdir()
    (resumes / "eligible.txt").write_text(
        "Avery Eligible\nPython FastAPI LangGraph RAG. Built a Python RAG service using FastAPI and LangGraph.",
        encoding="utf-8",
    )
    (resumes / "rejected.txt").write_text(
        "Bailey Rejected\nPython FastAPI PostgreSQL. Built a Python API backend with tests.",
        encoding="utf-8",
    )

    monkeypatch.setattr("src.pipeline.enrich_github", lambda *args, **kwargs: {
        "status": "missing",
        "summary": "No GitHub link found in resume.",
        "error": "",
        "points": 0,
    })
    pipeline = ResumePipeline(resumes, tmp_path / "results.json")
    pipeline.llm = StubLLM()
    result = pipeline.run()

    assert result["batch_summary"]["total_resumes"] == 2
    assert result["batch_summary"]["eligible"] == 1
    assert result["batch_summary"]["rejected"] == 1
    assert set(result) == {"batch_summary", "candidates"}
    assert len(result["candidates"]) == 2
    assert [candidate["rank"] for candidate in result["candidates"]] == [1, 2]
    assert result["candidates"][0]["total_score"] >= result["candidates"][1]["total_score"]
    rejected = next(candidate for candidate in result["candidates"] if not candidate["eligible"])
    assert rejected["total_score"] > 0
    assert rejected["rejection_reasons"]
    assert rejected["status"] == "REJECTED"
    assert "AI " in rejected["score_display"]
    assert "Python " in rejected["score_display"]
    assert next(candidate for candidate in result["candidates"] if candidate["eligible"])["status"] == "ELIGIBLE"
    assert all(candidate["score_breakdown"] for candidate in result["candidates"])
    written = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(written) == {"batch_summary", "candidates"}
    assert written["candidates"]


def test_unreadable_resume_still_appears_in_complete_report(tmp_path: Path, monkeypatch):
    resumes = tmp_path / "resumes"
    resumes.mkdir()
    (resumes / "broken.pdf").write_bytes(b"not a PDF")
    monkeypatch.setattr("src.pipeline.enrich_github", lambda *args, **kwargs: {
        "status": "missing",
        "summary": "No GitHub link found in resume.",
        "error": "",
        "points": 0,
    })
    pipeline = ResumePipeline(resumes, tmp_path / "results.json")
    pipeline.llm = StubLLM()

    result = pipeline.run()

    assert result["batch_summary"]["total_resumes"] == 1
    assert result["batch_summary"]["failed_or_unreadable"] == 1
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["parse_error"]
    assert result["candidates"][0]["total_score"] == 0
    assert sum(result["candidates"][0]["score_breakdown"].values()) == 0
