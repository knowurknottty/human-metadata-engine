"""Optional remote Mythic prose realization over a privacy-minimized fact packet.

The deterministic synthesis remains the source of truth. This module never sends
raw identity, birth inputs, aliases, observations, or user-supplied psychology to
the remote model. The remote model is a presentation layer over already-derived
symbolic outputs and may be disabled without affecting analysis.
"""
from __future__ import annotations

import json
import os
import re
from urllib import error as urlerror
from urllib import request as urlrequest

MODEL = "qwen/qwen3.8-flash"
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
SCHEMA_VERSION = "mythic-remote-v1"


class RemoteMythicUnavailable(RuntimeError):
    """The optional remote narration service is not configured or reachable."""


class RemoteMythicInvalid(RuntimeError):
    """The model returned output that failed the local presentation contract."""


def _encoder_data(encoders: dict, name: str) -> dict:
    value = encoders.get(name) or {}
    if isinstance(value, dict) and isinstance(value.get("data"), dict):
        return value["data"]
    return value if isinstance(value, dict) else {}


def _clean_plan_motifs(synthesis: dict) -> list[dict]:
    evidence_items = (synthesis.get("evidence") or {}).get("evidence_items") or []
    evidence_system = {
        item.get("evidence_id"): item.get("system")
        for item in evidence_items if isinstance(item, dict)
    }
    motifs = []
    for motif in (synthesis.get("plan") or {}).get("dominant_motifs") or []:
        non_user = [
            evidence_id for evidence_id in motif.get("evidence_ids", [])
            if evidence_system.get(evidence_id) != "user_context"
        ]
        groups = [g for g in motif.get("independence_groups", []) if g != "user_context"]
        if len(non_user) < 2 or not groups:
            continue
        motifs.append({
            "label": motif.get("label"),
            "confidence": motif.get("confidence"),
            "independent_group_count": len(set(groups)),
        })
        if len(motifs) == 6:
            break
    return motifs


def build_symbolic_packet(result: dict) -> dict:
    """Return only derived symbolic facts suitable for optional remote narration."""
    signature = result.get("signature") or {}
    encoders = signature.get("encoders") or {}
    astrology = _encoder_data(encoders, "astrology")
    human_design = _encoder_data(encoders, "human_design")
    pythagorean = _encoder_data(encoders, "pythagorean")
    chaldean = _encoder_data(encoders, "chaldean")
    ordinal = _encoder_data(encoders, "ordinal")
    gematria = _encoder_data(encoders, "gematria")
    isopsephy = _encoder_data(encoders, "isopsephy")
    tarot = _encoder_data(encoders, "tarot")
    chinese = _encoder_data(encoders, "chinese")
    tree = _encoder_data(encoders, "kabbalah_tree_of_life")

    planets = []
    for p in astrology.get("planets") or []:
        if not isinstance(p, dict):
            continue
        planets.append({
            "planet": p.get("planet"), "sign": p.get("sign"), "house": p.get("house"),
            "retrograde": bool(p.get("retrograde")),
        })
    aspects = []
    for aspect in astrology.get("aspects") or []:
        if not isinstance(aspect, dict):
            continue
        pair = list(aspect.get("planets") or [])
        if len(pair) != 2:
            continue
        aspects.append({
            "planets": pair, "type": aspect.get("type"),
            "orb": aspect.get("orb"), "exact": bool(aspect.get("exact")),
        })
    channels = []
    for channel in human_design.get("channels") or []:
        if not isinstance(channel, dict):
            continue
        channels.append({"gates": list(channel.get("gates") or []), "centers": list(channel.get("centers") or [])})

    packet = {
        "epistemic_boundary": (
            "The calculations below are deterministic or rule-derived within named symbolic conventions. "
            "Their personal meanings are interpretive and are not scientific personality measurements, diagnosis, prediction, or destiny."
        ),
        "astrology": {
            "sun": astrology.get("sun_sign"), "moon": astrology.get("moon_sign"),
            "ascendant": astrology.get("ascendant"), "midheaven": astrology.get("midheaven"),
            "dominant_element": astrology.get("dominant_element"),
            "dominant_modality": astrology.get("dominant_modality"),
            "house_system": astrology.get("house_system"),
            "planets": planets, "aspects": aspects,
        },
        "human_design": {
            "status": human_design.get("status"), "type": human_design.get("type"),
            "strategy": human_design.get("strategy"), "authority": human_design.get("authority"),
            "definition": human_design.get("definition"), "profile": human_design.get("profile"),
            "active_gates": list(human_design.get("gates") or []), "channels": channels,
            "defined_centers": [c.get("name") for c in (human_design.get("centers") or []) if isinstance(c, dict) and c.get("defined")],
        },
        "name_symbols": {
            "pythagorean_expression": pythagorean.get("expression"),
            "pythagorean_soul_urge": pythagorean.get("soul_urge"),
            "pythagorean_personality": pythagorean.get("personality"),
            "chaldean_name_number": chaldean.get("name_number"),
            "ordinal_reduced": ordinal.get("ordinal_reduced"),
            "gematria_reduced": gematria.get("absolute_reduced"),
            "isopsephy_reduced": isopsephy.get("reduced"),
            "tarot_major_arcana": tarot.get("major_arcana"),
            "tarot_major_arcana_index": tarot.get("major_arcana_index"),
            "wu_xing_element": chinese.get("wu_xing_element"),
            "tree_of_life_dominant_sephirah": tree.get("dominant_sephirah"),
        },
        "cross_system_theme_hints": _clean_plan_motifs(result.get("synthesis") or {}),
        "independence_warning": (
            "Name-derived systems share one source string and must not be described as independent confirmations. "
            "Astrology and Human Design share birth-derived inputs and likewise are not independent empirical observations."
        ),
    }
    # Drop null leaves to keep the remote packet compact without changing its shape.
    def prune(value):
        if isinstance(value, dict):
            return {k: prune(v) for k, v in value.items() if v is not None and v != []}
        if isinstance(value, list):
            return [prune(v) for v in value]
        return value
    return prune(packet)


def build_messages(packet: dict) -> list[dict]:
    system = """You are the Mythic narrator for Human Metadata Atlas. Write for an audience that enjoys astrology, tarot, Human Design, archetypal language, and beautiful long-form readings, while preserving strict epistemic boundaries.

Rules:
- Use ONLY facts present in the supplied DERIVED SYMBOLIC FACTS. Do not invent placements, houses, aspects, gates, channels, centers, numbers, archetypes, biographical facts, motives, diagnoses, events, relationships, futures, or abilities.
- Calculated geometry and rule-derived labels may be stated as returned/calculated. Their personal meaning must remain symbolic, interpretive, invitational, or metaphorical.
- Never state symbolic interpretation as a biographical fact. Prefer phrases such as “symbolically this can suggest,” “traditional interpretation associates,” or “one way to read this is” instead of asserting what the person is, feels, fears, needs, or has experienced.
- Never claim scientific validation, proof, diagnosis, prediction, destiny, supernatural certainty, or that several name systems independently confirm one another.
- Do not mention the person's name, age, birthplace, birth date/time, MBTI, Enneagram, Big Five, medical information, or any fact not in the packet.
- Do not repeat a disclaimer in every paragraph. Establish the boundary elegantly near the opening and preserve it through wording.
- Write an actual story, not a database dump and not a horoscope list. Synthesize relationships among the returned facts. Prefer memorable images, tensions, paradoxes, and thematic arcs.
- Explain tight aspects by their actual returned orb when useful. Distinguish harmonious geometry from friction without calling either good or bad.
- Treat contradictions as contextual tensions rather than forcing a flattering resolution.
- When discussing numerology or related name systems, explicitly acknowledge shared-input dependence once, then move on.
- Human Design is provisional/rule-derived where the packet says so.
- Avoid therapy-speak, canned affirmations, excessive rhetorical questions, and generic mystical filler.
- Tone: intelligent, intimate, vivid, slightly strange, grounded, elegant. The astronomy/tarot girlies should enjoy reading it; a skeptical engineer should still be able to audit every factual statement.

Output Markdown only. Aim for 900-1,300 words with 6-9 meaningful section headings. Open with a compelling title and narrative hook. End with a concise integrative image, not a prediction."""
    user = "DERIVED SYMBOLIC FACTS\n" + json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def request_openrouter(messages: list[dict], *, api_key: str, endpoint: str = DEFAULT_ENDPOINT, timeout: float = 28.0) -> str:
    if not api_key:
        raise RemoteMythicUnavailable("OPENROUTER_API_KEY is not configured on the HME backend.")
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.58,
        "top_p": 0.9,
        "max_tokens": 2600,
        "reasoning": {"effort": "none"},
        "provider": {"sort": "throughput"},
    }
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    req = urlrequest.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "HTTP-Referer": "https://inversionlabs-hmd.netlify.app",
            "X-Title": "Human Metadata Atlas",
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            raw = response.read(2_000_000)
    except (urlerror.HTTPError, urlerror.URLError, TimeoutError) as exc:
        status = getattr(exc, "code", None)
        suffix = f" (HTTP {status})" if status else ""
        raise RemoteMythicUnavailable(f"OpenRouter Mythic inference failed{suffix}.") from exc
    try:
        data = json.loads(raw)
        choice = data["choices"][0]
        if choice.get("finish_reason") == "length":
            raise RemoteMythicInvalid("OpenRouter returned a truncated Mythic completion.")
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RemoteMythicInvalid("OpenRouter returned an invalid Mythic response envelope.") from exc
    if isinstance(content, list):
        content = "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
    if not isinstance(content, str):
        raise RemoteMythicInvalid("OpenRouter returned non-text Mythic content.")
    content = content.strip()
    if not content:
        raise RemoteMythicInvalid("OpenRouter returned empty Mythic content.")
    return content


def _story_fact_errors(story: str, packet: dict) -> list[str]:
    """Catch high-value unsupported symbolic proper nouns before user display."""
    errors: list[str] = []
    zodiac = {"Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"}
    allowed_signs = {v for k, v in packet.get("astrology", {}).items() if k in {"sun","moon","ascendant","midheaven"} and isinstance(v, str)}
    allowed_signs.update(p.get("sign") for p in packet.get("astrology", {}).get("planets", []) if isinstance(p, dict))
    mentioned_signs = {sign for sign in zodiac if re.search(rf"\b{re.escape(sign)}\b", story)}
    unsupported = sorted(mentioned_signs - allowed_signs)
    if unsupported:
        errors.append("unsupported zodiac signs: " + ", ".join(unsupported))

    active_gates = set(packet.get("human_design", {}).get("active_gates", []))
    mentioned_gates = {int(n) for n in re.findall(r"\bGate\s+(\d{1,2})\b", story, flags=re.I)}
    bad_gates = sorted(n for n in mentioned_gates if n not in active_gates)
    if bad_gates:
        errors.append("unsupported Human Design gates: " + ", ".join(map(str, bad_gates)))

    returned_type = packet.get("human_design", {}).get("type")
    for hd_type in ("Manifestor", "Projector", "Reflector", "Manifesting Generator", "Generator"):
        if hd_type != returned_type and re.search(rf"\b{re.escape(hd_type)}\b", story, flags=re.I):
            errors.append(f"unsupported Human Design type: {hd_type}")

    planet_names = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto")
    aspect_aliases = {
        "conjunct": "Conjunction", "conjunction": "Conjunction",
        "square": "Square", "squares": "Square",
        "trine": "Trine", "trines": "Trine",
        "sextile": "Sextile", "sextiles": "Sextile",
        "opposition": "Opposition", "opposes": "Opposition", "opposite": "Opposition",
    }
    allowed_aspects = {
        (frozenset(a.get("planets", [])), str(a.get("type")))
        for a in packet.get("astrology", {}).get("aspects", [])
        if isinstance(a, dict) and len(a.get("planets", [])) == 2 and a.get("type")
    }
    planets_re = "|".join(planet_names)
    aspects_re = "|".join(sorted(aspect_aliases, key=len, reverse=True))
    patterns = (
        rf"\b({planets_re})\b\s+(?:is\s+)?({aspects_re})\s+\b({planets_re})\b",
        rf"\b({planets_re})\b\s*[-–—]\s*({planets_re})\b\s+({aspects_re})\b",
    )
    for index, pattern in enumerate(patterns):
        for match in re.finditer(pattern, story, flags=re.I):
            if index == 0:
                first, raw_aspect, second = match.groups()
            else:
                first, second, raw_aspect = match.groups()
            canonical_planets = frozenset(next(p for p in planet_names if p.casefold() == x.casefold()) for x in (first, second))
            canonical_aspect = aspect_aliases[raw_aspect.casefold()]
            if (canonical_planets, canonical_aspect) not in allowed_aspects:
                pair = "–".join(sorted(canonical_planets))
                errors.append(f"unsupported astrology aspect: {pair} {canonical_aspect}")
    return sorted(set(errors))



def _story_style_errors(story: str) -> list[str]:
    """Reject unqualified personality assertions while allowing direct calculation statements."""
    patterns = (
        r"\byou are\b",
        r"\byou have\b",
        r"\byou need\b",
        r"\byou fear\b",
        r"\byou feel\b",
        r"\bthis person\b",
        r"\bthe person (?:is|has|feels|fears|needs)\b",
        r"\bthis is (?:not )?a person who\b",
        r"\bthe result is a person who\b",
        r"\byour challenge is\b",
    )
    matches = sorted({m.group(0) for pattern in patterns for m in re.finditer(pattern, story, flags=re.I)})
    return ["unqualified symbolic identity claim: " + match for match in matches]

def generate_remote_mythic(result: dict) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RemoteMythicUnavailable("OPENROUTER_API_KEY is not configured on the HME backend.")
    packet = build_symbolic_packet(result)
    messages = build_messages(packet)
    story = request_openrouter(messages, api_key=api_key)
    if len(story.split()) < 250 or len(story) > 80_000:
        raise RemoteMythicInvalid("OpenRouter returned a Mythic story outside the accepted length bounds.")
    errors = _story_fact_errors(story, packet) + _story_style_errors(story)
    if errors:
        repair = messages + [
            {"role": "assistant", "content": story},
            {"role": "user", "content": "Revise the story. Preserve its voice, but correct every factual or epistemic-style issue listed here: " + "; ".join(errors) + ". Calculated chart facts may be stated directly; symbolic meanings must remain clearly interpretive rather than claims about the person. Output the complete corrected Markdown story only."},
        ]
        story = request_openrouter(repair, api_key=api_key)
        errors = _story_fact_errors(story, packet) + _story_style_errors(story)
        if errors:
            raise RemoteMythicInvalid("Remote Mythic narration failed local fact validation: " + "; ".join(errors))
    return {
        "schema_version": SCHEMA_VERSION,
        "story": story,
        "provider": "OpenRouter",
        "model": MODEL,
        "ai_used": True,
        "source": "derived_symbolic_facts_only",
        "privacy": {
            "sent": "derived symbolic calculation outputs",
            "not_sent": ["name", "aliases", "raw birth date/time/location/coordinates", "raw psychology", "observations"],
        },
        "epistemic_boundary": packet["epistemic_boundary"],
    }
