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

const INTAKE_VERSION = "household-intake-v1";
const MAX_ADDED_MEMBERS = 7;
const intakeMembers = [];

const ROLE_META = Object.freeze({
  partner:{label:"Spouse / partner",subjectClass:"person_adult",authority:"adult_consent_attested"},
  adult_family:{label:"Adult family member",subjectClass:"person_adult",authority:"adult_consent_attested"},
  child:{label:"Child / adolescent",subjectClass:"person_minor",authority:"guardian_attested"},
  pet:{label:"Pet / companion animal",subjectClass:"nonhuman_animal",authority:"owner_attested"},
});

function intakeEl(id) { return document.getElementById(id); }

function intakeId() {
  if (globalThis.crypto?.randomUUID) return "subj_" + crypto.randomUUID().replaceAll("-","");
  const bytes = new Uint8Array(16);
  globalThis.crypto?.getRandomValues?.(bytes);
  const suffix = Array.from(bytes,b=>b.toString(16).padStart(2,"0")).join("") || Date.now().toString(16);
  return "subj_" + suffix;
}

function intakeStatus(message, isError=false) {
  const node=intakeEl("household-intake-status");
  if (!node) return;
  node.textContent=message || "";
  node.classList.toggle("inline-warning",Boolean(isError));
}
function updateIntakeRole() {
  const role=intakeEl("household-member-role")?.value || "partner";
  const adult=role === "partner" || role === "adult_family";
  const child=role === "child";
  const pet=role === "pet";
  if (intakeEl("household-adult-fields")) intakeEl("household-adult-fields").hidden=!adult;
  if (intakeEl("household-child-fields")) intakeEl("household-child-fields").hidden=!child;
  if (intakeEl("household-pet-fields")) intakeEl("household-pet-fields").hidden=!pet;
  const label=intakeEl("household-authority-label");
  if (label) label.textContent = child
    ? "I am a parent/guardian or otherwise authorized to enter this child's roster details."
    : pet
      ? "I am responsible for this animal's care or have the owner's permission to enter these details."
      : "I have this adult's permission to enter these details.";
  intakeStatus("");
}

function memberSummary(member) {
  if (member.subject_role === "child") return member.age_band === "adolescent" ? "Adolescent · guardian-attested" : "Child · guardian-attested";
  if (member.subject_role === "pet") return [member.species || "Species not supplied", member.age_band && member.age_band !== "unknown" ? member.age_band : null, "care-context only"].filter(Boolean).join(" · ");
  const birth=[member.birth_date || null, member.birth_time_unknown ? "time unknown" : member.birth_time || null, member.birth_place || null].filter(Boolean);
  return birth.length ? birth.join(" · ") : "Adult roster entry · birth details not supplied";
}
function renderIntakeRoster() {
  const list=intakeEl("household-roster-list");
  const count=intakeEl("household-roster-count");
  if (!list || !count) return;
  count.textContent=intakeMembers.length + " / " + MAX_ADDED_MEMBERS + " added";
  if (!intakeMembers.length) {
    list.innerHTML='<p class="household-roster-empty">No additional household members staged yet.</p>';
    return;
  }
  list.innerHTML=intakeMembers.map(member => '<article class="household-roster-card" data-intake-subject-id="' + esc(member.subject_id) + '">' +
    '<div><span>' + esc(ROLE_META[member.subject_role]?.label || member.subject_role) + '</span><strong>' + esc(member.display_alias) + '</strong><small>' + esc(memberSummary(member)) + '</small></div>' +
    '<button type="button" class="household-roster-remove" data-household-remove="' + esc(member.subject_id) + '" aria-label="Remove ' + esc(member.display_alias) + ' from household roster">Remove</button>' +
  '</article>').join("");
}

function resetIntakeFields() {
  ["household-member-label","household-adult-date","household-adult-time","household-adult-place","household-pet-species"].forEach(id => {
    const node=intakeEl(id); if (node) node.value="";
  });
  if (intakeEl("household-adult-time-unknown")) intakeEl("household-adult-time-unknown").checked=false;
  if (intakeEl("household-child-age-band")) intakeEl("household-child-age-band").value="child";
  if (intakeEl("household-pet-age-band")) intakeEl("household-pet-age-band").value="unknown";
  if (intakeEl("household-authority-attest")) intakeEl("household-authority-attest").checked=false;
}
function addIntakeMember() {
  if (intakeMembers.length >= MAX_ADDED_MEMBERS) return intakeStatus("A household supports at most seven added members plus the primary profile.",true);
  const role=intakeEl("household-member-role")?.value || "partner";
  const meta=ROLE_META[role];
  const displayAlias=(intakeEl("household-member-label")?.value || "").trim();
  if (!meta || !displayAlias) return intakeStatus("Choose a role and enter a display name or nickname.",true);
  if (!intakeEl("household-authority-attest")?.checked) return intakeStatus("Confirm that you are authorized to enter this member's roster details.",true);

  const member={
    schema_version:INTAKE_VERSION,
    subject_id:intakeId(),
    subject_role:role,
    subject_class:meta.subjectClass,
    display_alias:displayAlias,
    authority_status:meta.authority,
    transmission_state:"local_only",
  };

  if (role === "partner" || role === "adult_family") {
    member.birth_date=intakeEl("household-adult-date")?.value || null;
    member.birth_time=intakeEl("household-adult-time")?.value || null;
    member.birth_time_unknown=Boolean(intakeEl("household-adult-time-unknown")?.checked);
    member.birth_place=(intakeEl("household-adult-place")?.value || "").trim() || null;
    if (member.birth_time_unknown) member.birth_time=null;
  } else if (role === "child") {
    member.age_band=intakeEl("household-child-age-band")?.value || "child";
  } else if (role === "pet") {
    member.species=(intakeEl("household-pet-species")?.value || "").trim() || null;
    member.age_band=intakeEl("household-pet-age-band")?.value || "unknown";
  }
  intakeMembers.push(member);
  renderIntakeRoster();
  resetIntakeFields();
  intakeStatus(displayAlias + " added locally. Nothing was sent to the server.");
  document.dispatchEvent(new CustomEvent("hme:household-roster-change",{detail:{count:intakeMembers.length}}));
}

function removeIntakeMember(subjectId) {
  const index=intakeMembers.findIndex(item => item.subject_id === subjectId);
  if (index < 0) return;
  const removed=intakeMembers.splice(index,1)[0];
  renderIntakeRoster();
  intakeStatus(removed.display_alias + " removed from the local roster.");
}

function listIntakeMembers() { return JSON.parse(JSON.stringify(intakeMembers)); }

function clearIntakeMembers() {
  intakeMembers.splice(0,intakeMembers.length);
  renderIntakeRoster();
  intakeStatus("Local household roster cleared.");
}

function initIntake() {
  const role=intakeEl("household-member-role");
  const add=document.querySelector("[data-household-add]");
  const list=intakeEl("household-roster-list");
  if (!role || !add || !list) return;
  role.addEventListener("change",updateIntakeRole);
  add.addEventListener("click",addIntakeMember);
  list.addEventListener("click",event => {
    const button=event.target.closest("[data-household-remove]");
    if (button) removeIntakeMember(button.dataset.householdRemove);
  });
  updateIntakeRole();
  renderIntakeRoster();
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded",initIntake,{once:true});
else initIntake();

window.HMEHousehold = Object.freeze({
  version:"household-ui-v2",
  intakeVersion:INTAKE_VERSION,
  renderRelationalView,
  listIntakeMembers,
  clearIntakeMembers,
});
})();