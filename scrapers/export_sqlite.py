#!/usr/bin/env python3
"""Export the deduped catalog to SQLite (codex.db).

Loads catalog_v2.json into table `apis` and quarantined.json into table
`quarantined`, replacing codex.db each run. Stdlib only.
"""
import json
import os
import sqlite3

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

SCHEMA = """
CREATE TABLE apis (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT,
  docs_url TEXT, website TEXT, category TEXT, auth TEXT,
  pricing_free TEXT, free_tier_known INTEGER, health REAL,
  provenance TEXT, source_ids TEXT);
CREATE TABLE quarantined (
  id INTEGER PRIMARY KEY, name TEXT, description TEXT, website TEXT,
  docs_url TEXT, reason TEXT);
"""


def _text(v):
    return None if v is None else str(v)


def _flag(v):
    return 1 if v in (True, "True", 1, "1") else 0


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _json(v):
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return json.dumps(v)


def main():
    with open(os.path.join(BASE, "catalog_v2.json")) as f:
        catalog = json.load(f)
    qpath = os.path.join(BASE, "quarantined.json")
    quarantined = []
    if os.path.exists(qpath):
        with open(qpath) as f:
            quarantined = json.load(f)

    db_path = os.path.join(BASE, "codex.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    db = sqlite3.connect(db_path)
    db.executescript(SCHEMA)
    db.executemany(
        "INSERT INTO apis (name, description, docs_url, website, category,"
        " auth, pricing_free, free_tier_known, health, provenance, source_ids)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [
            (
                r.get("name") or "",
                _text(r.get("description")),
                _text(r.get("docs_url")),
                _text(r.get("website")),
                _text(r.get("category")),
                _text(r.get("auth")),
                _text(r.get("pricing_free")),
                _flag(r.get("free_tier_known")),
                _num(r.get("health")),
                _json(r.get("provenance")),
                _json(r.get("source_ids")),
            )
            for r in catalog
        ],
    )
    db.executemany(
        "INSERT INTO quarantined (name, description, website, docs_url, reason)"
        " VALUES (?,?,?,?,?)",
        [
            (
                _text(r.get("name")),
                _text(r.get("description")),
                _text(r.get("website")),
                _text(r.get("docs_url")),
                _text(r.get("quarantine_reason")),
            )
            for r in quarantined
        ],
    )
    db.commit()
    db.close()
    print(f"codex.db: {len(catalog)} apis, {len(quarantined)} quarantined")


if __name__ == "__main__":
    main()
