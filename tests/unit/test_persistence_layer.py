"""Unit tests for PersistenceLayer."""
from __future__ import annotations

import os
import tempfile

from larql.graph_store import GraphStore
from larql.models import Triple
from larql.persistence_layer import PersistenceLayer


def _edges_set(store: GraphStore) -> set[tuple]:
    return {(t.subject, t.predicate, t.object) for t in store.all_edges()}


def test_save_and_load_round_trip():
    pl = PersistenceLayer()
    store = GraphStore()
    store.upsert(Triple("Eiffel Tower", "is in", "Paris"))
    store.upsert(Triple("Python", "created by", "Guido"))

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        pl.save(store, db_path)
        loaded = pl.load(db_path)
        assert _edges_set(loaded) == _edges_set(store)
    finally:
        os.unlink(db_path)


def test_load_missing_file_returns_empty():
    pl = PersistenceLayer()
    store = pl.load("/nonexistent/path/that/does/not/exist.db")
    assert store.all_edges() == []


def test_save_replaces_previous_data():
    pl = PersistenceLayer()
    store1 = GraphStore()
    store1.upsert(Triple("A", "r", "B"))

    store2 = GraphStore()
    store2.upsert(Triple("C", "r", "D"))

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        pl.save(store1, db_path)
        pl.save(store2, db_path)
        loaded = pl.load(db_path)
        assert _edges_set(loaded) == {("C", "r", "D")}
    finally:
        os.unlink(db_path)


def test_empty_store_saves_and_loads():
    pl = PersistenceLayer()
    store = GraphStore()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        pl.save(store, db_path)
        loaded = pl.load(db_path)
        assert loaded.all_edges() == []
    finally:
        os.unlink(db_path)
