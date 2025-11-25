import os
import json
import pytest
from types import SimpleNamespace


class MockResponse:
    def __init__(self, status_code, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text

    def json(self):
        return self._data


def test_llm_adapter_retry_and_fallback(monkeypatch):
    # Arrange: import adapter fresh
    import importlib
    module = importlib.import_module("app.core.llm_adapter")

    # Mock /models verification to include all three
    def mock_get(url, headers=None, timeout=15):
        if url.endswith("/models"):
            data = {
                "data": [
                    {"id": "meta-llama/llama-3.2-3b-instruct:free"},
                    {"id": "qwen/qwen-2-7b-instruct:free"},
                    {"id": "google/gemini-2.0-flash-exp:free"},
                ]
            }
            return MockResponse(200, data)
        raise AssertionError("Unexpected GET: " + url)

    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    monkeypatch.setenv("LLM_MODELS", "meta-llama/llama-3.2-3b-instruct:free,qwen/qwen-2-7b-instruct:free,google/gemini-2.0-flash-exp:free")
    monkeypatch.setattr(module.requests, "get", mock_get)

    # Sequence of POST responses per attempt
    post_calls = {"count": 0}

    def mock_post(url, headers=None, json=None, timeout=30):
        assert url.endswith("/chat/completions")
        model = json.get("model")
        post_calls["count"] += 1
        # First model: llama -> 429 three times then move on
        if model.startswith("meta-llama/"):
            return MockResponse(429, {"error": {"message": "rate limit"}})
        # Second model: qwen -> 404 endpoint not found
        if model.startswith("qwen/"):
            return MockResponse(404, {"error": {"message": "endpoint not found"}})
        # Third model: gemini -> success
        if model.startswith("google/"):
            data = {
                "model": model,
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"total_tokens": 42},
            }
            return MockResponse(200, data)
        return MockResponse(400, {"error": {"message": "bad request"}})

    monkeypatch.setattr(module.requests, "post", mock_post)

    adapter = module.LLMAdapter()
    res = adapter.send_with_fallback("hello", max_tokens=10, temperature=0)

    # Assert: succeeded on third model after backoff/fallbacks
    assert res["success"] is True
    assert res["response"] == "ok"
    assert res["model"].startswith("google/")
    assert post_calls["count"] >= 3