from __future__ import annotations

import json
import re

from larql.exceptions import MalformedTripleError
from larql.llm_client import LLMClient
from larql.models import QuerySpec, Triple

_STATEMENT_PROMPT = """\
Extract a knowledge triple from the following sentence.
Return ONLY a JSON object with exactly these keys: subject, predicate, object.
Do not include any explanation or extra text.

Sentence: {text}

JSON:"""

_QUERY_PROMPT = """\
Extract the query subject and optional predicate filter from the following question.
Return ONLY a JSON object with key "subject" (required) and optionally "predicate_filter".
Do not include any explanation or extra text.

Question: {text}

JSON:"""


def _extract_json(raw: str) -> dict:
    """Pull the first JSON object out of a potentially noisy LLM response."""
    match = re.search(r"\{.*?\}", raw, re.DOTALL)
    if not match:
        raise MalformedTripleError(f"No JSON object found in LLM response: {raw!r}")
    return json.loads(match.group())


class LARQLParser:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def parse_statement(self, text: str) -> Triple:
        raw = self._llm.complete(_STATEMENT_PROMPT.format(text=text))
        data = _extract_json(raw)
        for field in ("subject", "predicate", "object"):
            if not data.get(field):
                raise MalformedTripleError(f"Missing required field: '{field}'")
        return Triple(
            subject=data["subject"],
            predicate=data["predicate"],
            object=data["object"],
        )

    def parse_query(self, text: str) -> QuerySpec:
        raw = self._llm.complete(_QUERY_PROMPT.format(text=text))
        data = _extract_json(raw)
        if not data.get("subject"):
            raise MalformedTripleError("Missing required field: 'subject'")
        return QuerySpec(
            subject=data["subject"],
            predicate_filter=data.get("predicate_filter"),
        )
