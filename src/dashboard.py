"""
Batch Comparison Dashboard
===========================

Interactive HTML dashboard for comparing identities side by side.
Generates a self-contained HTML file with all data embedded.

Usage:
    from src.dashboard import generate_dashboard
    html = generate_dashboard("output/unified_signatures.json")
    with open("output/dashboard.html", "w") as f:
        f.write(html)
"""

import json
import os

from analytics import feature_vector


def _script_json(value) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("/", "\\u002f")
    )


def generate_dashboard(signatures_path: str, output_path: str = None) -> str:
    """Generate interactive comparison dashboard."""
    with open(signatures_path) as f:
        data = json.load(f)

    if isinstance(data, list):
        sigs = {s.get("id", s.get("identity", "")): s for s in data}
    else:
        sigs = data

    # Prepare data for JS
    identities = []
    for name, sig in sigs.items():
        encoders = sig.get("encoders", {})
        analytics = sig.get("analytics", {})

        pyth = encoders.get("pythagorean", {})
        ling = encoders.get("linguistic", {})
        binary = encoders.get("binary_prime", {})
        gem = encoders.get("gematria", {})
        iso = encoders.get("isopsephy", {})

        identities.append({
            "name": name,
            "expression": pyth.get("expression", pyth.get("life_path", 0)),
            "soul_urge": pyth.get("soul_urge", 0),
            "personality": pyth.get("personality", 0),
            "entropy": ling.get("entropy", ling.get("shannon_entropy", 0)),
            "syllables": ling.get("syllables", ling.get("syllable_count", 0)),
            "vowel_ratio": ling.get("vowel_ratio", 0),
            "polarity": binary.get("polarity_score", 0),
            "resonance": sig.get("resonance", {}).get(
                "score", analytics.get("composite_resonance", analytics.get("resonance_score", 0))
            ),
            "gematria": gem.get("absolute_value", gem.get("value", 0)),
            "isopsephy": iso.get("absolute_value", iso.get("value", 0)),
            "comparison_features": feature_vector(sig),
        })

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Identity Comparison Dashboard</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0a0a0a; color: #e0e0e0; font-family: 'SF Mono', monospace; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #4fc3f7; font-size: 18px; margin-bottom: 4px; }}
.subtitle {{ color: #666; font-size: 11px; margin-bottom: 20px; }}
.controls {{ display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }}
select, input {{ background: #1a1a1a; color: #fff; border: 1px solid #333; padding: 8px 12px; border-radius: 4px; font-family: inherit; font-size: 12px; }}
select:focus, input:focus {{ border-color: #4fc3f7; outline: none; }}
.comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
.card {{ background: #111; border: 1px solid #222; border-radius: 8px; padding: 16px; }}
.card h2 {{ color: #4fc3f7; font-size: 14px; margin-bottom: 12px; }}
.stat {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #1a1a1a; font-size: 11px; }}
.stat-label {{ color: #888; }}
.stat-value {{ color: #fff; font-weight: bold; }}
.bar-container {{ height: 8px; background: #1a1a1a; border-radius: 4px; overflow: hidden; margin-top: 4px; }}
.bar {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
.bar-{{color: #4fc3f7; }}
.bar-a {{ background: #4fc3f7; }}
.bar-b {{ background: #ff7043; }}
.similarity {{ text-align: center; padding: 20px; background: #111; border: 1px solid #222; border-radius: 8px; margin-bottom: 20px; }}
.similarity .score {{ font-size: 48px; color: #4fc3f7; }}
.similarity .label {{ color: #666; font-size: 12px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
th {{ background: #1a1a1a; color: #4fc3f7; padding: 8px; text-align: left; font-size: 11px; }}
td {{ padding: 8px; border-bottom: 1px solid #1a1a1a; font-size: 11px; }}
tr:hover {{ background: #111; }}
</style>
</head>
<body>
<div class="container">
  <h1>Identity Comparison Dashboard</h1>
  <p class="subtitle">{len(identities)} identities loaded · Human Metadata Engine v0.4.0</p>

  <div class="controls">
    <select id="selectA" onchange="compare()">
      {"".join(f'<option value="{i}">{identities[i]["name"]}</option>' for i in range(len(identities)))}
    </select>
    <span style="color:#666">vs</span>
    <select id="selectB" onchange="compare()">
      {"".join(f'<option value="{i}">{identities[i]["name"]}</option>' for i in range(len(identities)))}
    </select>
  </div>

  <div class="similarity" id="simBox">
    <div class="score" id="simScore">—</div>
    <div class="label">Feature Agreement (not person-level similarity)</div>
  </div>

  <div class="comparison" id="comp">
    <div class="card" id="cardA"></div>
    <div class="card" id="cardB"></div>
  </div>

  <h2 style="margin-top:24px; color:#4fc3f7; font-size:14px;">All Identities</h2>
  <table id="table"></table>
</div>

<script>
const data = {_script_json(identities)};
const CONTINUOUS_TOLERANCES = [0.18, 0.15, 0.20, 0.30, 0.20, 0.35];
const esc = (value) => String(value).replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));

function featureAgreement(a, b) {{
  const discrete = a.slice(0, 8).map((value, index) => value === b[index] ? 1 : 0);
  const continuous = a.slice(8).map((value, index) =>
    Math.max(0, 1 - Math.abs(value - b[index + 8]) / CONTINUOUS_TOLERANCES[index]));
  return [...discrete, ...continuous].reduce((sum, value) => sum + value, 0) / 14;
}}

function renderCard(el, d, colorClass) {{
  el.innerHTML = `
    <h2>${{esc(d.name)}}</h2>
    <div class="stat"><span class="stat-label">Expression</span><span class="stat-value">${{d.expression}}</span></div>
    <div class="stat"><span class="stat-label">Soul Urge</span><span class="stat-value">${{d.soul_urge}}</span></div>
    <div class="stat"><span class="stat-label">Personality</span><span class="stat-value">${{d.personality}}</span></div>
    <div class="stat"><span class="stat-label">Entropy</span><span class="stat-value">${{(d.entropy || 0).toFixed(2)}}</span></div>
    <div class="stat"><span class="stat-label">Syllables</span><span class="stat-value">${{d.syllables}}</span></div>
    <div class="stat"><span class="stat-label">Vowel Ratio</span><span class="stat-value">${{(d.vowel_ratio || 0).toFixed(2)}}</span></div>
    <div class="stat"><span class="stat-label">Polarity</span><span class="stat-value">${{(d.polarity || 0).toFixed(2)}}</span></div>
    <div class="stat"><span class="stat-label">Gematria</span><span class="stat-value">${{d.gematria}}</span></div>
    <div class="stat"><span class="stat-label">Isopsephy</span><span class="stat-value">${{d.isopsephy}}</span></div>
    <div class="stat"><span class="stat-label">Resonance</span><span class="stat-value">${{(d.resonance || 0).toFixed(1)}}/100</span></div>
    <div class="bar-container"><div class="bar ${{colorClass}}" style="width:${{d.resonance || 0}}%"></div></div>
  `;
}}

function compare() {{
  const a = data[document.getElementById('selectA').value];
  const b = data[document.getElementById('selectB').value];
  renderCard(document.getElementById('cardA'), a, 'bar-a');
  renderCard(document.getElementById('cardB'), b, 'bar-b');

  const agreement = featureAgreement(a.comparison_features, b.comparison_features);
  document.getElementById('simScore').textContent = (agreement * 100).toFixed(1) + '%';
}}

// Build table
let html = '<tr><th>Name</th><th>Expression</th><th>Soul</th><th>Personality</th><th>Entropy</th><th>Resonance</th></tr>';
data.forEach(d => {{
  html += `<tr><td>${{esc(d.name)}}</td><td>${{d.expression}}</td><td>${{d.soul_urge}}</td><td>${{d.personality}}</td><td>${{(d.entropy||0).toFixed(2)}}</td><td>${{(d.resonance||0).toFixed(1)}}</td></tr>`;
}});
document.getElementById('table').innerHTML = html;

compare();
</script>
</body>
</html>"""

    if output_path:
        with open(output_path, "w") as f:
            f.write(html)

    return html
