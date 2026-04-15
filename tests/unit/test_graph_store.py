import pytest

from larql.graph_store import GraphStore
from larql.models import QuerySpec, Triple


def make_triple(s="Eiffel Tower", p="is located in", o="Paris"):
    return Triple(subject=s, predicate=p, object=o)


def test_upsert_stores_triple():
    store = GraphStore()
    t = make_triple()
    store.upsert(t)
    assert store.all_edges() == [t]


def test_upsert_idempotent():
    store = GraphStore()
    t = make_triple()
    store.upsert(t)
    store.upsert(t)
    assert store.all_edges() == [t]


def test_upsert_batch():
    store = GraphStore()
    triples = [
        Triple("A", "rel", "B"),
        Triple("A", "rel2", "C"),
    ]
    store.upsert_batch(triples)
    assert set(map(tuple, [(t.subject, t.predicate, t.object) for t in store.all_edges()])) == {
        ("A", "rel", "B"),
        ("A", "rel2", "C"),
    }


def test_query_returns_matching_edges():
    store = GraphStore()
    store.upsert(Triple("Paris", "has", "Eiffel Tower"))
    store.upsert(Triple("Paris", "has", "Louvre"))
    store.upsert(Triple("London", "has", "Big Ben"))
    results = store.query(QuerySpec(subject="Paris"))
    subjects = {t.subject for t in results}
    objects = {t.object for t in results}
    assert subjects == {"Paris"}
    assert objects == {"Eiffel Tower", "Louvre"}


def test_query_with_predicate_filter():
    store = GraphStore()
    store.upsert(Triple("Paris", "has", "Eiffel Tower"))
    store.upsert(Triple("Paris", "capital_of", "France"))
    results = store.query(QuerySpec(subject="Paris", predicate_filter="has"))
    assert len(results) == 1
    assert results[0].object == "Eiffel Tower"


def test_query_absent_subject_returns_empty():
    store = GraphStore()
    assert store.query(QuerySpec(subject="Unknown")) == []


def test_query_empty_graph_returns_empty():
    store = GraphStore()
    assert store.query(QuerySpec(subject="Anything")) == []


def test_all_edges_empty_graph():
    store = GraphStore()
    assert store.all_edges() == []


def test_all_edges_returns_all():
    store = GraphStore()
    triples = [Triple("A", "r1", "B"), Triple("C", "r2", "D")]
    store.upsert_batch(triples)
    result = {(t.subject, t.predicate, t.object) for t in store.all_edges()}
    assert result == {("A", "r1", "B"), ("C", "r2", "D")}
