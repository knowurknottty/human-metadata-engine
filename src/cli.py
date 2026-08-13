import logging
"""
CLI Batch Tool
===============

Command-line interface for adding identities one at a time
and running analyses.

Usage:
    python3 -m src.cli add "Captain"
    python3 -m src.cli add "Jenn" --birth 1990-05-15
    python3 -m src.cli compare "Captain" "Jenn"
    python3 -m src.cli search "Captain"
    python3 -m src.cli narrative "Captain"
    python3 -m src.cli cluster
    python3 -m src.cli anomaly
    python3 -m src.cli export --format csv
    python3 -m src.cli stats
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def main():
    parser = argparse.ArgumentParser(description="Human Metadata Engine CLI")
    sub = parser.add_subparsers(dest="command")

    # add
    add_p = sub.add_parser("add", help="Add an identity")
    add_p.add_argument("name", help="Name to encode")
    add_p.add_argument("--birth", help="Birth date (YYYY-MM-DD)")
    add_p.add_argument("--birth-time", help="Birth time (HH:MM)")
    add_p.add_argument("--birth-place", help="Birth place")

    # compare
    comp_p = sub.add_parser("compare", help="Compare two identities")
    comp_p.add_argument("name_a")
    comp_p.add_argument("name_b")

    # search
    search_p = sub.add_parser("search", help="Find similar identities")
    search_p.add_argument("query")
    search_p.add_argument("--top", type=int, default=5)

    # narrative
    narr_p = sub.add_parser("narrative", help="Generate personality narrative")
    narr_p.add_argument("name")

    # cluster
    sub.add_parser("cluster", help="Cluster all identities")

    # anomaly
    sub.add_parser("anomaly", help="Detect anomalies")

    # export
    exp_p = sub.add_parser("export", help="Export data")
    exp_p.add_argument("--format", choices=["csv", "jsonl", "markdown"], default="csv")
    exp_p.add_argument("--output", default=None)

    # stats
    sub.add_parser("stats", help="Show database stats")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "add":
        cmd_add(args)
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "narrative":
        cmd_narrative(args)
    elif args.command == "cluster":
        cmd_cluster()
    elif args.command == "anomaly":
        cmd_anomaly()
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "stats":
        cmd_stats()


def cmd_add(args):
    from engine import compute_unified_signature
    from narrative import generate_narrative
    from fingerprint import generate_fingerprint_svg
    from persistence import IdentityDB

    ident = {"name": args.name, "text": args.name, "id": args.name}
    if args.birth:
        parts = args.birth.split("-")
        ident["birth"] = {
            "year": int(parts[0]),
            "month": int(parts[1]),
            "day": int(parts[2]),
        }
        if args.birth_time:
            tparts = args.birth_time.split(":")
            ident["birth"]["hour"] = int(tparts[0])
            ident["birth"]["minute"] = int(tparts[1])

    sig = compute_unified_signature(ident)

    # Store in DB
    db = IdentityDB()
    db.store_signature(args.name, sig)
    stats = db.stats()
    db.close()

    # Generate narrative
    narrative = generate_narrative(sig, args.name)

    # Generate fingerprint
    svg = generate_fingerprint_svg(sig, identity_name=args.name)
    os.makedirs("output/fingerprints", exist_ok=True)
    safe = args.name.replace(" ", "_")
    with open(f"output/fingerprints/{safe}.svg", "w") as f:
        f.write(svg)

    res = sig.get("resonance", {})
    score = res.get("score", 0) if isinstance(res, dict) else 0

    logging.info(f"Added: {args.name}")
    logging.info(f"  Resonance: {score:.1f}/100")
    logging.info(f"  Stored in DB ({stats['signatures']} total)")
    logging.info(f"  Narrative: output/narratives/{safe}.md")
    logging.info(f"  Fingerprint: output/fingerprints/{safe}.svg")


def cmd_compare(args):
    from engine import compute_unified_signature
    from sigdiff import diff_signatures, diff_summary

    sig_a = compute_unified_signature({"name": args.name_a, "text": args.name_a, "id": args.name_a})
    sig_b = compute_unified_signature({"name": args.name_b, "text": args.name_b, "id": args.name_b})

    result = diff_signatures(sig_a, sig_b, args.name_a, args.name_b)
    logging.info(diff_summary(result))


def cmd_search(args):
    from search import IdentitySearch

    search = IdentitySearch.from_signatures("output/unified_signatures.json")
    results = search.find_similar(args.query, top_n=args.top)

    logging.info(f"Top {args.top} feature-agreement matches for '{args.query}':")
    for r in results:
        logging.info(f"  #{r.rank} {r.identity} (agreement: {r.score:.4f})")


def cmd_narrative(args):
    from engine import compute_unified_signature
    from narrative import generate_narrative

    sig = compute_unified_signature({"name": args.name, "text": args.name, "id": args.name})
    logging.info(generate_narrative(sig, args.name))


def cmd_cluster():
    from clustering import cluster_identities
    result = cluster_identities("output/unified_signatures.json")

    logging.info(f"Clusters: {result['n_clusters']}")
    for cid, cluster in result["clusters"].items():
        logging.info(f"\n  Cluster {cid} ({cluster['size']} members, avg resonance {cluster['avg_resonance']}):")
        for m in cluster["members"]:
            logging.info(f"    - {m}")


def cmd_anomaly():
    from anomaly import detect_anomalies
    result = detect_anomalies("output/unified_signatures.json")

    logging.info(f"Anomalies: {result['anomalous_count']}/{result['total_identities']}")
    for name, data in result["anomalies"].items():
        logging.info(f"\n  {name} (max z={data['max_z_score']}, {data['anomaly_count']} features):")
        for feat, info in list(data["features"].items())[:3]:
            logging.info(f"    {feat}: {info['value']} (mean={info['mean']}, z={info['z_score']})")


def cmd_export(args):
    from export import export_csv, export_jsonl, export_markdown_report

    sig_path = "output/unified_signatures.json"
    fmt = args.format

    if fmt == "csv":
        out = args.output or "output/identities.csv"
        export_csv(sig_path, out)
    elif fmt == "jsonl":
        out = args.output or "output/identities.jsonl"
        export_jsonl(sig_path, out)
    elif fmt == "markdown":
        out = args.output or "output/identities_report.md"
        export_markdown_report(sig_path, out)

    logging.info(f"Exported to {out}")


def cmd_stats():
    from persistence import IdentityDB

    db = IdentityDB()
    stats = db.stats()
    names = db.get_all_names()
    db.close()

    logging.info("Database Stats:")
    for k, v in stats.items():
        logging.info(f"  {k}: {v}")
    if names:
        logging.info(f"\nStored identities:")
        for n in names:
            logging.info(f"  - {n}")


if __name__ == "__main__":
    main()
