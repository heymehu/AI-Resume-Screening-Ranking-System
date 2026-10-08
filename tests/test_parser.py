from pathlib import Path

from src.extractor import extract_name
from src.parser import parse_resume


def test_parse_valid_resume_text(tmp_path: Path):
    path = tmp_path / "candidate.txt"
    path.write_text("Alice Smith\nPython Developer\nLangChain | FastAPI | Docker\n", encoding="utf-8")
    text = parse_resume(path)
    assert "Alice Smith" in text
    assert "FastAPI" in text


def test_parse_empty_resume_is_handled_gracefully(tmp_path: Path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    text = parse_resume(path)
    assert text == ""


def test_name_extraction_drops_contact_and_role_labels():
    assert extract_name("Kartikay Sinha Phone: +91 1234567890 | Email: person@example.com") == "Kartikay Sinha"
    assert extract_name("Prajwal A S Python Backend Developer | RAG") == "Prajwal A S"


def test_name_extraction_does_not_treat_section_heading_as_name():
    assert extract_name("SUMMARY Software Engineering Job Simulation\nPython | TensorFlow") == "Unknown Candidate"
