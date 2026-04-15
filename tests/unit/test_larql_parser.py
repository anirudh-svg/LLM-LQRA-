"""Unit tests for LARQLParser."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from larql.exceptions import MalformedTripleError
from larql.larql_parser import LARQLParser
from larql.models import QuerySpec, Triple


def _parser(response: str) -> LARQLParser:
    llm = MagicMock()
    llm.complete.return_value = response
    return LARQLParser(llm)


def test_parse_statement_success():
    parser = _parser('{"subject": "Eiffel Tower", "predicate": "is located in", "object": "Paris"}')
    triple = parser.parse_statement("The Eiffel Tower is located in Paris")
    assert triple == Triple("Eiffel Tower", "is located in", "Paris")


def test_parse_statement_missing_subject():
    parser = _parser('{"predicate": "is located in", "object": "Paris"}')
    with pytest.raises(MalformedTripleError, match="subject"):
        parser.parse_statement("...")


def test_parse_statement_missing_predicate():
    parser = _parser('{"subject": "Eiffel Tower", "object": "Paris"}')
    with pytest.raises(MalformedTripleError, match="predicate"):
        parser.parse_statement("...")


def test_parse_statement_missing_object():
    parser = _parser('{"subject": "Eiffel Tower", "predicate": "is located in"}')
    with pytest.raises(MalformedTripleError, match="object"):
        parser.parse_statement("...")


def test_parse_statement_no_json():
    parser = _parser("I cannot extract a triple from this.")
    with pytest.raises(MalformedTripleError):
        parser.parse_statement("...")


def test_parse_query_success():
    parser = _parser('{"subject": "Eiffel Tower", "predicate_filter": "is located in"}')
    spec = parser.parse_query("Where is the Eiffel Tower?")
    assert spec == QuerySpec(subject="Eiffel Tower", predicate_filter="is located in")


def test_parse_query_no_filter():
    parser = _parser('{"subject": "Eiffel Tower"}')
    spec = parser.parse_query("Tell me about the Eiffel Tower")
    assert spec.subject == "Eiffel Tower"
    assert spec.predicate_filter is None


def test_parse_query_missing_subject():
    parser = _parser('{"predicate_filter": "is located in"}')
    with pytest.raises(MalformedTripleError, match="subject"):
        parser.parse_query("...")
