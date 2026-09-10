/* Human Metadata Atlas — deterministic visualization layer.
 *
 * This file renders structured API output only. It does not calculate symbolic
 * results, infer missing relationships, or mutate the analysis response.
 */

(function () {
"use strict";

const esc = (value) => String(value ?? "").replace(/[&<>\"]/g, character => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
}[character]));

const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
const SIGN_GLYPHS = ["♈︎", "♉︎", "♊︎", "♋︎", "♌︎", "♍︎", "♎︎", "♏︎", "♐︎", "♑︎", "♒︎", "♓︎"];
const PLANET_GLYPHS = {Sun:"☉", Moon:"☽", Mercury:"☿", Venus:"♀", Mars:"♂", Jupiter:"♃", Saturn:"♄", Uranus:"♅", Neptune:"♆", Pluto:"♇", "North Node":"☊", "South Node":"☋", Earth:"⊕"};
const SYSTEM_CATALOG = [
  ["astrology", "Astrology", "astronomical"],
  ["human_design", "Human Design", "astronomical"],
  ["kabbalah_tree_of_life", "Tree of Life", "correspondence"],
  ["pythagorean", "Pythagorean", "numeric"],
  ["chaldean", "Chaldean", "numeric"],
  ["gematria", "Gematria", "numeric"],
  ["isopsephy", "Isopsephy", "numeric"],
  ["tarot", "Tarot", "correspondence"],
  ["chinese", "I Ching / Wu Xing", "correspondence"],
  ["elder_futhark", "Runes", "language"],
  ["ogham", "Ogham", "language"],
  ["sacred_geometry", "Sacred Geometry", "geometry"],
];

// Mirrors src/encoders/kabbalah.py PATHS_22. These are reference marks, not
// calculated relationships in an individual response.
const TREE_PATHS_22 = [
  ["A",1,2], ["B",1,6], ["G",1,3], ["D",2,3], ["H",2,6], ["V",2,4],
  ["Z",3,6], ["Ch",4,5], ["T",4,6], ["I",4,7], ["K",5,8], ["L",5,6],
  ["M",6,7], ["N",6,8], ["S",6,9], ["O",7,8], ["P",7,9], ["Ts",7,10],
  ["Q",8,9], ["R",8,10], ["Sh",9,10], ["Th",9,10],
];

function polar(cx, cy, radius, degrees) {
  const radians = (degrees - 90) * Math.PI / 180;
  return [cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)];
}

function populatedCount(value) {
  if (!value || typeof value !== "object") return 0;
  const body = value.data && typeof value.data === "object" ? value.data : value;
  return Object.values(body).filter(item => item !== null && item !== undefined && item !== "" && item !== false).length;
}

function encoderProvenance(encoder, fallback) {
  const provenance = encoder?.provenance || {};
  return {
    source: (provenance.source_ids || []).join(", ") || fallback || "Engine response",
    method: provenance.convention || encoder?.calculation_engine || encoder?.calculation_standard || "Versioned engine calculation",
    confidence: encoder?.confidence || encoder?.status || "See report metadata",
    interpretation: encoder?.interpretation_level || encoder?.epistemic_class || "See information-type label",
  };
}

function selectionButton({id, label, linkKeys = [], className = "", body = "", title = ""}) {
  const links = [id, ...linkKeys].join(" ");
  return `<button type="button" class="atlas-select ${className}" data-atlas-select="${esc(id)}" data-link-keys="${esc(links)}" aria-label="${esc(label)}"${title ? ` title="${esc(title)}"` : ""}>${body}</button>`;
}

function astrologyLongitude(planet) {
  const sign = SIGNS.indexOf(planet?.sign);
  return sign < 0 ? null : sign * 30 + Number(planet.degree || 0);
}

function astrologyWheel(astrology, register, activationsByPlanet) {
  if (!astrology) return unavailablePanel("astrology", "Astrology wheel", "Birth details were not supplied, so no astronomical chart was calculated.");
  const size = 520, center = size / 2;
  const planets = (astrology.planets || []).map(planet => ({...planet, longitude: astrologyLongitude(planet)})).filter(planet => planet.longitude !== null);
  const planetByName = Object.fromEntries(planets.map(planet => [planet.planet, planet]));
  const parts = [
    `<circle class="astro-boundary" cx="${center}" cy="${center}" r="226"/>`,
    `<circle class="astro-ring" cx="${center}" cy="${center}" r="188"/>`,
    `<circle class="astro-ring astro-ring--inner" cx="${center}" cy="${center}" r="132"/>`,
  ];

  SIGNS.forEach((sign, index) => {
    const [x1, y1] = polar(center, center, 132, index * 30);
    const [x2, y2] = polar(center, center, 226, index * 30);
    const [tx, ty] = polar(center, center, 207, index * 30 + 15);
    parts.push(`<line class="astro-sector" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`);
    parts.push(`<text class="astro-sign" x="${tx.toFixed(1)}" y="${ty.toFixed(1)}">${SIGN_GLYPHS[index]}</text>`);
  });

  (astrology.house_cusps || []).forEach((longitude, index) => {
    const [x1, y1] = polar(center, center, 78, Number(longitude));
    const [x2, y2] = polar(center, center, 132, Number(longitude));
    const id = `house:${index + 1}`;
    register(id, {
      title: `House ${index + 1}`,
      category: "Calculated house cusp",
      summary: `Cusp at ${Number(longitude).toFixed(2)}° ecliptic longitude.`,
      source: astrology.calculation_engine || "Configured ephemeris",
      method: `${astrology.house_system || "Configured"} house system`,
      inputs: "Exact birth moment and resolved coordinates",
      confidence: astrology.confidence || "Computed",
      interpretation: "Astronomical geometry; house meaning is traditional",
      limitations: "House placement is time-sensitive and depends on the configured house convention.",
      reportTarget: "birth-chart", links: planets.filter(planet => planet.house === index + 1).map(planet => `planet:${planet.planet}`),
    });
    parts.push(`<line class="astro-house" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" data-atlas-select="${id}" data-link-keys="${id} system:astrology" tabindex="0" role="button" aria-label="House ${index + 1} cusp at ${Number(longitude).toFixed(2)} degrees"/>`);
    const [tx, ty] = polar(center, center, 111, Number(longitude) + 8);
    parts.push(`<text class="astro-house-label" x="${tx.toFixed(1)}" y="${ty.toFixed(1)}">${index + 1}</text>`);
  });

  (astrology.aspects || []).forEach((aspect, index) => {
    const first = planetByName[aspect.planets?.[0]], second = planetByName[aspect.planets?.[1]];
    if (!first || !second) return;
    const [x1, y1] = polar(center, center, 150, first.longitude);
    const [x2, y2] = polar(center, center, 150, second.longitude);
    const id = `aspect:${index}`;
    const links = [`planet:${first.planet}`, `planet:${second.planet}`];
    const dataLinks = [...links, "system:astrology"];
    register(id, {
      title: `${first.planet} ${aspect.type} ${second.planet}`,
      category: "Astronomical relationship",
      summary: `${Number(aspect.orb || 0).toFixed(2)}° orb${aspect.exact ? ", marked exact by the engine" : ""}.`,
      source: astrology.calculation_engine || "Configured ephemeris",
      method: `${aspect.type} aspect returned by the astronomy encoder`,
      confidence: astrology.confidence || "Computed",
      interpretation: "Astronomical calculation; symbolic meaning is traditional",
      limitations: "An aspect is a geometric relationship between calculated longitudes. It is not evidence of a trait or outcome.",
      reportTarget: "birth-chart", links,
    });
    parts.push(`<line class="astro-aspect astro-aspect--${esc(String(aspect.type || "aspect").toLowerCase())}" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" data-atlas-select="${id}" data-link-keys="${[id, ...dataLinks].join(" ")}" tabindex="0" role="button" aria-label="${esc(first.planet)} ${esc(aspect.type)} ${esc(second.planet)}"/>`);
  });

  planets.forEach((planet, index) => {
    const radius = 164 + (index % 2) * 18;
    const [x, y] = polar(center, center, radius, planet.longitude);
    const id = `planet:${planet.planet}`;
    const activations = activationsByPlanet[planet.planet] || [];
    const aspectLinks = (astrology.aspects || []).map((aspect, aspectIndex) => aspect.planets?.includes(planet.planet) ? `aspect:${aspectIndex}` : null).filter(Boolean);
    const links = [...activations.map(item => `gate:${item.gate}`), ...aspectLinks, ...(planet.house ? [`house:${planet.house}`] : []), "relation:astrology", ...(activations.length ? ["relation:human_design"] : [])];
    const dataLinks = ["system:astrology", ...links];
    register(id, {
      title: planet.planet,
      category: "Calculated planetary position",
      summary: `${planet.sign} ${Number(planet.degree).toFixed(2)}°${planet.house ? ` · house ${planet.house}` : ""}${planet.retrograde ? " · retrograde" : ""}.`,
      source: astrology.calculation_engine || "Configured ephemeris",
      method: "Geocentric ecliptic longitude mapped to sign, degree, and configured house system",
      inputs: "Birth date, resolved UTC moment, coordinates, and house convention when exact time is available",
      confidence: astrology.confidence || "Computed",
      interpretation: "Astronomical calculation",
      limitations: activations.length ? `${activations.length} Human Design activation records name this planet; those links use the engine response directly.` : "No Human Design activation record in this response names this planet.",
      reportTarget: "birth-chart", links,
    });
    parts.push(`<g class="astro-planet atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc([id, ...dataLinks].join(" "))}" tabindex="0" role="button" aria-label="${esc(planet.planet)} in ${esc(planet.sign)} at ${Number(planet.degree).toFixed(2)} degrees"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="15"/><text x="${x.toFixed(1)}" y="${(y + .5).toFixed(1)}">${PLANET_GLYPHS[planet.planet] || planet.planet.slice(0, 1)}</text></g>`);
  });

  register("system:astrology", {
    title: "Astrology",
    category: "Astronomical subsystem",
    summary: `${planets.length} planetary positions and ${(astrology.aspects || []).length} configured aspects are present in this response.`,
    source: astrology.calculation_engine || "Configured ephemeris",
    method: `${astrology.house_system || "Configured"} houses; historical timezone reconstruction is performed server-side`,
    inputs: "Validated birth data",
    confidence: astrology.confidence || "Computed",
    interpretation: "Astronomical calculation followed by traditional symbolic interpretation",
    limitations: "The chart does not diagnose, predict, or validate symbolic meaning.",
    reportTarget: "birth-chart", links: planets.map(planet => `planet:${planet.planet}`),
  });

  return panel("astrology", "Astrology wheel", "Calculated longitude, houses, and aspects", `<svg class="astrology-wheel" viewBox="0 0 ${size} ${size}" role="group" aria-labelledby="astrology-wheel-title astrology-wheel-desc"><title id="astrology-wheel-title">Calculated astrology wheel</title><desc id="astrology-wheel-desc">Twelve zodiac sectors with ${planets.length} selectable planets and ${(astrology.aspects || []).length} selectable aspects. Use Tab to move between chart objects.</desc>${parts.join("")}</svg>`, "system:astrology");
}

function humanDesignBodygraph(humanDesign, register) {
  if (!humanDesign) return unavailablePanel("human-design", "Human Design bodygraph", "An exact birth time is required for this calculated surface.");
  const positions = {
    Head:[160,24], Ajna:[160,94], Throat:[160,174], "G/Identity":[160,258], "Heart/Ego":[247,259], Spleen:[69,337], Sacral:[160,348], "Solar Plexus":[254,337], Root:[160,443],
  };
  const centers = humanDesign.centers || [];
  const centerName = value => ({G:"G/Identity", Heart:"Heart/Ego", "Heart/Will":"Heart/Ego", Splenic:"Spleen"}[value] || value);
  const parts = [];
  (humanDesign.channels || []).forEach((channel, index) => {
    const left = positions[centerName(channel.centers?.[0])], right = positions[centerName(channel.centers?.[1])];
    if (!left || !right) return;
    const id = `channel:${channel.gates.join("-")}`;
    const links = [...channel.gates.map(gate => `gate:${gate}`), ...channel.centers.map(center => `center:${centerName(center)}`)];
    const dataLinks = ["system:human_design", ...links];
    register(id, {
      title: channel.name,
      category: "Active Human Design channel",
      summary: `${channel.centers.join(" ↔ ")} · gates ${channel.gates.join("–")}.`,
      source: humanDesign.calculation_engine || humanDesign.calculation_standard,
      method: "Channel returned by the Human Design topology engine",
      confidence: humanDesign.confidence || humanDesign.status,
      interpretation: humanDesign.epistemic_class || "Traditional symbolic system",
      limitations: humanDesign.confidence_note || "This is not a psychological or medical measurement.",
      reportTarget: "human-design", links,
    });
    parts.push(`<line class="bodygraph-channel" x1="${left[0]}" y1="${left[1]}" x2="${right[0]}" y2="${right[1]}" data-atlas-select="${esc(id)}" data-link-keys="${esc([id, ...dataLinks].join(" "))}" tabindex="0" role="button" aria-label="${esc(channel.name)} channel"/>`);
  });
  centers.forEach(center => {
    const name = centerName(center.core_name || center.name);
    const point = positions[name];
    if (!point) return;
    const id = `center:${name}`;
    const links = (humanDesign.channels || []).filter(channel => channel.centers.map(centerName).includes(name)).map(channel => `channel:${channel.gates.join("-")}`);
    const dataLinks = ["system:human_design", ...links];
    register(id, {
      title: name,
      category: `${center.defined ? "Defined" : "Undefined"} Human Design center`,
      summary: `The engine marked this center ${center.defined ? "defined" : "undefined"} for this chart.`,
      source: humanDesign.calculation_engine || humanDesign.calculation_standard,
      method: "Center definition resolved from completed active channels",
      confidence: humanDesign.confidence || humanDesign.status,
      interpretation: humanDesign.epistemic_class || "Traditional symbolic system",
      limitations: "Center labels are symbolic classifications, not clinical findings.",
      reportTarget: "human-design", links,
    });
    parts.push(`<g class="bodygraph-center atlas-select ${center.defined ? "is-defined" : "is-open"}" data-atlas-select="${esc(id)}" data-link-keys="${esc([id, ...dataLinks].join(" "))}" tabindex="0" role="button" aria-label="${esc(name)}, ${center.defined ? "defined" : "undefined"}"><rect x="${point[0] - 33}" y="${point[1] - 22}" width="66" height="44" rx="3"/><text x="${point[0]}" y="${point[1] + 4}">${esc(name.replace("G/Identity", "Identity").replace("Solar Plexus", "Solar").replace("Heart/Ego", "Heart"))}</text></g>`);
  });

  const activations = [...(humanDesign.personality_gates || []).map(item => ({...item, side:"personality"})), ...(humanDesign.design_gates || []).map(item => ({...item, side:"design"}))];
  const byGate = activations.reduce((output, activation) => {
    (output[activation.gate] ||= []).push(activation);
    return output;
  }, {});
  const activeGates = new Set((humanDesign.gates || []).map(Number));
  const gateGrid = Array.from({length:64}, (_, index) => {
    const gate = index + 1, active = activeGates.has(gate), records = byGate[gate] || [];
    const id = `gate:${gate}`;
    const planets = [...new Set(records.map(record => record.planet))];
    const links = [...planets.map(planet => `planet:${planet}`), ...(humanDesign.channels || []).filter(channel => channel.gates.includes(gate)).map(channel => `channel:${channel.gates.join("-")}`)];
    const dataLinks = ["system:human_design", ...links];
    register(id, {
      title: `Gate ${gate}`,
      category: active ? "Active Human Design gate" : "Inactive Human Design gate",
      summary: active ? `${records.map(record => `${record.side} ${record.planet} line ${record.line}`).join("; ") || "Returned in the active gate set"}.` : "This gate is present in the 64-gate activation index but is not active in this response.",
      source: humanDesign.calculation_engine || humanDesign.calculation_standard,
      method: active ? "Planetary longitude mapped to the Human Design mandala" : "Numbered activation index; no active calculation attached",
      confidence: humanDesign.confidence || humanDesign.status,
      interpretation: humanDesign.epistemic_class || "Traditional symbolic system",
      limitations: active ? "Activation is a deterministic symbolic mapping, not an observed personal trait." : "Inactive status carries no negative meaning.",
      reportTarget: "human-design", links,
    });
    return selectionButton({id, label:`Gate ${gate}, ${active ? "active" : "inactive"}`, linkKeys:dataLinks, className:`gate-chip ${active ? "is-active" : ""}`, body:String(gate), title:records.map(record => `${record.planet} · ${record.side} · line ${record.line}`).join("; ")});
  }).join("");

  register("system:human_design", {
    title: "Human Design",
    category: "Calculated symbolic subsystem",
    summary: `${humanDesign.type} · ${humanDesign.strategy} · ${humanDesign.authority} authority · profile ${(humanDesign.profile || []).join("/")}.`,
    source: humanDesign.calculation_engine || humanDesign.calculation_standard,
    method: humanDesign.calculation_standard || "Versioned Human Design calculation",
    inputs: "Exact birth moment and design-date astronomical positions",
    confidence: humanDesign.confidence || humanDesign.status,
    interpretation: humanDesign.epistemic_class || "Traditional symbolic system",
    limitations: humanDesign.confidence_note || "This classification is not a scientific personality measurement.",
    reportTarget: "human-design", links: Array.from(activeGates, gate => `gate:${gate}`),
  });

  const body = `<div class="bodygraph-layout"><svg class="bodygraph" viewBox="0 0 320 480" role="group" aria-labelledby="bodygraph-title bodygraph-desc"><title id="bodygraph-title">Calculated Human Design center and channel diagram</title><desc id="bodygraph-desc">Nine selectable centers and ${(humanDesign.channels || []).length} active selectable channels. A separate 64-gate activation index follows; gates are not spatially placed on channel endpoints.</desc>${parts.join("")}</svg><div class="bodygraph-summary" aria-label="Human Design summary"><span>${esc(humanDesign.type)}</span><span>${esc(humanDesign.authority)} authority</span><span>Profile ${esc((humanDesign.profile || []).join("/"))}</span><span>${activeGates.size} active gates</span></div></div><h3 class="gate-index-title">64-gate activation index</h3><div class="gate-grid" aria-label="64-gate Human Design activation index">${gateGrid}</div><p class="research-only visual-footnote"><strong>Spatial limitation:</strong> v1.0 lists all gates in numeric order and draws only returned complete channels between centers. It does not place gates at canonical channel endpoints. See the v1.1 topology decision record.</p>`;
  return panel("human-design", "Human Design bodygraph", "Centers, active channels, and a 64-gate activation index", body, "system:human_design");
}

function treeOfLife(tree, register) {
  if (!tree?.data) return unavailablePanel("tree-of-life", "Tree of Life", "No Tree-of-Life mapping is present in this response.");
  const data = tree.data;
  const nodes = [
    ["Kether",160,28], ["Chokmah",248,88], ["Binah",72,88], ["Chesed",248,176], ["Geburah",72,176],
    ["Tiphareth",160,236], ["Netzach",248,310], ["Hod",72,310], ["Yesod",160,374], ["Malkuth",160,456],
  ];
  const parts = TREE_PATHS_22.map(([letter, first, second]) => `<line class="tree-path" data-reference-path="${esc(letter)}" x1="${nodes[first - 1][1]}" y1="${nodes[first - 1][2]}" x2="${nodes[second - 1][1]}" y2="${nodes[second - 1][2]}" aria-hidden="true"><title>Configured path ${esc(letter)}: ${esc(nodes[first - 1][0])} to ${esc(nodes[second - 1][0])}</title></line>`);
  nodes.forEach(([name,x,y], index) => {
    const active = String(data.dominant_sephirah).toLowerCase() === name.toLowerCase();
    const id = `sephirah:${name}`;
    const links = [active ? `numerology:value:${data.reduced_value}` : ""].filter(Boolean);
    const dataLinks = ["system:kabbalah_tree_of_life", ...links];
    register(id, {
      title: name,
      category: active ? "Calculated dominant Sephirah" : "Tree-of-Life reference position",
      summary: active ? `The calculated reduced value ${data.reduced_value} maps to ${name} under the configured convention.` : `${name} is shown to preserve the reference topology; this response does not mark it active.`,
      ...encoderProvenance(tree),
      inputs: active ? `Total ${data.total_value}; reduced value ${data.reduced_value}` : "Reference topology only",
      limitations: active ? "This is a traditional correspondence, not an empirical classification." : "An unhighlighted Sephirah does not encode an absence or deficit.",
      reportTarget: "name-calculations", links,
    });
    parts.push(`<g class="tree-node atlas-select ${active ? "is-active" : ""}" data-atlas-select="${esc(id)}" data-link-keys="${esc([id, ...dataLinks].join(" "))}" tabindex="0" role="button" aria-label="${esc(name)}${active ? ", calculated dominant Sephirah" : ", reference position"}"><circle cx="${x}" cy="${y}" r="28"/><text x="${x}" y="${y + 4}">${esc(name)}</text><text class="tree-index" x="${x}" y="${y + 40}">${index + 1}</text></g>`);
  });
  register("system:kabbalah_tree_of_life", {
    title: "Tree of Life",
    category: "Calculated symbolic correspondence",
    summary: `Total ${data.total_value} reduces to ${data.reduced_value}, mapped to ${data.dominant_sephirah}.`,
    ...encoderProvenance(tree),
    inputs: "Normalized name under the configured Kabbalah convention",
    limitations: "The 22 paths reproduce the configured ten-sephirot-and-22-paths-v1 reference map. Only the highlighted Sephirah represents a calculated active mapping.",
    reportTarget: "name-calculations", links:[`sephirah:${data.dominant_sephirah}`, `numerology:value:${data.reduced_value}`],
  });
  const body = `<div class="tree-layout"><svg class="tree-of-life" viewBox="0 0 320 490" role="group" aria-labelledby="tree-title tree-desc"><title id="tree-title">Tree of Life mapping</title><desc id="tree-desc">Ten keyboard-selectable Sephiroth and 22 configured reference paths. ${esc(data.dominant_sephirah)} is highlighted as the calculated mapping.</desc>${parts.join("")}</svg><dl class="tree-metrics"><div><dt>Total</dt><dd>${esc(data.total_value)}</dd></div><div><dt>Reduction</dt><dd>${esc(data.reduced_value)}</dd></div><div><dt>Tree depth</dt><dd>${esc(data.tree_depth)}</dd></div><div><dt>Unique paths</dt><dd>${esc(data.unique_paths)}</dd></div></dl></div>`;
  return panel("tree-of-life", "Tree of Life", "Calculated mapping within a reference topology", body, "system:kabbalah_tree_of_life");
}

function numerologyMatrix(encoders, register) {
  const rows = [
    {key:"pythagorean", label:"Pythagorean", input:encoders.pythagorean?.total, method:"Digital reduction", result:encoders.pythagorean?.master_preserved || encoders.pythagorean?.expression},
    {key:"chaldean", label:"Chaldean", input:encoders.chaldean?.compound_number, method:"Compound reduction", result:encoders.chaldean?.name_number},
    {key:"ordinal", label:"Ordinal", input:encoders.ordinal?.ordinal_total, method:"A1Z26 reduction", result:encoders.ordinal?.ordinal_reduced},
    {key:"gematria", label:"Gematria", input:encoders.gematria?.absolute_total, method:"Absolute reduction", result:encoders.gematria?.absolute_reduced},
    {key:"isopsephy", label:"Isopsephy", input:encoders.isopsephy?.total, method:"Greek correspondence reduction", result:encoders.isopsephy?.reduced},
  ].filter(row => row.result !== undefined && row.result !== null);
  const results = rows.reduce((group, row) => ((group[row.result] ||= []).push(row.key), group), {});
  const body = rows.map(row => {
    const id = `numerology:${row.key}`;
    const valueId = `numerology:value:${row.result}`;
    const peers = results[row.result].filter(key => key !== row.key).map(key => `numerology:${key}`);
    const links = [`system:${row.key}`, valueId, ...peers];
    register(id, {
      title: row.label,
      category: "Mathematical calculation",
      summary: `${row.input ?? "Configured input"} → ${row.result} using ${row.method.toLowerCase()}.`,
      source: "Versioned name encoder",
      method: row.method,
      inputs: "Normalized primary name",
      confidence: "Deterministic arithmetic",
      interpretation: "The arithmetic is calculated; assigned meaning is traditional",
      limitations: peers.length ? `${peers.length} other configured system${peers.length === 1 ? "" : "s"} produced the same reduced value. This is agreement, not validation.` : "No other displayed system produced the same reduced value.",
      reportTarget: "name-calculations", links,
    });
    if (!register.has(valueId)) register(valueId, {
      title:`Reduced value ${row.result}`, category:"Cross-system numeric value", summary:`Used by ${results[row.result].map(key => rows.find(item => item.key === key)?.label).join(", ")}.`, source:"Displayed numerology encoders", method:"Exact equality of returned reduced values", inputs:"Calculated encoder results", confidence:"Deterministic comparison", interpretation:"Cross-system relationship", limitations:"Shared values do not establish scientific validity or personal significance.", reportTarget:"name-calculations", links:results[row.result].map(key => `numerology:${key}`),
    });
    return selectionButton({id, label:`${row.label}: ${row.input} reduces to ${row.result}`, linkKeys:links, className:"numerology-row", body:`<span class="numerology-name">${esc(row.label)}</span><span class="numerology-input">${esc(row.input ?? "—")}</span><span class="numerology-operation" aria-hidden="true">→</span><span class="numerology-result">${esc(row.result)}</span><small>${esc(row.method)}</small>`});
  }).join("");
  rows.forEach(row => register(`system:${row.key}`, register.get(`numerology:${row.key}`)));
  return panel("numerology", "Numerology matrix", "Inputs, reductions, results, and exact agreement", `<div class="numerology-matrix" role="list">${body}</div><p class="visual-footnote">Matching result highlights represent exact equality in this response. They are not accuracy or confidence scores.</p>`, rows[0] ? `numerology:${rows[0].key}` : "");
}

function identityFingerprint(signature, register) {
  const fingerprint = signature.fingerprint || {};
  const id = "system:fingerprint";
  const links = (fingerprint.spokes || []).map(spoke => `system:${spoke.encoder}`);
  register(id, {
    title: "Identity fingerprint",
    category: "Deterministic identity visualization",
    summary: `${fingerprint.symmetry}-fold geometry with ${(fingerprint.spokes || []).length} normalized encoder spokes and a ${String(fingerprint.ring_pattern || "").length}-segment binary ring.`,
    source: "signature-v2 identity_fingerprint specification",
    method: "SHA-256 over sorted digit-level outputs, binary pattern, and normalized text; Pythagorean expression controls 3–9 fold symmetry; each spoke uses an encoder-specific declared scale",
    inputs: (fingerprint.spokes || []).map(spoke => `${spoke.encoder}=${spoke.value}`).join(", "),
    confidence: "Deterministic visual hash",
    interpretation: "Identity visualization; not authentication",
    limitations: "It must not be treated as biometric uniqueness, proof of identity, or a security credential.",
    reportTarget: "overview", links,
  });
  const spokes = (fingerprint.spokes || []).map(spoke => `<li><button type="button" data-atlas-select="system:${esc(spoke.encoder)}" data-link-keys="system:${esc(spoke.encoder)} ${id}"><span>${esc(spoke.encoder.replaceAll("_", " "))}</span><strong>${Number(spoke.value).toFixed(4)}</strong></button></li>`).join("");
  const body = `<div class="fingerprint-atlas"><button type="button" class="fingerprint-stage atlas-select" data-atlas-select="${id}" data-link-keys="${esc([id, ...links].join(" "))}" aria-label="Inspect deterministic identity fingerprint">${window.HMEFingerprintSVG(signature.fingerprint, 360)}</button><div><dl class="fingerprint-params"><div><dt>Hash</dt><dd><code>${esc(fingerprint.hash)}</code></dd></div><div><dt>Symmetry</dt><dd>${esc(fingerprint.symmetry)}-fold</dd></div><div><dt>Ring</dt><dd><code>${esc(fingerprint.ring_pattern)}</code></dd></div></dl><h3>Normalized spokes</h3><ul class="fingerprint-spokes">${spokes}</ul></div></div><details class="research-only algorithm-note"><summary>Algorithm and parameters</summary><p>The engine hashes the normalized name, configured digit-level outputs, and vowel/consonant binary string with SHA-256. Symmetry is the Pythagorean expression constrained to 3–9. Spoke magnitudes are clipped to 0–1 after division by encoder-specific declared scales; hue is fixed by encoder. The ring directly reproduces the returned binary pattern.</p></details>`;
  return panel("fingerprint", "Identity fingerprint", "Deterministic visual hash, explicitly non-biometric", body, id);
}

function crossSystemGraph(encoders, psychology, register) {
  const available = SYSTEM_CATALOG.filter(([key]) => {
    const value = encoders[key];
    if (!value) return false;
    if (key === "human_design") return value.available !== false && Boolean(value.type);
    return value.status !== "unavailable";
  });
  if (psychology) available.push(["user_context", "User Context", "reported"]);
  const bridge = encoders.esoteric_bridge?.data?.links || {};
  const size = 620, center = size / 2, radius = 222;
  const coords = {};
  available.forEach(([key], index) => { coords[key] = polar(center, center, radius, index * (360 / available.length)); });
  const lines = [];
  available.forEach(([key]) => {
    const [x,y] = coords[key];
    lines.push(`<line class="system-edge" x1="${center}" y1="${center}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" data-link-keys="system:${esc(key)} system:identity"/>`);
  });
  const bridgeKeys = {astrology:"astrology", kabbalah:"kabbalah_tree_of_life", numerology:"pythagorean", tarot:"tarot"};
  const explicit = Object.keys(bridge).map(key => bridgeKeys[key]).filter(key => coords[key]);
  const nodes = available.map(([key,label,category]) => {
    const encoder = key === "user_context" ? psychology : encoders[key];
    const participation = Math.max(1, populatedCount(encoder));
    const nodeRadius = Math.min(31, 17 + participation * 1.2);
    const [x,y] = coords[key];
    if (!register.has(`system:${key}`)) register(`system:${key}`, {
      title:label, category:`${category} system`, summary:`${participation} populated top-level result fields participate in this visualization.`, ...encoderProvenance(encoder, key === "user_context" ? "Supplied by user" : "Engine response"), inputs:key === "user_context" ? "Optional submitted context" : "Normalized analysis request", limitations:"Node size reflects populated returned fields, not importance, accuracy, or personal strength.", reportTarget:key === "user_context" ? "personal-context-report" : "name-calculations", links:["system:identity"],
    });
    return `<g class="system-node atlas-select system-node--${category}" data-atlas-select="system:${esc(key)}" data-link-keys="system:${esc(key)} system:identity relation:${esc(key)}" tabindex="0" role="button" aria-label="${esc(label)}, ${participation} populated returned fields"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${nodeRadius.toFixed(1)}"/><text x="${x.toFixed(1)}" y="${(y + nodeRadius + 18).toFixed(1)}">${esc(label)}</text><text class="node-count" x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}">${participation}</text></g>`;
  }).join("");
  register("system:identity", {
    title:"Calculated identity", category:"Analysis root", summary:`${available.length} available systems participate in this atlas.`, source:"analysis-v1 response", method:"Presence and populated-field inventory only", inputs:"Validated request", confidence:"Deterministic response inventory", interpretation:"Navigation structure", limitations:"Central placement does not imply a composite truth or scientific identity model.", reportTarget:"overview", links:available.map(([key]) => `system:${key}`),
  });
  register("system:esoteric_bridge", {
    title:"Explicit correspondence record", category:"Configured cross-system mapping", summary:Object.entries(bridge).map(([key,value]) => `${key}: ${value.mapping || value.source || "configured link"}`).join("; ") || "No explicit bridge data returned.", ...encoderProvenance(encoders.esoteric_bridge), inputs:"Returned bridge data", limitations:"The record names independent convention results; it does not assert pairwise relationships or empirical validation between traditions.", reportTarget:"cross-system", links:explicit.map(key => `system:${key}`),
  });
  const bridgeRecord = explicit.length ? selectionButton({id:"system:esoteric_bridge", label:`Inspect configured correspondence record for ${explicit.length} systems`, linkKeys:explicit.map(key => `system:${key}`), className:"bridge-record", body:`Configured correspondence record: ${explicit.length} named systems`}) : "";
  const body = `<svg class="system-graph" viewBox="0 0 ${size} ${size}" role="group" aria-labelledby="system-graph-title system-graph-desc"><title id="system-graph-title">Cross-system participation graph</title><desc id="system-graph-desc">${available.length} selectable computed systems orbit the analysis root. Node size reflects populated returned fields. Lines connect each available system only to the analysis root; they do not assert relationships between systems.</desc>${lines.join("")}<g class="system-node system-node--identity atlas-select" data-atlas-select="system:identity" data-link-keys="system:identity" tabindex="0" role="button" aria-label="Calculated identity root"><circle cx="${center}" cy="${center}" r="48"/><text x="${center}" y="${center - 3}">IDENTITY</text><text class="node-count" x="${center}" y="${center + 17}">${available.length} systems</text></g>${nodes}</svg><div class="graph-legend"><span><i class="legend-line"></i> Returned system participates in this analysis</span><span>Node number = populated fields</span></div>${bridgeRecord}`;
  return panel("constellation", "Identity constellation", "The signature view of computed participation and documented bridges", body, "system:identity", true);
}

function panel(id, title, subtitle, body, selection, featured = false) {
  return `<article id="atlas-${id}" class="atlas-panel${featured ? " atlas-panel--featured" : ""}" data-atlas-panel="${esc(id)}"><header><div><p class="panel-index">${esc(id.replaceAll("-", " "))}</p><h2>${esc(title)}</h2><p>${esc(subtitle)}</p></div><div class="panel-controls">${selection ? `<button type="button" class="panel-inspect" data-atlas-select="${esc(selection)}">Inspect method</button>` : ""}<button type="button" class="panel-expand" data-atlas-expand="${esc(id)}" aria-pressed="false" aria-label="View ${esc(title)} fullscreen">Fullscreen</button></div></header><div class="atlas-canvas">${body}</div></article>`;
}

function unavailablePanel(id, title, explanation) {
  return panel(id, title, "Not calculated for this request", `<div class="atlas-unavailable"><span aria-hidden="true">∅</span><p>${esc(explanation)}</p></div>`, "");
}

function livingPattern(result) {
  const synthesis = result.synthesis;
  if (!synthesis?.plan || !synthesis?.narratives) {
    return `<section class="living-pattern living-pattern--unavailable" aria-labelledby="living-pattern-title"><p class="eyebrow">Human Metadata Narrative</p><h2 id="living-pattern-title">The Living Pattern</h2><p>Narrative synthesis is unavailable for this analysis.</p></section>`;
  }
  const evidenceById = new Map((synthesis.evidence?.evidence_items || []).map(item => [item.evidence_id, item]));
  const plan = synthesis.plan;
  const central = plan.central_archetype;
  const sentenceHTML = sentence => {
    const items = sentence.evidence_ids.map(id => evidenceById.get(id)).filter(Boolean);
    const targets = [...new Set(items.flatMap(item => item.atlas_targets || []))];
    const contradiction = sentence.contradiction ? `<span class="contradiction-mark">Contradiction retained</span>` : "";
    return `<button type="button" class="narrative-sentence" data-narrative-sentence="${esc(sentence.sentence_id)}" data-evidence-ids="${esc(sentence.evidence_ids.join(" "))}" data-atlas-targets="${esc(targets.join(" "))}" aria-label="${esc(sentence.text)} Confidence ${esc(sentence.strength)}. ${items.length} evidence references.${sentence.contradiction ? " Contradiction retained." : ""}"><span>${esc(sentence.text)}</span><small>${esc(sentence.strength)} confidence · ${items.length} evidence ${contradiction}</small></button>`;
  };
  const modes = ["plain", "mythic", "research"];
  const panels = modes.map(mode => {
    const narrative = synthesis.narratives[mode];
    const contents = `<nav class="narrative-contents" aria-label="${esc(mode)} reading chapters">${narrative.sections.map(section => `<a href="#reading-${mode}-${esc(section.section_id)}">${esc(section.heading)}</a>`).join("")}</nav>`;
    const sections = narrative.sections.map((section, index) => `<details id="reading-${mode}-${esc(section.section_id)}" class="narrative-section narrative-chapter"${index === 0 ? " open" : ""}><summary><h3 tabindex="-1">${esc(section.heading)}</h3><span>${section.paragraphs.length} ${section.paragraphs.length === 1 ? "passage" : "passages"}</span></summary>${section.paragraphs.map(paragraph => `<div class="narrative-paragraph">${paragraph.sentences.map(sentenceHTML).join("")}</div>`).join("")}</details>`).join("");
    const deterministic = `${contents}${sections}<p class="narrative-disclaimer">${esc(narrative.disclaimer)}</p>`;
    if (mode === "mythic") return `<div class="narrative-mode-panel" data-narrative-panel="${mode}" hidden><div class="remote-mythic-intro"><p data-remote-mythic-status>Mythic uses optional AI narration when selected. Until it loads, the deterministic reading remains below.</p><small>Only derived symbolic outputs are sent to OpenRouter/NVIDIA; your name, aliases, raw birth details, coordinates, raw psychology, and observations are not sent.</small></div><article class="remote-mythic-story" data-remote-mythic-story hidden></article><div data-deterministic-mythic>${deterministic}</div></div>`;
    return `<div class="narrative-mode-panel" data-narrative-panel="${mode}"${mode === "plain" ? "" : " hidden"}>${deterministic}</div>`;
  }).join("");
  const tension = plan.originating_tension;
  const tensionHTML = tension ? `<div class="tension-axis" role="group" aria-label="Unresolved tension between ${esc(tension.pole_a)} and ${esc(tension.pole_b)}"><strong>${esc(tension.pole_a)}</strong><span aria-hidden="true">←──────→</span><strong>${esc(tension.pole_b)}</strong><p>Unresolved ${esc(tension.type.replaceAll("_", " "))}; ${esc(tension.uncertainty)} confidence.</p></div>` : `<p class="tension-empty">No sufficiently supported polarity was detected.</p>`;
  const ledgerClaims = plan.narrative_sections.filter(section => section.section_id !== "evidence_ledger").flatMap(section => section.claims);
  const ledger = ledgerClaims.map(claim => {
    const items = claim.evidence_ids.map(id => evidenceById.get(id)).filter(Boolean);
    const systems = [...new Set(items.map(item => item.system))];
    const sources = items.map(item => `${item.source_path} = ${typeof item.source_value === "object" ? JSON.stringify(item.source_value) : item.source_value}`).join("; ");
    return `<tr><th scope="row">${esc(claim.claim_type.replaceAll("_", " "))}: ${esc(claim.motif.replace("|", " / "))}</th><td>${esc(systems.join(", "))}</td><td>${items.length}</td><td>${esc(claim.strength)}</td><td>${claim.contradicting_evidence_ids.length ? "Retained" : "None linked"}</td><td><details><summary>Sources and limits</summary><p>${esc(sources)}</p><p>${esc(claim.limitation)}</p></details></td></tr>`;
  }).join("");
  return `<section class="living-pattern" aria-labelledby="living-pattern-title">
    <header class="living-pattern-header"><div><p class="eyebrow">Human Metadata Narrative</p><h2 id="living-pattern-title">The Living Pattern</h2><p>Evidence-linked symbolic synthesis. The six Atlas surfaces remain the calculation record.</p></div><div><div class="narrative-mode-switch" role="group" aria-label="Narrative mode">${modes.map(mode => `<button type="button" data-narrative-mode="${mode}" aria-pressed="${mode === "plain"}">${esc(mode)}</button>`).join("")}</div><p class="narrative-ai-note">Plain and Research are local and deterministic. Mythic may use Qwen3.8 Flash through OpenRouter when selected.</p></div></header>
    <div class="central-pattern-card"><div class="archetype-seal" role="img" aria-label="Deterministic text seal for ${esc(central.title)}"><span>${esc(central.motif_ids.map(id => id.replace("motif_", "").slice(0, 2).toUpperCase()).join(" · ") || "—")}</span></div><div><p class="panel-index">Central pattern</p><h3>${esc(central.title)}</h3><p>${esc(central.definition)}</p><p><strong>${esc(central.confidence)} confidence</strong> · ${central.systems.length} participating systems</p></div></div>
    ${tensionHTML}
    <div class="living-pattern-narratives">${panels}</div>
    <details class="narrative-ledger"><summary>Open the sentence-level evidence ledger</summary><div class="table-scroll"><table><caption>Claims, source systems, evidence count, confidence, contradictions, and limits</caption><thead><tr><th>Claim</th><th>Systems</th><th>Evidence</th><th>Confidence</th><th>Contradiction</th><th>Trace</th></tr></thead><tbody>${ledger}</tbody></table></div></details>
    <p class="living-pattern-limits"><strong>Coverage:</strong> ${esc(plan.missing_or_uncertain_dimensions.join("; ") || "all requested dimensions available")}. Plain and Research are local and deterministic. Mythic remote narration is optional and is never used as calculation evidence.</p>
  </section>`;
}

function buildAtlas(result, options = {}) {
  const signature = result.signature || {};
  const encoders = signature.encoders || {};
  const selections = new Map();
  const register = (id, item) => {
    if (!id || !item) return;
    selections.set(id, {...item, id, links:[...new Set((item.links || []).filter(Boolean))]});
  };
  register.has = id => selections.has(id);
  register.get = id => selections.get(id);

  const humanDesign = encoders.human_design?.available !== false && encoders.human_design?.type ? encoders.human_design : null;
  const activations = humanDesign ? [...(humanDesign.personality_gates || []), ...(humanDesign.design_gates || [])] : [];
  const activationsByPlanet = activations.reduce((output, activation) => {
    (output[activation.planet] ||= []).push(activation);
    return output;
  }, {});
  const astrology = encoders.astrology && !encoders.astrology.error ? encoders.astrology : null;
  const reportMeta = result.report?.metadata || {};
  const payload = options.requestPayload || {};
  const coverage = [
    ["Name systems", "complete"],
    ["Astronomy", astrology ? "complete" : "not included"],
    ["Human Design", humanDesign ? "complete" : "not included"],
    ["User context", options.psychology ? "supplied" : "not included"],
  ];

  const panels = [
    crossSystemGraph(encoders, options.psychology, register),
    astrologyWheel(astrology, register, activationsByPlanet),
    humanDesignBodygraph(humanDesign, register),
    treeOfLife(encoders.kabbalah_tree_of_life, register),
    numerologyMatrix(encoders, register),
    identityFingerprint(signature, register),
  ];

  const html = `<section class="atlas" data-atlas-mode="explorer" aria-labelledby="atlas-title">
    <header class="atlas-header">
      <div class="atlas-heading"><p class="eyebrow">Human Metadata Atlas</p><h1 id="atlas-title" tabindex="-1">${esc(signature.text)}</h1><p>A visual index of calculated systems. Select any object to trace its values, method, provenance, and limits.</p></div>
      <div class="atlas-header-actions"><div class="mode-switch" role="group" aria-label="Atlas presentation mode"><button type="button" data-atlas-mode-button="explorer" aria-pressed="true">Explorer</button><button type="button" data-atlas-mode-button="research" aria-pressed="false">Research</button></div><div class="action-group"><button type="button" class="button" onclick="app.downloadReport()">Download report</button><button type="button" class="button" onclick="window.print()">Print</button><button type="button" class="button" onclick="app.editInputs()">Edit inputs</button></div></div>
    </header>
    <section class="atlas-summary" aria-label="Analysis identity and coverage"><div><span>Analysis</span><strong>${esc(result.input_hash?.slice(0, 12) || "not supplied")}</strong></div><div><span>Engine</span><strong>${esc(result.engine_version || "signature-v2")}</strong></div><div><span>Report</span><strong>${esc(reportMeta.report_schema_version || "report-v1")}</strong></div><div><span>Birth data</span><strong>${payload.birth ? (payload.birth.time_accuracy === "unknown" ? "Date only" : "Exact time") : "Not supplied"}</strong></div>${coverage.map(([label,status]) => `<div data-status="${esc(status)}"><span>${esc(label)}</span><strong>${esc(status)}</strong></div>`).join("")}</section>
    ${livingPattern(result)}
    <nav class="atlas-rail" aria-label="Visual systems">${[["constellation","Constellation"],["astrology","Astrology"],["human-design","Bodygraph"],["tree-of-life","Tree of Life"],["numerology","Numerology"],["fingerprint","Fingerprint"]].map(([id,label]) => `<a href="#atlas-${id}"><span>${esc(label.slice(0,2).toUpperCase())}</span>${esc(label)}</a>`).join("")}</nav>
    <div class="atlas-workspace"><div class="atlas-panels">${panels.join("")}</div><aside class="atlas-inspector" aria-labelledby="inspector-title"><div class="inspector-sticky"><p class="panel-index">Trace</p><h2 id="inspector-title">Select a visual object</h2><div id="atlas-inspector-content"><p>Choose a planet, aspect, gate, center, Sephirah, number system, or network node. Its supporting calculation and provenance will appear here.</p></div><div id="atlas-selection-status" class="sr-only" aria-live="polite"></div></div></aside></div>
    <div class="atlas-text-equivalent research-only"><h2>Text equivalent</h2><p>The atlas contains six views. The identity constellation inventories available systems; the astrology wheel plots returned longitudes and aspects; the bodygraph shows returned centers, channels, and all gates; the Tree of Life highlights the calculated Sephirah; the numerology matrix shows exact reductions; and the fingerprint renders the returned deterministic visual-hash parameters.</p></div>
  </section>`;
  return {html, selections};
}

document.addEventListener("click", event => {
  const link = event.target.closest(".narrative-contents a");
  if (!link) return;
  const chapter = document.getElementById(link.getAttribute("href").slice(1));
  if (chapter) chapter.open = true;
});
// Print all chapters without changing the reader's chosen expansion state.
let chapterPrintState = [];
window.addEventListener("beforeprint", () => {
  chapterPrintState = [...document.querySelectorAll(".narrative-chapter, .tarot-card-reading details, .tarot-method")].map(node => [node, node.open]);
  chapterPrintState.forEach(([node]) => { node.open = true; });
});
window.addEventListener("afterprint", () => {
  chapterPrintState.forEach(([node, open]) => { node.open = open; });
  chapterPrintState = [];
});
window.HMEAtlas = {buildAtlas};
})( );
