"""Unit tests for AccuracyEvaluator."""
from __future__ import annotations

from larql.accuracy_evaluator import AccuracyEvaluator
from larql.models import Triple


def test_full_match():
    ev = AccuracyEvaluator()
    triples = [Triple("Eiffel Tower", "is in", "Paris")]
    result = ev.evaluate("The Eiffel Tower is in Paris.", triples)
    assert result.score == 1.0
    assert result.results[0].matched is True


def test_no_match():
    ev = AccuracyEvaluator()
    triples = [Triple("Eiffel Tower", "is in", "Paris")]
    result = ev.evaluate("I don't know.", triples)
    assert result.score == 0.0
    assert result.results[0].matched is False


def test_partial_match():
    ev = AccuracyEvaluator()
    triples = [
        Triple("A", "r", "Paris"),
        Triple("B", "r", "London"),
    ]
    result = ev.evaluate("Paris is a city.", triples)
    assert result.score == 0.5
    matched = {r.triple.object: r.matched for r in result.results}
    assert matched["Paris"] is True
    assert matched["London"] is False


def test_case_insensitive():
    ev = AccuracyEvaluator()
    triples = [Triple("X", "r", "PARIS")]
    result = ev.evaluate("paris is great", triples)
    assert result.score == 1.0


def test_empty_expected():
    ev = AccuracyEvaluator()
    result = ev.evaluate("some response", [])
    assert result.score == 0.0
    assert "No expected facts" in result.message
    assert result.results == []
