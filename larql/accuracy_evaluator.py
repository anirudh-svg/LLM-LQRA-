from __future__ import annotations

from larql.models import EvaluationResult, FactResult, Triple


class AccuracyEvaluator:
    def evaluate(self, response: str, expected: list[Triple]) -> EvaluationResult:
        if not expected:
            return EvaluationResult(results=[], score=0.0, message="No expected facts provided")

        response_lower = response.lower()
        results: list[FactResult] = []
        for triple in expected:
            matched = triple.object.lower() in response_lower
            results.append(FactResult(triple=triple, matched=matched))

        score = sum(1 for r in results if r.matched) / len(results)
        return EvaluationResult(results=results, score=score)
