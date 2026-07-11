"""
Run All Inventions
===================

Master orchestrator that runs all 10 inventions in sequence
and generates all outputs.

Usage:
    python3 -m src.run_all
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from engine import IDENTITIES, compute_unified_signature
from analytics import (
    composite_resonance, identity_fingerprint,
    numerological_convergence, linguistic_harmony, polarity_balance,
    symbolic_depth, identity_similarity_matrix, cross_encoder_correlations,
    batch_report
)
from search import IdentitySearch
from narrative import generate_narrative
from fingerprint import generate_fingerprint_svg
from knowledge_miner import mine_bubbles
from prediction import predict_personality
from drift import track_drift
from graph_viz import generate_graph_html
from dashboard import generate_dashboard

OUTPUT_DIR = "output"


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  Human Metadata Engine — Full Invention Suite")
    print("  10 inventions, 1 orchestrator, 0 dependencies")
    print("=" * 60)

    # ── 1. Compute all unified signatures ──
    print("\n[1/10] Computing unified signatures...")
    sigs = {}
    for ident in IDENTITIES:
        name = ident.get("text", ident.get("name", ident.get("id", "")))
        sig = compute_unified_signature(ident)
        sigs[name] = sig

    # Custom JSON encoder for dataclass/namedtuple objects
    class SigEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: getattr(obj, k) for k in obj.__dataclass_fields__}
            if hasattr(obj, '_asdict'):
                return obj._asdict()
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return super().default(obj)

    with open(f"{OUTPUT_DIR}/unified_signatures.json", "w") as f:
        json.dump(sigs, f, indent=2, cls=SigEncoder)
    print(f"  → {len(sigs)} signatures computed")

    # ── 2. Build search index ──
    print("\n[2/10] Building search index...")
    search = IdentitySearch.from_signatures(f"{OUTPUT_DIR}/unified_signatures.json")
    print(f"  → Index built: {len(search.identities)} identities indexed")

    # Test search
    results = search.find_similar("Captain", top_n=3)
    print(f"  → 'Captain' top 3: {[r.identity for r in results]}")

    # ── 3. Generate narratives ──
    print("\n[3/10] Generating personality narratives...")
    narratives = {}
    for name, sig in sigs.items():
        narratives[name] = generate_narrative(sig, name)

    os.makedirs(f"{OUTPUT_DIR}/narratives", exist_ok=True)
    for name, story in narratives.items():
        safe = name.replace(" ", "_").replace("/", "_")
        with open(f"{OUTPUT_DIR}/narratives/{safe}.md", "w") as f:
            f.write(story)
    print(f"  → {len(narratives)} narratives generated")

    # ── 4. Generate fingerprints ──
    print("\n[4/10] Generating SVG fingerprints...")
    os.makedirs(f"{OUTPUT_DIR}/fingerprints", exist_ok=True)
    for name, sig in sigs.items():
        svg = generate_fingerprint_svg(sig, size=300, identity_name=name)
        safe = name.replace(" ", "_").replace("/", "_")
        with open(f"{OUTPUT_DIR}/fingerprints/{safe}.svg", "w") as f:
            f.write(svg)
    print(f"  → {len(sigs)} fingerprints generated")

    # ── 5. Mine knowledge bubbles ──
    print("\n[5/10] Mining knowledge bubbles...")
    bubbles = mine_bubbles(f"{OUTPUT_DIR}/unified_signatures.json")
    bubble_data = [
        {
            "topic": b.topic,
            "insight": b.insight,
            "confidence": b.confidence,
            "evidence": b.evidence,
            "category": b.category,
        }
        for b in bubbles
    ]
    with open(f"{OUTPUT_DIR}/knowledge_bubbles.json", "w") as f:
        json.dump(bubble_data, f, indent=2)
    print(f"  → {len(bubbles)} knowledge bubbles discovered")
    for b in bubbles[:5]:
        print(f"    • {b.topic}: {b.insight[:80]}...")

    # ── 6. Run ensemble predictions ──
    print("\n[6/10] Running ensemble predictions...")
    predictions = {}
    for name, sig in sigs.items():
        predictions[name] = predict_personality(sig)

    with open(f"{OUTPUT_DIR}/predictions.json", "w") as f:
        json.dump(predictions, f, indent=2)
    print(f"  → {len(predictions)} personality predictions generated")

    # Show a sample
    sample_name = list(predictions.keys())[0]
    sample = predictions[sample_name]
    print(f"    Sample ({sample_name}): MBTI={sample['mbti_guess']}, Openness={sample['big_five']['openness']}")

    # ── 7. Track temporal drift ──
    print("\n[7/10] Tracking identity drift...")
    drift_reports = {}
    # Test with Captain variants
    captain_variants = ["Captain", "testuser42", "The Captain"]
    drift = track_drift("Captain", captain_variants, lambda n: compute_unified_signature({"name": n, "id": n}))
    drift_reports["Captain"] = {
        "identity": drift.identity,
        "stages": [
            {"name": s.name_used, "resonance": s.resonance, "delta": s.delta_from_previous}
            for s in drift.stages
        ],
        "total_drift": drift.total_drift,
        "direction": drift.drift_direction,
        "stability": drift.stability_score,
        "analysis": drift.analysis,
    }
    with open(f"{OUTPUT_DIR}/drift_reports.json", "w") as f:
        json.dump(drift_reports, f, indent=2)
    print(f"  → Captain drift: stability={drift.stability_score}, direction={drift.drift_direction[:50]}")

    # ── 8. Generate graph visualization ──
    print("\n[8/10] Generating graph visualization...")
    graph_html = generate_graph_html(
        f"{OUTPUT_DIR}/identity_graph.json",
        f"{OUTPUT_DIR}/graph.html"
    )
    print(f"  → Interactive graph: {OUTPUT_DIR}/graph.html ({len(graph_html)} bytes)")

    # ── 9. Generate dashboard ──
    print("\n[9/10] Generating comparison dashboard...")
    dashboard_html = generate_dashboard(
        f"{OUTPUT_DIR}/unified_signatures.json",
        f"{OUTPUT_DIR}/dashboard.html"
    )
    print(f"  → Interactive dashboard: {OUTPUT_DIR}/dashboard.html ({len(dashboard_html)} bytes)")

    # ── 10. API server (ready to launch) ──
    print("\n[10/10] API server ready at src/api.py")
    print(f"  → Run with: python3 -m src.api")
    print(f"  → Endpoints: /encode, /compare, /search, /narrative, /fingerprint, /identities, /health")

    # ── Summary ──
    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print("  COMPLETE")
    print(f"  Time: {elapsed:.1f}s")
    print(f"  Signatures: {len(sigs)}")
    print(f"  Narratives: {len(narratives)}")
    print(f"  Fingerprints: {len(sigs)}")
    print(f"  Knowledge Bubbles: {len(bubbles)}")
    print(f"  Predictions: {len(predictions)}")
    print(f"  Drift Reports: {len(drift_reports)}")
    print(f"  Graph Nodes: {len(sigs)}")
    print(f"  Outputs: {OUTPUT_DIR}/")
    print("=" * 60)

    # List all output files
    for root, dirs, files in os.walk(OUTPUT_DIR):
        level = root.replace(OUTPUT_DIR, "").count(os.sep)
        indent = "  " * (level + 1)
        basename = os.path.basename(root)
        if root != OUTPUT_DIR:
            print(f"{indent}{basename}/")
        subindent = "  " * (level + 2)
        for f in sorted(files)[:5]:
            size = os.path.getsize(os.path.join(root, f))
            print(f"{subindent}{f} ({size:,} bytes)")
        if len(files) > 5:
            print(f"{subindent}... and {len(files) - 5} more")


if __name__ == "__main__":
    main()
