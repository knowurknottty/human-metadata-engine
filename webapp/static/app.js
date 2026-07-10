/* Identity Resonance — client app.
   Renders the free dashboard + paywalled report from /api/analyze. */

(function () {
"use strict";

// ------------------------------------------------------------------
// Constants
// ------------------------------------------------------------------

const ACCENT = {
  pythagorean: "#fbbf24", chaldean: "#f59e0b", ordinal: "#93c5fd",
  linguistic: "#60a5fa", binary_prime: "#2dd4bf", gematria: "#a78bfa",
  isopsephy: "#c4b5fd", astrology: "#e879f9", human_design: "#34d399",
  psychology: "#fb7185",
};

const NUM_MEANING = {
  1: "the Initiator", 2: "the Diplomat", 3: "the Communicator",
  4: "the Builder", 5: "the Freedom-Seeker", 6: "the Guardian",
  7: "the Analyst", 8: "the Executive", 9: "the Humanitarian",
  11: "the Illuminator ✦", 22: "the Master Builder ✦", 33: "the Master Teacher ✦",
};

const MBTI_TYPES = ["INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
                    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"];
const MBTI_STACK = {
  INTJ:["Ni","Te","Fi","Se"],INTP:["Ti","Ne","Si","Fe"],ENTJ:["Te","Ni","Se","Fi"],
  ENTP:["Ne","Ti","Fe","Si"],INFJ:["Ni","Fe","Ti","Se"],INFP:["Fi","Ne","Si","Te"],
  ENFJ:["Fe","Ni","Se","Ti"],ENFP:["Ne","Fi","Te","Si"],ISTJ:["Si","Te","Fi","Ne"],
  ISFJ:["Si","Fe","Ti","Ne"],ESTJ:["Te","Si","Ne","Fi"],ESFJ:["Fe","Si","Ne","Ti"],
  ISTP:["Ti","Se","Ni","Fe"],ISFP:["Fi","Se","Ni","Te"],ESTP:["Se","Ti","Fe","Ni"],
  ESFP:["Se","Fi","Te","Ni"],
};
const B5 = [
  ["openness","Openness"],["conscientiousness","Conscientiousness"],
  ["extraversion","Extraversion"],["agreeableness","Agreeableness"],
  ["neuroticism","Neuroticism"],
];

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

let STATE = { result: null, paid: false, psychology: null };

// ------------------------------------------------------------------
// Fingerprint glyph renderer (from the deterministic server spec)
// ------------------------------------------------------------------

function fingerprintSVG(fp, size) {
  const S = size || 200, C = S / 2, R = S * 0.44;
  const sym = fp.symmetry || 5;
  const spokes = fp.spokes || [];
  const ring = fp.ring_pattern || "";
  let el = [];
  // Outer binary ring: consonant=arc segment, vowel=gap
  const n = Math.max(ring.length, 1);
  for (let i = 0; i < ring.length; i++) {
    const a0 = (i / n) * 2 * Math.PI - Math.PI / 2, a1 = ((i + 0.8) / n) * 2 * Math.PI - Math.PI / 2;
    const r = R;
    const x0 = C + r * Math.cos(a0), y0 = C + r * Math.sin(a0);
    const x1 = C + r * Math.cos(a1), y1 = C + r * Math.sin(a1);
    const col = ring[i] === "1" ? "rgba(226,232,240,.75)" : "rgba(251,191,36,.9)";
    const w = ring[i] === "1" ? 2 : 3.5;
    el.push(`<path d="M${x0.toFixed(1)},${y0.toFixed(1)} A${r},${r} 0 0 1 ${x1.toFixed(1)},${y1.toFixed(1)}" stroke="${col}" stroke-width="${w}" fill="none" stroke-linecap="round"/>`);
  }
  // Symmetric petal figure: for each symmetry fold, draw the spoke polygon
  for (let k = 0; k < sym; k++) {
    const rot = (k / sym) * 360;
    let pts = [];
    spokes.forEach((sp, i) => {
      const a = (i / spokes.length) * 2 * Math.PI / sym - Math.PI / 2;
      const r = R * 0.18 + R * 0.62 * sp.value;
      pts.push(`${(C + r * Math.cos(a)).toFixed(1)},${(C + r * Math.sin(a)).toFixed(1)}`);
    });
    pts.push(`${C},${C}`);
    const hue = spokes.length ? spokes[k % spokes.length].hue : 45;
    el.push(`<polygon points="${pts.join(" ")}" fill="hsla(${hue},80%,65%,.16)" stroke="hsla(${hue},85%,70%,.55)" stroke-width="1" transform="rotate(${rot.toFixed(2)} ${C} ${C})"/>`);
  }
  // Spoke dots
  spokes.forEach((sp, i) => {
    const a = (i / spokes.length) * 2 * Math.PI - Math.PI / 2;
    const r = R * 0.18 + R * 0.62 * sp.value;
    el.push(`<circle cx="${(C + r * Math.cos(a)).toFixed(1)}" cy="${(C + r * Math.sin(a)).toFixed(1)}" r="${S * 0.014}" fill="hsl(${sp.hue},85%,70%)"/>`);
  });
  el.push(`<circle cx="${C}" cy="${C}" r="${S * 0.03}" fill="rgba(251,191,36,.9)"/>`);
  return `<svg viewBox="0 0 ${S} ${S}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="identity fingerprint">${el.join("")}</svg>`;
}

// Simple decorative glyph for landing (before any analysis)
function decorativeFP(seed, size) {
  const rand = mulberry(seed);
  const spokes = Array.from({length: 7}, (_, i) => ({value: 0.3 + rand() * 0.7, hue: [45,30,200,220,160,280,260][i]}));
  return fingerprintSVG({symmetry: 3 + Math.floor(rand() * 6), spokes,
    ring_pattern: Array.from({length: 10 + Math.floor(rand()*8)}, () => rand() > 0.4 ? "1" : "0").join("")}, size);
}
function mulberry(a) { return function() { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ------------------------------------------------------------------
// Small chart builders (pure SVG)
// ------------------------------------------------------------------

function gaugeSVG(score) {
  const r = 84, cx = 100, cy = 100;
  const arc = Math.PI * 1.5; // 270°
  const len = r * arc;
  const filled = len * (score / 100);
  const hue = 20 + (score / 100) * 120; // red->green sweep via gold
  return `
  <svg viewBox="0 0 200 170" class="w-full max-w-[260px] mx-auto">
    <g transform="rotate(135 ${cx} ${cy})">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="rgba(255,255,255,.07)" stroke-width="13"
        stroke-dasharray="${len} ${2*Math.PI*r}" stroke-linecap="round"/>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="hsl(${hue},85%,60%)" stroke-width="13"
        class="gauge-arc" stroke-dasharray="${len} ${2*Math.PI*r}" stroke-dashoffset="${len}" stroke-linecap="round"
        data-target="${(len - filled).toFixed(1)}"/>
    </g>
    <text x="100" y="102" text-anchor="middle" font-size="40" font-weight="800" fill="#f8fafc" class="stat-num gauge-num">0</text>
    <text x="100" y="126" text-anchor="middle" font-size="12" fill="#94a3b8">/ 100 resonance</text>
  </svg>`;
}

function animateGauge(container, score) {
  const arc = container.querySelector(".gauge-arc");
  const num = container.querySelector(".gauge-num");
  requestAnimationFrame(() => {
    arc.style.strokeDashoffset = arc.dataset.target;
    const t0 = performance.now();
    (function tick(t) {
      const p = Math.min(1, (t - t0) / 1500);
      num.textContent = (score * (1 - Math.pow(1 - p, 3))).toFixed(1);
      if (p < 1) requestAnimationFrame(tick);
    })(t0);
  });
}

function meter(label, value, max, color, suffix) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return `<div class="mt-2">
    <div class="flex justify-between text-xs text-slate-400"><span>${esc(label)}</span>
      <span class="stat-num text-slate-200">${typeof value === "number" ? value.toFixed(2).replace(/\.00$/, "") : value}${suffix || ""}</span></div>
    <div class="h-1.5 mt-1 rounded-full bg-white/8"><div class="h-full rounded-full" style="width:${pct}%;background:${color}"></div></div>
  </div>`;
}

function pieSVG(a, b, colA, colB, labA, labB) {
  const total = a + b || 1, fa = a / total;
  const r = 40, c = 2 * Math.PI * r;
  return `<div class="flex items-center gap-4">
    <svg viewBox="0 0 100 100" class="w-20 h-20 -rotate-90">
      <circle cx="50" cy="50" r="${r}" fill="none" stroke="${colB}" stroke-width="16"/>
      <circle cx="50" cy="50" r="${r}" fill="none" stroke="${colA}" stroke-width="16"
        stroke-dasharray="${(fa*c).toFixed(1)} ${c}"/>
    </svg>
    <div class="text-xs space-y-1">
      <div><span class="inline-block w-2.5 h-2.5 rounded-sm mr-1.5" style="background:${colA}"></span>${labA}: <b class="stat-num">${a}</b></div>
      <div><span class="inline-block w-2.5 h-2.5 rounded-sm mr-1.5" style="background:${colB}"></span>${labB}: <b class="stat-num">${b}</b></div>
    </div></div>`;
}

function radarSVG(values, labels, color) {
  const n = values.length, C = 90, R = 62;
  const pt = (i, v) => {
    const a = (i / n) * 2 * Math.PI - Math.PI / 2;
    return [(C + R * v * Math.cos(a)).toFixed(1), (C + R * v * Math.sin(a)).toFixed(1)];
  };
  let grid = "";
  for (const g of [0.33, 0.66, 1]) {
    grid += `<polygon points="${Array.from({length: n}, (_, i) => pt(i, g).join(",")).join(" ")}" fill="none" stroke="rgba(255,255,255,.09)"/>`;
  }
  const poly = values.map((v, i) => pt(i, v).join(",")).join(" ");
  const lbls = labels.map((l, i) => {
    const [x, y] = pt(i, 1.24);
    return `<text x="${x}" y="${y}" text-anchor="middle" font-size="9" fill="#94a3b8">${esc(l)}</text>`;
  }).join("");
  return `<svg viewBox="0 0 180 180" class="w-full max-w-[240px] mx-auto">${grid}
    <polygon points="${poly}" fill="${color}33" stroke="${color}" stroke-width="1.5"/>
    ${values.map((v,i)=>{const[x,y]=pt(i,v);return `<circle cx="${x}" cy="${y}" r="2.5" fill="${color}"/>`}).join("")}${lbls}</svg>`;
}

function heatmapHTML(corr) {
  const encs = corr.digit_encoders;
  const cells = encs.map(a =>
    `<tr><th class="text-right pr-2 text-[10px] sm:text-xs text-slate-400 font-normal">${a}</th>` +
    encs.map(b => {
      const v = corr.digit_agreement[a][b];
      const hue = 260 - v * 215; // purple->gold
      return `<td class="p-0.5"><div class="hm-cell rounded aspect-square flex items-center justify-center text-[9px] sm:text-[11px] font-semibold"
        style="background:hsla(${hue},75%,55%,${0.15 + v * 0.75});color:${v > 0.5 ? "#0f172a" : "#e2e8f0"}" title="${a} vs ${b}: ${(v*100).toFixed(0)}%">${(v*100).toFixed(0)}</div></td>`;
    }).join("") + "</tr>").join("");
  return `<div class="overflow-x-auto"><table class="mx-auto"><thead><tr><th></th>${
    encs.map(e => `<th class="pb-1 text-[10px] sm:text-xs text-slate-400 font-normal rotate-0">${e.slice(0,6)}</th>`).join("")
  }</tr></thead><tbody>${cells}</tbody></table></div>
  <p class="text-xs text-slate-500 mt-3 text-center">% of analyzed identities where each pair of digit systems reduces to the same root (your name included).</p>`;
}

function natalWheelSVG(astro) {
  const SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
  const GLYPH = {Aries:"♈",Taurus:"♉",Gemini:"♊",Cancer:"♋",Leo:"♌",Virgo:"♍",Libra:"♎",Scorpio:"♏",Sagittarius:"♐",Capricorn:"♑",Aquarius:"♒",Pisces:"♓"};
  const PG = {Sun:"☉",Moon:"☽",Mercury:"☿",Venus:"♀",Mars:"♂",Jupiter:"♃",Saturn:"♄",Uranus:"♅",Neptune:"♆",Pluto:"♇"};
  const C = 130, R1 = 122, R2 = 98;
  let el = [`<circle cx="${C}" cy="${C}" r="${R1}" fill="none" stroke="rgba(232,121,249,.35)"/>`,
            `<circle cx="${C}" cy="${C}" r="${R2}" fill="none" stroke="rgba(255,255,255,.12)"/>`];
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * 2 * Math.PI - Math.PI / 2;
    el.push(`<line x1="${C + R2 * Math.cos(a)}" y1="${C + R2 * Math.sin(a)}" x2="${C + R1 * Math.cos(a)}" y2="${C + R1 * Math.sin(a)}" stroke="rgba(255,255,255,.15)"/>`);
    const am = a + Math.PI / 12;
    el.push(`<text x="${C + (R1 - 12) * Math.cos(am)}" y="${C + (R1 - 12) * Math.sin(am) + 4}" text-anchor="middle" font-size="12" fill="rgba(232,121,249,.8)">${GLYPH[SIGNS[i]]}</text>`);
  }
  (astro.planets || []).forEach(p => {
    const si = SIGNS.indexOf(p.sign);
    if (si < 0) return;
    const lon = si * 30 + p.degree;
    const a = (lon / 360) * 2 * Math.PI - Math.PI / 2;
    const r = R2 - 16;
    el.push(`<text x="${C + r * Math.cos(a)}" y="${C + r * Math.sin(a) + 4}" text-anchor="middle" font-size="13" fill="#f0abfc">${PG[p.planet] || "•"}</text>`);
    el.push(`<line x1="${C + (R2-4) * Math.cos(a)}" y1="${C + (R2-4) * Math.sin(a)}" x2="${C + R2 * Math.cos(a)}" y2="${C + R2 * Math.sin(a)}" stroke="#f0abfc" stroke-width="1.5"/>`);
  });
  el.push(`<text x="${C}" y="${C - 4}" text-anchor="middle" font-size="13" fill="#e2e8f0" font-weight="700">${esc(astro.sun_sign)} ☉</text>`);
  el.push(`<text x="${C}" y="${C + 14}" text-anchor="middle" font-size="10" fill="#94a3b8">${esc(astro.moon_sign)} ☽ · ${esc(astro.ascendant)} ↑</text>`);
  return `<svg viewBox="0 0 260 260" class="w-full max-w-[280px] mx-auto">${el.join("")}</svg>`;
}

// ------------------------------------------------------------------
// Markdown → HTML (small, safe subset for our own generated report)
// ------------------------------------------------------------------

function mdToHTML(md) {
  const lines = md.split("\n");
  let html = "", inList = false;
  const inline = (s) => esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  for (const raw of lines) {
    const l = raw.trimEnd();
    if (/^###\s/.test(l)) { if (inList) { html += "</ul>"; inList = false; } html += `<h3>${inline(l.slice(4))}</h3>`; }
    else if (/^##\s/.test(l)) { if (inList) { html += "</ul>"; inList = false; } html += `<h2>${inline(l.slice(3))}</h2>`; }
    else if (/^#\s/.test(l)) { if (inList) { html += "</ul>"; inList = false; } html += `<h1>${inline(l.slice(2))}</h1>`; }
    else if (/^[-*]\s/.test(l)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inline(l.slice(2))}</li>`; }
    else if (/^\d+\.\s/.test(l)) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inline(l.replace(/^\d+\.\s/, ""))}</li>`; }
    else if (l === "---") { if (inList) { html += "</ul>"; inList = false; } html += "<hr>"; }
    else if (l === "") { if (inList) { html += "</ul>"; inList = false; } }
    else { if (inList) { html += "</ul>"; inList = false; } html += `<p>${inline(l)}</p>`; }
  }
  if (inList) html += "</ul>";
  return html;
}

// ------------------------------------------------------------------
// Dashboard rendering
// ------------------------------------------------------------------

function card(title, accent, bodyHTML, extraClass) {
  return `<div class="enc-card ${extraClass || ""}" style="--accent:${accent}">
    <h3 class="text-sm font-semibold tracking-wide" style="color:${accent}">${esc(title)}</h3>
    <div class="mt-3">${bodyHTML}</div></div>`;
}

function bigNum(v, label, meaning) {
  return `<div class="flex items-baseline gap-3">
    <span class="text-4xl font-extrabold stat-num text-slate-50">${v}</span>
    <div><div class="text-xs text-slate-400">${esc(label)}</div>
    ${meaning ? `<div class="text-xs text-amber-200/90">${esc(meaning)}</div>` : ""}</div></div>`;
}

function renderDashboard(result) {
  const sig = result.signature;
  const e = sig.encoders;
  const res = sig.resonance;
  const fp = sig.fingerprint;
  const name = sig.text;
  const d = $("dashboard");

  // --- Hero + score row ---
  let html = `
  <div class="grid md:grid-cols-5 gap-6 fade-up">
    <div class="glass rounded-2xl p-6 md:col-span-3 flex flex-col sm:flex-row items-center gap-6">
      <div class="w-40 h-40 shrink-0">${fingerprintSVG(fp, 200)}</div>
      <div class="text-center sm:text-left">
        <div class="text-xs uppercase tracking-widest text-slate-500">Identity analysis</div>
        <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-50 mt-1">${esc(name)}</h2>
        <div class="mt-2 text-xs text-slate-400">Fingerprint <code class="text-amber-300">${fp.hash}</code> · ${fp.symmetry}-fold symmetry</div>
        <div class="mt-3 flex flex-wrap gap-2 justify-center sm:justify-start">
          ${Object.keys(e).map(k => `<span class="px-2 py-0.5 rounded-full text-[10px] border" style="color:${ACCENT[k]||"#94a3b8"};border-color:${(ACCENT[k]||"#94a3b8")}44">${k.replace("_"," ")}</span>`).join("")}
        </div>
        <div class="mt-3 text-xs text-slate-500">${sig.dimensions} dimensions computed · deterministic</div>
      </div>
    </div>
    <div class="glass rounded-2xl p-6 md:col-span-2 text-center" id="gauge-card">
      <div class="text-xs uppercase tracking-widest text-slate-500 mb-2">Composite resonance</div>
      ${gaugeSVG(res.score)}
      <div class="grid grid-cols-4 gap-1.5 mt-3 text-[10px] text-slate-400">
        ${Object.entries(res.components).map(([k, v]) => `
          <div><div class="h-1 rounded-full bg-white/10 mb-1"><div class="h-full rounded-full bg-amber-400" style="width:${v*100}%"></div></div>${k.split("_")[0]}</div>`).join("")}
      </div>
    </div>
  </div>`;

  // --- Encoder grid ---
  const p = e.pythagorean, c = e.chaldean, o = e.ordinal, l = e.linguistic,
        b = e.binary_prime, g = e.gematria, iso = e.isopsephy;

  const cards = [];
  cards.push(card("Pythagorean Numerology", ACCENT.pythagorean, `
    ${bigNum(p.master_preserved || p.expression, "Expression", NUM_MEANING[p.master_preserved || p.expression])}
    <div class="grid grid-cols-2 gap-3 mt-4 text-sm">
      <div class="rounded-lg bg-white/5 p-2.5"><div class="text-[10px] text-slate-500">Soul urge</div><b class="stat-num text-lg">${p.soul_urge}</b> <span class="text-[11px] text-slate-400">${NUM_MEANING[p.soul_urge]||""}</span></div>
      <div class="rounded-lg bg-white/5 p-2.5"><div class="text-[10px] text-slate-500">Personality</div><b class="stat-num text-lg">${p.personality}</b> <span class="text-[11px] text-slate-400">${NUM_MEANING[p.personality]||""}</span></div>
    </div>
    <p class="text-xs text-slate-400 mt-3">The expression is the name's operating system; soul urge is what it wants (vowels); personality is the surface strangers meet (consonants).${p.master_preserved ? " Master number preserved — high-voltage variant." : ""}</p>
    ${meter("Raw total", p.total, 200, ACCENT.pythagorean)}`));

  cards.push(card("Chaldean Numerology", ACCENT.chaldean, `
    ${bigNum(c.name_number, "Name number", NUM_MEANING[c.name_number])}
    <div class="mt-4 rounded-lg bg-white/5 p-2.5 text-sm"><div class="text-[10px] text-slate-500">Compound (occult) number</div>
      <b class="stat-num text-lg">${c.compound_number}</b></div>
    <p class="text-xs text-slate-400 mt-3">The Babylonian vibration table — no letter maps to the sacred 9. The compound number carries the karmic circumstance behind the visible digit.</p>`));

  cards.push(card("Ordinal Ciphers", ACCENT.ordinal, `
    <div class="grid grid-cols-3 gap-2 text-center">
      <div class="rounded-lg bg-white/5 p-2.5"><div class="text-[10px] text-slate-500">A1Z26</div><b class="stat-num text-xl">${o.ordinal_total}</b><div class="text-[10px] text-slate-400">→ ${o.ordinal_reduced}</div></div>
      <div class="rounded-lg bg-white/5 p-2.5"><div class="text-[10px] text-slate-500">Reverse</div><b class="stat-num text-xl">${o.reverse}</b><div class="text-[10px] text-slate-400">→ ${o.reverse_reduced}</div></div>
      <div class="rounded-lg bg-white/5 p-2.5"><div class="text-[10px] text-slate-500">Reduced</div><b class="stat-num text-xl">${o.reduced_total}</b><div class="text-[10px] text-slate-400">per-letter</div></div>
    </div>
    <p class="text-xs text-slate-400 mt-3">${o.ordinal_total < o.reverse ? "Letters cluster toward the front of the alphabet — a primary, label-like signature." : "Letters cluster toward the back of the alphabet — an accumulated, pressure-bearing signature."}</p>`));

  cards.push(card("Linguistic Analysis", ACCENT.linguistic, `
    ${meter("Shannon entropy", l.shannon_entropy, l.max_possible_entropy || 5, ACCENT.linguistic, " bits")}
    ${meter("Entropy ratio", l.entropy_ratio * 100, 100, ACCENT.linguistic, "%")}
    <div class="mt-4">${pieSVG(Math.round(l.vowel_ratio * l.letter_count), l.letter_count - Math.round(l.vowel_ratio * l.letter_count), "#fbbf24", "#60a5fa", "Vowels", "Consonants")}</div>
    <div class="mt-3 flex flex-wrap gap-2 text-[11px] text-slate-300">
      <span class="px-2 py-1 rounded bg-white/5">${l.syllable_estimate} syllable${l.syllable_estimate !== 1 ? "s" : ""}</span>
      <span class="px-2 py-1 rounded bg-white/5">${l.plosive_count} plosives</span>
      <span class="px-2 py-1 rounded bg-white/5">${l.fricative_count} fricatives</span>
      <span class="px-2 py-1 rounded bg-white/5">${l.nasal_count} nasals</span>
      ${l.is_palindrome ? '<span class="px-2 py-1 rounded bg-amber-400/20 text-amber-300">palindrome!</span>' : ""}
    </div>`));

  const polNorm = (b.vowel_power - b.consonant_power) / ((b.vowel_power + b.consonant_power) || 1);
  cards.push(card("Binary / Prime Encoding", ACCENT.binary_prime, `
    <div class="flex flex-wrap gap-1 mb-3">${[...b.binary_string].map(bit =>
      `<span class="w-5 h-7 rounded flex items-center justify-center text-[11px] font-bold ${bit === "1" ? "bg-teal-400/20 text-teal-300" : "bg-amber-400/25 text-amber-300"}">${bit}</span>`).join("")}</div>
    <div class="text-[10px] text-slate-500 mb-3">vowel = 0 (gold) · consonant = 1 (teal)</div>
    <div class="relative h-2 rounded-full bg-gradient-to-r from-amber-400/60 via-white/10 to-teal-400/60">
      <div class="absolute -top-1 w-4 h-4 rounded-full bg-slate-100 border-2 border-slate-800" style="left:calc(${(50 + polNorm * 50).toFixed(1)}% - 8px)"></div>
    </div>
    <div class="flex justify-between text-[10px] text-slate-500 mt-1"><span>vowel pole</span><span>consonant pole</span></div>
    ${meter("Prime total (A=2…Z=101)", b.prime_total, 1000, ACCENT.binary_prime)}
    ${meter("Pattern entropy", b.binary_entropy, 1, ACCENT.binary_prime)}`));

  cards.push(card("Hebrew Gematria", ACCENT.gematria, `
    <div class="flex flex-wrap gap-1.5 mb-3">${(g.letter_values || []).slice(0, 24).map(lv =>
      `<span class="px-1.5 py-1 rounded bg-white/5 text-center"><span class="block text-[13px] text-violet-300 font-semibold">${esc(lv.char)}</span><span class="block text-[9px] text-slate-500 stat-num">${lv.absolute ?? lv.value ?? ""}</span></span>`).join("")}</div>
    <div class="grid grid-cols-3 gap-2 text-center text-sm">
      <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Absolute</div><b class="stat-num">${g.absolute_total}</b><div class="text-[10px] text-slate-400">→ ${g.absolute_reduced}</div></div>
      <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Ordinal</div><b class="stat-num">${g.ordinal_total}</b><div class="text-[10px] text-slate-400">→ ${g.ordinal_reduced}</div></div>
      <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Katan</div><b class="stat-num">${g.reduced_total}</b></div>
    </div>`));

  const chain = (iso.digital_root_chain || []).map(String);
  cards.push(card("Greek Isopsephy", ACCENT.isopsephy, `
    <div class="flex flex-wrap gap-1.5 mb-3">${(iso.greek_correspondence || []).slice(0, 24).map(gc =>
      `<span class="px-1.5 py-1 rounded bg-white/5 text-center"><span class="block text-[13px] text-violet-200 font-semibold">${esc(gc.greek)}</span><span class="block text-[9px] text-slate-500">${esc(gc.letter)}·${gc.value}</span></span>`).join("")}</div>
    <div class="flex items-center gap-2 flex-wrap text-lg font-bold stat-num">
      ${chain.map((v, i) => `<span class="${i === chain.length - 1 ? "text-amber-300 text-2xl" : "text-slate-300"}">${v}</span>${i < chain.length - 1 ? '<span class="text-slate-600">→</span>' : ""}`).join("")}
    </div>
    <p class="text-xs text-slate-400 mt-2">The digital-root cascade — each arrow is one act of distillation toward the name's terminal essence.</p>`));

  // Keep extension conventions visible and separate from the resonance score.
  const extensions = Object.values(e).filter(extension =>
    extension && extension.system && extension.data && extension.provenance
  );
  if (extensions.length) {
    const extensionRows = extensions.map(extension => {
      const convention = extension.provenance.convention || "named convention";
      const sourceIds = (extension.provenance.source_ids || []).join(", ");
      const completeData = esc(JSON.stringify(extension.data, null, 2));
      return `<details class="rounded-lg bg-white/5 px-3 py-2">
        <summary class="cursor-pointer text-xs text-slate-200 flex justify-between gap-2">
          <span>${esc(extension.system.replaceAll("_", " "))}</span>
          <span class="text-[10px] text-slate-500">${esc(extension.phase)} · ${esc(extension.interpretation_level)}</span>
        </summary>
        <p class="mt-1 text-[10px] text-slate-500">Convention: ${esc(convention)}</p>
        <p class="mt-1 text-[10px] text-slate-500">Sources: ${esc(sourceIds)}</p>
        <pre class="mt-2 whitespace-pre-wrap break-words text-[11px] leading-relaxed text-slate-300">${completeData}</pre>
      </details>`;
    }).join("");
    cards.push(card("Expanded Symbolic Systems", "#a78bfa", `
      <p class="text-xs text-slate-400 mb-3">${extensions.length} provenance-aware symbolic extensions. Each reports its selected convention and epistemic level; none changes the composite resonance score.</p>
      <div class="space-y-1.5">${extensionRows}</div>`, "md:col-span-2"));
  }

  // Astrology
  const astro = e.astrology;
  if (astro && !astro.error && astro.sun_sign) {
    cards.push(card("Astrology — Natal Chart", ACCENT.astrology, `
      ${natalWheelSVG(astro)}
      <div class="grid grid-cols-3 gap-2 text-center text-xs mt-3">
        <div class="rounded-lg bg-white/5 p-2">☉ <b>${esc(astro.sun_sign)}</b><div class="text-[10px] text-slate-500">Sun</div></div>
        <div class="rounded-lg bg-white/5 p-2">☽ <b>${esc(astro.moon_sign)}</b><div class="text-[10px] text-slate-500">Moon</div></div>
        <div class="rounded-lg bg-white/5 p-2">↑ <b>${esc(astro.ascendant)}</b><div class="text-[10px] text-slate-500">Rising</div></div>
      </div>
      <div class="mt-3 text-xs text-slate-300 space-y-1">
        <div>Dominant element: <b style="color:${ACCENT.astrology}">${esc(astro.dominant_element || "—")}</b> · modality: <b>${esc(astro.dominant_modality || "—")}</b></div>
        <div>Lunar phase: <b>${esc(astro.lunar_phase || "—")}</b> (${astro.is_waxing ? "waxing" : "waning"}) · chart ruler: <b>${esc(astro.chart_ruler || "—")}</b></div>
      </div>
      <div class="mt-3 space-y-1">${(astro.aspects || []).slice(0, 5).map(a =>
        `<div class="text-[11px] text-slate-400 flex justify-between"><span>${esc(a.planets[0])} <span class="text-fuchsia-300">${esc(a.type)}</span> ${esc(a.planets[1])}</span><span class="stat-num">${a.orb}°${a.exact ? " ✦" : ""}</span></div>`).join("")}</div>
      <p class="text-[10px] text-slate-500 mt-2">Swiss Ephemeris, tropical zodiac · confidence ${astro.confidence}</p>`, "md:col-span-2"));
  }

  // Human Design
  const hd = e.human_design;
  if (hd && !hd.error && hd.type) {
    const gateSet = new Set(hd.gates || []);
    cards.push(card("Human Design", ACCENT.human_design, `
      <div class="flex items-baseline gap-3"><span class="text-2xl font-extrabold text-emerald-300">${esc(hd.type)}</span>
        <span class="text-xs text-slate-400">profile ${(hd.profile || []).join("/")}</span></div>
      <div class="grid grid-cols-2 gap-2 mt-3 text-xs">
        <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Strategy</div><b>${esc(hd.strategy || "—")}</b></div>
        <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Authority</div><b>${esc(hd.authority || "—")}</b></div>
        <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Not-self theme</div><b>${esc(hd.not_self_theme || "—")}</b></div>
        <div class="rounded-lg bg-white/5 p-2"><div class="text-[10px] text-slate-500">Signature</div><b>${esc(hd.signature || "—")}</b></div>
      </div>
      <div class="mt-3"><div class="text-[10px] text-slate-500 mb-1.5">64-gate activation map</div>
        <div class="grid grid-cols-16 gap-0.5" style="grid-template-columns:repeat(16,minmax(0,1fr))">${Array.from({length: 64}, (_, i) =>
          `<div class="aspect-square rounded-[3px] flex items-center justify-center text-[7px] ${gateSet.has(i+1) ? "bg-emerald-400/70 text-emerald-950 font-bold" : "bg-white/5 text-slate-600"}">${i+1}</div>`).join("")}</div></div>
      ${(hd.channels || []).length ? `<div class="mt-3 flex flex-wrap gap-1.5">${hd.channels.map(ch =>
        `<span class="px-2 py-0.5 rounded-full text-[10px] bg-emerald-400/10 text-emerald-300 border border-emerald-400/30">${esc(ch.name)} ${ch.gates[0]}–${ch.gates[1]}</span>`).join("")}</div>` : ""}`, "md:col-span-2"));
  }

  // Psychology
  if (STATE.psychology) {
    const ps = STATE.psychology;
    let body = "";
    if (ps.big_five) {
      body += radarSVG(B5.map(([k]) => ps.big_five[k] ?? 0.5), B5.map(([,l]) => l.slice(0,5)), ACCENT.psychology);
    }
    if (ps.mbti) {
      const stack = MBTI_STACK[ps.mbti] || [];
      body += `<div class="mt-3 text-center"><span class="text-xl font-extrabold text-rose-300">${esc(ps.mbti)}</span>
        <div class="flex justify-center gap-1.5 mt-1">${stack.map((f, i) =>
          `<span class="px-2 py-1 rounded bg-white/5 text-[11px] ${i === 0 ? "text-rose-300 font-bold" : "text-slate-400"}">${f}</span>`).join("")}</div></div>`;
    }
    if (ps.enneagram && ps.enneagram.type) {
      body += `<div class="mt-3 text-center text-sm text-slate-300">Enneagram <b class="text-rose-300">Type ${ps.enneagram.type}${ps.enneagram.wing ? "w" + ps.enneagram.wing : ""}</b>${ps.attachment ? ` · ${esc(ps.attachment)} attachment` : ""}</div>`;
    }
    cards.push(card("Psychology (self-reported)", ACCENT.psychology, body || "<p class='text-xs text-slate-500'>No assessments supplied.</p>"));
  }

  html += `<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 mt-6 fade-up-1">${cards.join("")}</div>`;

  // --- Cross-encoder + narrative row ---
  html += `<div class="grid lg:grid-cols-2 gap-6 mt-6 fade-up-2">
    <div class="glass rounded-2xl p-6">
      <h3 class="text-sm font-semibold text-violet-300 tracking-wide">Cross-Encoder Agreement Heatmap</h3>
      <div class="mt-4">${heatmapHTML(result.correlations)}</div>
    </div>
    <div class="glass rounded-2xl p-6">
      <h3 class="text-sm font-semibold text-amber-300 tracking-wide">Composite Narrative</h3>
      <div class="mt-3 text-sm leading-relaxed text-slate-300 space-y-3">${
        sig.snapshot.narrative.split("\n\n").map(par => `<p>${esc(par)}</p>`).join("")
      }</div>
      ${sig.snapshot.highlights.length ? `<div class="mt-3 flex flex-wrap gap-2">${sig.snapshot.highlights.map(h =>
        `<span class="px-2.5 py-1 rounded-full text-[11px] bg-amber-400/10 text-amber-200 border border-amber-400/25">${esc(h)}</span>`).join("")}</div>` : ""}
    </div>
  </div>`;

  // --- Comparison section ---
  const maxSim = Math.max(...result.comparisons.map(cm => cm.similarity), 0.01);
  html += `<div class="glass rounded-2xl p-6 mt-6 fade-up-2">
    <h3 class="text-sm font-semibold text-sky-300 tracking-wide">Resonance With the Reference Population</h3>
    <p class="text-xs text-slate-500 mt-1">Cosine similarity in the shared 14-dimensional feature space.</p>
    <div class="mt-4 space-y-2">${result.comparisons.slice(0, 8).map(cm => `
      <div class="flex items-center gap-3 text-sm">
        <span class="w-36 sm:w-48 truncate text-slate-300">${esc(cm.text)}</span>
        <div class="flex-1 h-2 rounded-full bg-white/5"><div class="h-full rounded-full bg-gradient-to-r from-sky-500 to-fuchsia-400" style="width:${(cm.similarity / maxSim * 100).toFixed(1)}%"></div></div>
        <span class="stat-num text-xs text-slate-400 w-12 text-right">${(cm.similarity * 100).toFixed(1)}%</span>
      </div>`).join("")}</div>
  </div>`;

  // --- Report section (paywalled) ---
  html += `<div class="glass rounded-2xl p-6 sm:p-8 mt-6 fade-up-3" id="report-card">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h3 class="text-lg font-bold text-slate-50">The Full Written Analysis</h3>
        <p class="text-xs text-slate-400 mt-0.5">${result.report.word_count.toLocaleString()} words · ${result.report.sections.length} sections · deterministic</p>
      </div>
      <div class="flex gap-2" id="report-actions"></div>
    </div>
    <div class="relative mt-5">
      <div id="report-print-area"><div class="report-body" id="report-body"></div></div>
      <div id="report-overlay" class="absolute inset-0 hidden items-end justify-center bg-gradient-to-b from-transparent via-[#07070d]/60 to-[#07070d] pb-10">
        <button onclick="app.openPaywall()" class="px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-bold text-lg shadow-2xl shadow-indigo-500/40 hover:scale-[1.03] transition">
          $10 — Unlock Full Analysis
        </button>
      </div>
    </div>
  </div>`;

  d.innerHTML = html;
  d.classList.remove("hidden");
  renderReport();
  animateGauge($("gauge-card"), res.score);
  d.scrollIntoView({behavior: "smooth", block: "start"});
}

function renderReport() {
  const r = STATE.result.report;
  const body = $("report-body");
  const overlay = $("report-overlay");
  const actions = $("report-actions");
  if (STATE.paid) {
    body.innerHTML = mdToHTML(r.markdown);
    body.classList.remove("locked-blur");
    overlay.classList.add("hidden"); overlay.classList.remove("flex");
    actions.innerHTML = `
      <button onclick="app.downloadReport()" class="px-3.5 py-2 rounded-lg text-xs font-semibold bg-emerald-400/10 text-emerald-300 border border-emerald-400/30 hover:bg-emerald-400/20 transition">⬇ Download .md</button>
      <button onclick="window.print()" class="px-3.5 py-2 rounded-lg text-xs font-semibold bg-white/5 text-slate-300 border border-white/15 hover:bg-white/10 transition">🖨 Save as PDF</button>`;
  } else {
    // Free preview: executive summary only, then blur teaser
    const teaserEnd = r.markdown.indexOf("## 2.");
    const teaser = teaserEnd > 0 ? r.markdown.slice(0, teaserEnd) : r.markdown.slice(0, 1500);
    body.innerHTML = mdToHTML(teaser) +
      `<div class="locked-blur">${mdToHTML(r.markdown.slice(teaserEnd, teaserEnd + 2200))}</div>`;
    overlay.classList.remove("hidden"); overlay.classList.add("flex");
    actions.innerHTML = `<span class="px-3 py-2 rounded-lg text-xs bg-white/5 text-slate-400 border border-white/10">🔒 Sections 2–10 locked</span>`;
  }
}

// ------------------------------------------------------------------
// App controller
// ------------------------------------------------------------------

const PROCESSING_STEPS = [
  "Normalizing identity string…", "Pythagorean expression, soul urge, personality…",
  "Chaldean vibration table…", "Ordinal ciphers (A1Z26 / reverse / reduced)…",
  "Shannon entropy & phonetic profile…", "Prime-index & binary polarity…",
  "Hebrew Gematria transliteration…", "Greek Isopsephy cascade…",
  "Swiss Ephemeris planetary positions…", "Human Design gates & channels…",
  "25 provenance-aware symbolic extensions…", "Composite resonance & fingerprint…", "Writing your report…",
];

const app = {
  scrollToForm() { $("form-section").scrollIntoView({behavior: "smooth"}); $("name").focus({preventScroll: true}); },

  toggleSection(which) {
    const on = $(`${which}-enabled`).checked;
    const el = $(`${which}-fields`);
    el.classList.toggle("opacity-40", !on);
    el.classList.toggle("pointer-events-none", !on);
  },

  reset() {
    STATE = {result: null, paid: false, psychology: null};
    $("dashboard").classList.add("hidden");
    $("landing").classList.remove("hidden");
    $("form-section").classList.remove("hidden");
    window.scrollTo({top: 0, behavior: "smooth"});
  },

  async submit(ev) {
    ev.preventDefault();
    const errEl = $("form-error");
    errEl.classList.add("hidden");
    const payload = {name: $("name").value.trim()};

    if ($("birth-enabled").checked && $("b-date").value) {
      const [y, m, day] = $("b-date").value.split("-").map(Number);
      const t = $("b-time").value || "12:00";
      const [hh, mm] = t.split(":").map(Number);
      payload.birth = {
        year: y, month: m, day: day, hour: hh, minute: mm,
        timezone_offset: parseFloat($("b-tz").value || "0"),
        location: $("b-loc").value,
      };
      if ($("b-lat").value && $("b-lon").value) {
        payload.birth.lat = parseFloat($("b-lat").value);
        payload.birth.lon = parseFloat($("b-lon").value);
      }
    }
    if ($("psych-enabled").checked) {
      const psych = {};
      const bf = {};
      let any = false;
      B5.forEach(([k]) => { const v = $(`bf-${k}`); if (v) { bf[k] = parseInt(v.value, 10) / 100; any = true; } });
      if (any) psych.big_five = bf;
      if ($("p-mbti").value) psych.mbti = $("p-mbti").value;
      if ($("p-enne").value) psych.enneagram = {type: parseInt($("p-enne").value, 10),
        wing: $("p-wing").value ? parseInt($("p-wing").value, 10) : null};
      if ($("p-attach").value) psych.attachment = $("p-attach").value;
      if (Object.keys(psych).length) payload.psychology = psych;
      STATE.psychology = payload.psychology || null;
    } else {
      STATE.psychology = null;
    }

    // Processing animation
    $("landing").classList.add("hidden");
    $("form-section").classList.add("hidden");
    $("dashboard").classList.add("hidden");
    $("processing").classList.remove("hidden");
    let step = 0;
    const stepTimer = setInterval(() => {
      step = (step + 1) % PROCESSING_STEPS.length;
      $("processing-step").textContent = PROCESSING_STEPS[step];
    }, 380);
    const started = Date.now();

    try {
      const resp = await fetch("/api/analyze", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Analysis failed");
      // Let the animation play at least ~2.2s so it feels substantive
      const wait = Math.max(0, 2200 - (Date.now() - started));
      await new Promise(res => setTimeout(res, wait));
      STATE.result = data;
      STATE.paid = false;
      renderDashboard(data);
    } catch (err) {
      $("form-section").classList.remove("hidden");
      errEl.textContent = err.message;
      errEl.classList.remove("hidden");
    } finally {
      clearInterval(stepTimer);
      $("processing").classList.add("hidden");
    }
  },

  openPaywall() {
    $("paywall").classList.remove("hidden");
    $("paywall").classList.add("flex");
    $("cc-num").focus();
  },
  closePaywall() {
    $("paywall").classList.add("hidden");
    $("paywall").classList.remove("flex");
  },

  pay(ev) {
    ev.preventDefault();
    const num = $("cc-num").value.replace(/\s/g, "");
    const err = $("pay-error");
    if (!/^\d{13,19}$/.test(num)) {
      err.textContent = "Enter a valid card number (test mode: 4242 4242 4242 4242).";
      err.classList.remove("hidden");
      return;
    }
    err.classList.add("hidden");
    const btn = $("pay-btn");
    btn.disabled = true;
    btn.textContent = "Processing payment…";
    setTimeout(() => {
      btn.textContent = "✓ Payment confirmed";
      setTimeout(() => {
        this.closePaywall();
        btn.disabled = false;
        btn.textContent = "$10 — Unlock Full Analysis";
        STATE.paid = true;
        renderReport();
        $("report-card").scrollIntoView({behavior: "smooth"});
      }, 700);
    }, 1400);
  },

  downloadReport() {
    const r = STATE.result.report;
    const name = STATE.result.signature.text.replace(/[^a-z0-9]+/gi, "_").toLowerCase();
    const blob = new Blob([r.markdown], {type: "text/markdown"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `identity_resonance_${name}.md`;
    a.click();
    URL.revokeObjectURL(a.href);
  },
};
window.app = app;

// ------------------------------------------------------------------
// Init
// ------------------------------------------------------------------

function init() {
  // Decorative glyphs
  $("logo-glyph").innerHTML = decorativeFP(7, 60);
  $("hero-glyph").innerHTML = decorativeFP(42, 240);

  // Big Five sliders
  $("bigfive-sliders").innerHTML = B5.map(([k, label]) => `
    <div><div class="flex justify-between text-xs text-slate-400 mb-1"><span>${label}</span><span id="bf-${k}-val" class="stat-num">50</span></div>
    <input type="range" id="bf-${k}" min="0" max="100" value="50" class="w-full accent-rose-400"
      oninput="document.getElementById('bf-${k}-val').textContent=this.value"></div>`).join("");

  // MBTI / Enneagram selects
  $("p-mbti").innerHTML += MBTI_TYPES.map(t => `<option>${t}</option>`).join("");
  $("p-enne").innerHTML += Array.from({length: 9}, (_, i) => `<option>${i + 1}</option>`).join("");
  $("p-wing").innerHTML += Array.from({length: 9}, (_, i) => `<option>${i + 1}</option>`).join("");

  // Reference-population gallery
  fetch("/api/defaults").then(r => r.json()).then(d => {
    const picks = (d.identities || []).filter(x => x.fingerprint)
      .sort((a, b) => b.resonance - a.resonance).slice(0, 10);
    $("gallery").innerHTML = picks.map(p => `
      <div class="glass rounded-xl p-3 text-center hover:scale-[1.03] transition cursor-default">
        <div class="w-16 h-16 mx-auto">${fingerprintSVG(p.fingerprint, 100)}</div>
        <div class="mt-2 text-[11px] text-slate-300 truncate">${esc(p.text)}</div>
        <div class="text-[10px] text-amber-300/80 stat-num">${p.resonance}</div>
      </div>`).join("");
  }).catch(() => {});
}

document.addEventListener("DOMContentLoaded", init);
})();
