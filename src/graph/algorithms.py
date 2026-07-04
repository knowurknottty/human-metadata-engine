"""
Advanced Graph Algorithms
=========================

Implements PageRank, spectral clustering, and other graph algorithms
for the identity graph.

Algorithms:
1. PageRank — importance ranking of nodes
2. Spectral Clustering — community detection via eigenvectors
3. Connected Components — find isolated subgraphs
4. Shortest Paths — distance between any two nodes
5. Graph Diameter — longest shortest path
6. Clustering Coefficient — local density measure
7. HITS (Hubs and Authorities) — hub/authority scoring

All algorithms work on the identity graph JSON structure.
"""

from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
import json
import math


@dataclass
class PageRankResult:
    node_id: str
    rank: float
    iterations: int


@dataclass
class SpectralCluster:
    cluster_id: int
    members: list[str]
    internal_density: float


@dataclass
class GraphAlgorithmResults:
    # PageRank
    pagerank: list[PageRankResult]

    # Spectral clustering
    spectral_clusters: list[SpectralCluster]

    # Connected components
    connected_components: list[list[str]]
    num_components: int

    # Diameter and radius
    diameter: int
    radius: int
    eccentricities: dict[str, int]

    # Clustering coefficient
    avg_clustering_coefficient: float
    clustering_coefficients: dict[str, float]

    # HITS
    hubs: dict[str, float]
    authorities: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "pagerank": [{"node_id": r.node_id, "rank": r.rank} for r in self.pagerank],
            "spectral_clusters": [{"id": c.cluster_id, "members": c.members, "density": c.internal_density} for c in self.spectral_clusters],
            "connected_components": self.connected_components,
            "num_components": self.num_components,
            "diameter": self.diameter,
            "radius": self.radius,
            "eccentricities": self.eccentricities,
            "avg_clustering_coefficient": self.avg_clustering_coefficient,
            "clustering_coefficients": self.clustering_coefficients,
            "hubs": self.hubs,
            "authorities": self.authorities,
        }


def load_graph(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def build_adjacency(graph: dict) -> tuple[dict[str, set], dict[str, set], set]:
    """Build adjacency sets: out_adj, in_adj, all_nodes."""
    out_adj = defaultdict(set)
    in_adj = defaultdict(set)
    all_nodes = set()

    for node in graph.get("nodes", []):
        all_nodes.add(node["id"])

    for edge in graph.get("edges", []):
        out_adj[edge["source"]].add(edge["target"])
        in_adj[edge["target"]].add(edge["source"])

    return dict(out_adj), dict(in_adj), all_nodes


# ===================== PAGERANK =====================

def pagerank(
    graph: dict,
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> list[PageRankResult]:
    """Compute PageRank for all nodes."""
    out_adj, in_adj, all_nodes = build_adjacency(graph)
    n = len(all_nodes)
    if n == 0:
        return []

    # Initialize ranks
    ranks = {node: 1.0 / n for node in all_nodes}

    for iteration in range(max_iter):
        new_ranks = {}
        max_diff = 0

        for node in all_nodes:
            # Sum of ranks from incoming links
            in_sum = sum(ranks[src] / len(out_adj.get(src, {node}))
                        for src in in_adj.get(node, []))

            # Personalized PageRank with teleportation
            new_rank = (1 - damping) / n + damping * in_sum
            new_ranks[node] = new_rank
            max_diff = max(max_diff, abs(new_rank - ranks[node]))

        ranks = new_ranks
        if max_diff < tol:
            break

    # Sort by rank
    results = sorted(
        [PageRankResult(node_id=node, rank=round(rank, 6), iterations=iteration + 1)
         for node, rank in ranks.items()],
        key=lambda x: -x.rank,
    )
    return results


# ===================== SPECTRAL CLUSTERING =====================

def spectral_clustering(graph: dict, n_clusters: int = 3) -> list[SpectralCluster]:
    """
    Simplified spectral clustering using the Laplacian.
    Uses power iteration to approximate the Fiedler vector.
    """
    out_adj, _, all_nodes = build_adjacency(graph)
    nodes = sorted(all_nodes)
    n = len(nodes)
    if n < n_clusters:
        return [SpectralCluster(0, nodes, 1.0)]

    node_idx = {node: i for i, node in enumerate(nodes)}

    # Build adjacency matrix (simplified)
    adj = [[0.0] * n for _ in range(n)]
    for src in all_nodes:
        for tgt in out_adj.get(src, []):
            if src in node_idx and tgt in node_idx:
                adj[node_idx[src]][node_idx[tgt]] = 1.0
                adj[node_idx[tgt]][node_idx[src]] = 1.0

    # Degree matrix
    degrees = [sum(row) for row in adj]

    # Laplacian (simplified: L = D - A)
    laplacian = [[0.0] * n for _ in range(n)]
    for i in range(n):
        laplacian[i][i] = degrees[i]
        for j in range(n):
            laplacian[i][j] -= adj[i][j]

    # Power iteration for smallest non-zero eigenvector
    import random
    random.seed(42)
    vector = [random.gauss(0, 1) for _ in range(n)]

    for _ in range(100):
        new_vec = [0.0] * n
        for i in range(n):
            for j in range(n):
                new_vec[i] += laplacian[i][j] * vector[j]
        norm = math.sqrt(sum(v * v for v in new_vec))
        if norm > 0:
            vector = [v / norm for v in new_vec]

    # Sort nodes by eigenvector value and split into clusters
    indexed_vec = [(nodes[i], vector[i]) for i in range(n)]
    indexed_vec.sort(key=lambda x: x[1])

    clusters = []
    chunk_size = n // n_clusters
    for c in range(n_clusters):
        start = c * chunk_size
        end = start + chunk_size if c < n_clusters - 1 else n
        members = [x[0] for x in indexed_vec[start:end]]

        # Compute internal density
        internal_edges = 0
        possible_edges = len(members) * (len(members) - 1) / 2
        for m1 in members:
            for m2 in out_adj.get(m1, set()):
                if m2 in members:
                    internal_edges += 1
        density = internal_edges / possible_edges if possible_edges > 0 else 0

        clusters.append(SpectralCluster(c, members, round(density, 4)))

    return clusters


# ===================== CONNECTED COMPONENTS =====================

def connected_components(graph: dict) -> list[list[str]]:
    """Find connected components using BFS."""
    out_adj, in_adj, all_nodes = build_adjacency(graph)

    # Build undirected adjacency
    undir = defaultdict(set)
    for node in all_nodes:
        for neighbor in out_adj.get(node, set()):
            undir[node].add(neighbor)
            undir[neighbor].add(node)
        for neighbor in in_adj.get(node, set()):
            undir[node].add(neighbor)
            undir[neighbor].add(node)

    visited = set()
    components = []

    for node in all_nodes:
        if node in visited:
            continue
        component = []
        queue = [node]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            for neighbor in undir.get(current, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(sorted(component))

    return sorted(components, key=lambda c: -len(c))


# ===================== SHORTEST PATHS =====================

def shortest_paths(graph: dict) -> dict[str, dict[str, int]]:
    """BFS-based shortest paths between all pairs."""
    out_adj, _, all_nodes = build_adjacency(graph)
    paths = {}

    for source in all_nodes:
        distances = {source: 0}
        queue = [source]
        while queue:
            current = queue.pop(0)
            for neighbor in out_adj.get(current, set()):
                if neighbor not in distances:
                    distances[neighbor] = distances[current] + 1
                    queue.append(neighbor)
        paths[source] = distances

    return paths


def graph_diameter(graph: dict) -> tuple[int, int, dict[str, int]]:
    """Compute diameter, radius, and eccentricities."""
    paths = shortest_paths(graph)
    eccentricities = {}

    for node, dists in paths.items():
        if dists:
            eccentricities[node] = max(dists.values())
        else:
            eccentricities[node] = 0

    if eccentricities:
        diameter = max(eccentricities.values())
        radius = min(v for v in eccentricities.values() if v > 0) if any(v > 0 for v in eccentricities.values()) else 0
    else:
        diameter = 0
        radius = 0

    return diameter, radius, eccentricities


# ===================== CLUSTERING COEFFICIENT =====================

def clustering_coefficients(graph: dict) -> dict[str, float]:
    """Compute local clustering coefficient for each node."""
    out_adj, _, all_nodes = build_adjacency(graph)

    # Undirected adjacency
    undir = defaultdict(set)
    for node in all_nodes:
        for neighbor in out_adj.get(node, set()):
            undir[node].add(neighbor)
            undir[neighbor].add(node)

    coefficients = {}
    for node in all_nodes:
        neighbors = undir.get(node, set())
        k = len(neighbors)
        if k < 2:
            coefficients[node] = 0.0
            continue

        # Count edges between neighbors
        edges_between = 0
        for n1 in neighbors:
            for n2 in neighbors:
                if n1 < n2 and n2 in undir.get(n1, set()):
                    edges_between += 1

        possible = k * (k - 1) / 2
        coefficients[node] = round(edges_between / possible, 4) if possible > 0 else 0.0

    return coefficients


# ===================== HITS =====================

def hits(graph: dict, max_iter: int = 100) -> tuple[dict[str, float], dict[str, float]]:
    """HITS algorithm: compute hub and authority scores."""
    out_adj, in_adj, all_nodes = build_adjacency(graph)
    n = len(all_nodes)
    if n == 0:
        return {}, {}

    # Initialize
    hubs = {node: 1.0 for node in all_nodes}
    auths = {node: 1.0 for node in all_nodes}

    for _ in range(max_iter):
        # Update authorities
        new_auths = {}
        for node in all_nodes:
            new_auths[node] = sum(hubs[src] for src in in_adj.get(node, set()))
        auth_norm = math.sqrt(sum(v * v for v in new_auths.values())) or 1
        auths = {k: v / auth_norm for k, v in new_auths.items()}

        # Update hubs
        new_hubs = {}
        for node in all_nodes:
            new_hubs[node] = sum(auths[tgt] for tgt in out_adj.get(node, set()))
        hub_norm = math.sqrt(sum(v * v for v in new_hubs.values())) or 1
        hubs = {k: v / hub_norm for k, v in new_hubs.items()}

    return hubs, auths


# ===================== MAIN ANALYSIS =====================

def run_advanced_algorithms(graph_path: str) -> GraphAlgorithmResults:
    """Run all advanced graph algorithms."""
    graph = load_graph(graph_path)

    print("Running PageRank...")
    pr = pagerank(graph)

    print("Running spectral clustering...")
    sc = spectral_clustering(graph)

    print("Finding connected components...")
    cc = connected_components(graph)

    print("Computing diameter and eccentricities...")
    diameter, radius, eccentricities = graph_diameter(graph)

    print("Computing clustering coefficients...")
    cc_coeffs = clustering_coefficients(graph)
    avg_cc = sum(cc_coeffs.values()) / len(cc_coeffs) if cc_coeffs else 0

    print("Running HITS...")
    hubs, auths = hits(graph)

    return GraphAlgorithmResults(
        pagerank=pr,
        spectral_clusters=sc,
        connected_components=cc,
        num_components=len(cc),
        diameter=diameter,
        radius=radius,
        eccentricities=eccentricities,
        avg_clustering_coefficient=round(avg_cc, 4),
        clustering_coefficients=cc_coeffs,
        hubs={k: round(v, 4) for k, v in sorted(hubs.items(), key=lambda x: -x[1])[:10]},
        authorities={k: round(v, 4) for k, v in sorted(auths.items(), key=lambda x: -x[1])[:10]},
    )


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "output/identity_graph.json"
    results = run_advanced_algorithms(path)

    print(f"\n{'='*60}")
    print("ADVANCED GRAPH ALGORITHMS RESULTS")
    print(f"{'='*60}")
    print(f"\nPageRank Top 5:")
    for pr in results.pagerank[:5]:
        print(f"  {pr.node_id:<40} rank={pr.rank:.6f}")
    print(f"\nSpectral Clusters: {len(results.spectral_clusters)}")
    for sc in results.spectral_clusters:
        print(f"  Cluster {sc.cluster_id}: {len(sc.members)} members, density={sc.internal_density}")
    print(f"\nConnected Components: {results.num_components}")
    print(f"Diameter: {results.diameter}, Radius: {results.radius}")
    print(f"Avg Clustering Coefficient: {results.avg_clustering_coefficient}")
    print(f"\nTop Hubs (HITS):")
    for k, v in list(results.hubs.items())[:5]:
        print(f"  {k:<40} hub={v:.4f}")
    print(f"\nTop Authorities (HITS):")
    for k, v in list(results.authorities.items())[:5]:
        print(f"  {k:<40} auth={v:.4f}")
