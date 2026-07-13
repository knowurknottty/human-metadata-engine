/* Human Metadata Engine — accessible editorial client for the v0.7 public API. */

(function () {
"use strict";

const MBTI_TYPES = ["INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
                    "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"];
const ENNEAGRAM_WINGS = {
  1:[9,2],2:[1,3],3:[2,4],4:[3,5],5:[4,6],6:[5,7],7:[6,8],8:[7,9],9:[8,1],
};
const B5 = [
  ["openness","Openness"],["conscientiousness","Conscientiousness"],
  ["extraversion","Extraversion"],["agreeableness","Agreeableness"],
  ["neuroticism","Neuroticism"],
];
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

let STATE;

function updateWingOptions() {
  const core = parseInt($("p-enne").value, 10);
  const wing = $("p-wing");
  const warning = $("p-wing-warning");
  const current = wing.value;
  if (!core || !ENNEAGRAM_WINGS[core]) {
    wing.innerHTML = '<option value="">Select a core type first</option>';
    wing.disabled = true;
    if (warning) warning.hidden = true;
    return;
  }
  const options = ['<option value="">Not assessed</option>']
    .concat(ENNEAGRAM_WINGS[core].map(value => `<option value="${value}">${core}w${value}</option>`));
  wing.innerHTML = options.join("");
  wing.disabled = false;
  if (ENNEAGRAM_WINGS[core].map(String).includes(current)) wing.value = current;
  else if (current) {
    wing.value = "";
    if (warning) {
      warning.textContent = `Wing reset: ${core} can only use ${ENNEAGRAM_WINGS[core].join(" or ")}.`;
      warning.hidden = false;
    }
  }
}

function updateSecondaryWarning() {
  const core = $("p-enne").value;
  const secondary = $("p-secondary").value;
  const warning = $("p-secondary-warning");
  if (warning && core && secondary && secondary !== "unknown" && core === secondary) {
    warning.textContent = "Same as the core type: this adds little additional information.";
    warning.hidden = false;
  } else if (warning) {
    warning.hidden = true;
  }
}

function clientProfileSections(psychology) {
  const statusLabels = {validated:"validated", structured:"structured assessment", self_identified:"self-identified", provisional:"provisional", unknown:"unknown status"};
  const statuses = psychology.assessment_status || {};
  const sections = {core_cognition_motivation: [], relational_patterns: [], self_regulation: []};
  const add = (section, field, label, value) => {
    if (value === null || value === undefined || value === "" || value === "unknown") return;
    const status = statuses[field]?.status || "unknown";
    sections[section].push({field, label, value: String(value), status, status_label: statusLabels[status] || status});
  };
  if (psychology.mbti) add("core_cognition_motivation", "mbti", "MBTI", psychology.mbti);
  const enne = psychology.enneagram || {};
  if (enne.type) {
    add("core_cognition_motivation", "enneagram", "Enneagram", `Type ${enne.type}`);
    if (enne.wing) add("core_cognition_motivation", "wing", "Wing", `${enne.type}w${enne.wing}`);
  }
  if (psychology.secondary_enneagram_influence) add("core_cognition_motivation", "secondary_enneagram_influence", "Secondary pattern", `Type ${psychology.secondary_enneagram_influence} influence`);
  if (psychology.instinctual_variant) add("core_cognition_motivation", "instinctual_variant", "Instinctual variant", psychology.instinctual_variant.replaceAll("_", "/"));
  const attachment = psychology.attachment || psychology.relational_patterns?.attachment_style;
  if (attachment) add("relational_patterns", "attachment", "Attachment style", attachment.replaceAll("_", "-"));
  if (psychology.conflict_style) add("self_regulation", "conflict_style", "Conflict style", psychology.conflict_style.replaceAll("_", "-"));
  return sections;
}

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

function compactLabel(value) {
  return String(value || "—").replaceAll("_", " ").replace(/\b\w/g, char => char.toUpperCase());
}

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

function normalizeBirthDateInput(value) {
  const digits = String(value || "").replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 4) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 4)}-${digits.slice(4)}`;
  return `${digits.slice(0, 4)}-${digits.slice(4, 6)}-${digits.slice(6)}`;
}

function parseBirthDateInput(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value || "").trim());
  if (!match) return null;
  const year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
  const check = new Date(Date.UTC(year, month - 1, day));
  if (check.getUTCFullYear() !== year || check.getUTCMonth() !== month - 1 || check.getUTCDate() !== day) return null;
  return {year, month, day};
}

function apiErrorField(data) {
  const code = data?.code || "";
  const message = String(data?.message || data?.error || "").toLowerCase();
  if (code.includes("location") || code === "invalid_timezone") return $("b-zone").value ? "b-zone" : "b-loc";
  if (message.includes("birth") || message.includes("calendar date")) return "b-date";
  if (message.includes("alias")) return "aliases";
  if (message.includes("name")) return "name";
  return null;
}

const app = {};
window.app = app;

// v0.8 editorial workflow
// ------------------------------------------------------------------

const TYPE_LABELS = {
  mathematical: "Mathematical calculation",
  astronomical: "Astronomical calculation",
  user_reported: "Supplied by you",
  traditional_symbolic: "Traditional interpretation",
  heuristic: "Rule-based estimate",
  speculative_synthesis: "Interpretive synthesis",
};

const ERROR_COPY = {
  invalid_name: "Enter a name using ordinary text, without markup or control characters.",
  invalid_location_query: "Enter a city, town, or postal code for the birthplace.",
  location_not_found: "We could not find that birthplace. Add a state, region, or country and try again.",
  location_provider_unavailable: "The location provider could not be reached. Try again, or use Advanced birth settings if you know the timezone and coordinates.",
  malformed_location_provider_response: "We found the place, but its timezone information was incomplete. Try a nearby city or enter the timezone in Advanced birth settings.",
  invalid_timezone: "The timezone information conflicts with the birthplace. Check Advanced birth settings or clear them and try again.",
  rate_limited: "Too many analyses were requested in a short time. Wait a moment and try again.",
  service_busy: "The analysis service is busy. Your entries are still here; try again shortly.",
  payload_too_large: "The submitted information is too long. Shorten the name or optional entries and try again.",
  internal_error: "The report could not be created because the server encountered an unexpected problem. Your entries are still here.",
};

const STATUS_FIELDS = [
  ["mbti", "p-mbti", "Personality type"], ["enneagram", "p-enne", "Enneagram"],
  ["wing", "p-wing", "Enneagram wing"], ["secondary_enneagram_influence", "p-secondary", "Secondary pattern"],
  ["instinctual_variant", "p-instinct", "Instinctual pattern"], ["attachment", "p-attach", "Relationship style"],
  ["conflict_style", "p-conflict", "Conflict style"],
];

function newEditorialState() {
  return {
    result: null, psychology: null, customSigil: null, mode: "magic", requestPayload: null,
    switchingMode: false, aliases: [], locationChoices: [], selectedLocation: null,
    submitting: false, generatedAt: null,
  };
}

function typeLabel(category) {
  return TYPE_LABELS[category] || compactLabel(category || "configured method");
}

function formatDate(parts) {
  if (!parts) return "Not included";
  return `${parts.year}-${String(parts.month).padStart(2, "0")}-${String(parts.day).padStart(2, "0")}`;
}

function setSurface(id, visible) {
  const element = $(id);
  if (element) element.hidden = !visible;
}

function updateReviewSummary() {
  const target = $("review-summary");
  if (!target) return;
  const name = $("name").value.trim() || "Not entered";
  const birthOn = $("birth-enabled").checked;
  const unknownTime = birthOn && $("b-time-unknown").checked;
  const date = birthOn ? ($("b-date").value || "Not entered") : "Not included";
  const time = !birthOn ? "Not included" : unknownTime ? "Unknown" : ($("b-time").value || "Not entered");
  const location = birthOn ? ($("b-loc").value.trim() || "Not entered") : "Not included";
  let contextCount = 0;
  if ($("psych-enabled").checked) {
    ["p-mbti", "p-enne", "p-secondary", "p-instinct", "p-attach", "p-conflict"].forEach(id => {
      if ($(id).value && $(id).value !== "unknown") contextCount += 1;
    });
    B5.forEach(([key]) => { if ($(`bf-${key}`)?.dataset.touched === "true") contextCount += 1; });
  }
  const rows = [
    ["Name", name], ["Other names", STATE.aliases.length ? STATE.aliases.join(", ") : "None"],
    ["Birth date", date], ["Birth time", time], ["Birthplace", location],
    ["Personal context", contextCount ? `${contextCount} supplied field${contextCount === 1 ? "" : "s"}` : "Not included"],
  ];
  target.innerHTML = rows.map(([term, value]) => `<div><dt>${esc(term)}</dt><dd>${esc(value)}</dd></div>`).join("");
}

function syncAliasField() {
  $("aliases").value = STATE.aliases.join("\n");
  $("alias-list").innerHTML = STATE.aliases.map((alias, index) => `<span class="alias-token"><span>${esc(alias)}</span><button type="button" onclick="app.removeAlias(${index})" aria-label="Remove ${esc(alias)}">×</button></span>`).join("");
  updateReviewSummary();
}

function addAliasValue(raw) {
  const alias = String(raw || "").replace(/\s+/g, " ").trim();
  if (!alias) return false;
  const normalized = alias.toLocaleLowerCase();
  const primary = $("name").value.replace(/\s+/g, " ").trim().toLocaleLowerCase();
  if (alias.length > 120) {
    showEditorialError("Keep each other name to 120 characters or fewer.", "alias-input", "invalid_alias");
    return false;
  }
  if (normalized === primary) {
    showEditorialError("An other name must be different from the primary name.", "alias-input", "duplicate_alias");
    return false;
  }
  if (STATE.aliases.some(value => value.toLocaleLowerCase() === normalized)) {
    showEditorialError("That other name has already been added.", "alias-input", "duplicate_alias");
    return false;
  }
  if (STATE.aliases.length >= 12) {
    showEditorialError("You can add up to 12 other names.", "alias-input", "too_many_aliases");
    return false;
  }
  STATE.aliases.push(alias);
  $("alias-input").value = "";
  $("alias-status").textContent = `${alias} added.`;
  syncAliasField();
  return true;
}

function clearEditorialErrors() {
  const summary = $("form-error-summary");
  summary.hidden = true;
  $("form-error").textContent = "";
  $("form-error-technical").hidden = true;
  $("form-error-code").textContent = "";
  document.querySelectorAll(".generated-inline-error").forEach(error => error.remove());
  document.querySelectorAll('[aria-invalid="true"]').forEach(control => {
    control.removeAttribute("aria-invalid");
    const values = (control.getAttribute("aria-describedby") || "").split(/\s+/).filter(value => value && value !== "form-error" && !value.includes("-inline-error-"));
    if (values.length) control.setAttribute("aria-describedby", values.join(" "));
    else control.removeAttribute("aria-describedby");
  });
}

function showEditorialErrors(errors, code) {
  const summary = $("form-error-summary");
  $("form-error").innerHTML = errors.length === 1
    ? `<p>${esc(errors[0].message)}</p>`
    : `<p>Correct these ${errors.length} items:</p><ul>${errors.map(error => `<li>${esc(error.message)}</li>`).join("")}</ul>`;
  summary.hidden = false;
  if (code) {
    $("form-error-code").textContent = code;
    $("form-error-technical").hidden = false;
  }
  errors.forEach((error, index) => {
    const control = error.fieldId ? $(error.fieldId) : null;
    if (!control) return;
    control.setAttribute("aria-invalid", "true");
    const describedBy = new Set((control.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
    describedBy.add("form-error");
    const inlineId = `${error.fieldId}-inline-error-${index}`;
    describedBy.add(inlineId);
    control.setAttribute("aria-describedby", Array.from(describedBy).join(" "));
    const inline = document.createElement("p");
    inline.id = inlineId;
    inline.className = "inline-error generated-inline-error";
    inline.textContent = error.message;
    control.insertAdjacentElement("afterend", inline);
  });
  const firstControl = errors[0]?.fieldId ? $(errors[0].fieldId) : null;
  if (firstControl) firstControl.focus();
  else summary.focus();
}

function showEditorialError(message, fieldId, code) {
  showEditorialErrors([{message, fieldId}], code);
}

function collectEditorialValidationErrors() {
  const errors = [];
  const name = $("name").value.replace(/\s+/g, " ").trim();
  if (!name) errors.push({message: "Enter the full birth or legal name to analyze.", fieldId: "name"});
  else if (/[<>]/.test(name) || Array.from(name).some(char => /[\u0000-\u001f\u007f]/.test(char))) errors.push({message: ERROR_COPY.invalid_name, fieldId: "name"});
  if ($("birth-enabled").checked) {
    const dateParts = parseBirthDateInput($("b-date").value);
    if (!dateParts) errors.push({message: "Enter a real birth date in YYYY-MM-DD format.", fieldId: "b-date"});
    else {
      const enteredDate = new Date(Date.UTC(dateParts.year, dateParts.month - 1, dateParts.day));
      const today = new Date();
      if (enteredDate > new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()))) errors.push({message: "Birth date cannot be in the future.", fieldId: "b-date"});
    }
    if (!$("b-time-unknown").checked && !$("b-time").value) errors.push({message: "Enter the local birth time, or choose ‘I do not know my exact birth time.’", fieldId: "b-time"});
    const latitude = $("b-lat").value, longitude = $("b-lon").value;
    const hasEitherCoordinate = latitude !== "" || longitude !== "";
    const hasCoordinates = latitude !== "" && longitude !== "";
    if (hasEitherCoordinate && !hasCoordinates) errors.push({message: "Enter both latitude and longitude, or clear both fields.", fieldId: latitude === "" ? "b-lat" : "b-lon"});
    const hasManualLocation = hasCoordinates && ($("b-zone").value.trim() || $("b-tz").value !== "");
    if (!$("b-loc").value.trim() && !hasManualLocation) errors.push({message: "Enter a birthplace. Advanced users may instead supply coordinates and a timezone identifier.", fieldId: "b-loc"});
  }
  return errors;
}

function renderLocationChoices(choices) {
  STATE.locationChoices = choices.slice(0, 5);
  $("location-choice-list").innerHTML = STATE.locationChoices.map((choice, index) => `
    <button type="button" class="location-choice" role="radio" aria-checked="false" onclick="app.selectLocation(${index})" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();app.selectLocation(${index})}">
      <strong>${esc(choice.display_name)}</strong>
      <span>${esc(choice.timezone_name)} timezone</span>
      <details onclick="event.stopPropagation()"><summary>Technical location details</summary>${Number(choice.latitude).toFixed(4)}, ${Number(choice.longitude).toFixed(4)}</details>
    </button>`).join("");
  $("location-choices").hidden = false;
  $("location-choices-title").focus();
}

function readPsychologyPayload() {
  if (!$("psych-enabled").checked) return null;
  const psychology = {};
  const bigFive = {};
  B5.forEach(([key]) => {
    const control = $(`bf-${key}`);
    if (control?.dataset.touched === "true") bigFive[key] = Number(control.value) / 100;
  });
  if (Object.keys(bigFive).length) psychology.big_five = bigFive;
  if ($("p-mbti").value) psychology.mbti = $("p-mbti").value;
  if ($("p-enne").value) psychology.enneagram = {type: Number($("p-enne").value), wing: $("p-wing").value ? Number($("p-wing").value) : null};
  if ($("p-secondary").value && $("p-secondary").value !== "unknown") psychology.secondary_enneagram_influence = Number($("p-secondary").value);
  if ($("p-instinct").value && $("p-instinct").value !== "unknown") psychology.instinctual_variant = $("p-instinct").value;
  if ($("p-attach").value && $("p-attach").value !== "unknown") psychology.attachment = $("p-attach").value;
  if ($("p-conflict").value && $("p-conflict").value !== "unknown") psychology.conflict_style = $("p-conflict").value;
  const assessmentStatus = {};
  STATUS_FIELDS.forEach(([field, controlId]) => {
    const value = $(controlId)?.value;
    const status = $(`p-status-${field}`)?.value;
    if (value && value !== "unknown" && status) assessmentStatus[field] = {status};
  });
  if (Object.keys(assessmentStatus).length) psychology.assessment_status = assessmentStatus;
  return Object.keys(psychology).length ? psychology : null;
}

function buildRequestPayload() {
  const name = $("name").value.replace(/\s+/g, " ").trim();
  if (!name) throw {message: "Enter the full birth or legal name to analyze.", fieldId: "name", code: "missing_name"};
  if (/[<>]/.test(name) || Array.from(name).some(char => /[\u0000-\u001f\u007f]/.test(char))) {
    throw {message: ERROR_COPY.invalid_name, fieldId: "name", code: "invalid_name"};
  }
  if ($("alias-input").value.trim() && !addAliasValue($("alias-input").value)) throw {handled: true};
  const payload = {name, mode: "magic"};
  if (STATE.aliases.length) payload.aliases = [...STATE.aliases];
  if ($("birth-enabled").checked) {
    const dateParts = parseBirthDateInput($("b-date").value);
    if (!dateParts) throw {message: "Enter a real birth date in YYYY-MM-DD format.", fieldId: "b-date", code: "invalid_birth_date"};
    const enteredDate = new Date(Date.UTC(dateParts.year, dateParts.month - 1, dateParts.day));
    const today = new Date();
    if (enteredDate > new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()))) {
      throw {message: "Birth date cannot be in the future.", fieldId: "b-date", code: "future_birth_date"};
    }
    const unknownTime = $("b-time-unknown").checked;
    const suppliedTime = $("b-time").value;
    if (!unknownTime && !suppliedTime) throw {message: "Enter the local birth time, or choose ‘I do not know my exact birth time.’", fieldId: "b-time", code: "missing_birth_time"};
    const [hour, minute] = (unknownTime ? "12:00" : suppliedTime).split(":").map(Number);
    const location = $("b-loc").value.trim();
    const timezoneName = $("b-zone").value.trim();
    const timezoneOffset = $("b-tz").value;
    const latitude = $("b-lat").value;
    const longitude = $("b-lon").value;
    const hasEitherCoordinate = latitude !== "" || longitude !== "";
    const hasCoordinates = latitude !== "" && longitude !== "";
    if (hasEitherCoordinate && !hasCoordinates) throw {message: "Enter both latitude and longitude, or clear both fields.", fieldId: latitude === "" ? "b-lat" : "b-lon", code: "partial_coordinates"};
    if (!location && !(hasCoordinates && (timezoneName || timezoneOffset !== ""))) {
      throw {message: "Enter a birthplace. Advanced users may instead supply coordinates and a timezone identifier.", fieldId: "b-loc", code: "missing_birthplace"};
    }
    payload.birth = {year: dateParts.year, month: dateParts.month, day: dateParts.day, hour, minute, time_accuracy: unknownTime ? "unknown" : "exact"};
    if (location) payload.birth.location = location;
    if (hasCoordinates) { payload.birth.lat = Number(latitude); payload.birth.lon = Number(longitude); }
    if (timezoneName) payload.birth.timezone_name = timezoneName;
    if (timezoneOffset !== "") payload.birth.timezone_offset = Number(timezoneOffset);
  }
  const psychology = readPsychologyPayload();
  if (psychology) payload.psychology = psychology;
  STATE.psychology = psychology;
  return payload;
}

function reportActions() {
  return `<div class="action-group">
    <button type="button" class="button" onclick="app.downloadReport()">Download Markdown</button>
    <button type="button" class="button" onclick="window.print()">Print or save as PDF</button>
    <button type="button" class="button" onclick="app.editInputs()">Edit inputs</button>
    <button type="button" class="button" onclick="app.startNew()">Start a new analysis</button>
  </div>`;
}

function coverageItem(label, status, detail) {
  return `<div class="coverage-item" data-status="${esc(status)}"><strong>${esc(label)}: ${esc(status === "not-included" ? "not included" : status)}</strong><span>${esc(detail)}</span></div>`;
}

function valueCell(label, value) {
  return `<div><span>${esc(label)}</span><strong>${esc(value ?? "—")}</strong></div>`;
}

function renderEditorialReport(result) {
  const signature = result.signature;
  const encoders = signature.encoders;
  const astrology = encoders.astrology && !encoders.astrology.error ? encoders.astrology : null;
  const humanDesign = encoders.human_design && encoders.human_design.available !== false && encoders.human_design.type ? encoders.human_design : null;
  const payload = STATE.requestPayload || {};
  const birth = payload.birth || null;
  const aliases = payload.aliases || [];
  const reportMeta = result.report.metadata || {};
  const place = STATE.selectedLocation?.display_name || birth?.location || "Not included";
  const timezone = STATE.selectedLocation?.timezone_name || birth?.timezone_name || (birth ? "Resolved by the server" : "Not included");
  const timeLabel = !birth ? "Not included" : birth.time_accuracy === "unknown" ? "Unknown" : `${String(birth.hour).padStart(2, "0")}:${String(birth.minute).padStart(2, "0")} local time`;
  const extensions = Object.values(encoders).filter(item => item?.system && item?.provenance);
  const sectionTypes = (result.report.section_metadata || []).map(item => `<li><strong>${esc(item.title)}</strong> — ${esc(typeLabel(item.category))}</li>`).join("");
  const pythagorean = encoders.pythagorean || {};
  const chaldean = encoders.chaldean || {};
  const ordinal = encoders.ordinal || {};
  const gematria = encoders.gematria || {};
  const isopsephy = encoders.isopsephy || {};
  const linguistic = encoders.linguistic || {};
  const convergence = signature.resonance || {};
  const contextSections = STATE.psychology ? clientProfileSections(STATE.psychology) : null;
  const contextRows = contextSections ? Object.values(contextSections).flat() : [];
  const reducedValues = [pythagorean.expression, chaldean.name_number, ordinal.ordinal_reduced, gematria.absolute_reduced, isopsephy.reduced].filter(value => value !== undefined);
  const distinctValues = [...new Set(reducedValues)];

  $("dashboard").innerHTML = `
    <header class="report-header">
      <div><p class="eyebrow">Structured analysis</p><h1 id="report-heading" class="report-title" tabindex="-1">${esc(signature.text)}</h1><p class="report-subtitle">A calculated report with mathematical, astronomical, supplied, and interpretive information labeled separately.</p></div>
      ${reportActions()}
    </header>

    <section class="report-identity" aria-labelledby="identity-title">
      <div><h2 id="identity-title">Report identity</h2><dl class="identity-facts">
        <div><dt>Analyzed name</dt><dd>${esc(signature.text)}</dd></div>
        <div><dt>Other names</dt><dd>${aliases.length ? esc(aliases.join(", ")) : "None"}</dd></div>
        <div><dt>Birth date</dt><dd>${birth ? esc(formatDate(birth)) : "Not included"}</dd></div>
        <div><dt>Birth time</dt><dd>${esc(timeLabel)}</dd></div>
        <div><dt>Resolved birthplace</dt><dd>${esc(place)}${birth ? " · confirmed for calculation" : ""}</dd></div>
        <div><dt>Historical timezone</dt><dd>${esc(timezone)}</dd></div>
        <div><dt>Generated</dt><dd>${esc(STATE.generatedAt)}</dd></div>
        <div><dt>Report version</dt><dd>${esc(reportMeta.report_schema_version || "report-v1")} · API ${esc(result.contract_version || "analysis-v1")}</dd></div>
      </dl></div>
      <aside><h2>Reproduction details</h2><p>The same normalized input and versioned conventions produce the same calculated values.</p><details class="technical-details"><summary>Show technical identifiers</summary><p><code>Input ${esc(result.input_hash || "not supplied")}</code><br><code>Build ${esc(result.build_revision || reportMeta.build_revision || "not supplied")}</code><br><code>Engine ${esc(result.engine_version || "not supplied")}</code><br><code>Reproduction ${esc(reportMeta.reproducibility_id || "not supplied")}</code></p></details></aside>
    </section>

    <section class="coverage" aria-labelledby="coverage-title"><h2 id="coverage-title">Data quality and coverage</h2><div class="coverage-list">
      ${coverageItem("Name calculations", "complete", "All supported name systems were calculated.")}
      ${coverageItem("Birth-date calculations", birth ? "complete" : "not-included", birth ? "Date-based astronomy was calculated." : "No birth date was supplied.")}
      ${coverageItem("Time-sensitive calculations", !birth ? "not-included" : birth.time_accuracy === "unknown" ? "limited" : "complete", !birth ? "No birth details were supplied." : birth.time_accuracy === "unknown" ? "Rising sign, houses, and Human Design are withheld." : "An exact local time was supplied.")}
      ${coverageItem("Location resolution", birth ? "complete" : "not-included", birth ? "Coordinates and historical timezone were resolved or supplied." : "No birthplace was supplied.")}
      ${coverageItem("Personal context", STATE.psychology ? "complete" : "not-included", STATE.psychology ? "Only fields supplied by you are included." : "No self-reported context was supplied.")}
    </div></section>

    <nav class="report-navigation" aria-label="Report sections" data-open="false"><button type="button" aria-expanded="false" onclick="app.toggleReportNavigation(this)">Report sections</button><ul>
      <li><a href="#overview">Overview</a></li><li><a href="#name-calculations">Name calculations</a></li><li><a href="#birth-chart">Birth chart</a></li><li><a href="#human-design">Human Design</a></li><li><a href="#personal-context-report">Personal context</a></li><li><a href="#cross-system">Cross-system synthesis</a></li><li><a href="#tensions">Tensions</a></li><li><a href="#methods">Methods and limitations</a></li>
    </ul></nav>

    <div class="report-content">
      <section id="overview" class="report-section"><p class="section-number">01</p><h2>Overview</h2><p class="information-type">Type of information: Interpretive synthesis</p><p class="section-summary">The calculated systems produced several numeric descriptions of the same name. Their agreement and disagreement are shown as project-specific patterns, not facts about personality or fate.</p><div class="interpretation-note"><strong>Interpretive boundary.</strong> This section combines several symbolic frameworks. It is interpretive rather than scientific.</div>
        <p>The name contains ${esc(linguistic.letter_count ?? "—")} analyzed letters and ${esc(linguistic.unique_letters ?? "—")} unique letters. The supported reduced-number systems produced ${distinctValues.length} distinct result${distinctValues.length === 1 ? "" : "s"}. That variation is expected because each tradition uses different mappings and assumptions.</p>
        <details class="fingerprint-disclosure"><summary>Calculated identity graphic</summary><div class="fingerprint-layout"><div class="fingerprint-art">${fingerprintSVG(signature.fingerprint, 220)}</div><p>This image is generated deterministically from selected numeric outputs. It is decorative and is not a biometric identifier. Text alternative: a radial geometric pattern with ${esc(signature.fingerprint.symmetry)}-fold symmetry derived from the report values.</p></div></details>
      </section>

      <section id="name-calculations" class="report-section"><p class="section-number">02</p><h2>Name calculations</h2><p class="information-type">Type of information: Mathematical calculation, followed by traditional interpretation</p><p class="section-summary">Each system maps letters to numbers using its own stated convention.</p><div class="value-grid">
        ${valueCell("Pythagorean expression", pythagorean.master_preserved || pythagorean.expression)}${valueCell("Pythagorean soul urge", pythagorean.soul_urge)}${valueCell("Chaldean name number", chaldean.name_number)}${valueCell("Ordinal total", ordinal.ordinal_total)}${valueCell("Hebrew gematria reduction", gematria.absolute_reduced)}${valueCell("Greek isopsephy reduction", isopsephy.reduced)}
        </div><div class="interpretation-note"><strong>Traditional interpretation.</strong> Meanings assigned to these numbers come from their named symbolic traditions. The arithmetic is reproducible; the meanings are not scientific measurements.</div><details class="technical-details"><summary>How these values were calculated</summary><p>Letters are normalized by the public input contract and passed to versioned Pythagorean, Chaldean, ordinal, gematria, and isopsephy mappings. Formula and convention details remain in the complete generated report below.</p></details>
      </section>

      <section id="birth-chart" class="report-section"><p class="section-number">03</p><h2>Birth chart</h2><p class="information-type">Type of information: Astronomical calculation and traditional interpretation</p>${astrology ? `<p class="section-summary">Planetary positions were calculated with ${esc(astrology.calculation_engine || "the configured ephemeris")} for the supplied date${birth?.time_accuracy === "exact" ? ", local time," : ""} and resolved location.</p><div class="value-grid">${valueCell("Sun", astrology.sun_sign)}${valueCell("Moon", astrology.moon_sign)}${valueCell("Rising sign (Ascendant)", astrology.ascendant || "Unavailable without an exact time")}${valueCell("Lunar phase", astrology.lunar_phase)}${valueCell("Dominant element", astrology.dominant_element)}${valueCell("House system", astrology.time_sensitive_fields_withheld ? "Withheld" : astrology.house_system)}</div><p>The Ascendant, or rising sign, is the zodiac sign on the eastern horizon at the recorded birth time. A house cusp is the calculated boundary between two chart houses.</p>${astrology.time_sensitive_fields_withheld ? `<div class="limits-note"><strong>Limited by unknown time.</strong> The report withholds rising sign, house cusps, aspects, and other time-sensitive fields instead of presenting an estimated noon as exact.</div>` : `<details class="technical-details"><summary>How the chart was calculated</summary><p>${esc((astrology.planets || []).length)} planetary positions and ${esc((astrology.aspects || []).length)} configured aspects were returned. The geographic timezone identifier applies historical daylight-saving rules; the UTC offset is the difference between local time and Coordinated Universal Time at birth.</p></details>`}` : `<div class="omitted-note"><strong>Not included.</strong> No birth details were supplied, so this section makes no astronomical claims.</div>`}</section>

      <section id="human-design" class="report-section"><p class="section-number">04</p><h2>Human Design</h2><p class="information-type">Type of information: Traditional interpretation using calculated astronomical inputs</p>${humanDesign ? `<p class="section-summary">The configured Human Design adapter returned a ${esc(humanDesign.type)} result using the supplied exact birth time.</p><div class="value-grid">${valueCell("Type", humanDesign.type)}${valueCell("Strategy", humanDesign.strategy)}${valueCell("Authority", humanDesign.authority)}${valueCell("Profile", (humanDesign.profile || []).join(" / "))}${valueCell("Active gates", (humanDesign.gates || []).length)}${valueCell("Defined centers", (humanDesign.centers || []).filter(center => center.defined).length)}</div><div class="limits-note"><strong>Limits.</strong> Human Design is a symbolic system. These labels are not psychological or medical measurements.</div>` : `<div class="omitted-note"><strong>Not included.</strong> ${birth?.time_accuracy === "unknown" ? "An exact birth time is required, so this section was withheld." : "No exact birth date, time, and location were supplied."}</div>`}</section>

      <section id="personal-context-report" class="report-section"><p class="section-number">05</p><h2>Personal context</h2><p class="information-type">Type of information: Supplied by you</p>${contextRows.length ? `<p class="section-summary">These entries came directly from the form and were not inferred by the engine.</p><dl class="calculation-list">${contextRows.map(row => `<div><dt>${esc(row.label)}</dt><dd>${esc(row.value)} · ${esc(row.status_label)}</dd></div>`).join("")}</dl>` : `<div class="omitted-note"><strong>Not included.</strong> No optional personal context was supplied. The engine did not infer it from the name or birth data.</div>`}</section>

      <section id="cross-system" class="report-section"><p class="section-number">06</p><h2>Cross-system synthesis</h2><p class="information-type">Type of information: Interpretive synthesis</p><p class="section-summary">The cross-system convergence score is ${Number(convergence.score || 0).toFixed(1)} out of 100.</p><p>A project-specific summary of how often selected symbolic calculations produce similar reduced values. It is not a scientific measure.</p><dl class="calculation-list">${Object.entries(convergence.components || {}).map(([key, value]) => `<div><dt>${esc(compactLabel(key))}</dt><dd>${(Number(value) * 100).toFixed(0)} of 100 within this configured index</dd></div>`).join("")}</dl><div class="limits-note"><strong>Do not read this as confidence.</strong> A higher value does not mean greater accuracy, compatibility, ability, or worth.</div></section>

      <section id="tensions" class="report-section"><p class="section-number">07</p><h2>Where the systems disagree</h2><p class="information-type">Type of information: Interpretive synthesis</p><p class="section-summary">Different symbolic systems use different assumptions and can produce conflicting descriptions. This report does not force them into false agreement.</p><ul class="tension-list"><li>The selected reduced-number systems produced ${distinctValues.length} distinct values: ${esc(distinctValues.join(", ") || "none available")}.</li><li>Name calculations and birth calculations describe different inputs; one cannot validate the other.</li><li>Self-reported context, when present, is evidence of what you supplied—not proof that a symbolic result predicted it.</li></ul><p>Contradiction can be useful as a reflection prompt: ask which description fits an observable situation, which does not, and what evidence would change your view.</p></section>

      <section id="methods" class="report-section"><p class="section-number">08</p><h2>Methods and limitations</h2><p class="information-type">Type of information: Method and source</p><p class="section-summary">The report keeps arithmetic, astronomy, supplied information, traditional interpretation, and experimental synthesis distinct.</p><dl class="method-list">
        <div><dt>Mathematical</dt><dd>Letter mappings, totals, reductions, ratios, entropy, and the deterministic graphic.</dd></div>
        <div><dt>Astronomical</dt><dd>${astrology ? esc(astrology.calculation_engine || "Configured ephemeris") : "Not used in this report"}; positions are calculations, while astrological meanings remain traditional.</dd></div>
        <div><dt>Supplied by you</dt><dd>Name, other names, birth details, and any optional personal context.</dd></div>
        <div><dt>Interpretive</dt><dd>${extensions.length} configured symbolic extensions and the traditional meanings attached to calculated values.</dd></div>
        <div><dt>Experimental</dt><dd>The cross-system convergence score and synthesis language. These are project-specific, not scientifically validated.</dd></div>
        <div><dt>Privacy</dt><dd>${esc(result.privacy?.retention || "Not persisted by the web process")}. ${esc(result.privacy?.warning || "Network and infrastructure logs may still exist.")}</dd></div>
        <div><dt>Location provider</dt><dd>${birth ? "Open-Meteo geocoding may receive the birthplace text to resolve coordinates and historical timezone." : "Not used because no birthplace was supplied."}</dd></div>
        <div><dt>Application</dt><dd>${esc(result.application_version || "not supplied")} · API ${esc(result.contract_version || "analysis-v1")} · engine ${esc(result.engine_version || "not supplied")} · build ${esc(result.build_revision || "not supplied")}</dd></div>
      </dl><details class="technical-details"><summary>Complete generated report and section labels</summary><p>The backend report contains ${esc(result.report.sections.length)} versioned sections and ${esc(result.report.word_count)} words.</p><ul>${sectionTypes}</ul><div id="report-print-area" class="report-body">${mdToHTML(result.report.markdown)}</div></details></section>

      <div class="end-actions"><h2>Report actions</h2>${reportActions()}<p>Editing an input and creating another analysis produces a new deterministic result for the changed input.</p></div>
    </div>`;

  setSurface("landing", false);
  setSurface("form-section", false);
  setSurface("processing", false);
  setSurface("dashboard", true);
  $("report-heading").focus();
}

Object.assign(app, {
  scrollToForm() {
    $("form-section").scrollIntoView({behavior: "smooth", block: "start"});
    $("name").focus({preventScroll: true});
  },

  toggleSection(which) {
    const on = $(`${which}-enabled`).checked;
    const fields = $(`${which}-fields`);
    fields.hidden = !on;
    fields.setAttribute("aria-disabled", String(!on));
    fields.querySelectorAll("input, select, textarea").forEach(control => { control.disabled = !on; });
    if (which === "birth" && on) this.toggleUnknownTime();
    updateReviewSummary();
  },

  toggleUnknownTime() {
    const unknown = $("b-time-unknown").checked;
    $("birth-time-field").hidden = unknown;
    $("b-time").disabled = unknown || !$("birth-enabled").checked;
    if (unknown) $("b-time").value = "";
    updateReviewSummary();
  },

  syncPersonalContext() { updateReviewSummary(); },

  handleAliasKeydown(event) {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      clearEditorialErrors();
      addAliasValue(event.currentTarget.value);
    } else if (event.key === "Backspace" && !event.currentTarget.value && STATE.aliases.length) {
      this.removeAlias(STATE.aliases.length - 1);
    }
  },

  handleAliasPaste(event) {
    const text = event.clipboardData?.getData("text") || "";
    if (!/[\n,]/.test(text)) return;
    event.preventDefault();
    clearEditorialErrors();
    text.split(/[\n,]+/).map(value => value.trim()).filter(Boolean).forEach(addAliasValue);
  },

  removeAlias(index) {
    const removed = STATE.aliases.splice(index, 1)[0];
    if (removed) $("alias-status").textContent = `${removed} removed.`;
    syncAliasField();
    $("alias-input").focus();
  },

  selectLocation(index) {
    const choice = STATE.locationChoices[index];
    if (!choice) return;
    STATE.selectedLocation = choice;
    $("b-loc").value = choice.display_name;
    $("b-zone").value = choice.timezone_name;
    $("b-lat").value = choice.latitude;
    $("b-lon").value = choice.longitude;
    $("b-tz").value = "";
    $("location-choices").hidden = true;
    updateReviewSummary();
    $("analyze-form").requestSubmit();
  },

  toggleReportNavigation(button) {
    const nav = button.closest(".report-navigation");
    const open = nav.dataset.open !== "true";
    nav.dataset.open = String(open);
    button.setAttribute("aria-expanded", String(open));
  },

  async submit(event) {
    event.preventDefault();
    if (STATE.submitting) return;
    clearEditorialErrors();
    $("location-choices").hidden = true;
    const validationErrors = collectEditorialValidationErrors();
    if (validationErrors.length) {
      showEditorialErrors(validationErrors, "invalid_form");
      return;
    }
    let payload;
    try {
      payload = buildRequestPayload();
    } catch (error) {
      if (!error.handled) showEditorialError(error.message, error.fieldId, error.code);
      return;
    }
    STATE.requestPayload = JSON.parse(JSON.stringify(payload));
    STATE.submitting = true;
    const submitButton = $("submit-btn");
    submitButton.disabled = true;
    submitButton.setAttribute("aria-busy", "true");
    submitButton.textContent = "Creating your analysis…";
    setSurface("landing", false);
    setSurface("form-section", false);
    setSurface("dashboard", false);
    setSurface("processing", true);
    try {
      const response = await fetch("/api/analyze", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
      let data;
      try { data = await response.json(); }
      catch (_) { throw {message: "The server returned an unreadable response. Your entries are still here.", code: "malformed_server_response"}; }
      if (!response.ok) {
        if (data.code === "ambiguous_location" && Array.isArray(data.details?.choices)) {
          setSurface("form-section", true);
          renderLocationChoices(data.details.choices);
          return;
        }
        throw {message: ERROR_COPY[data.code] || data.message || "The report could not be created. Check the highlighted information and try again.", fieldId: apiErrorField(data), code: data.code};
      }
      STATE.result = data;
      STATE.generatedAt = new Date().toISOString();
      renderEditorialReport(data);
    } catch (error) {
      setSurface("form-section", true);
      const isNetworkError = error instanceof TypeError;
      showEditorialError(isNetworkError ? "The server could not be reached. Your entries are still here; check the connection and try again." : error.message, error.fieldId || null, error.code || (isNetworkError ? "server_unavailable" : "unexpected_error"));
    } finally {
      STATE.submitting = false;
      submitButton.disabled = false;
      submitButton.removeAttribute("aria-busy");
      submitButton.textContent = "Create my analysis";
      setSurface("processing", false);
    }
  },

  reset() { this.startNew(); },

  editInputs() {
    setSurface("dashboard", false);
    setSurface("landing", false);
    setSurface("processing", false);
    setSurface("form-section", true);
    updateReviewSummary();
    $("form-section").scrollIntoView({behavior: "smooth", block: "start"});
    $("name").focus({preventScroll: true});
  },

  startNew() {
    $("analyze-form").reset();
    STATE = newEditorialState();
    clearEditorialErrors();
    $("location-choices").hidden = true;
    B5.forEach(([key]) => {
      const control = $(`bf-${key}`);
      if (control) { control.dataset.touched = "false"; control.value = "50"; }
      if ($(`bf-${key}-val`)) $(`bf-${key}-val`).textContent = "Not supplied";
    });
    app.toggleSection("birth");
    app.toggleSection("psych");
    syncAliasField();
    updateReviewSummary();
    setSurface("dashboard", false);
    setSurface("processing", false);
    setSurface("landing", true);
    setSurface("form-section", true);
    $("form-section").scrollIntoView({behavior: "smooth", block: "start"});
    $("name").focus({preventScroll: true});
  },

  downloadReport() {
    if (!STATE.result) return;
    const markdown = STATE.result.report.markdown;
    const name = STATE.result.signature.text.replace(/[^a-z0-9]+/gi, "_").toLowerCase();
    const blob = new Blob([markdown], {type: "text/markdown"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `human_metadata_${name}.md`;
    link.click();
    URL.revokeObjectURL(link.href);
  },
});

function initEditorial() {
  STATE = newEditorialState();
  $("p-mbti").innerHTML += MBTI_TYPES.map(type => `<option>${type}</option>`).join("");
  $("p-enne").innerHTML += Array.from({length: 9}, (_, index) => `<option>${index + 1}</option>`).join("");
  $("p-enne").addEventListener("change", () => { updateWingOptions(); updateSecondaryWarning(); updateReviewSummary(); });
  $("p-secondary").addEventListener("change", () => { updateSecondaryWarning(); updateReviewSummary(); });
  $("bigfive-sliders").innerHTML = B5.map(([key, label]) => `<div class="field-group"><label for="bf-${key}">${label}: <span id="bf-${key}-val">Not supplied</span></label><input type="range" id="bf-${key}" min="0" max="100" value="50" data-touched="false" oninput="this.dataset.touched='true'; document.getElementById('bf-${key}-val').textContent=this.value + ' of 100'"></div>`).join("");
  const statusOptions = `<option value="provisional">Provisional</option><option value="validated">Validated assessment</option><option value="structured">Comparable structured assessment</option><option value="self_identified">Self-identified</option><option value="unknown">Unknown</option>`;
  $("assessment-status-fields").innerHTML = STATUS_FIELDS.map(([field, , label]) => `<div class="field-group"><label for="p-status-${field}">${esc(label)} status</label><select id="p-status-${field}">${statusOptions}</select></div>`).join("");
  $("b-date").addEventListener("input", event => { event.target.value = normalizeBirthDateInput(event.target.value); updateReviewSummary(); });
  $("analyze-form").addEventListener("input", updateReviewSummary);
  $("analyze-form").addEventListener("change", updateReviewSummary);
  app.toggleSection("birth");
  app.toggleSection("psych");
  updateWingOptions();
  syncAliasField();
  updateReviewSummary();
}

document.addEventListener("DOMContentLoaded", initEditorial);
})();
