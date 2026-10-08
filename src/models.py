from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    candidate_name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    experience: str = ""
    education: str = ""
    github_url: str = ""
    github_username: str = ""
    resume_text: str = ""
    eligible: bool = False
    status: str = "REJECTED"
    rejection_reasons: List[str] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    score_breakdown: Dict[str, int] = Field(default_factory=dict)
    total_score: int = 0
    screening_score: int = 0
    project_summary: str = ""
    github_summary: str = ""
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    source_file: str = ""
    github_status: str = "missing"
    github_error: str = ""
    parse_error: str = ""
    duplicate_of: Optional[str] = None
    rank: Optional[int] = None
    overall_position: Optional[int] = None
    score_display: str = ""


class BatchSummary(BaseModel):
    total_resumes: int = 0
    successfully_parsed: int = 0
    eligible: int = 0
    rejected: int = 0
    failed_or_unreadable: int = 0
    duplicate_resumes: int = 0


class FailureRecord(BaseModel):
    file: str
    error: str
