from __future__ import annotations

import os
import sqlite3

from larql.graph_store import GraphStore
from larql.models import Triple

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS edges (
    subject   TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object    TEXT NOT NULL,
    PRIMARY KEY (subject, predicate, object)
);
"""


class PersistenceLayer:
    def save(self, store: GraphStore, db_path: str) -> None:
        con = sqlite3.connect(db_path)
        try:
            con.execute(_CREATE_TABLE)
            con.execute("DELETE FROM edges")
            con.executemany(
                "INSERT OR REPLACE INTO edges (subject, predicate, object) VALUES (?, ?, ?)",
                [(t.subject, t.predicate, t.object) for t in store.all_edges()],
            )
            con.commit()
        finally:
            con.close()

    def load(self, db_path: str) -> GraphStore:
        store = GraphStore()
        if not os.path.exists(db_path):
            return store
        con = sqlite3.connect(db_path)
        try:
            con.execute(_CREATE_TABLE)
            rows = con.execute("SELECT subject, predicate, object FROM edges").fetchall()
        finally:
            con.close()
        for subject, predicate, obj in rows:
            store.upsert(Triple(subject=subject, predicate=predicate, object=obj))
        return store
