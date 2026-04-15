"""Integration smoke test for the full pipeline (mocked LLM)."""
from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from larql.models import Triple
from larql.pipeline import LARQLPipeline


def _make_pipeline(db_path: str, llm_responses: list[str]) -> LARQLPipeline:
    """Build a pipeline with a mocked LLM that returns responses in sequence."""
    pipeline = LARQLPipeline.__new__(LARQLPipeline)
    pipeline._db_path = db_path

    from larql.accuracy_evaluator import AccuracyEvaluator
    from larql.context_builder import ContextBuilder
    from larql.graph_store import GraphStore
    from larql.larql_parser import LARQLParser
    from larql.llm_client import LLMClient
    from larql.persistence_layer import PersistenceLayer

    mock_llm = MagicMock(spec=LLMClient)
    mock_llm.complete.side_effect = llm_responses

    pipeline._llm = mock_llm
    pipeline._parser = LARQLParser(mock_llm)
    pipeline._store = GraphStore()
    pipeline._persistence = PersistenceLayer()
    pipeline._context_builder = ContextBuilder()
    pipeline._evaluator = AccuracyEvaluator()
    return pipeline


def test_inject_then_query_end_to_end():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        # LLM responses: parse_statement, parse_query, complete (answer)
        responses = [
            '{"subject": "Eiffel Tower", "predicate": "is located in", "object": "Paris"}',
            '{"subject": "Eiffel Tower"}',
            "The Eiffel Tower is located in Paris.",
        ]
        pipeline = _make_pipeline(db_path, responses)

        triple = pipeline.inject("The Eiffel Tower is located in Paris")
        assert triple == Triple("Eiffel Tower", "is located in", "Paris")

        result = pipeline.query_and_answer(
            "Where is the Eiffel Tower?",
            expected_triples=[Triple("Eiffel Tower", "is located in", "Paris")],
        )
        assert "Paris" in result["response"]
        assert result["evaluation"].score == 1.0
    finally:
        os.unlink(db_path)


def test_inject_batch():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        responses = [
            '{"subject": "A", "predicate": "r", "object": "B"}',
            '{"subject": "C", "predicate": "r", "object": "D"}',
        ]
        pipeline = _make_pipeline(db_path, responses)
        triples = pipeline.inject_batch(["A r B", "C r D"])
        assert len(triples) == 2
        edges = {(t.subject, t.predicate, t.object) for t in pipeline._store.all_edges()}
        assert ("A", "r", "B") in edges
        assert ("C", "r", "D") in edges
    finally:
        os.unlink(db_path)
