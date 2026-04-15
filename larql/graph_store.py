from __future__ import annotations

import networkx as nx

from larql.models import QuerySpec, Triple


class GraphStore:
    def __init__(self) -> None:
        self._graph: nx.DiGraph = nx.DiGraph()

    def upsert(self, triple: Triple) -> None:
        self._graph.add_edge(
            triple.subject,
            triple.object,
            predicate=triple.predicate,
        )

    def upsert_batch(self, triples: list[Triple]) -> None:
        for triple in triples:
            self.upsert(triple)

    def query(self, spec: QuerySpec) -> list[Triple]:
        if not self._graph.has_node(spec.subject):
            return []
        results = []
        for _, obj, data in self._graph.out_edges(spec.subject, data=True):
            predicate = data.get("predicate", "")
            if spec.predicate_filter is not None and predicate != spec.predicate_filter:
                continue
            results.append(Triple(subject=spec.subject, predicate=predicate, object=obj))
        return results

    def all_edges(self) -> list[Triple]:
        return [
            Triple(subject=subj, predicate=data.get("predicate", ""), object=obj)
            for subj, obj, data in self._graph.edges(data=True)
        ]
