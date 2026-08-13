#!/usr/bin/env python3
"""Build an auditable public-figure catalog from Wikidata.

Operational definition of the corpus: a Wikidata item that is a human and
has an English Wikipedia biography. This is a reproducible inclusion rule,
not a claim that a finite seed list contains every famous person.

The importer retains Wikidata IDs and revisions, date precision, birth-place
coordinates when present, and an exclusion record for every seed that fails
validation. It does *not* send uncertain historic birth times to astrology or
Human Design; all imported records are currently ``core_only``.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = ROOT / "data" / "famous_people.seeds.json"
DEFAULT_OUTPUT = ROOT / "data" / "famous_people.catalog.json"
API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "HumanMetadataEngine/0.5 (https://github.com/knowurknottty/human-metadata-engine)"
HUMAN_QID = "Q5"


def api_get(params: dict) -> dict:
    query = urllib.parse.urlencode({**params, "format": "json"})
    request = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def claims(entity: dict, property_id: str) -> list[dict]:
    return entity.get("claims", {}).get(property_id, [])


def entity_id(statement: dict) -> str | None:
    value = statement.get("mainsnak", {}).get("datavalue", {}).get("value", {})
    return value.get("id") if isinstance(value, dict) else None


def entity_value(statement: dict):
    return statement.get("mainsnak", {}).get("datavalue", {}).get("value")


def label(entity: dict) -> str | None:
    # Some Wikidata records expose the canonical English display label under
    # the multilingual (``mul``) code even when ``languages=en`` was asked
    # for.  Prefer English, then that canonical label, before giving up.
    labels = entity.get("labels", {})
    for language in ("en", "mul"):
        value = labels.get(language, {}).get("value")
        if value:
            return value
    return next(
        (entry.get("value") for entry in labels.values() if entry.get("value")),
        None,
    )


def description(entity: dict) -> str:
    descriptions = entity.get("descriptions", {})
    for language in ("en", "mul"):
        value = descriptions.get(language, {}).get("value")
        if value:
            return value
    return ""


def resolve_seeds(seeds: list[dict]) -> tuple[list[tuple[dict, str]], list[dict]]:
    """Resolve English-Wikipedia titles in batches; QID overrides stay exact."""
    resolved = [(seed, seed["qid"]) for seed in seeds if seed.get("qid")]
    unresolved = [seed for seed in seeds if not seed.get("qid")]
    exclusions = []
    for start in range(0, len(unresolved), 50):
        chunk = unresolved[start:start + 50]
        payload = api_get({
            "action": "wbgetentities", "sites": "enwiki",
            "titles": "|".join(seed["query"] for seed in chunk),
            "props": "labels|sitelinks|info",
        })
        title_to_qid = {
            entity.get("sitelinks", {}).get("enwiki", {}).get("title", "").casefold(): qid
            for qid, entity in payload.get("entities", {}).items()
            if not qid.startswith("-")
        }
        for seed in chunk:
            qid = title_to_qid.get(seed["query"].casefold())
            if qid:
                resolved.append((seed, qid))
            else:
                exclusions.append({
                    "seed": seed,
                    "reason": "No exact English Wikipedia title mapping; add a Wikidata QID override.",
                })
        if start + 50 < len(unresolved):
            time.sleep(0.1)
    return resolved, exclusions


def fetch_entities(qids: list[str]) -> dict[str, dict]:
    entities: dict[str, dict] = {}
    for start in range(0, len(qids), 50):
        chunk = qids[start:start + 50]
        payload = api_get({
            "action": "wbgetentities", "ids": "|".join(chunk),
            "props": "labels|descriptions|claims|sitelinks|info",
        })
        entities.update(payload.get("entities", {}))
        if start + 50 < len(qids):
            time.sleep(0.1)
    return entities


def birth_fact(entity: dict) -> dict | None:
    statements = claims(entity, "P569")
    if not statements:
        return None
    value = entity_value(statements[0])
    if not isinstance(value, dict) or "time" not in value:
        return None
    return {
        "raw": value["time"],
        "precision": value.get("precision"),
        "calendar_model": value.get("calendarmodel"),
    }


def enwiki_url(entity: dict) -> str | None:
    title = entity.get("sitelinks", {}).get("enwiki", {}).get("title")
    if not title:
        return None
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


def make_record(entity: dict, place_entities: dict[str, dict]) -> dict:
    qid = entity["id"]
    person_label = label(entity)
    if not person_label:
        raise ValueError("No English label")
    if HUMAN_QID not in {entity_id(statement) for statement in claims(entity, "P31")}:
        raise ValueError("Wikidata item is not directly typed as human (Q5)")
    article_url = enwiki_url(entity)
    if not article_url:
        raise ValueError("No English Wikipedia biography")
    place_qid = next((entity_id(statement) for statement in claims(entity, "P19") if entity_id(statement)), None)
    place = place_entities.get(place_qid, {}) if place_qid else {}
    coordinate = next((entity_value(statement) for statement in claims(place, "P625")), None)
    coordinates = None
    if isinstance(coordinate, dict) and "latitude" in coordinate and "longitude" in coordinate:
        coordinates = {"lat": coordinate["latitude"], "lon": coordinate["longitude"]}
    return {
        "id": f"figure:wikidata:{qid.lower()}",
        "qid": qid,
        "text": person_label,
        "description": description(entity),
        "birth": birth_fact(entity),
        "birth_place": {
            "qid": place_qid,
            "label": label(place) if place else None,
            "coordinates": coordinates,
        },
        "calculation_status": "core_only",
        "calculation_note": "Birth time is not established by this catalog import; time-sensitive encoders are withheld.",
        "provenance": {
            "notability_rule": "Wikidata human with an English Wikipedia biography",
            "wikidata_url": f"https://www.wikidata.org/wiki/{qid}",
            "wikidata_revision": entity.get("lastrevid"),
            "enwiki_url": article_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    seeds = json.loads(args.seeds.read_text(encoding="utf-8"))
    resolved, exclusions = resolve_seeds(seeds["people"])
    entities = fetch_entities([qid for _, qid in resolved])
    place_qids = sorted({
        place_qid
        for entity in entities.values()
        for place_qid in [next((entity_id(statement) for statement in claims(entity, "P19") if entity_id(statement)), None)]
        if place_qid
    })
    places = fetch_entities(place_qids)
    records = []
    for seed, qid in resolved:
        try:
            records.append(make_record(entities[qid], places))
        except ValueError as exc:
            exclusions.append({"seed": seed, "qid": qid, "reason": str(exc)})
    records.sort(key=lambda record: (record["text"].casefold(), record["qid"]))
    catalog = {
        "schema_version": 1,
        "scope": seeds["scope"],
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "seed_count": len(seeds["people"]),
        "record_count": len(records),
        "records": records,
        "exclusions": exclusions,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} catalog records and {len(exclusions)} exclusions to {args.output}")
    return 0 if not exclusions else 2


if __name__ == "__main__":
    raise SystemExit(main())
