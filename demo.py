"""LARQL demo: inject facts, query, evaluate accuracy."""
from __future__ import annotations

import sys

from larql.exceptions import LLMUnavailableError
from larql.models import Triple
from larql.pipeline import LARQLPipeline

FACTS = [
    "The Eiffel Tower is located in Paris",
    "Python was created by Guido van Rossum",
    "The Great Wall is in China",
]

QUERIES = [
    ("Where is the Eiffel Tower?", [Triple("Eiffel Tower", "is located in", "Paris")]),
    ("Who created Python?", [Triple("Python", "was created by", "Guido van Rossum")]),
    ("Where is the Great Wall?", [Triple("Great Wall", "is in", "China")]),
]


def main() -> None:
    try:
        pipeline = LARQLPipeline(db_path="knowledge.db")

        print("=== Injecting facts ===")
        injected: list[Triple] = []
        for fact in FACTS:
            triple = pipeline.inject(fact)
            injected.append(triple)
            print(f"  + {triple.subject} | {triple.predicate} | {triple.object}")

        print("\n=== Querying ===")
        for question, expected in QUERIES:
            print(f"\nQ: {question}")
            result = pipeline.query_and_answer(question, expected_triples=expected)
            print(f"Context:\n{result['context']}")
            print(f"Response: {result['response']}")
            ev = result["evaluation"]
            print(f"Accuracy: {ev.score:.0%} ({sum(r.matched for r in ev.results)}/{len(ev.results)} facts matched)")
            for fr in ev.results:
                status = "✓" if fr.matched else "✗"
                print(f"  {status} {fr.triple.object}")

    except LLMUnavailableError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
