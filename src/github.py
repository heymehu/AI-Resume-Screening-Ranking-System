from __future__ import annotations

import re
from typing import Any

import requests

from src.config import settings


def extract_github_username(github_url: str) -> str:
    if not github_url:
        return ""
    match = re.search(r"github\.com/([A-Za-z0-9_.\-]+)", github_url, re.I)
    return match.group(1) if match else ""


def enrich_github(github_url: str, token: str | None = None) -> dict[str, Any]:
    if not github_url:
        return {
            "status": "missing",
            "summary": "No GitHub link found in resume.",
            "error": "",
            "points": 0,
        }

    username = extract_github_username(github_url)
    if not username:
        return {
            "status": "missing",
            "summary": "GitHub URL could not be parsed.",
            "error": "",
            "points": 0,
        }

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "resume-screening-bot",
    }
    auth_token = token or settings.github_token
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        profile_resp = requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers,
            timeout=10,
        )
        if profile_resp.status_code == 404:
            return {
                "status": "missing",
                "summary": "GitHub profile not found or private.",
                "error": f"404 for {username}",
                "points": 0,
            }
        if profile_resp.status_code == 403:
            return {
                "status": "rate_limited",
                "summary": "GitHub API rate limit reached.",
                "error": profile_resp.text[:200],
                "points": 0,
            }
        profile_resp.raise_for_status()
        profile = profile_resp.json()
        repos_resp = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated",
            headers=headers,
            timeout=10,
        )
        repos = repos_resp.json() if repos_resp.status_code == 200 else []
        relevant = []
        points = 0
        for repo in repos[:5]:
            is_relevant = any(tag in (repo.get("language") or "").lower() for tag in ["python", "javascript", "typescript", "go", "java"]) or "agent" in (repo.get("name") or "").lower()
            if is_relevant:
                relevant.append(repo.get("name"))
        if profile.get("updated_at"):
            points += 2
        if relevant:
            points += 3
        if profile.get("public_repos", 0) > 2:
            points += 2
        if profile.get("public_repos", 0) == 0:
            points = 0
        summary = (
            f"GitHub profile {username} is active with {profile.get('public_repos', 0)} public repos; "
            f"relevant repos: {', '.join(relevant) if relevant else 'none observed'}."
        )
        return {
            "status": "ok",
            "summary": summary,
            "error": "",
            "points": min(points, 10),
            "username": username,
        }
    except requests.RequestException as exc:
        return {
            "status": "failed",
            "summary": "GitHub enrichment failed.",
            "error": str(exc),
            "points": 0,
        }
