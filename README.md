# AI Resume Screening & Ranking System

This project processes a directory of PDF resumes, extracts structured candidate information, applies a deterministic Python + AI eligibility filter, scores every candidate, enriches GitHub signals, and writes one final score-ranked candidate list.

## Project Overview

The system is designed for a practical batch screening workflow:

- Parse all resumes in a given folder
- Handle unreadable or malformed PDF files without stopping the batch
- Extract email, phone, skills, project language, GitHub URL, and other metadata
- Apply a hard filter for Python + AI/agentic evidence before ranking
- Score all candidates using the same evidence-based 100-point rubric; eligibility is shown as a separate status
- Enrich GitHub data as a lightweight factor
- Emit explainable results in JSON for downstream review
- Print a single final candidate ranking containing eligible and rejected candidates

## Architecture

PDF
 ↓
Parser
 ↓
Extraction
 ↓
Eligibility
 ↓
LLM Analysis
 ↓
Scoring
 ↓
GitHub Enrichment
 ↓
Ranking
 ↓
JSON

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
```

## Environment Variables

The implementation uses environment variables only for optional external integrations:

- `LLM_API_KEY`: Google Gemini API key for resume summarization
- `LLM_MODEL`: Gemini model name (defaults to `gemini-2.5-flash`)
- `GITHUB_TOKEN`: optional GitHub API token to reduce rate limits

Copy the template file and adjust values as needed:

```bash
cp .env.example .env
```

## Run

```bash
python main.py --input ./resumes --output ./output/results.json
```

## Scoring Strategy

The score is capped at 100 points and split into these categories:

- AI / Agentic / RAG Project Depth: 40
- Python & Backend Engineering: 30
- Cloud / Deployment / Full Stack: 15
- GitHub Activity: 10
- Engineering Depth: 5

The AI/project-depth score is weighted highest because the assignment emphasizes applied AI engineering rather than thin API wrappers. Shallow LLM-only projects are penalized.

## Eligibility Strategy

A resume is only eligible when both conditions are satisfied:

- Python evidence must appear in real work, skills, or project language
- AI/agentic evidence must be meaningful, including terms like LangChain, LangGraph, RAG, embeddings, vector search, agentic workflows, tool calling, or LLM-based systems

This logic remains deterministic and is enforced before scoring.

## GitHub Strategy

If a GitHub URL is present, the system attempts a lightweight public API lookup. A maximum of 10 points is available:

- recent activity and repository freshness
- maintained public repositories
- Python/AI-relevant repositories

Private profiles, missing GitHub links, or API failures do not reject the candidate; they simply record a status and zero or reduced points.

## LLM Strategy

The Google Gemini SDK is used to add value to a resume summary where it is helpful, mainly for project summaries and evidence-backed strengths/concerns. The default model is `gemini-2.5-flash`. The hard eligibility logic still stays deterministic and does not rely on model output.

If the API key is absent or the request fails, the system falls back to a deterministic local summary without failing the whole run.

The score breakdown is based on matched resume evidence. Mentions in extracted project/work experience receive more weight than other resume mentions. All candidates, including rejected candidates, appear exactly once in the same ranking, sorted by score; eligibility remains a separate status.

## Error Handling

The pipeline is designed to isolate failures:

- corrupted or unreadable PDFs
- empty resumes
- missing GitHub data
- API timeout or rate limit failures
- invalid LLM output
- duplicate resumes

None of these stop the full batch. Failures are recorded in the output JSON instead.

## Design Decisions

### Filtering strategy
The project keeps the eligibility rule explicit and deterministic. This avoids unpredictable LLM gatekeeping and ensures the evaluation is explainable.

### Scoring strategy
The scoring rubric matches the assignment: strong AI project depth is rewarded most heavily, while shallow wrappers or tutorial-style implementations receive penalties.

### LLM usage
The LLM is used as a summary assist rather than the primary decision engine. This keeps the system robust and transparent.

### GitHub scoring
GitHub scoring is intentionally lightweight and additive: it helps differentiate active engineers without turning missing GitHub into a hard rejection.

### Why the architecture was kept simple
The repository uses a small set of focused modules and avoids frontend, database, or deployment complexity. That keeps the work within a practical 2–3 hour scope while still satisfying the assignment requirements.

## If I Had More Time

- Add a more advanced PDF cleaning and section parser for inconsistent resumes
- Add stronger GitHub repository scoring and commit-pattern analysis
- Add resume clustering and deduplication via similarity matching
- Add CI-based automated output validation for the full dataset
