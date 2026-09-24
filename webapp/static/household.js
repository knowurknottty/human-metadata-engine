/* The Human Manual — household relational-view renderer.
 * Dormant until a real entitled relational-view-v1 artifact is supplied.
 */
(function () {
"use strict";

const esc = value => String(value ?? "").replace(/[&<>"]/g, ch => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;"
}[ch]));

function labelFor(subject, labels) {
  const explicit = labels?.[subject.subject_id];
  if (typeof explicit === "string" && explicit.trim()) return explicit.trim();
  return String(subject.subject_role || "member").replaceAll("_"," ").replace(/\b\w/g, c => c.toUpperCase());
}

function subjectCard(subject, labels) {
  const systems = Array.isArray(subject.systems) ? subject.systems : [];
  return `<article class="household-subject-card" data-household-subject-id="${esc(subject.subject_id)}">
    <header><span class="household-role" data-subject-class="${esc(subject.subject_class || "unknown")}">${esc(String(subject.subject_role || "member").replaceAll("_"," "))}</span><strong>${esc(labelFor(subject, labels))}</strong></header>
    <dl>
      <div><dt>Record</dt><dd>${esc(subject.record_contract || "—")}</dd></div>
      <div><dt>Input</dt><dd>${esc(subject.input_readiness || "—")}</dd></div>
      <div><dt>Systems</dt><dd>${esc(subject.system_availability || "—")}</dd></div>
      <div><dt>Declared relation</dt><dd>${esc(String(subject.declared_relationship || "—").replaceAll("_"," "))}</dd></div>
    </dl>
    <p class="household-system-list">${systems.length ? systems.map(esc).join(" · ") : "No symbolic systems in this subject policy."}</p>
    <p class="household-policy-label">${esc(subject.label || "")}</p>
  </article>`;
}

function observationTable(view, labels) {
  const subjectsById = Object.fromEntries((view.subjects || []).map(item => [item.subject_id,item]));
  const rows = (view.observations || []).map(item => {
    const names = (item.subjects || []).map(id => labelFor(subjectsById[id] || {subject_id:id,subject_role:"member"}, labels));
    const kind = item.kind === "same_marker" ? "Same returned marker" : "Different returned markers";
    return `<tr>
      <th scope="row"><span class="household-observation-kind">${esc(kind)}</span><small>${esc(item.system || "unknown system")}</small></th>
      <td>${esc(names.join(" ↔ "))}</td>
      <td><code>${esc(item.values?.[0])}</code></td>
      <td><code>${esc(item.values?.[1])}</code></td>
      <td>${esc(item.policy_note || "")}</td>
    </tr>`;
  }).join("");
  if (!rows) return `<div class="household-empty-observations"><strong>No adult same-system marker observations.</strong><p>This can be expected for child/pet additions or records without comparable markers. Absence is not a relationship judgment.</p></div>`;
  return `<div class="household-observation-table-wrap"><table class="household-observation-table">
    <caption>Same-system observations only. These rows do not measure relationship quality.</caption>
    <thead><tr><th>Observation</th><th>Subjects</th><th>Left</th><th>Right</th><th>Boundary</th></tr></thead>
    <tbody>${rows}</tbody>
  </table></div>`;
}

function pairView(view, labels) {
  const subjects = view.subjects || [];
  const primary = subjects.find(item => item.subject_role === "primary") || subjects[0];
  const partner = subjects.find(item => item.subject_role === "partner") || subjects[1];
  return `<section class="household-view household-view--pair" aria-labelledby="household-view-title">
    <header class="household-view-head"><p>ME → YOU → US</p><h2 id="household-view-title">US · Pair composition</h2><span>Two independent manuals, compared only where the same system exposes the same field.</span></header>
    <div class="household-pair-lanes">
      ${primary ? subjectCard(primary, labels) : ""}
      <div class="household-us-axis" aria-hidden="true"><span>US</span><i></i><small>composition, not ranking</small></div>
      ${partner ? subjectCard(partner, labels) : ""}
    </div>
    ${observationTable(view, labels)}
    <p class="household-boundary">US does not produce a compatibility, soulmate, fit, harmony, or outcome judgment. Same/different markers remain inside their source systems.</p>
  </section>`;
}

function householdView(view, labels) {
  return `<section class="household-view household-view--we" aria-labelledby="household-view-title">
    <header class="household-view-head"><p>ME → YOU → US → WE</p><h2 id="household-view-title">WE · Household composition</h2><span>Member roles, record readiness, system availability, and provenance-bound observations.</span></header>
    <div class="household-member-grid">${(view.subjects || []).map(item => subjectCard(item, labels)).join("")}</div>
    ${observationTable(view, labels)}
    <p class="household-boundary">Children use child-safe worksheet policy. Pets use care-context policy. Neither is scored or interpreted as an adult relationship subject.</p>
  </section>`;
}

function unavailableView(view) {
  const reasons = (view?.degradation_reasons || []).map(reason => `<li>${esc(reason)}</li>`).join("");
  return `<section class="household-view household-view--unavailable"><header class="household-view-head"><p>US / WE</p><h2>Composition unavailable</h2></header><p>One or more subject records are stale or unresolved, so relational output is suppressed.</p><ul>${reasons}</ul></section>`;
}

function renderRelationalView(view, labels = {}) {
  if (!view || view.schema_version !== "relational-view-v1") throw new Error("Expected relational-view-v1.");
  if (view.status !== "computed" || view.degraded) return unavailableView(view);
  return view.composition === "pair" ? pairView(view, labels) : householdView(view, labels);
}

window.HMEHousehold = Object.freeze({version:"household-ui-v1", renderRelationalView});
})();