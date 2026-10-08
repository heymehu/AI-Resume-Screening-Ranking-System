from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.default_input_dir = Path("./resumes")
        self.default_output_path = Path("./output/results.json")


settings = Settings()
