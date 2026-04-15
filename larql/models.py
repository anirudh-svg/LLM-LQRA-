from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Triple:
    subject: str
    predicate: str
    object: str


@dataclass
class QuerySpec:
    subject: str
    predicate_filter: str | None = None


@dataclass
class FactResult:
    triple: Triple
    matched: bool


@dataclass
class EvaluationResult:
    results: list[FactResult]
    score: float  # 0.0 - 1.0
    message: str = ""
