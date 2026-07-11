"""
SQLite Persistence Layer
=========================

Stores identity signatures, drift history, and knowledge bubbles
in a local SQLite database for historical tracking.

Usage:
    from src.persistence import IdentityDB
    db = IdentityDB("output/identity.db")
    db.store_signature("Captain", signature_dict)
    history = db.get_history("Captain")
"""

import json
import os
import sqlite3
import time
from typing import Optional


class IdentityDB:
    def __init__(self, db_path: str = "output/identity.db"):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                signature TEXT NOT NULL,
                resonance REAL,
                fingerprint TEXT,
                created_at REAL DEFAULT (strftime('%s','now')),
                UNIQUE(name)
            );
            CREATE TABLE IF NOT EXISTS drift_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                variant TEXT NOT NULL,
                resonance REAL,
                delta REAL,
                created_at REAL DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS knowledge_bubbles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                insight TEXT NOT NULL,
                confidence REAL,
                category TEXT,
                evidence TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                prediction TEXT NOT NULL,
                method TEXT,
                created_at REAL DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS reference_figures (
                qid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                metadata TEXT NOT NULL,
                source_revision INTEGER,
                refreshed_at REAL DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS reference_signatures (
                qid TEXT PRIMARY KEY REFERENCES reference_figures(qid),
                signature TEXT NOT NULL,
                feature_vector TEXT NOT NULL,
                engine_revision TEXT NOT NULL,
                created_at REAL DEFAULT (strftime('%s','now'))
            );
        """)
        self.conn.commit()

    def _json_default(self, obj):
        if hasattr(obj, '__dataclass_fields__'):
            return {k: getattr(obj, k) for k in obj.__dataclass_fields__}
        if hasattr(obj, '_asdict'):
            return obj._asdict()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    def store_signature(self, name: str, sig: dict):
        resonance = sig.get("resonance", {})
        score = resonance.get("score", 0) if isinstance(resonance, dict) else 0
        fingerprint = sig.get("fingerprint", {})
        fp_hash = fingerprint.get("hash", "") if isinstance(fingerprint, dict) else ""

        self.conn.execute(
            "INSERT OR REPLACE INTO signatures (name, signature, resonance, fingerprint) VALUES (?, ?, ?, ?)",
            (name, json.dumps(sig, default=self._json_default), score, fp_hash),
        )
        self.conn.commit()

    def store_reference_signature(self, record: dict, sig: dict,
                                  vector: list[float], engine_revision: str):
        """Persist source metadata and the exact signature used for comparison."""
        self.conn.execute(
            """INSERT OR REPLACE INTO reference_figures
               (qid, name, metadata, source_revision, refreshed_at)
               VALUES (?, ?, ?, ?, strftime('%s','now'))""",
            (
                record["qid"], record["text"],
                json.dumps(record, sort_keys=True, default=self._json_default),
                record.get("provenance", {}).get("wikidata_revision"),
            ),
        )
        self.conn.execute(
            """INSERT OR REPLACE INTO reference_signatures
               (qid, signature, feature_vector, engine_revision, created_at)
               VALUES (?, ?, ?, ?, strftime('%s','now'))""",
            (
                record["qid"], json.dumps(sig, default=self._json_default),
                json.dumps(vector), engine_revision,
            ),
        )
        self.conn.commit()

    def reference_stats(self) -> dict:
        figures = self.conn.execute("SELECT COUNT(*) FROM reference_figures").fetchone()[0]
        signatures = self.conn.execute("SELECT COUNT(*) FROM reference_signatures").fetchone()[0]
        return {"reference_figures": figures, "reference_signatures": signatures}

    def get_signature(self, name: str) -> Optional[dict]:
        row = self.conn.execute("SELECT signature FROM signatures WHERE name = ?", (name,)).fetchone()
        return json.loads(row[0]) if row else None

    def get_all_names(self) -> list:
        return [r[0] for r in self.conn.execute("SELECT name FROM signatures ORDER BY name").fetchall()]

    def store_drift(self, name: str, variant: str, resonance: float, delta: float):
        self.conn.execute(
            "INSERT INTO drift_history (name, variant, resonance, delta) VALUES (?, ?, ?, ?)",
            (name, variant, resonance, delta),
        )
        self.conn.commit()

    def get_drift_history(self, name: str) -> list:
        rows = self.conn.execute(
            "SELECT variant, resonance, delta, created_at FROM drift_history WHERE name = ? ORDER BY created_at",
            (name,),
        ).fetchall()
        return [{"variant": r[0], "resonance": r[1], "delta": r[2], "timestamp": r[3]} for r in rows]

    def store_bubble(self, topic: str, insight: str, confidence: float, category: str, evidence: list):
        self.conn.execute(
            "INSERT INTO knowledge_bubbles (topic, insight, confidence, category, evidence) VALUES (?, ?, ?, ?, ?)",
            (topic, insight, confidence, category, json.dumps(evidence)),
        )
        self.conn.commit()

    def get_bubbles(self, category: str = None) -> list:
        if category:
            rows = self.conn.execute(
                "SELECT topic, insight, confidence, category, evidence, created_at FROM knowledge_bubbles WHERE category = ? ORDER BY confidence DESC",
                (category,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT topic, insight, confidence, category, evidence, created_at FROM knowledge_bubbles ORDER BY confidence DESC"
            ).fetchall()
        return [{"topic": r[0], "insight": r[1], "confidence": r[2], "category": r[3], "evidence": json.loads(r[4]), "timestamp": r[5]} for r in rows]

    def store_prediction(self, name: str, prediction: dict, method: str):
        self.conn.execute(
            "INSERT INTO predictions (name, prediction, method) VALUES (?, ?, ?)",
            (name, json.dumps(prediction), method),
        )
        self.conn.commit()

    def get_prediction(self, name: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT prediction, method, created_at FROM predictions WHERE name = ? ORDER BY created_at DESC LIMIT 1",
            (name,),
        ).fetchone()
        if row:
            return {"prediction": json.loads(row[0]), "method": row[1], "timestamp": row[2]}
        return None

    def stats(self) -> dict:
        sigs = self.conn.execute("SELECT COUNT(*) FROM signatures").fetchone()[0]
        bubbles = self.conn.execute("SELECT COUNT(*) FROM knowledge_bubbles").fetchone()[0]
        predictions = self.conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        drift = self.conn.execute("SELECT COUNT(*) FROM drift_history").fetchone()[0]
        return {"signatures": sigs, "bubbles": bubbles, "predictions": predictions, "drift_records": drift}

    def close(self):
        self.conn.close()
