"""Unit tests for ContextBuilder."""
from __future__ import annotations

from larql.context_builder import ContextBuilder
from larql.models import Triple


def test_empty_triples_returns_question():
    cb = ContextBuilder()
    result = cb.build([], "What is the capital of France?")
    assert result == "What is the capital of France?"


def test_non_empty_triples_contains_facts_header():
    cb = ContextBuilder()
    triples = [Triple("Eiffel Tower", "is located in", "Paris")]
    result = cb.build(triples, "Where is the Eiffel Tower?")
    assert "Known facts:" in result
    assert "Eiffel Tower" in result
    assert "is located in" in result
    assert "Paris" in result


def test_non_empty_triples_contains_question():
    cb = ContextBuilder()
    triples = [Triple("A", "rel", "B")]
    question = "What is A?"
    result = cb.build(triples, question)
    assert question in result


def test_context_before_question():
    cb = ContextBuilder()
    triples = [Triple("A", "rel", "B")]
    result = cb.build(triples, "Question here")
    assert result.index("Known facts:") < result.index("Question here")


def test_multiple_triples_all_present():
    cb = ContextBuilder()
    triples = [
        Triple("A", "r1", "B"),
        Triple("C", "r2", "D"),
    ]
    result = cb.build(triples, "q")
    assert "A r1 B" in result
    assert "C r2 D" in result
