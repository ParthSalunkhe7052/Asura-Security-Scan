import os
import importlib
import pytest

def test_llm_adapter_no_key_does_not_raise(monkeypatch):
    monkeypatch.delenv("OPENROUTER_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    module = importlib.import_module("app.core.llm_adapter")
    result = module.send_prompt("hello", use_fallback=True)
    assert result["success"] is False
    assert "key" in result["error"].lower()