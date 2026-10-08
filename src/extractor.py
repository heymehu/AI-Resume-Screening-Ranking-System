from __future__ import annotations

import re
from typing import Iterable, List

from src.models import Candidate

SKILLS: List[str] = [
    "python",
    "fastapi",
    "django",
    "flask",
    "langchain",
    "langgraph",
    "llamaindex",
    "rag",
    "retrieval",
    "embeddings",
    "vector",
    "vector db",
    "agent",
    "agents",
    "tool calling",
    "multi-agent",
    "llm",
    "openai",
    "gemini",
    "pydantic",
    "postgres",
    "postgresql",
    "redis",
    "docker",
    "kubernetes",
    "gcp",
    "aws",
    "azure",
    "react",
    "next.js",
    "typescript",
    "javascript",
    "java",
    "spring boot",
    "sql",
    "mongodb",
    "ci/cd",
    "microservices",
    "kafka",
    "system design",
    "testing",
    "pytest",
]


def normalize_name(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned.title() if cleaned else ""


def extract_name(text: str) -> str:
    title_words = {
        "associate",
        "senior",
        "junior",
        "software",
        "engineer",
        "developer",
        "student",
        "intern",
        "lead",
        "manager",
        "analyst",
        "architect",
        "consultant",
        "full",
        "stack",
        "data",
        "scientist",
        "ai",
        "ml",
        "frontend",
        "backend",
        "generative",
        "machine",
        "learning",
        "engineering",
        "platform",
        "specialist",
        "technical",
        "aspiring",
        "python",
        "simulation",
        "skills",
        "job",
    }
    location_words = {
        "bangalore",
        "bengaluru",
        "hyderabad",
        "delhi",
        "mumbai",
        "india",
        "chennai",
        "pune",
        "ghaziabad",
        "mathura",
        "noida",
        "gurugram",
        "jaipur",
        "indore",
        "lucknow",
        "ahmedabad",
        "kolkata",
        "visakhapatnam",
        "coimbatore",
        "karnataka",
        "tamil",
        "nadu",
        "up",
        "uttar",
        "pradesh",
        "west",
        "bengal",
        "kharagpur",
    }

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:30]:
        line = re.sub(r"^[^A-Za-z]+", "", line)
        if re.match(r"(?i)^(summary|professional summary|skills|experience|work experience|education|projects|objective)\b", line):
            continue
        match = re.match(r"^\s*([A-Z][A-Za-z'&.-]*(?:\s+[A-Z][A-Za-z'&.-]*){1,4})\b", line)
        if not match:
            continue
        tokens = match.group(1).split()
        if len(tokens) < 2 or len(tokens) > 5:
            continue
        if tokens[0].isdigit() or any(token.isdigit() for token in tokens):
            continue

        while tokens:
            last = tokens[-1].lower()
            attached_location = next(
                (
                    location
                    for location in location_words
                    if len(tokens[-1]) > len(location)
                    and tokens[-1].lower().endswith(location)
                ),
                None,
            )
            if attached_location:
                tokens[-1] = tokens[-1][: -len(attached_location)]
                continue
            cleaned = re.sub(
                r"(?i)(?:phone(?:-alt)?|email|linkedin|github|portfolio|mobile|skills|summary|experience|education|project)$",
                "",
                tokens[-1],
            ).strip()
            if cleaned != tokens[-1]:
                if cleaned:
                    tokens[-1] = cleaned
                else:
                    tokens.pop()
                continue
            if (
                last in title_words
                or last in location_words
                or "full-stack" in last
                or last.endswith("stack")
                or re.search(r"(?:b\.tech|m\.tech|b\.e|m\.e|bsc|msc|mba|mca|b\.com|phd)$", last)
            ):
                tokens.pop()
                continue
            break
        if len(tokens) < 2:
            continue

        name = " ".join(tokens)
        if re.match(r"^[A-Z][A-Za-z'&.-]*(?:\s+[A-Z][A-Za-z'&.-]*){1,4}$", name):
            return normalize_name(name)

    return "Unknown Candidate"


def extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)
    return match.group(0).strip() if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    return match.group(0).strip() if match else ""


def extract_github_url(text: str) -> str:
    pattern = r"https?://github\.com/([A-Za-z0-9_.\-]+)\/?|github\.com/([A-Za-z0-9_.\-]+)\/?"
    match = re.search(pattern, text, re.I)
    if not match:
        return ""
    cleaned = match.group(0)
    if cleaned.lower().startswith("http"):
        return cleaned.strip()
    return "https://github.com/" + cleaned.lower().replace("github.com/", "").strip("/")


def extract_github_username(github_url: str) -> str:
    if not github_url:
        return ""
    match = re.search(r"github\.com/([A-Za-z0-9_.\-]+)", github_url, re.I)
    if match:
        return match.group(1)
    return ""


def match_skills(text: str) -> List[str]:
    lowered = text.lower()
    matched: List[str] = []
    for skill in SKILLS:
        if skill in lowered:
            matched.append(skill)
    return matched


def extract_projects(text: str) -> List[str]:
    project_lines = []
    for line in text.splitlines():
        lower = line.lower()
        if "project" in lower or "portfolio" in lower or "intern" in lower:
            project_lines.append(line.strip())
    return project_lines[:8]


def extract_experience(text: str) -> str:
    lines = text.splitlines()
    captured: List[str] = []
    in_section = False
    for line in lines:
        lower = line.lower()
        if "experience" in lower or "work experience" in lower or "internship" in lower or "projects" in lower:
            in_section = True
            continue
        if in_section and len(captured) < 8 and line.strip():
            captured.append(line.strip())
        if in_section and len(captured) >= 8:
            break
    return " ".join(captured)


def extract_education(text: str) -> str:
    lines = text.splitlines()
    captured: List[str] = []
    in_section = False
    for line in lines:
        lower = line.lower()
        if "education" in lower:
            in_section = True
            continue
        if in_section and len(captured) < 6 and line.strip():
            captured.append(line.strip())
        if in_section and len(captured) >= 6:
            break
    return " ".join(captured)


def extract_candidate(file_name: str, text: str) -> Candidate:
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    github_url = extract_github_url(text)
    skills = match_skills(text)
    candidate = Candidate(
        candidate_name=name,
        email=email,
        phone=phone,
        skills=skills,
        projects=extract_projects(text),
        experience=extract_experience(text),
        education=extract_education(text),
        github_url=github_url,
        github_username=extract_github_username(github_url),
        resume_text=text,
        source_file=file_name,
        matched_skills=skills,
    )
    return candidate
