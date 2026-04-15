from __future__ import annotations

import requests

from larql.exceptions import LLMUnavailableError

_OLLAMA_URL = "http://localhost:11434/api/generate"
_OLLAMA_MODEL = "llama3"


class LLMClient:
    """Thin wrapper: tries Ollama first, falls back to OpenAI."""

    def complete(self, prompt: str) -> str:
        try:
            return self._ollama(prompt)
        except Exception:
            pass
        try:
            return self._openai(prompt)
        except Exception:
            pass
        raise LLMUnavailableError(
            "Neither Ollama nor OpenAI is reachable. "
            "Start Ollama locally or set the OPENAI_API_KEY environment variable."
        )

    # ------------------------------------------------------------------
    def _ollama(self, prompt: str) -> str:
        resp = requests.post(
            _OLLAMA_URL,
            json={"model": _OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["response"]

    def _openai(self, prompt: str) -> str:
        import openai  # lazy import so missing key doesn't crash at import time

        client = openai.OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content or ""
