"""
Signature Diff Tool
====================

Compare two identity signatures dimension by dimension.
Shows exactly where they agree and diverge.

Usage:
    from src.sigdiff import diff_signatures
    result = diff_signatures(sig_a, sig_b, "Captain", "Jenn")
"""

import json
from typing import Optional


def diff_signatures(sig_a: dict, sig_b: dict, name_a: str = "A", name_b: str = "B") -> dict:
    """Dimension-by-dimension comparison of two signatures."""
    enc_a = sig_a.get("encoders", {})
    enc_b = sig_b.get("encoders", {})

    all_encoders = set(enc_a.keys()) | set(enc_b.keys())

    dimensions = []
    agreements = 0
    disagreements = 0

    for enc in sorted(all_encoders):
        data_a = enc_a.get(enc, {})
        data_b = enc_b.get(enc, {})

        if isinstance(data_a, dict) and isinstance(data_b, dict):
            all_keys = set(data_a.keys()) | set(data_b.keys())
            for key in sorted(all_keys):
                val_a = data_a.get(key)
                val_b = data_b.get(key)

                if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                    diff = val_a - val_b
                    pct = abs(diff) / max(abs(val_a), abs(val_b), 1) * 100
                    match = abs(diff) < 0.01

                    if match:
                        agreements += 1
                    else:
                        disagreements += 1

                    dimensions.append({
                        "encoder": enc,
                        "field": key,
                        "value_a": val_a,
                        "value_b": val_b,
                        "diff": round(diff, 4),
                        "pct_diff": round(pct, 1),
                        "match": match,
                    })

    # Resonance comparison
    res_a = sig_a.get("resonance", {})
    res_b = sig_b.get("resonance", {})
    score_a = res_a.get("score", 0) if isinstance(res_a, dict) else 0
    score_b = res_b.get("score", 0) if isinstance(res_b, dict) else 0

    total = agreements + disagreements
    agreement_rate = agreements / total * 100 if total > 0 else 0

    return {
        "name_a": name_a,
        "name_b": name_b,
        "total_dimensions": total,
        "agreements": agreements,
        "disagreements": disagreements,
        "agreement_rate": round(agreement_rate, 1),
        "resonance_a": score_a,
        "resonance_b": score_b,
        "resonance_diff": round(score_a - score_b, 1),
        "dimensions": dimensions,
        "biggest_differences": sorted(
            [d for d in dimensions if not d["match"]],
            key=lambda x: abs(x["diff"]),
            reverse=True,
        )[:10],
        "exact_matches": [d for d in dimensions if d["match"]],
    }


def diff_summary(result: dict) -> str:
    """Human-readable summary of a diff result."""
    lines = [
        f"# Signature Diff: {result['name_a']} vs {result['name_b']}",
        "",
        f"Agreement rate: {result['agreement_rate']:.1f}% ({result['agreements']}/{result['total_dimensions']})",
        f"Resonance: {result['name_a']}={result['resonance_a']:.1f}, {result['name_b']}={result['resonance_b']:.1f} (Δ={result['resonance_diff']:.1f})",
        "",
        "## Top Differences",
    ]
    for d in result["biggest_differences"][:5]:
        lines.append(f"  {d['encoder']}.{d['field']}: {d['value_a']} → {d['value_b']} (Δ={d['diff']:.2f}, {d['pct_diff']:.0f}%)")

    lines.append("")
    lines.append(f"## Exact Matches: {len(result['exact_matches'])}")
    if result["exact_matches"][:5]:
        for d in result["exact_matches"][:5]:
            lines.append(f"  {d['encoder']}.{d['field']} = {d['value_a']}")

    return "\n".join(lines)
