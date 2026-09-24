/* The Human Manual — additive Atlas coverage extension.
 *
 * Loaded after atlas.js and before app.js. This module intentionally does not
 * replace or edit the protected baseline visual surfaces. It wraps buildAtlas(),
 * appends new panels and rail entries, and extends the same selection Map used
 * by the existing Trace inspector.
 */
(function () {
"use strict";

if (!window.HMEAtlas?.buildAtlas) return;

const baseBuildAtlas = window.HMEAtlas.buildAtlas;
const esc = value => String(value ?? "").replace(/[&<>"]/g, ch => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;"
}[ch]));

const SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SIGN_GLYPHS = ["♈︎","♉︎","♊︎","♋︎","♌︎","♍︎","♎︎","♏︎","♐︎","♑︎","♒︎","♓︎"];
const PLANET_GLYPHS = {Sun:"☉",Moon:"☽",Mercury:"☿",Venus:"♀",Mars:"♂",Jupiter:"♃",Saturn:"♄",Uranus:"♅",Neptune:"♆",Pluto:"♇",Rahu:"☊",Ketu:"☋"};
const CHALDEAN_ORDER = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"];
const WU_XING_ORDER = ["Wood","Fire","Earth","Metal","Water"];

const CATALOG = [
  ["astrology","Astrology","astronomical","encoder"],
  ["human_design","Human Design","astronomical","encoder"],
  ["kabbalah_tree_of_life","Tree of Life","correspondence","encoder"],
  ["pythagorean","Pythagorean","numeric","encoder"],
  ["chaldean","Chaldean","numeric","encoder"],
  ["ordinal","Ordinal","numeric","encoder"],
  ["linguistic","Language structure","language","encoder"],
  ["binary_prime","Binary / Prime","numeric","encoder"],
  ["gematria","Gematria","numeric","encoder"],
  ["isopsephy","Isopsephy","numeric","encoder"],
  ["sacred_geometry","Sacred Geometry","geometry","encoder"],
  ["alchemical_transformation","Alchemy","correspondence","encoder"],
  ["sumerian_sexagesimal","Sumerian base-60","numeric","encoder"],
  ["sumerian_me_ontology","Sumerian me corpus","historical","encoder"],
  ["hermetic_principles","Hermetic principles","correspondence","encoder"],
  ["tarot","Tarot","correspondence","encoder"],
  ["babylonian_planetary","Babylonian planetary","correspondence","encoder"],
  ["hermes_thoth_nabu","Hermes / Thoth / Nabu","historical","encoder"],
  ["solomonic","Solomonic","correspondence","encoder"],
  ["arabic_abjad","Arabic Abjad","language","encoder"],
  ["chinese","I Ching / Wu Xing","correspondence","encoder"],
  ["egyptian","Egyptian","historical","encoder"],
  ["vedic_jyotish","Jyotish compatibility","astronomical","encoder"],
  ["mayan_tzolkin","Tzolkin compatibility","calendrical","encoder"],
  ["cuneiform_magic","Cuneiform structure","historical","encoder"],
  ["elder_futhark","Elder Futhark","language","encoder"],
  ["ogham","Ogham","language","encoder"],
  ["egyptian_maat","Ma'at balance","correspondence","encoder"],
  ["mandaean_duodecimal","Mandaean base-12","numeric","encoder"],
  ["tartaria_architecture","Architecture proportion","historical","encoder"],
  ["indus_valley","Indus structure","historical","encoder"],
  ["unicode_codepoint","Unicode structure","language","encoder"],
  ["apollonius","Apollonius","historical","encoder"],
  ["temporal_numerology","Temporal numerology","numeric","encoder"],
  ["esoteric_bridge","Explicit crosswalk","correspondence","encoder"],
  ["jyotish","Jyotish","astronomical","system"],
  ["bazi","BaZi","calendrical","system"],
  ["maya_classical","Classical Maya","calendrical","system"],
];

const VISUAL_COVERAGE_REGISTRY = {
  encoders: {
    astrology:"astrology", human_design:"human-design", kabbalah_tree_of_life:"tree-of-life",
    pythagorean:"numerology", chaldean:"numerology", ordinal:"numerology",
    linguistic:"script-number-lab", binary_prime:"script-number-lab", gematria:"numerology",
    isopsephy:"numerology", sacred_geometry:"correspondence-lab",
    alchemical_transformation:"correspondence-lab", sumerian_sexagesimal:"script-number-lab",
    sumerian_me_ontology:"historical-boundaries", hermetic_principles:"correspondence-lab",
    tarot:"correspondence-lab", babylonian_planetary:"correspondence-lab",
    hermes_thoth_nabu:"historical-boundaries", solomonic:"correspondence-lab",
    arabic_abjad:"script-number-lab", chinese:"correspondence-lab",
    egyptian:"historical-boundaries", vedic_jyotish:"correspondence-lab",
    mayan_tzolkin:"correspondence-lab", cuneiform_magic:"historical-boundaries",
    elder_futhark:"script-number-lab", ogham:"script-number-lab",
    egyptian_maat:"correspondence-lab", mandaean_duodecimal:"script-number-lab",
    tartaria_architecture:"historical-boundaries", indus_valley:"historical-boundaries",
    unicode_codepoint:"script-number-lab", apollonius:"correspondence-lab",
    temporal_numerology:"correspondence-lab", esoteric_bridge:"historical-boundaries"
  },
  systems: {jyotish:"jyotish", bazi:"bazi", maya_classical:"maya-classical"},
  layers: {
    comparisons:"evidence-map", correlations:"evidence-map", evidence:"evidence-map",
    sumerian_me_reflection:"historical-boundaries", "synthesis.pattern_map":"living-pattern"
  },
  protectedPanels:["constellation","astrology","human-design","tree-of-life","numerology","fingerprint"]
};

const RAIL = [
  ["script-number-lab","Scripts + Numbers"],
  ["correspondence-lab","Symbols + Traditions"],
  ["jyotish","Time Systems"],
  ["evidence-map","Comparisons + Evidence"]
];

const SCRIPT_NUMBER_KEYS = [
  "linguistic","binary_prime","sumerian_sexagesimal","arabic_abjad",
  "elder_futhark","ogham","mandaean_duodecimal","unicode_codepoint"
];
const CORRESPONDENCE_KEYS = [
  "sacred_geometry","alchemical_transformation","hermetic_principles","tarot",
  "babylonian_planetary","solomonic","chinese","egyptian_maat","apollonius",
  "temporal_numerology","vedic_jyotish","mayan_tzolkin"
];
const HISTORICAL_KEYS = [
  "sumerian_me_ontology","hermes_thoth_nabu","egyptian","cuneiform_magic",
  "tartaria_architecture","indus_valley","esoteric_bridge"
];
const BOUNDARIES = {
  sumerian_me_ontology:"Historical/textual ontology. No automatic personal assignment is permitted.",
  hermes_thoth_nabu:"Comparative historical correspondence. Role parallels are not identity claims.",
  egyptian:"Returned transliteration/decan structure only; visualization does not assign an Egyptian identity.",
  cuneiform_magic:"Unicode/cuneiform structure only. Lexical meaning is not invented.",
  tartaria_architecture:"Historical-claim status remains visible; speculative claims are not upgraded by visualization.",
  indus_valley:"The script remains explicitly undeciphered. Structural counts are not translated into fabricated meaning.",
  esoteric_bridge:"Project-authored crosswalk. It cannot count as independent evidence."
};

function polar(cx, cy, radius, degrees) {
  const radians = (degrees - 90) * Math.PI / 180;
  return [cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)];
}

function bodyOf(record) {
  if (!record || typeof record !== "object") return {};
  if (record.data && typeof record.data === "object") return record.data;
  if (record.calculation && typeof record.calculation === "object") return record.calculation;
  return record;
}

function compact(value) {
  if (value === null || value === undefined || value === "") return "—";
  if (Array.isArray(value)) {
    if (value.length <= 4 && value.every(item => ["string","number","boolean"].includes(typeof item))) return value.join(" · ");
    return `${value.length} items`;
  }
  if (typeof value === "object") return `${Object.keys(value).length} fields`;
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : String(Number(value.toFixed(6)));
  return String(value);
}

function metrics(record, limit = 6) {
  return Object.entries(bodyOf(record))
    .filter(([key]) => !["provenance","license","limitations"].includes(key))
    .slice(0, limit);
}

function recordProvenance(record, fallback = "Engine response") {
  const provenance = record?.provenance || {};
  return {
    source:(provenance.source_ids || []).join(", ") || fallback,
    method:record?.convention || provenance.convention || record?.calculation_engine || record?.calculation_standard || "Versioned engine calculation",
    confidence:record?.confidence || record?.status || "Returned record",
    interpretation:record?.epistemic_class || record?.interpretation_level || "See information-type label"
  };
}

function register(selections, id, item) {
  if (!id || selections.has(id)) return;
  selections.set(id, {...item, id, links:[...new Set((item.links || []).filter(Boolean))]});
}

function panel(id, title, subtitle, body, selection = "", featured = true) {
  return `<article id="atlas-${esc(id)}" class="atlas-panel atlas-expansion-panel${featured ? " atlas-panel--featured" : ""}" data-atlas-panel="${esc(id)}"><header><div><p class="panel-index">${esc(id.replaceAll("-"," "))}</p><h2>${esc(title)}</h2><p>${esc(subtitle)}</p></div><div class="panel-controls">${selection ? `<button type="button" class="panel-inspect" data-atlas-select="${esc(selection)}">Inspect method</button>` : ""}<button type="button" class="panel-expand" data-atlas-expand="${esc(id)}" aria-pressed="false" aria-label="View ${esc(title)} fullscreen">Fullscreen</button></div></header><div class="atlas-canvas">${body}</div></article>`;
}

function unavailablePanel(id, title, reason) {
  return panel(id, title, "Not calculated for this request", `<div class="atlas-unavailable"><span aria-hidden="true">∅</span><p>${esc(reason)}</p></div>`, "", true);
}

function ensureSystemSelection(selections, key, label, record, category, limitation = "") {
  if (!record) return;
  register(selections, `system:${key}`, {
    title:label,
    category,
    summary:metrics(record, 4).map(([field,value]) => `${field.replaceAll("_"," ")}: ${compact(value)}`).join("; ") || "Returned record is available.",
    ...recordProvenance(record, record?.system_id || key),
    inputs:(record?.input_dependencies || []).join(", ") || "Normalized analysis request",
    limitations:limitation || (record?.limitations || []).join(" ") || "Visual marks reproduce returned structure only; they do not establish personal truth.",
    reportTarget:"symbolic-systems",
    links:[]
  });
}

function systemInventory(result, selections) {
  const encoders = result.signature?.encoders || {};
  const systems = result.signature?.systems || {};
  const returned = CATALOG.filter(([key,_label,_category,sourceKind]) => sourceKind === "system" ? systems[key] : encoders[key]);
  returned.forEach(([key,label,category,sourceKind]) => {
    const record = sourceKind === "system" ? systems[key] : encoders[key];
    ensureSystemSelection(selections, key, label, record, `${category} ${sourceKind}`);
  });
  const groups = ["astronomical","calendrical","numeric","language","geometry","correspondence","historical"];
  const sections = groups.map(group => {
    const items = returned.filter(item => item[2] === group);
    if (!items.length) return "";
    return `<section class="inventory-group"><h3>${esc(group)}</h3><div>${items.map(([key,label,_category,sourceKind]) => {
      const record = sourceKind === "system" ? systems[key] : encoders[key];
      const count = Object.values(bodyOf(record)).filter(value => value !== null && value !== undefined && value !== "" && value !== false).length;
      return `<button type="button" class="inventory-node atlas-select" data-atlas-select="system:${esc(key)}" data-link-keys="system:${esc(key)}" aria-label="${esc(label)}, ${count} populated returned fields"><span>${esc(label)}</span><strong>${count}</strong><small>${esc(sourceKind === "system" ? record.system_version || "system-result-v2" : record.status || "returned")}</small></button>`;
    }).join("")}</div></section>`;
  }).join("");
  const body = `<div class="inventory-summary"><strong>${returned.length}</strong><span>returned encoder/system records now have a visual home</span></div><div class="system-inventory">${sections}</div><p class="visual-footnote">This inventory adds coverage without changing the original Identity Constellation. Counts describe populated returned fields, not importance, validity, or personal strength.</p>`;
  return panel("system-inventory", "Full system inventory", "Every returned backend encoder and richer calculator, grouped without collapsing traditions", body, "", true);
}

function jyotishPanel(system, selections) {
  if (!system || system.status !== "computed") return unavailablePanel("jyotish","Jyotish sidereal map","No computed Jyotish system-result-v2 record is available.");
  const calc = system.calculation || {};
  ensureSystemSelection(selections, "jyotish", "Jyotish", system, "sidereal astronomical/symbolic system",
    (system.limitations || []).join(" "));
  const bodies = [
    ...Object.entries(calc.planets || {}),
    ...Object.entries(calc.lunar_nodes || {}).filter(([key,value]) => ["Rahu","Ketu"].includes(key) && value && typeof value === "object")
  ];
  const size = 620, center = size / 2;
  const svg = [
    `<circle class="exp-wheel-boundary" cx="${center}" cy="${center}" r="260"/>`,
    `<circle class="exp-wheel-ring" cx="${center}" cy="${center}" r="210"/>`,
    `<circle class="exp-wheel-ring" cx="${center}" cy="${center}" r="154"/>`
  ];
  SIGNS.forEach((sign,index) => {
    const [x1,y1] = polar(center,center,154,index*30), [x2,y2] = polar(center,center,260,index*30), [tx,ty] = polar(center,center,239,index*30+15);
    svg.push(`<line class="exp-wheel-sector" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`);
    svg.push(`<text class="exp-wheel-sign" x="${tx.toFixed(1)}" y="${ty.toFixed(1)}">${SIGN_GLYPHS[index]}</text>`);
  });
  Array.from({length:27},(_,index) => {
    const degree = index * 360 / 27, [x1,y1] = polar(center,center,210,degree), [x2,y2] = polar(center,center,222,degree);
    svg.push(`<line class="nakshatra-tick" x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}"/>`);
  });
  bodies.forEach(([name,body],index) => {
    const longitude = Number(body.sign_index) * 30 + Number(body.degree || 0);
    if (!Number.isFinite(longitude)) return;
    const [x,y] = polar(center,center,178 + (index % 2) * 18,longitude);
    const id = `jyotish:body:${name}`;
    register(selections,id,{
      title:`${name} — sidereal`, category:"Jyotish calculated position",
      summary:`${body.sign} ${Number(body.degree || 0).toFixed(2)}° · ${body.nakshatra?.name || "nakshatra unavailable"} pada ${body.nakshatra?.pada || "—"}${body.retrograde ? " · retrograde" : ""}.`,
      ...recordProvenance(system), inputs:(system.input_dependencies || []).join(", "),
      limitations:"Lahiri sidereal coordinate; distinct from the tropical astrology panel. This does not establish empirical personality validity.",
      reportTarget:"jyotish", links:["system:jyotish"]
    });
    svg.push(`<g class="exp-wheel-body atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:jyotish`)}" tabindex="0" role="button" aria-label="${esc(name)} sidereal ${esc(body.sign)} ${Number(body.degree || 0).toFixed(2)} degrees"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="14"/><text x="${x.toFixed(1)}" y="${(y+.5).toFixed(1)}">${PLANET_GLYPHS[name] || esc(name.slice(0,2))}</text></g>`);
  });
  const nakshatras = [...new Map(bodies.filter(([,body]) => body.nakshatra).map(([,body]) => [body.nakshatra.index,body.nakshatra])).values()].sort((a,b)=>a.index-b.index);
  const chips = nakshatras.map(item => {
    const id = `jyotish:nakshatra:${item.index}`;
    register(selections,id,{title:item.name,category:"Nakshatra zone",summary:`27-nakshatra index ${item.index+1}; ruler ${item.ruler}.`,...recordProvenance(system),inputs:"Sidereal longitude under the selected ayanamsa",limitations:"Traditional interpretive zone; the visual mark reports the returned coordinate only.",reportTarget:"jyotish",links:["system:jyotish"]});
    return `<button type="button" class="nakshatra-chip atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:jyotish`)}"><strong>${esc(item.name)}</strong><span>${esc(item.ruler)} · #${item.index+1}</span></button>`;
  }).join("");
  const divisions = Object.entries(calc.planets || {}).map(([name,body]) => `<div class="division-row"><strong>${esc(name)}</strong><span>D9 ${esc(body.d9_navamsha?.sign || "—")}</span><span>D10 ${esc(body.d10_dasamsa?.sign || "—")}</span></div>`).join("");
  const body = `<div class="jyotish-layout"><svg class="jyotish-wheel" viewBox="0 0 ${size} ${size}" role="group" aria-labelledby="jyotish-expanded-title jyotish-expanded-desc"><title id="jyotish-expanded-title">Jyotish sidereal chart</title><desc id="jyotish-expanded-desc">Lahiri sidereal zodiac with 27 nakshatra boundaries and ${bodies.length} selectable returned positions. It is intentionally distinct from tropical astrology.</desc>${svg.join("")}</svg><div><dl class="exp-metrics"><div><dt>Ayanamsa</dt><dd>${esc(calc.ayanamsa?.name || "—")} ${calc.ayanamsa?.degrees !== undefined ? Number(calc.ayanamsa.degrees).toFixed(4)+"°" : ""}</dd></div><div><dt>Zodiac</dt><dd>${esc(calc.zodiac || "sidereal")}</dd></div><div><dt>Moon nakshatra</dt><dd>${esc(calc.moon_nakshatra?.name || "—")} · pada ${esc(calc.moon_nakshatra?.pada || "—")}</dd></div><div><dt>Node mode</dt><dd>${esc(calc.lunar_nodes?.mode || "—")}</dd></div></dl><h3>Active nakshatras</h3><div class="nakshatra-index">${chips}</div></div></div><div class="divisional-grid">${divisions}</div><p class="visual-footnote">D9 Navamsha and D10 Dasamsa remain separate deterministic divisional projections. They are not collapsed into the tropical wheel or into one blended zodiac.</p>`;
  return panel("jyotish","Jyotish sidereal map","Lahiri zodiac, nakshatras, lunar nodes, D9 and D10",body,"system:jyotish",true);
}

function baziPanel(system, selections) {
  if (!system || system.status !== "computed") return unavailablePanel("bazi","BaZi Four Pillars","No computed BaZi system-result-v2 record is available.");
  const calc = system.calculation || {}, pillars = calc.pillars || {}, gods = calc.ten_gods || {};
  ensureSystemSelection(selections,"bazi","BaZi",system,"Chinese Four Pillars calculation",(system.limitations || []).join(" "));
  const pillarCards = ["year","month","day","hour"].map(name => {
    const item = pillars[name];
    if (!item) return "";
    const id = `bazi:pillar:${name}`, relation = gods[name] || (name === "day" ? "Day Master" : "—");
    register(selections,id,{title:`${name[0].toUpperCase()+name.slice(1)} pillar`,category:"BaZi pillar",summary:`${item.stem} ${item.branch} · ${item.stem_polarity} ${item.stem_element} / ${item.branch_element} · ${relation}.`,...recordProvenance(system),inputs:(system.input_dependencies || []).join(", "),limitations:"Pillar and Ten-God labels follow the named BaZi convention; they are not empirical measurements.",reportTarget:"bazi",links:["system:bazi"]});
    return `<button type="button" class="bazi-pillar atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:bazi`)}"><span class="pillar-name">${esc(name)}</span><strong>${esc(item.stem)} · ${esc(item.branch)}</strong><span>${esc(item.stem_polarity)} ${esc(item.stem_element)} / ${esc(item.branch_element)}</span><small>${esc(relation)}</small><em>Hidden: ${esc((item.hidden_stems || []).join(" · ") || "—")}</em></button>`;
  }).join("");
  const phases = Object.entries(calc.five_phase_distribution || {}).map(([phase,value]) => {
    const pct = Math.max(0,Math.min(100,Number(value)*100)), id = `bazi:phase:${phase}`;
    register(selections,id,{title:`${phase} structural share`,category:"BaZi five-phase structural count",summary:`${pct.toFixed(1)}% of the returned equal-share visible/hidden-stem count.`,...recordProvenance(system),inputs:"Returned visible and hidden stems",limitations:"Explicitly not a Day-Master strength score.",reportTarget:"bazi",links:["system:bazi"]});
    return `<button type="button" class="phase-row atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:bazi`)}"><span>${esc(phase)}</span><i><b style="width:${pct.toFixed(2)}%"></b></i><strong>${pct.toFixed(1)}%</strong></button>`;
  }).join("");
  const dm = calc.day_master || {};
  const body = `<div class="bazi-master"><span>Day Master</span><strong>${esc(dm.stem || "—")}</strong><span>${esc(dm.polarity || "")} ${esc(dm.element || "")}</span></div><div class="bazi-pillars">${pillarCards}</div><h3 class="exp-subhead">Five-Phase structural distribution</h3><div class="phase-bars">${phases}</div><p class="visual-footnote">Four Pillars, hidden stems, Ten Gods, and Five-Phase counts remain inside the BaZi convention. The displayed distribution is structural and not a personality or strength score.</p>`;
  return panel("bazi","BaZi Four Pillars","Stems, branches, hidden stems, Ten Gods and Five Phases",body,"system:bazi",true);
}

function mayaPanel(system, selections) {
  if (!system || system.status !== "computed") return unavailablePanel("maya-classical","Classical Maya calendar","No computed Classical Maya system-result-v2 record is available.");
  const calc = system.calculation || {}, count = calc.long_count || {};
  ensureSystemSelection(selections,"maya_classical","Classical Maya",system,"Classical Maya calendrical calculation",(system.limitations || []).join(" "));
  const units = [["baktun",count.baktun],["katun",count.katun],["tun",count.tun],["winal",count.winal],["kin",count.kin]];
  const longCount = units.map(([unit,value]) => {
    const id = `maya:long-count:${unit}`;
    register(selections,id,{title:`${unit} ${value}`,category:"Classical Maya Long Count place",summary:`Returned ${unit} value ${value} within ${count.notation}.`,...recordProvenance(system),inputs:"Birth date under GMT 584283 correlation",limitations:"Calendrical coordinate only; not a personality or destiny claim.",reportTarget:"maya-classical",links:["system:maya_classical"]});
    return `<button type="button" class="maya-count-cell atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:maya_classical`)}"><strong>${esc(value)}</strong><span>${esc(unit)}</span></button>`;
  }).join("");
  const cycles = [
    ["Tzolkin",calc.tzolkin?.label,"maya:cycle:tzolkin"],
    ["Haab",calc.haab?.label,"maya:cycle:haab"],
    ["Calendar Round",calc.calendar_round,"maya:cycle:calendar-round"],
    ["Lord of Night",calc.lord_of_night,"maya:cycle:lord-of-night"]
  ].map(([label,value,id]) => {
    register(selections,id,{title:label,category:"Classical Maya calendrical cycle",summary:String(value || "Unavailable"),...recordProvenance(system),inputs:"Birth date under the recorded correlation constant",limitations:"Calendar coordinate only; no personality or future-event inference.",reportTarget:"maya-classical",links:["system:maya_classical"]});
    return `<button type="button" class="maya-cycle-card atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:maya_classical`)}"><span>${esc(label)}</span><strong>${esc(value || "—")}</strong></button>`;
  }).join("");
  const body = `<div class="maya-correlation"><span>GMT correlation</span><strong>${esc(calc.correlation?.constant || "—")}</strong><small>${esc(calc.correlation?.name || "")}</small></div><div class="maya-long-count">${longCount}</div><p class="maya-notation">${esc(count.notation || "")}</p><div class="maya-cycle-grid">${cycles}</div><p class="visual-footnote">Classical Maya remains distinct from the legacy mayan_tzolkin compatibility encoder and from modern Dreamspell systems.</p>`;
  return panel("maya-classical","Classical Maya calendar","Long Count, Tzolkin, Haab, Calendar Round and Lord of Night",body,"system:maya_classical",true);
}

function sequenceVisual(key, record, selections) {
  const data = bodyOf(record);
  if (key === "elder_futhark" && Array.isArray(data.runes)) {
    const tiles = data.runes.map((rune,index) => {
      const id = `futhark:rune:${index}`;
      register(selections,id,{
        title:`Rune ${index+1} · ${rune}`, category:"Elder Futhark returned sequence",
        summary:`Returned rune ${rune} at sequence position ${index+1}.`,
        ...recordProvenance(record), inputs:"Normalized name/transliteration",
        limitations:"Sequence position and rune glyph reproduce the returned encoder output. No divinatory meaning is added.",
        reportTarget:"symbolic-systems", links:["system:elder_futhark"]
      });
      return `<button type="button" class="sequence-glyph atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:elder_futhark`)}"><strong>${esc(rune)}</strong><span>${index+1}</span></button>`;
    }).join("");
    return `<div class="bespoke-visual"><div class="sequence-track rune-track" role="group" aria-label="Returned Elder Futhark rune sequence">${tiles || '<span class="empty-visual">No runes returned</span>'}</div><p class="bespoke-caption">Returned sequence only · total ${esc(data.rune_total ?? "—")} · unmapped Latin ${esc(data.unmapped_latin || "none")}</p></div>`;
  }
  if (key === "ogham" && Array.isArray(data.tree_letters)) {
    const tiles = data.tree_letters.map((item,index) => {
      const id = `ogham:letter:${index}`;
      register(selections,id,{
        title:`${item.letter} · ${item.tree}`, category:"Ogham returned sequence",
        summary:`Returned Ogham token ${item.letter} with tree label ${item.tree} at position ${index+1}.`,
        ...recordProvenance(record), inputs:"Normalized name/transliteration",
        limitations:"This is the returned project mapping. The visual does not infer ancestry, identity, or botanical traits.",
        reportTarget:"symbolic-systems", links:["system:ogham"]
      });
      return `<button type="button" class="sequence-glyph ogham-glyph atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:ogham`)}"><strong>${esc(item.letter)}</strong><span>${esc(item.tree)}</span></button>`;
    }).join("");
    return `<div class="bespoke-visual"><div class="sequence-track ogham-track" role="group" aria-label="Returned Ogham token sequence">${tiles || '<span class="empty-visual">No Ogham tokens returned</span>'}</div><p class="bespoke-caption">${esc(data.tree_count ?? 0)} returned tokens · correspondence display only</p></div>`;
  }
  return "";
}

function positionalVisual(key, record, selections) {
  const data = bodyOf(record);
  let digits = null, base = null, label = null;
  if (key === "sumerian_sexagesimal" && Array.isArray(data.base_60_digits)) {
    digits = data.base_60_digits; base = 60; label = "Base 60";
  } else if (key === "mandaean_duodecimal" && Array.isArray(data.base_12_digits)) {
    digits = data.base_12_digits; base = 12; label = "Base 12";
  }
  if (digits) {
    const cells = digits.map((digit,index) => {
      const power = digits.length - index - 1;
      const id = `${key}:digit:${index}`;
      register(selections,id,{
        title:`${label} digit ${digit}`, category:"Positional representation",
        summary:`Digit ${digit} in the ${base}^${power} place of decimal total ${data.decimal_total}.`,
        ...recordProvenance(record), inputs:"Returned decimal total",
        limitations:"Arithmetic place-value representation only; no lexical or personal meaning is inferred.",
        reportTarget:"symbolic-systems", links:[`system:${key}`]
      });
      return `<button type="button" class="place-cell atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:${key}`)}"><strong>${esc(digit)}</strong><span>${base}<sup>${power}</sup></span></button>`;
    }).join("");
    return `<div class="bespoke-visual"><div class="place-strip" aria-label="${label} returned positional digits">${cells}</div><p class="bespoke-caption">${esc(data.decimal_total)} decimal → ${label} positional notation</p></div>`;
  }
  if (key === "unicode_codepoint" && Array.isArray(data.codepoints)) {
    const cells = data.codepoints.slice(0,24).map((point,index) => {
      const id = `unicode:codepoint:${index}`;
      register(selections,id,{
        title:`Unicode ${point}`, category:"Unicode scalar-value record",
        summary:`Returned codepoint ${point} at normalized-text position ${index+1}.`,
        ...recordProvenance(record), inputs:"Normalized Unicode text",
        limitations:"Codepoint identity is structural metadata; it does not assign linguistic or symbolic meaning.",
        reportTarget:"symbolic-systems", links:["system:unicode_codepoint"]
      });
      return `<button type="button" class="codepoint-cell atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:unicode_codepoint`)}">${esc(point)}</button>`;
    }).join("");
    return `<div class="bespoke-visual"><div class="codepoint-strip">${cells}</div><p class="bespoke-caption">${data.codepoints.length > 24 ? `${data.codepoints.length} codepoints · first 24 shown` : `${data.codepoints.length} codepoints`} · UTF-8 ${esc(data.utf8_byte_length ?? "—")} bytes</p></div>`;
  }
  if (key === "binary_prime" && typeof data.binary_string === "string") {
    const bits = [...data.binary_string].slice(0,64).map((bit,index) => `<span class="bit bit-${esc(bit)}" title="bit ${index+1}: ${esc(bit)}">${esc(bit)}</span>`).join("");
    return `<div class="bespoke-visual"><div class="bit-strip" aria-label="Returned binary string">${bits}</div><p class="bespoke-caption">${data.binary_string.length > 64 ? `${data.binary_string.length} bits · first 64 shown` : `${data.binary_string.length} bits`} · prime total ${esc(data.prime_total ?? "—")}</p></div>`;
  }
  return "";
}

function chineseCoordinateVisual(record, selections) {
  const data = bodyOf(record);
  const index = Number(data.iching_hexagram_index);
  if (!Number.isInteger(index) || index < 1 || index > 64) return "";
  const cells = Array.from({length:64},(_,i) => {
    const n=i+1, active=n===index;
    return `<span class="hex-index-cell${active ? " is-active" : ""}" aria-label="hexagram index ${n}${active ? ", returned" : ""}">${n}</span>`;
  }).join("");
  const id="chinese:coordinate";
  register(selections,id,{
    title:`I Ching index ${index}`, category:"Returned Chinese-system coordinate",
    summary:`Hexagram index ${index}; trigram ${data.trigram || "—"}; Wu Xing element ${data.wu_xing_element || "—"}${data.year_pillar ? `; year pillar ${data.year_pillar}` : ""}.`,
    ...recordProvenance(record), inputs:"Returned encoder fields",
    limitations:"The grid locates the returned King-Wen index only. It does not fabricate hexagram line structure or imply empirical validity.",
    reportTarget:"symbolic-systems", links:["system:chinese"]
  });
  const elements = WU_XING_ORDER.map(element => `<span class="wuxing-node${element===data.wu_xing_element ? " is-active" : ""}">${esc(element)}</span>`).join("");
  return `<div class="bespoke-visual atlas-select chinese-coordinate" data-atlas-select="${id}" data-link-keys="${id} system:chinese" tabindex="0" role="button" aria-label="I Ching index ${index}, ${esc(data.trigram || "")}, ${esc(data.wu_xing_element || "")}"><div class="hex-index-grid">${cells}</div><div class="wuxing-row">${elements}</div><p class="bespoke-caption">King-Wen index ${index} · trigram ${esc(data.trigram || "—")} · ${esc(data.year_pillar || "no birth-year pillar returned")}</p></div>`;
}

function sacredGeometryVisual(record, selections) {
  const data=bodyOf(record), sides=Number(data.polygon_sides), layer=Number(data.tetractys_layer);
  if (!Number.isInteger(sides) || sides < 3 || sides > 12) return "";
  const cx=90,cy=90,r=68;
  const points=Array.from({length:sides},(_,i)=>polar(cx,cy,r,i*360/sides)).map(([x,y])=>`${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const tetractys=[[90,25],[72,55],[108,55],[54,88],[90,88],[126,88],[36,126],[72,126],[108,126],[144,126]];
  const dots=tetractys.map(([x,y],i)=>`<circle cx="${x}" cy="${y}" r="5" class="${i < Math.max(0,Math.min(10,layer)) ? "is-active" : ""}"/>`).join("");
  const id="sacred-geometry:plate";
  register(selections,id,{
    title:`${sides}-sided geometry plate`, category:"Sacred-geometry indexed visualization",
    summary:`Returned polygon_sides=${sides}; tetractys_layer=${layer}; digital_root=${data.digital_root}.`,
    ...recordProvenance(record), inputs:"Returned integer fields",
    limitations:"The polygon and ten-dot plate visualize returned indices only. They do not establish metaphysical or empirical properties.",
    reportTarget:"symbolic-systems", links:["system:sacred_geometry"]
  });
  return `<button type="button" class="bespoke-visual geometry-plate atlas-select" data-atlas-select="${id}" data-link-keys="${id} system:sacred_geometry"><svg viewBox="0 0 180 160" role="img" aria-label="${sides}-sided returned polygon and tetractys index ${layer}"><polygon points="${points}" class="geometry-polygon"/><g class="tetractys-dots">${dots}</g></svg><span>${sides}-gon · tetractys index ${esc(layer)} · root ${esc(data.digital_root ?? "—")}</span></button>`;
}

function planetaryOrderVisual(record, selections) {
  const data=bodyOf(record), activeIndex=Number(data.chaldean_order_index);
  if (!Number.isInteger(activeIndex) || activeIndex < 1 || activeIndex > 7) return "";
  const size=220,c=size/2,r=76;
  const nodes=CHALDEAN_ORDER.map((planet,index)=>{
    const [x,y]=polar(c,c,r,index*360/7), id=`chaldean-order:${index+1}`;
    register(selections,id,{
      title:`Chaldean order ${index+1} · ${planet}`, category:"Canonical Chaldean planetary order",
      summary:`Position ${index+1} in Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon.${index+1===activeIndex ? " This is the returned active position." : ""}`,
      ...recordProvenance(record), inputs:"Named Chaldean-order convention",
      limitations:"Traditional ordering context only; the active marker is the returned encoder result.",
      reportTarget:"symbolic-systems", links:["system:babylonian_planetary"]
    });
    return `<g class="planet-order-node atlas-select${index+1===activeIndex ? " is-active" : ""}" data-atlas-select="${id}" data-link-keys="${id} system:babylonian_planetary" tabindex="0" role="button" aria-label="${planet}, Chaldean order ${index+1}${index+1===activeIndex ? ", returned" : ""}"><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="17"/><text x="${x.toFixed(1)}" y="${(y+1).toFixed(1)}">${PLANET_GLYPHS[planet] || esc(planet[0])}</text></g>`;
  }).join("");
  return `<div class="bespoke-visual planetary-order"><svg viewBox="0 0 ${size} ${size}" role="group" aria-label="Chaldean planetary order"><circle cx="${c}" cy="${c}" r="${r}" class="order-ring"/>${nodes}<text x="${c}" y="${c-4}" class="order-center">${esc(data.planet || "—")}</text><text x="${c}" y="${c+13}" class="order-center-small">#${activeIndex}</text></svg><p class="bespoke-caption">Traditional Chaldean order · returned active planet ${esc(data.planet || "—")}</p></div>`;
}

function bespokeVisual(key, record, selections) {
  return sequenceVisual(key,record,selections)
    || positionalVisual(key,record,selections)
    || (key === "chinese" ? chineseCoordinateVisual(record,selections) : "")
    || (key === "sacred_geometry" ? sacredGeometryVisual(record,selections) : "")
    || (key === "babylonian_planetary" ? planetaryOrderVisual(record,selections) : "");
}

function labPanel(id,title,subtitle,keys,encoders,selections,kind,boundary = false) {
  const cards = keys.map(key => {
    const record = encoders[key];
    if (!record) return "";
    const label = CATALOG.find(item => item[0] === key)?.[1] || key.replaceAll("_"," ");
    ensureSystemSelection(selections,key,label,record,kind,BOUNDARIES[key] || "");
    const returnedMetrics = metrics(record,6);
    const previewRows = returnedMetrics.slice(0,2).map(([field,value]) => `<div><dt>${esc(field.replaceAll("_"," "))}</dt><dd>${esc(compact(value))}</dd></div>`).join("");
    const moreRows = returnedMetrics.slice(2).map(([field,value]) => `<div><dt>${esc(field.replaceAll("_"," "))}</dt><dd>${esc(compact(value))}</dd></div>`).join("");
    const bespoke = bespokeVisual(key,record,selections);
    const note = boundary ? `<p class="boundary-note">${esc(BOUNDARIES[key] || "Provenance boundary shown; no additional meaning is inferred.")}</p>` : "";
    const more = moreRows ? `<details class="lab-card-more"><summary>More returned stats</summary><dl>${moreRows}</dl></details>` : "";
    return `<article class="visual-lab-card${boundary ? " visual-lab-card--boundary" : ""}"><button type="button" class="lab-card-select atlas-select" data-atlas-select="system:${esc(key)}" data-link-keys="system:${esc(key)}"><span>${esc(kind)}</span><strong>${esc(label)}</strong><small>Preview · inspect for full method</small></button>${bespoke}<dl class="lab-card-preview">${previewRows}</dl>${more}${note}<details class="research-only"><summary>Returned field inventory</summary><code>${esc(Object.keys(bodyOf(record)).join(" · "))}</code></details></article>`;
  }).filter(Boolean).join("");
  return cards ? panel(id,title,subtitle,`<div class="visual-lab-grid">${cards}</div>`,"",true) : unavailablePanel(id,title,"No records assigned to this visual family are available.");
}

function historicalPanel(encoders,result,selections) {
  const base = labPanel("historical-boundaries","History, corpus & boundary ledger","Historical, undeciphered, contested and project-authored records with their limits visible",HISTORICAL_KEYS,encoders,selections,"provenance boundary",true);
  const reflection = result.sumerian_me_reflection;
  if (!reflection) return base;
  const id = "layer:sumerian_me_reflection";
  register(selections,id,{
    title:"Sumerian me reflection", category:"Modern interpretive crosswalk status",
    summary:`${reflection.status}; enabled=${Boolean(reflection.enabled)}; mapping basis: ${reflection.mapping_basis}.`,
    source:reflection.source_ontology_version || "sumerian me ontology",
    method:reflection.version || "sumerian-me-reflection-v1",
    inputs:"Explicit user-supplied observation capacity_domains only when enabled",
    confidence:"Modern interpretive layer",
    interpretation:reflection.epistemic_layer || "modern_interpretive",
    limitations:"Not a historical claim and never automatically mapped from name, birth data, numerology, astrology, or symbolic resonance.",
    reportTarget:"sumerian-me-reflection", links:["system:sumerian_me_ontology"]
  });
  const card = `<button type="button" class="reflection-status atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:sumerian_me_ontology`)}"><span>Sumerian me reflection</span><strong>${esc(reflection.status || "unknown")}</strong><small>${esc(reflection.reason || "Explicit opt-in crosswalk only.")}</small></button>`;
  return base.replace('<div class="visual-lab-grid">', `${card}<div class="visual-lab-grid">`);
}

function evidencePanel(result,selections) {
  const evidence = result.evidence || {}, correlations = result.correlations || {}, pattern = result.synthesis?.pattern_map || {};
  const layers = evidence.layers || [];
  const rows = layers.map(layer => {
    const id = `evidence-layer:${layer.id}`, maximum = Number(layer.maximum_influence || 0), available = Number(layer.available_influence || 0), width = maximum > 0 ? Math.max(0,Math.min(100,available/maximum*100)) : 0;
    register(selections,id,{title:layer.label,category:`${layer.class} evidence layer`,summary:`Available influence ${available.toFixed(2)} of configured maximum ${maximum.toFixed(2)}.`,source:evidence.method_version || "evidence policy",method:evidence.normalization || "configured evidence normalization",inputs:layer.available ? "Layer available in this response" : "Layer unavailable in this response",confidence:"Policy weight, not truth confidence",interpretation:layer.class,limitations:layer.description,reportTarget:"evidence",links:["system:identity"]});
    return `<button type="button" class="evidence-layer-row atlas-select" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:identity`)}"><span>${esc(layer.label)}</span><i><b style="width:${width.toFixed(1)}%"></b></i><strong>${esc(layer.available ? available.toFixed(2) : "missing")}</strong></button>`;
  }).join("");
  const names = correlations.magnitude_encoders || [];
  const matrix = names.length ? `<div class="correlation-matrix" style="--matrix-n:${names.length}" role="table" aria-label="Dataset encoder Pearson correlation matrix"><span></span>${names.map(name => `<strong>${esc(name.slice(0,4))}</strong>`).join("")}${names.map(row => `<strong>${esc(row.slice(0,4))}</strong>${names.map(col => {
    const value = Number(correlations.pearson?.[row]?.[col]);
    const level = Number.isFinite(value) ? Math.max(0,Math.min(100,Math.abs(value)*100)) : 0;
    return `<span title="${esc(row)} × ${esc(col)}: ${Number.isFinite(value) ? value.toFixed(3) : "n/a"}" style="--cell-strength:${level.toFixed(1)}%">${Number.isFinite(value) ? value.toFixed(2) : "—"}</span>`;
  }).join("")}`).join("")}</div>` : "<p>No dataset correlation matrix is present.</p>";
  register(selections,"evidence:policy",{title:"Evidence architecture",category:"Evidence policy",summary:`Coverage ${(Number(evidence.coverage || 0)*100).toFixed(0)}% with ${layers.filter(item=>item.available).length}/${layers.length} configured layers available.`,source:evidence.method_version || "evidence policy",method:evidence.normalization || "absolute weights",inputs:"Returned evidence-layer availability",confidence:"Policy description only",interpretation:"Evidence governance",limitations:"Configured influence weights are not empirical truth probabilities.",reportTarget:"evidence",links:rows.length ? layers.map(item=>`evidence-layer:${item.id}`) : []});
  const comparisonCount = Array.isArray(result.comparisons) ? result.comparisons.length : 0;
  const ribbon = layers.map(layer => {
    const id = `evidence-layer:${layer.id}`;
    return `<button type="button" class="provenance-ribbon-segment atlas-select ${layer.available ? "is-available" : "is-missing"}" data-atlas-select="${esc(id)}" data-link-keys="${esc(`${id} system:identity`)}"><strong>${esc(layer.label)}</strong><span>${esc(layer.class)}</span></button>`;
  }).join("");
  const body = `<div class="provenance-ribbon" aria-label="Evidence provenance ribbon">${ribbon}</div><div class="evidence-map-summary"><button type="button" class="evidence-policy-card atlas-select" data-atlas-select="evidence:policy" data-link-keys="evidence:policy system:identity"><span>Evidence coverage</span><strong>${(Number(evidence.coverage || 0)*100).toFixed(0)}%</strong><small>${layers.filter(item=>item.available).length}/${layers.length} configured layers present</small></button><div><span>Pattern explanations</span><strong>${(pattern.agreement_explanations || []).length + (pattern.disagreement_explanations || []).length}</strong><small>same evidence graph; no added votes</small></div><div><span>Reference comparisons</span><strong>${comparisonCount}</strong><small>intentionally not visualized as person-level similarity</small></div></div><h3 class="exp-subhead">Evidence-layer availability</h3><div class="evidence-layer-bars">${rows}</div><h3 class="exp-subhead research-only">Dataset encoder correlations</h3><div class="research-only">${matrix}<p class="visual-footnote">These correlations describe the configured reference dataset across encoder magnitudes. They are not a similarity score for the person in this report.</p></div>`;
  return panel("evidence-map","Evidence & dependence map","What is available, how it is weighted, and what is intentionally not inferred",body,"evidence:policy",true);
}

function expandedBuildAtlas(result, options = {}) {
  const base = baseBuildAtlas(result, options);
  const selections = base.selections;
  const encoders = result.signature?.encoders || {};
  const systems = result.signature?.systems || {};

  const expansionPanels = [
    systemInventory(result,selections),
    jyotishPanel(systems.jyotish,selections),
    baziPanel(systems.bazi,selections),
    mayaPanel(systems.maya_classical,selections),
    labPanel("script-number-lab","Script & number laboratory","Language structure, bases, code points and deterministic transforms",SCRIPT_NUMBER_KEYS,encoders,selections,"deterministic transform"),
    labPanel("correspondence-lab","Symbolic correspondence atlas","Returned symbolic coordinates kept separate by convention",CORRESPONDENCE_KEYS,encoders,selections,"symbolic correspondence"),
    historicalPanel(encoders,result,selections),
    evidencePanel(result,selections)
  ].join("");

  const railLinks = RAIL.map(([id,label]) => `<a href="#atlas-${esc(id)}"><span>${esc(label.slice(0,2).toUpperCase())}</span>${esc(label)}</a>`).join("");
  let html = base.html;
  const railMarker = '</nav>\n    <div class="atlas-workspace">';
  if (html.includes(railMarker)) html = html.replace(railMarker, `${railLinks}</nav>\n    <div class="atlas-workspace">`);
  const panelMarker = '</div><aside class="atlas-inspector"';
  if (html.includes(panelMarker)) html = html.replace(panelMarker, `${expansionPanels}</div><aside class="atlas-inspector"`);
  html = html.replace(
    "The atlas contains six views.",
    "The protected six views remain intact, and additive expansion panels provide declared visual homes for every returned encoder and richer calculator."
  );
  html = html.replace(
    "Choose a planet, aspect, gate, center, Sephirah, number system, or network node.",
    "Choose any visual object: existing planets, aspects, gates, centers, Sephiroth, numbers, or network nodes, plus expanded system records, Jyotish bodies, BaZi pillars, Maya cycles, evidence layers, and provenance-boundary cards."
  );

  return {html,selections};
}

window.HMEAtlas.buildAtlas = expandedBuildAtlas;
window.HMEAtlas.coverageRegistry = VISUAL_COVERAGE_REGISTRY;
window.HMEAtlas.expansionVersion = "atlas-expansion-v1";
})();
