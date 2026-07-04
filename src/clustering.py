"""
Unsupervised Identity Clustering
==================================

Groups identities into clusters based on their encoder outputs.
Uses hierarchical clustering (no external dependencies).

Usage:
    from src.clustering import cluster_identities
    clusters = cluster_identities("output/unified_signatures.json", n_clusters=3)
"""

import json
import math
from collections import defaultdict
from typing import Optional


def cluster_identities(signatures_path: str, n_clusters: int = 3) -> dict:
    """Cluster identities using hierarchical agglomerative clustering."""
    with open(signatures_path) as f:
        data = json.load(f)

    if isinstance(data, list):
        sigs = {s.get("id", s.get("identity", "")): s for s in data}
    else:
        sigs = data

    # Extract feature vectors
    names = list(sigs.keys())
    vectors = {}
    for name, sig in sigs.items():
        vectors[name] = _flatten(sig)

    # Compute distance matrix
    n = len(names)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = _euclidean(vectors[names[i]], vectors[names[j]])
            dist[i][j] = d
            dist[j][i] = d

    # Agglomerative clustering (single linkage)
    clusters = [[i] for i in range(n)]
    cluster_dist = {}

    while len(clusters) > n_clusters:
        # Find closest pair of clusters
        min_dist = float("inf")
        merge_i, merge_j = 0, 1

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = _cluster_distance(clusters[i], clusters[j], dist)
                if d < min_dist:
                    min_dist = d
                    merge_i, merge_j = i, j

        # Merge
        clusters[merge_i] = clusters[merge_i] + clusters[merge_j]
        del clusters[merge_j]

    # Assign cluster labels
    assignments = {}
    for cluster_idx, member_indices in enumerate(clusters):
        for idx in member_indices:
            assignments[names[idx]] = cluster_idx

    # Compute cluster summaries
    cluster_summaries = {}
    for cluster_idx in range(n_clusters):
        members = [n for n, c in assignments.items() if c == cluster_idx]
        if not members:
            continue

        # Average resonance
        resonances = []
        for m in members:
            sig = sigs.get(m, {})
            res = sig.get("resonance", {})
            score = res.get("score", 0) if isinstance(res, dict) else 0
            resonances.append(score)

        avg_resonance = sum(resonances) / len(resonances) if resonances else 0

        cluster_summaries[cluster_idx] = {
            "members": members,
            "size": len(members),
            "avg_resonance": round(avg_resonance, 1),
            "member_resonances": dict(zip(members, [round(r, 1) for r in resonances])),
        }

    return {
        "n_clusters": n_clusters,
        "assignments": assignments,
        "clusters": cluster_summaries,
        "method": "agglomerative_single_linkage",
    }


def _flatten(sig: dict) -> dict:
    vec = {}
    for enc_name, enc_data in sig.get("encoders", {}).items():
        if isinstance(enc_data, dict):
            for k, v in enc_data.items():
                if isinstance(v, (int, float)):
                    vec[f"{enc_name}_{k}"] = float(v)
    return vec


def _euclidean(a: dict, b: dict) -> float:
    keys = set(a.keys()) | set(b.keys())
    return math.sqrt(sum((a.get(k, 0) - b.get(k, 0)) ** 2 for k in keys))


def _cluster_distance(c1: list, c2: list, dist: list) -> float:
    """Single linkage: minimum distance between any pair."""
    min_d = float("inf")
    for i in c1:
        for j in c2:
            if dist[i][j] < min_d:
                min_d = dist[i][j]
    return min_d
