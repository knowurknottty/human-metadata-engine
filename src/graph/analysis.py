"""
Graph Analysis Utilities
========================

Algorithms for analyzing the identity graph:
- Degree centrality (in/out/total)
- Betweenness centrality (approximate)
- Community detection (label propagation)
- Resonance clustering
- Contradiction detection
- Identity drift detection
- Alias convergence scoring

Works on the identity graph JSON structure.
"""

from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict, Counter
from typing import Optional
import json
import math


@dataclass
class NodeMetrics:
    node_id: str
    label: str
    node_type: str
    degree: int
    in_degree: int
    out_degree: int
    centrality: float  # normalized degree centrality
    betweenness: float  # approximate betweenness
    is_hub: bool
    communities: list[str]


@dataclass
class EdgeMetrics:
    source: str
    target: str
    edge_type: str
    confidence: float
    interpretation_level: str
    weight: float  # confidence-weighted weight


@dataclass
class GraphAnalysis:
    total_nodes: int
    total_edges: int
    node_metrics: list[NodeMetrics]
    edge_metrics: list[EdgeMetrics]
    hubs: list[str]  # node IDs with centrality > 0.5
    communities: dict[str, list[str]]  # community_id -> [node_ids]
    resonance_clusters: list[list[str]]  # groups of mutually resonant nodes
    contradictions: list[dict]
    density: float
    avg_degree: float
    strongest_edges: list[dict]
    weakest_edges: list[dict]


def load_graph(path: str) -> dict:
    """Load graph JSON."""
    with open(path, "r") as f:
        return json.load(f)


def compute_degree_centrality(nodes: list[dict], edges: list[dict]) -> dict[str, dict]:
    """Compute in/out/total degree for each node."""
    in_deg = Counter()
    out_deg = Counter()
    for e in edges:
        out_deg[e["source"]] += 1
        in_deg[e["target"]] += 1

    n = len(nodes)
    result = {}
    for node in nodes:
        nid = node["id"]
        total = in_deg[nid] + out_deg[nid]
        centrality = total / (n - 1) if n > 1 else 0
        result[nid] = {
            "in_degree": in_deg[nid],
            "out_degree": out_deg[nid],
            "total_degree": total,
            "centrality": round(centrality, 4),
        }
    return result


def compute_betweenness_approx(nodes: list[dict], edges: list[dict]) -> dict[str, float]:
    """Approximate betweenness centrality using shortest paths (BFS)."""
    node_ids = [n["id"] for n in nodes]
    adj = defaultdict(list)
    for e in edges:
        adj[e["source"]].append(e["target"])
        adj[e["target"]].append(e["source"])

    betweenness = Counter()
    for source in node_ids:
        # BFS from source
        visited = {source}
        queue = [source]
        parents = defaultdict(list)
        distances = {source: 0}
        order = []

        while queue:
            current = queue.pop(0)
            order.append(current)
            for neighbor in adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = distances[current] + 1
                    parents[neighbor].append(current)
                    queue.append(neighbor)

        # Back-propagate dependency
        delta = Counter()
        for node in reversed(order):
            for parent in parents[node]:
                delta[parent] += 1 + delta[node]
            if node != source:
                betweenness[node] += delta[node]

    # Normalize
    n = len(node_ids)
    norm = (n - 1) * (n - 2) if n > 2 else 1
    return {nid: round(betweenness[nid] / norm, 4) for nid in node_ids}


def detect_communities_label_propagation(
    nodes: list[dict], edges: list[dict], max_iter: int = 20
) -> dict[str, list[str]]:
    """Simple label propagation for community detection."""
    node_ids = [n["id"] for n in nodes]
    adj = defaultdict(set)
    for e in edges:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])

    # Initialize each node with its own label
    labels = {nid: nid for nid in node_ids}

    for _ in range(max_iter):
        changed = False
        for nid in node_ids:
            if not adj[nid]:
                continue
            neighbor_labels = Counter(labels[n] for n in adj[nid])
            if neighbor_labels:
                most_common = neighbor_labels.most_common(1)[0][0]
                if labels[nid] != most_common:
                    labels[nid] = most_common
                    changed = True
        if not changed:
            break

    # Group by community
    communities = defaultdict(list)
    for nid, label in labels.items():
        communities[label].append(nid)

    return dict(communities)


def find_resonance_clusters(edges: list[dict], threshold: float = 0.6) -> list[list[str]]:
    """Find groups of nodes connected by high-confidence symbolic edges."""
    symbolic_edges = [
        e for e in edges
        if e.get("interpretation_level") == "symbolic" and e.get("confidence", 0) >= threshold
    ]

    # Build adjacency from symbolic edges
    adj = defaultdict(set)
    for e in symbolic_edges:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])

    # Find connected components
    visited = set()
    clusters = []
    for node in adj:
        if node in visited:
            continue
        cluster = []
        queue = [node]
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            cluster.append(current)
            for neighbor in adj[current]:
                if neighbor not in visited:
                    queue.append(neighbor)
        if len(cluster) > 1:
            clusters.append(sorted(cluster))

    return clusters


def detect_contradictions(edges: list[dict]) -> list[dict]:
    """Find potential contradictions in the graph."""
    contradictions = []

    # Check for edges that might conflict
    edge_pairs = [
        ("LINGUISTICALLY_RESEMBLES", "CONTRASTS_WITH"),
        ("SYMBOLICALLY_RESONATES_WITH", "CONTRASTS_WITH"),
        ("CREATED_BY", "DERIVED_FROM"),  # Direction matters
    ]

    edge_map = defaultdict(list)
    for e in edges:
        key = (e["source"], e["target"])
        edge_map[key].append(e)

    for (src, tgt), es in edge_map.items():
        types = [e["edge_type"] for e in es]
        for type_a, type_b in edge_pairs:
            if type_a in types and type_b in types:
                contradictions.append({
                    "nodes": [src, tgt],
                    "conflict_types": [type_a, type_b],
                    "severity": "medium",
                    "resolution_status": "unresolved",
                    "evidence": [e.get("claim", "") for e in es],
                })

    return contradictions


def compute_graph_density(nodes: list[dict], edges: list[dict]) -> float:
    """Graph density: actual edges / possible edges."""
    n = len(nodes)
    if n <= 1:
        return 0.0
    possible = n * (n - 1)
    return round(len(edges) / possible, 4)


def score_identity_coherence(
    birth_expr: int, birth_soul: int, birth_personality: int,
    alias_exprs: list[int], project_exprs: list[int],
) -> float:
    """
    Score how coherent the identity system is.
    Higher = more aligned across birth, aliases, and projects.
    """
    all_exprs = [birth_expr] + alias_exprs + project_exprs

    # Count expression matches
    matches = 0
    total_pairs = 0
    for i in range(len(all_exprs)):
        for j in range(i + 1, len(all_exprs)):
            total_pairs += 1
            if all_exprs[i] == all_exprs[j]:
                matches += 1

    # Count soul/personality alignment
    alias_souls_match = sum(1 for _ in alias_exprs if True)  # placeholder
    project_souls_match = sum(1 for _ in project_exprs if True)

    if total_pairs == 0:
        return 0.0

    return round(matches / total_pairs, 4)


def analyze_graph(graph_path: str) -> GraphAnalysis:
    """Full graph analysis."""
    graph = load_graph(graph_path)
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    # Degree centrality
    degree = compute_degree_centrality(nodes, edges)

    # Betweenness
    betweenness = compute_betweenness_approx(nodes, edges)

    # Communities
    communities_raw = detect_communities_label_propagation(nodes, edges)
    communities = {}
    for comm_id, member_ids in communities_raw.items():
        label = f"community_{comm_id.split(':')[-1][:8]}"
        communities[label] = member_ids

    # Node metrics
    node_metrics = []
    for node in nodes:
        nid = node["id"]
        deg = degree.get(nid, {})
        btwn = betweenness.get(nid, 0)
        node_metrics.append(NodeMetrics(
            node_id=nid,
            label=node["label"],
            node_type=node["type"],
            degree=deg.get("total_degree", 0),
            in_degree=deg.get("in_degree", 0),
            out_degree=deg.get("out_degree", 0),
            centrality=deg.get("centrality", 0),
            betweenness=btwn,
            is_hub=deg.get("centrality", 0) > 0.3,
            communities=[k for k, v in communities.items() if nid in v],
        ))

    # Edge metrics
    edge_metrics = []
    for e in edges:
        edge_metrics.append(EdgeMetrics(
            source=e["source"],
            target=e["target"],
            edge_type=e["edge_type"],
            confidence=e.get("confidence", 1.0),
            interpretation_level=e.get("interpretation_level", "unknown"),
            weight=e.get("confidence", 1.0),
        ))

    # Hubs
    hubs = [nm.node_id for nm in node_metrics if nm.is_hub]

    # Resonance clusters
    resonance = find_resonance_clusters(edges)

    # Contradictions
    contradictions = detect_contradictions(edges)

    # Density and avg degree
    density = compute_graph_density(nodes, edges)
    avg_degree = sum(nm.degree for nm in node_metrics) / len(node_metrics) if node_metrics else 0

    # Strongest/weakest edges
    sorted_edges = sorted(edge_metrics, key=lambda e: e.confidence, reverse=True)
    strongest = [{"source": e.source, "target": e.target, "confidence": e.confidence}
                 for e in sorted_edges[:5]]
    weakest = [{"source": e.source, "target": e.target, "confidence": e.confidence}
               for e in sorted_edges[-5:]]

    return GraphAnalysis(
        total_nodes=len(nodes),
        total_edges=len(edges),
        node_metrics=node_metrics,
        edge_metrics=edge_metrics,
        hubs=hubs,
        communities=communities,
        resonance_clusters=resonance,
        contradictions=contradictions,
        density=density,
        avg_degree=round(avg_degree, 2),
        strongest_edges=strongest,
        weakest_edges=weakest,
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        graph_path = sys.argv[1]
    else:
        graph_path = "output/identity_graph.json"

    analysis = analyze_graph(graph_path)
    print(f"Graph: {analysis.total_nodes} nodes, {analysis.total_edges} edges")
    print(f"Density: {analysis.density}, Avg degree: {analysis.avg_degree}")
    print(f"Hubs: {analysis.hubs}")
    print(f"Communities: {list(analysis.communities.keys())}")
    print(f"Resonance clusters: {len(analysis.resonance_clusters)}")
    print(f"Contradictions: {len(analysis.contradictions)}")
    print(f"\nTop centrality:")
    for nm in sorted(analysis.node_metrics, key=lambda x: -x.centrality)[:5]:
        print(f"  {nm.label:<25} centrality={nm.centrality}  degree={nm.degree}")
