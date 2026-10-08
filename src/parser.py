from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def clean_text(value: str) -> str:
    text = unicodedata.normalize("NFKC", value)
    text = text.replace("\x00", "")
    text = re.sub(r"[\u0000-\u001F\u007F]+", " ", text)
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_text_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return clean_text(text)


def parse_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages: List[str] = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            pages.append(clean_text(extracted))
    return "\n".join(pages).strip()


def parse_resume(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf_file(path)
    if suffix == ".txt":
        return read_text_file(path)
    raise ValueError(f"Unsupported resume format: {suffix}")


def find_resume_files(input_dir: str | Path) -> List[Path]:
    base_dir = Path(input_dir)
    if not base_dir.exists():
        return []
    files = [
        path for path in base_dir.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files, key=lambda item: item.name.lower())


def iter_resume_files(input_dir: str | Path) -> Iterable[Path]:
    for path in find_resume_files(input_dir):
        yield path
