from __future__ import annotations

from larql.models import Triple


class ContextBuilder:
    def build(self, triples: list[Triple], question: str) -> str:
        if not triples:
            return question
        facts = "\n".join(
            f"- {t.subject} {t.predicate} {t.object}" for t in triples
        )
        return f"Known facts:\n{facts}\n\nQuestion: {question}"
