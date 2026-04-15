from __future__ import annotations

from larql.accuracy_evaluator import AccuracyEvaluator
from larql.context_builder import ContextBuilder
from larql.graph_store import GraphStore
from larql.larql_parser import LARQLParser
from larql.llm_client import LLMClient
from larql.models import Triple
from larql.persistence_layer import PersistenceLayer


class LARQLPipeline:
    def __init__(self, db_path: str = "knowledge.db") -> None:
        self._db_path = db_path
        self._llm = LLMClient()
        self._parser = LARQLParser(self._llm)
        self._store = PersistenceLayer().load(db_path)
        self._persistence = PersistenceLayer()
        self._context_builder = ContextBuilder()
        self._evaluator = AccuracyEvaluator()

    def inject(self, text: str) -> Triple:
        triple = self._parser.parse_statement(text)
        self._store.upsert(triple)
        self._persistence.save(self._store, self._db_path)
        return triple

    def inject_batch(self, texts: list[str]) -> list[Triple]:
        triples = [self._parser.parse_statement(t) for t in texts]
        self._store.upsert_batch(triples)
        self._persistence.save(self._store, self._db_path)
        return triples

    def query_and_answer(
        self,
        question: str,
        expected_triples: list[Triple] | None = None,
    ) -> dict:
        spec = self._parser.parse_query(question)
        edges = self._store.query(spec)
        context = self._context_builder.build(edges, question)
        response = self._llm.complete(context)
        evaluation = self._evaluator.evaluate(response, expected_triples or [])
        return {
            "context": context,
            "response": response,
            "evaluation": evaluation,
        }
