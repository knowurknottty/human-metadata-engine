from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .constants import ALL_CENTERS, CHANNELS, MOTOR_CENTERS


@dataclass(frozen=True)
class TopologyResult:
    active_gates: frozenset[int]
    channels: tuple[tuple[int, int], ...]
    defined_centers: frozenset[str]
    edges: tuple[tuple[str, str], ...]
    components: tuple[frozenset[str], ...]
    motor_to_throat: bool
    motor_to_throat_paths: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Resolution:
    value: str
    reasons: tuple[str, ...]
    rejected: tuple[str, ...] = ()


def _components(centers: set[str], adjacency: dict[str, set[str]]) -> tuple[frozenset[str], ...]:
    remaining = set(centers)
    result: list[frozenset[str]] = []
    while remaining:
        start = min(remaining)
        queue = [start]
        seen: set[str] = set()
        while queue:
            current = queue.pop()
            if current in seen:
                continue
            seen.add(current)
            queue.extend(adjacency.get(current, set()) - seen)
        remaining -= seen
        result.append(frozenset(seen))
    return tuple(sorted(result, key=lambda component: (len(component), sorted(component))))


def _motor_paths(adjacency: dict[str, set[str]], defined: set[str]) -> tuple[tuple[str, ...], ...]:
    if "Throat" not in defined:
        return ()
    paths: list[tuple[str, ...]] = []
    queue: deque[tuple[str, tuple[str, ...]]] = deque([("Throat", ("Throat",))])
    visited_paths: set[tuple[str, ...]] = set()
    while queue:
        current, path = queue.popleft()
        if path in visited_paths:
            continue
        visited_paths.add(path)
        if current in MOTOR_CENTERS and current != "Throat":
            paths.append(path)
            continue
        for nxt in sorted(adjacency.get(current, ())):
            if nxt not in path:
                queue.append((nxt, path + (nxt,)))
    return tuple(paths)


def build_topology(gates: set[int] | frozenset[int]) -> TopologyResult:
    active = frozenset(int(gate) for gate in gates)
    channels: list[tuple[int, int]] = []
    defined: set[str] = set()
    edges_set: set[tuple[str, str]] = set()
    adjacency = {center: set() for center in ALL_CENTERS}

    for channel, centers in CHANNELS.items():
        first_gate, second_gate = channel
        if first_gate in active and second_gate in active:
            channels.append(channel)
            first_center, second_center = centers
            defined.update((first_center, second_center))
            edges_set.add(tuple(sorted((first_center, second_center))))
            adjacency[first_center].add(second_center)
            adjacency[second_center].add(first_center)

    paths = _motor_paths(adjacency, defined)
    return TopologyResult(
        active_gates=active,
        channels=tuple(sorted(channels)),
        defined_centers=frozenset(defined),
        edges=tuple(sorted(edges_set)),
        components=_components(defined, adjacency),
        motor_to_throat=bool(paths),
        motor_to_throat_paths=paths,
    )


def resolve_type(topology: TopologyResult) -> Resolution:
    defined = topology.defined_centers
    sacral = "Sacral" in defined
    if not defined:
        return Resolution("Reflector", ("no_defined_centers",))
    if sacral and topology.motor_to_throat:
        return Resolution("Manifesting Generator", ("Sacral defined", "motor_to_throat"))
    if sacral:
        return Resolution("Generator", ("Sacral defined", "no motor_to_throat path"))
    if topology.motor_to_throat:
        return Resolution("Manifestor", ("Sacral undefined", "motor_to_throat"))
    return Resolution("Projector", ("defined centers present", "Sacral undefined", "no motor_to_throat path"))


def _same_component(topology: TopologyResult, left: str, right: str) -> bool:
    return any(left in component and right in component for component in topology.components)


def resolve_authority(topology: TopologyResult) -> Resolution:
    defined = topology.defined_centers
    rejected: list[str] = []
    if "Solar Plexus" in defined:
        return Resolution("Emotional", ("Solar Plexus defined",), tuple(rejected))
    rejected.append("Emotional: Solar Plexus undefined")
    if "Sacral" in defined:
        return Resolution("Sacral", ("Sacral defined",), tuple(rejected))
    rejected.append("Sacral: Sacral undefined")
    if "Spleen" in defined:
        return Resolution("Splenic", ("Spleen defined",), tuple(rejected))
    rejected.append("Splenic: Spleen undefined")
    if "Heart" in defined and "Throat" in defined and _same_component(topology, "Heart", "Throat"):
        return Resolution("Ego Manifested", ("Heart and Throat connected",), tuple(rejected))
    rejected.append("Ego Manifested: Heart not connected to Throat")
    if "Heart" in defined and "G" in defined and _same_component(topology, "Heart", "G"):
        return Resolution("Ego Projected", ("Heart and G connected",), tuple(rejected))
    rejected.append("Ego Projected: Heart not connected to G")
    if "G" in defined and "Throat" in defined and _same_component(topology, "G", "Throat"):
        return Resolution("Self-Projected", ("G and Throat connected",), tuple(rejected))
    rejected.append("Self-Projected: G not connected to Throat")
    if defined:
        return Resolution("Mental/Environmental", ("defined centers with no inner authority",), tuple(rejected))
    return Resolution("Lunar", ("no defined centers",), tuple(rejected))


def resolve_definition(topology: TopologyResult) -> Resolution:
    count = len(topology.components)
    labels = {0: "None", 1: "Single", 2: "Split", 3: "Triple Split", 4: "Quadruple Split"}
    return Resolution(labels.get(count, f"{count}-way Split"), (f"{count} connected component(s)",))


__all__ = ["Resolution", "TopologyResult", "build_topology", "resolve_authority", "resolve_definition", "resolve_type"]
