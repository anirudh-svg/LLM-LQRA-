"""Unit tests for LLMClient."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from larql.exceptions import LLMUnavailableError
from larql.llm_client import LLMClient


def _mock_ollama_response(text: str):
    resp = MagicMock()
    resp.json.return_value = {"response": text}
    resp.raise_for_status.return_value = None
    return resp


def test_ollama_success():
    client = LLMClient()
    with patch("larql.llm_client.requests.post", return_value=_mock_ollama_response("hello")) as mock_post:
        result = client.complete("say hello")
    assert result == "hello"
    mock_post.assert_called_once()


def test_openai_fallback():
    client = LLMClient()
    mock_choice = MagicMock()
    mock_choice.message.content = "openai answer"
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    with patch("larql.llm_client.requests.post", side_effect=Exception("ollama down")):
        with patch("openai.OpenAI") as mock_openai_cls:
            mock_openai_cls.return_value.chat.completions.create.return_value = mock_completion
            result = client.complete("test prompt")

    assert result == "openai answer"


def test_both_unavailable_raises():
    client = LLMClient()
    with patch("larql.llm_client.requests.post", side_effect=Exception("ollama down")):
        with patch("openai.OpenAI", side_effect=Exception("openai down")):
            with pytest.raises(LLMUnavailableError):
                client.complete("test")
