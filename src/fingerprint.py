"""
Identity Fingerprint Visualization
====================================

Generates a unique SVG visual fingerprint from an identity's hash.

Each identity gets a deterministic, reproducible visual signature
that encodes its multi-dimensional identity data as geometry.

Usage:
    from src.fingerprint import generate_fingerprint_svg
    svg = generate_fingerprint_svg(signature_dict)
"""

import hashlib
import math
from typing import Optional


def generate_fingerprint_svg(sig: dict, size: int = 200, identity_name: str = "") -> str:
    """Generate an SVG fingerprint from a signature dict."""
    name = identity_name or sig.get("id", "unknown")
    # Deterministic hash from the full signature
    sig_str = _serialize_sig(sig)
    h = hashlib.sha256(sig_str.encode()).hexdigest()

    # Extract geometric parameters from hash
    cx, cy = size / 2, size / 2
    rings = 6
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
        f'<rect width="{size}" height="{size}" fill="#0a0a0a"/>',
    ]

    # Background rings
    for i in range(rings):
        r = (i + 1) * (size / (2 * rings + 1))
        opacity = 0.1 + 0.05 * i
        svg_parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ffffff" '
            f'stroke-width="0.5" opacity="{opacity}"/>'
        )

    # Generate petals from hash bytes
    num_petals = max(3, min(12, int(h[0:2], 16) % 10 + 3))
    for i in range(num_petals):
        angle = (2 * math.pi * i) / num_petals
        petal_r = int(h[2 + i * 2:4 + i * 2] or 'ff', 16) / 255.0
        r = size * 0.15 + petal_r * size * 0.3
        x1 = cx + r * math.cos(angle - 0.2)
        y1 = cy + r * math.sin(angle - 0.2)
        x2 = cx + r * math.cos(angle + 0.2)
        y2 = cy + r * math.sin(angle + 0.2)

        # Color from hash (use modulo to stay within hash bounds)
        hue_idx = 20 + i * 4
        if hue_idx + 4 <= len(h):
            hue = int(h[hue_idx:hue_idx+4], 16) % 360
        else:
            hue = (int(h[hue_idx % len(h):(hue_idx + 4) % len(h)], 16) if hue_idx % len(h) + 4 <= len(h) else hash(name) + i * 40) % 360
        color = f"hsl({hue}, 70%, 60%)"

        svg_parts.append(
            f'<path d="M{cx},{cy} Q{x1},{y1} {cx + r * math.cos(angle)},{cy + r * math.sin(angle)} '
            f'Q{x2},{y2} {cx},{cy}" fill="{color}" opacity="0.6"/>'
        )

    # Center dot
    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#ffffff" opacity="0.8"/>')

    # Name label
    svg_parts.append(
        f'<text x="{cx}" y="{size - 8}" text-anchor="middle" '
        f'fill="#666666" font-size="8" font-family="monospace">{name}</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def _serialize_sig(sig: dict) -> str:
    """Deterministic serialization of signature dict."""
    parts = []
    for key in sorted(sig.keys()):
        val = sig[key]
        if isinstance(val, dict):
            for k2 in sorted(val.keys()):
                parts.append(f"{key}.{k2}={val[k2]}")
        else:
            parts.append(f"{key}={val}")
    return "|".join(parts)
