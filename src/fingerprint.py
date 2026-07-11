"""
Identity Fingerprint Visualization
====================================
All geometry derived from SHA-256 digest bytes only.
Python runtime hash() is never used.

Public API (unchanged):
    generate_fingerprint_svg(sig, size, identity_name) -> str

New:
    build_public_projection(sig)           -> dict
    build_private_projection(sig, secret)  -> dict
    build_manifest(projection, mode)       -> dict
    render_sigil_svg(manifest, size)       -> str
    export_manual_html(profiles, outpath)  -> str
"""

import hashlib
import hmac
import html
import json
import math
import os

# ---------------------------------------------------------------------------
# Projection layer
# ---------------------------------------------------------------------------

_PUBLIC_EXCLUDED = frozenset({
    "computed_at",
    "birth", "lat", "lon", "location", "coordinates",
    "health", "neuro", "neurodata",
    "contacts", "relationships", "relationship",
    "raw_assessments", "assessments", "tokens", "private_notes", "notes",
})

_PUBLIC_EXCLUDED_SUBSTRINGS = (
    "birth", "lat", "lon", "location", "coord",
    "health", "neuro", "contact", "relation",
    "token", "secret", "private", "assess",
)


def _key_is_excluded(key: str) -> bool:
    lk = key.lower()
    if lk in _PUBLIC_EXCLUDED:
        return True
    return any(sub in lk for sub in _PUBLIC_EXCLUDED_SUBSTRINGS)


def build_public_projection(sig: dict) -> dict:
    """Redacted copy of sig safe for public artifacts.

    Excluded: birth data, coordinates, locations, health/neurodata,
    contacts, relationship data, raw assessments, tokens, private notes.
    """
    out = {}
    for k, v in sig.items():
        if _key_is_excluded(k):
            continue
        if isinstance(v, dict):
            sub = {sk: sv for sk, sv in v.items() if not _key_is_excluded(sk)}
            if sub:
                out[k] = sub
        else:
            out[k] = v
    return out


def build_private_projection(sig: dict, secret: bytes) -> dict:
    """Full sig bound to an HMAC-SHA-256 tag from secret."""
    canonical = _canonical_bytes(sig)
    tag = hmac.new(secret, canonical, hashlib.sha256).hexdigest()
    return {"_hmac_sha256": tag, "_projection": "private", **sig}


# ---------------------------------------------------------------------------
# Canonical serialisation -- the ONLY source of digest bytes
# ---------------------------------------------------------------------------

def _canonical_bytes(obj: dict) -> bytes:
    """Stable, cross-process canonical bytes. Python hash() never used."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, default=str
    ).encode("utf-8")


def _digest_hex(obj: dict) -> str:
    return hashlib.sha256(_canonical_bytes(obj)).hexdigest()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

_SCHEMA_VERSION = "1.0.0"
_RENDER_SPEC    = "sigil-v1"


def build_manifest(projection: dict, mode: str = "public") -> dict:
    """Bind schema, render spec, projection mode, digest, layers, epistemic."""
    return {
        "schema_version":  _SCHEMA_VERSION,
        "render_spec":     _RENDER_SPEC,
        "projection_mode": mode,
        "digest": _digest_hex(projection),
        "layers": [
            "cryptographic", "fingerprint", "name_topology",
            "evidence", "symbolic", "provenance",
        ],
        "epistemic": {
            "cryptographic": "Established",
            "fingerprint":   "Established",
            "name_topology": "Experimental",
            "evidence":      "Experimental",
            "symbolic":      "Speculative",
            "provenance":    "Established",
        },
    }


# ---------------------------------------------------------------------------
# SVG rendering -- all geometry from digest bytes
# ---------------------------------------------------------------------------

def _hue(b0: int, b1: int) -> int:
    return ((b0 << 8) | b1) % 360


def _unit(b: int) -> float:
    return b / 255.0


def render_sigil_svg(manifest: dict, size: int = 300,
                     identity_name: str = "") -> str:
    """Layered SVG sigil. All geometry from manifest digest bytes only."""
    raw  = bytes.fromhex(manifest["digest"])
    name = identity_name or "unknown"
    display_name = html.escape(str(name), quote=True)
    cx = cy = size / 2
    R  = size * 0.46

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'data-digest="{manifest["digest"]}" '
        f'data-schema="{manifest["schema_version"]}" '
        f'data-render="{manifest["render_spec"]}" '
        f'data-mode="{manifest["projection_mode"]}">',
        f'  <rect width="{size}" height="{size}" fill="#0a0a0a"/>',
    ]

    # ---- layer: cryptographic -- 32 tick marks, one per digest byte ----
    p.append('  <g id="layer-cryptographic" opacity="0.85">')
    for i, b in enumerate(raw):
        a      = (2 * math.pi * i) / 32
        tlen   = 4 + _unit(b) * 8
        hue    = _hue(b, raw[(i + 1) % 32])
        x1     = cx + R * math.cos(a)
        y1     = cy + R * math.sin(a)
        x2     = cx + (R - tlen) * math.cos(a)
        y2     = cy + (R - tlen) * math.sin(a)
        p.append(
            f'    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="hsl({hue},80%,65%)" stroke-width="1.2"/>'
        )
    p.append("  </g>")

    # ---- layer: fingerprint -- petal rosette ----
    p.append('  <g id="layer-fingerprint" opacity="0.75">')
    num_petals = max(3, min(12, (raw[0] % 10) + 3))
    for i in range(num_petals):
        a   = (2 * math.pi * i) / num_petals
        r   = R * 0.30 + _unit(raw[(i * 3 + 1) % 32]) * R * 0.45
        hue = _hue(raw[(i * 3 + 4) % 32], raw[(i * 3 + 5) % 32])
        x1  = cx + r * math.cos(a - 0.22)
        y1  = cy + r * math.sin(a - 0.22)
        x2  = cx + r * math.cos(a + 0.22)
        y2  = cy + r * math.sin(a + 0.22)
        tx  = cx + r * math.cos(a)
        ty  = cy + r * math.sin(a)
        p.append(
            f'    <path d="M{cx:.2f},{cy:.2f} Q{x1:.2f},{y1:.2f} {tx:.2f},{ty:.2f} '
            f'Q{x2:.2f},{y2:.2f} {cx:.2f},{cy:.2f}" '
            f'fill="hsl({hue},70%,60%)" opacity="0.6"/>'
        )
    p.append("  </g>")

    # ---- layer: name_topology -- harmonic polygon from SHA-256 of name ----
    p.append('  <g id="layer-name_topology" opacity="0.45">')
    nb     = hashlib.sha256(name.encode("utf-8")).digest()
    sides  = max(3, min(9, (nb[0] % 7) + 3))
    poly_r = R * 0.55
    pts    = []
    for i in range(sides):
        a   = (2 * math.pi * i) / sides - math.pi / 2
        r_i = poly_r + (_unit(nb[i % 32]) - 0.5) * R * 0.12
        pts.append(f"{cx + r_i * math.cos(a):.2f},{cy + r_i * math.sin(a):.2f}")
    hue_n = _hue(nb[1], nb[2])
    p.append(
        f'    <polygon points="{" ".join(pts)}" '
        f'fill="none" stroke="hsl({hue_n},60%,70%)" stroke-width="1.0"/>'
    )
    p.append("  </g>")

    # ---- layer: evidence -- 8 radial bars from bytes 16..23 ----
    p.append('  <g id="layer-evidence" opacity="0.55">')
    for i in range(8):
        a     = (2 * math.pi * i) / 8 - math.pi / 2
        w     = _unit(raw[16 + i])
        bar_r = R * 0.20 + w * R * 0.25
        hue_e = _hue(raw[(16 + i) % 32], raw[(17 + i) % 32])
        xt    = cx + bar_r * math.cos(a)
        yt    = cy + bar_r * math.sin(a)
        p.append(
            f'    <line x1="{cx:.2f}" y1="{cy:.2f}" x2="{xt:.2f}" y2="{yt:.2f}" '
            f'stroke="hsl({hue_e},65%,55%)" stroke-width="{1.5 + w * 2.5:.2f}"/>'
        )
    p.append("  </g>")

    # ---- layer: symbolic -- inner glyph ring from bytes 24..31 ----
    p.append('  <g id="layer-symbolic" opacity="0.60">')
    chars      = "*+ox^~=-><"
    glyph_r    = R * 0.18
    num_glyphs = max(3, (raw[24] % 6) + 3)
    for i in range(num_glyphs):
        a     = (2 * math.pi * i) / num_glyphs
        gx    = cx + glyph_r * math.cos(a)
        gy    = cy + glyph_r * math.sin(a)
        ch    = html.escape(chars[raw[(24 + i) % 32] % len(chars)])
        hue_s = _hue(raw[(24 + i) % 32], raw[(25 + i) % 32])
        p.append(
            f'    <text x="{gx:.2f}" y="{gy:.2f}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'font-size="9" fill="hsl({hue_s},70%,75%)">{ch}</text>'
        )
    p.append("  </g>")

    # ---- layer: provenance ----
    p.append('  <g id="layer-provenance">')
    p.append(
        f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="3" fill="#ffffff" opacity="0.9"/>'
    )
    p.append(
        f'  <text x="{cx:.2f}" y="{size - 10}" text-anchor="middle" '
        f'fill="#444444" font-size="7" font-family="monospace">'
        f'{display_name} | {manifest["render_spec"]} | {manifest["digest"][:8]}</text>'
    )
    p.append("  </g>")
    p.append("</svg>")
    return "\n".join(p)


# ---------------------------------------------------------------------------
# Public API -- preserved signature
# ---------------------------------------------------------------------------

def generate_fingerprint_svg(sig: dict, size: int = 200,
                              identity_name: str = "") -> str:
    """
    Generate an SVG fingerprint from sig.

    Signature unchanged from previous versions. Internally:
    1. Builds a public projection (stripping excluded fields).
    2. Derives all geometry from SHA-256 digest bytes only --
       Python runtime hash() is never used.
    """
    projection = build_public_projection(sig)
    manifest   = build_manifest(projection, mode="public")
    name       = identity_name or sig.get("id", "unknown")
    return render_sigil_svg(manifest, size=size, identity_name=name)


# ---------------------------------------------------------------------------
# HTML Manual Export
# ---------------------------------------------------------------------------

_HTML_STYLE = """
<style>
  body{background:#0d0d0d;color:#e0e0e0;font-family:monospace;
       max-width:960px;margin:auto;padding:2rem}
  h1{color:#c8a96e;border-bottom:1px solid #333;padding-bottom:.5rem}
  h2{color:#8ab4f8;margin-top:2rem}
  .pb{border:1px solid #2a2a2a;border-radius:6px;padding:1rem;margin-bottom:2rem}
  .sw{text-align:center;margin:.5rem 0}
  table{border-collapse:collapse;width:100%;font-size:.85rem}
  td,th{border:1px solid #2a2a2a;padding:.4rem .7rem}
  th{background:#1a1a1a;color:#8ab4f8}
  .dg{font-size:.75rem;color:#666;word-break:break-all}
  @media print{body{background:#fff;color:#000}h1,h2{color:#000}}
</style>
"""


def export_manual_html(profiles: list, outpath: str, size: int = 200) -> str:
    """
    Produce a self-contained, print-ready HTML manual with inline SVG.

    Excluded fields (birth, coordinates, health, etc.) are stripped
    before any SVG or manifest byte is computed. No PDF dependency required.
    """
    sections = []
    for sig in profiles:
        name       = html.escape(str(sig.get("id", "unknown")), quote=True)
        projection = build_public_projection(sig)
        manifest   = build_manifest(projection, mode="public")
        svg        = render_sigil_svg(manifest, size=size, identity_name=name)
        epi_rows   = "".join(
            f"<tr><td>{layer}</td><td>{lbl}</td></tr>"
            for layer, lbl in manifest["epistemic"].items()
        )
        sections.append(f"""
<div class="pb">
  <h2>{name}</h2>
  <div class="sw">{svg}</div>
  <table>
    <tr><th>Field</th><th>Value</th></tr>
    <tr><td>Schema</td><td>{manifest['schema_version']}</td></tr>
    <tr><td>Render spec</td><td>{manifest['render_spec']}</td></tr>
    <tr><td>Projection</td><td>{manifest['projection_mode']}</td></tr>
    <tr><td colspan="2" class="dg">SHA-256: {manifest['digest']}</td></tr>
  </table>
  <table style="margin-top:.5rem">
    <tr><th>Layer</th><th>Epistemic Confidence</th></tr>
    {epi_rows}
  </table>
</div>""")

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Human Metadata Engine -- Sigil Manual</title>
  {_HTML_STYLE}
</head>
<body>
  <h1>Human Metadata Engine -- Sigil Manual</h1>
  <p class="dg">
    Render spec: {_RENDER_SPEC} | Schema: {_SCHEMA_VERSION} |
    All geometry derived from SHA-256 digest bytes only.
  </p>
  {"".join(sections)}
</body>
</html>"""

    os.makedirs(os.path.dirname(os.path.abspath(outpath)), exist_ok=True)
    with open(outpath, "w", encoding="utf-8") as fh:
        fh.write(document)
    return os.path.abspath(outpath)
