import sys
import types

from src.llm import LLMProvider


def test_gemini_analysis_uses_configured_model_and_structured_json(monkeypatch):
    calls = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.update(kwargs)
            return types.SimpleNamespace(
                text='{"project_summary":"Built a RAG service.","strengths":["Python"],"concerns":[]}'
            )

    class FakeClient:
        def __init__(self, api_key):
            calls["api_key"] = api_key
            self.models = FakeModels()

    google_module = types.ModuleType("google")
    google_module.genai = types.SimpleNamespace(Client=FakeClient)
    monkeypatch.setitem(sys.modules, "google", google_module)

    result = LLMProvider(api_key="test-key", model="gemini-2.5-flash").analyze_resume(
        "Python engineer built a RAG service."
    )

    assert calls["api_key"] == "test-key"
    assert calls["model"] == "gemini-2.5-flash"
    assert calls["config"]["response_mime_type"] == "application/json"
    assert result["project_summary"] == "Built a RAG service."
    assert result["strengths"] == ["Python"]


def test_gemini_invalid_json_uses_fallback_and_records_error(monkeypatch):
    class FakeModels:
        def generate_content(self, **kwargs):
            return types.SimpleNamespace(text="not json")

    class FakeClient:
        def __init__(self, api_key):
            self.models = FakeModels()

    google_module = types.ModuleType("google")
    google_module.genai = types.SimpleNamespace(Client=FakeClient)
    monkeypatch.setitem(sys.modules, "google", google_module)

    result = LLMProvider(api_key="test-key").analyze_resume(
        "Python engineer built a LangChain retrieval system."
    )

    assert result["error"]
    assert result["strengths"]
