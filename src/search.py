"""
Identity Similarity Search
==========================

Find identities most similar to a given one using precomputed
cosine similarity vectors.

Usage:
    from src.search import IdentitySearch
    search = IdentitySearch.from_signatures("output/unified_signatures.json")
    results = search.find_similar("Captain", top_n=5)
"""

import json
import math
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchResult:
    identity: str
    score: float
    rank: int
    encoder_matches: dict = field(default_factory=dict)


class IdentitySearch:
    """Precomputed identity similarity index for fast lookup."""

    def __init__(self, feature_vectors: dict, feature_keys: list):
        self.feature_keys = feature_keys
        self.vectors = {}
        self.identities = list(feature_vectors.keys())
        for identity, vec in feature_vectors.items():
            self.vectors[identity] = vec

    @classmethod
    def from_signatures(cls, signatures_path: str):
        """Build search index from unified signatures JSON."""
        with open(signatures_path) as f:
            data = json.load(f)

        # Support both list and dict format
        if isinstance(data, list):
            sigs = {s.get("id", s.get("identity", "")): s for s in data}
        else:
            sigs = data

        # Extract feature vectors
        feature_keys = set()
        feature_vectors = {}
        for identity, sig in sigs.items():
            vec = _extract_vector(sig)
            feature_vectors[identity] = vec
            feature_keys.update(vec.keys())

        feature_keys = sorted(feature_keys)
        return cls(feature_vectors, feature_keys)

    def find_similar(self, identity: str, top_n: int = 5) -> list:
        """Find top-N most similar identities."""
        if identity not in self.vectors:
            return []

        query_vec = self.vectors[identity]
        scores = []
        for other_id, other_vec in self.vectors.items():
            if other_id == identity:
                continue
            score = _cosine_similarity(query_vec, other_vec)
            scores.append((other_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []
        for rank, (other_id, score) in enumerate(scores[:top_n], 1):
            results.append(SearchResult(
                identity=other_id,
                score=round(score, 6),
                rank=rank,
            ))
        return results

    def find_twins(self, threshold: float = 0.90) -> list:
        """Find all identity pairs above similarity threshold."""
        pairs = []
        for i, id_a in enumerate(self.identities):
            for id_b in self.identities[i + 1:]:
                score = _cosine_similarity(self.vectors[id_a], self.vectors[id_b])
                if score >= threshold:
                    pairs.append((id_a, id_b, round(score, 6)))
        pairs.sort(key=lambda x: x[2], reverse=True)
        return pairs

    def search_by_pattern(self, pattern: dict) -> list:
        """Search by encoder value ranges.
        
        pattern: {"pythagorean_expression": (1, 9), "linguistic_syllables": (2, 4)}
        """
        results = []
        for identity, vec in self.vectors.items():
            match = True
            for key, (low, high) in pattern.items():
                val = vec.get(key, 0)
                if not (low <= val <= high):
                    match = False
                    break
            if match:
                results.append(identity)
        return results


def _extract_vector(sig: dict) -> dict:
    """Extract flat feature vector from a signature dict."""
    vec = {}
    encoders = sig.get("encoders", {})
    for encoder_name, encoder_data in encoders.items():
        if isinstance(encoder_data, dict):
            for key, val in encoder_data.items():
                if isinstance(val, (int, float)):
                    vec[f"{encoder_name}_{key}"] = float(val)
                elif isinstance(val, list):
                    for i, v in enumerate(val):
                        if isinstance(v, (int, float)):
                            vec[f"{encoder_name}_{key}_{i}"] = float(v)
    # Include analytics if present
    analytics = sig.get("analytics", {})
    for key, val in analytics.items():
        if isinstance(val, (int, float)):
            vec[f"analytics_{key}"] = float(val)
    return vec


def _cosine_similarity(a: dict, b: dict) -> float:
    """Cosine similarity between two sparse vectors."""
    keys = set(a.keys()) & set(b.keys())
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    mag_a = math.sqrt(sum(a[k] ** 2 for k in keys))
    mag_b = math.sqrt(sum(b[k] ** 2 for k in keys))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
