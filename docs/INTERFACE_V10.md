# v1.0 Visual Knowledge System

The v1.0.0 application changes the primary result from a document-first report
to the **Human Metadata Atlas**. This is a presentation-layer release over the
unchanged `analysis-v1` API, `signature-v2` engine, and `report-v1` report
contracts.

## Architecture boundary

| Layer | Location | Responsibility |
| --- | --- | --- |
| Computation | `src/`, `webapp/server.py` | Validation, deterministic encoders, provenance, report generation |
| Visualization | `webapp/static/atlas.js` | Convert structured response fields into SVG and semantic HTML |
| Interaction | `webapp/static/app.js` | Selection, cross-highlighting, Explorer/Research mode, focus, report navigation |
| Presentation | `webapp/static/styles.css` | Etched cartographic design, responsive layout, contrast, print, reduced motion |

The visualization layer does not calculate symbolic results or infer missing
relationships. Unavailable subsystems render an explicit unavailable state.

## Atlas surfaces

1. **Identity constellation** — inventories available systems. Every system is
   connected to the analysis root because it participates in the returned
   signature. Node number and radius reflect populated returned fields, not
   accuracy, importance, or personal strength. The returned `esoteric_bridge`
   is a selectable record; it does not create pairwise system edges.
2. **Astrology wheel** — plots returned planetary sign/degree values, house
   cusps, and configured aspects. Planet-to-gate links use the returned Human
   Design personality/design activation records.
3. **Human Design bodygraph** — shows all nine returned centers, returned active
   channels, and a keyboard-operable 64-gate activation index. Only gates present
   in the returned active set are highlighted; gates are not spatially placed at
   canonical channel endpoints in v1.0.
4. **Tree of Life** — preserves the configured ten-Sephiroth/22-path topology and
   highlights only the returned `dominant_sephirah` mapping.
5. **Numerology matrix** — shows returned input totals, named reductions, and
   results for five systems. Cross-highlighting occurs only when reduced values
   are exactly equal.
6. **Identity fingerprint** — renders the existing deterministic fingerprint
   specification and documents its hash inputs, symmetry rule, spoke
   normalization, fixed hues, and binary ring. It is explicitly non-biometric
   and is not an authentication mechanism.

## Exact data-to-mark inventory

All response paths below are relative to `analysis-v1`. Fixed layout coordinates
are presentation constants and do not create calculated identity data.

### Identity constellation (`crossSystemGraph`)

- **Source response fields:** `signature.encoders.<catalog-key>` plus envelope
  `data`, `status`, `available`, provenance/calculation fields; optional submitted
  context; `signature.encoders.esoteric_bridge.data.links`.
- **Deterministic transformation:** include only present/available catalog
  encoders; count populated top-level returned fields; radius is
  `min(31, 17 + 1.2 * count)`; place included nodes at equal angular intervals.
- **Visual marks:** root circle; one circle, count, label, and root-participation
  line per included system; optional correspondence-record button. No pairwise
  system relationship line is drawn.
- **Selectable entities:** root, included system nodes, correspondence record.
- **Outgoing cross-links:** node → root; root → included nodes; correspondence
  record → only returned astrology, Tree-of-Life, Pythagorean/numerology, and
  tarot categories.
- **Incoming cross-links:** fingerprint spokes and numerology rows → matching
  systems; astrology/Human Design selections → their systems.
- **Provenance source:** encoder `provenance.source_ids` and convention, falling
  back to the returned calculation engine/standard or `analysis-v1 response`.
- **Unavailable state:** missing/unavailable systems are omitted; an absent bridge
  yields no correspondence control; the exact available-system count remains.
- **Screen-reader equivalent:** SVG description gives count, size meaning, and
  participation-line meaning; each node names system and count; inspector gives
  source, method, inputs, confidence category, interpretation, and limitations.
- **Print fallback:** labeled graph, legend, correspondence label, Research text
  equivalent, and report provenance print; interaction-only controls do not.

### Astrology wheel (`astrologyWheel`)

- **Source response fields:** `signature.encoders.astrology.planets[]` fields
  `planet`, `sign`, `degree`, `house`, `retrograde`; `house_cusps[]`; `aspects[]`
  fields `planets`, `type`, `orb`, `exact`; house system, calculation engine, and
  confidence. Human Design personality/design activation records supply only
  planet-to-gate links.
- **Deterministic transformation:** plotted longitude is
  `index(sign) * 30 + degree`; returned cusp longitudes draw house lines; an
  aspect joins its two returned planet positions. Alternating planet radius is
  label spacing, not data.
- **Visual marks:** twelve reference sectors/glyphs; one line/number per returned
  cusp; one mark per valid returned planet; one line per returned aspect whose
  planets are present.
- **Selectable entities:** returned planets, cusps, and drawable aspects.
- **Outgoing cross-links:** planet → returned aspects, returned house, and
  same-planet Human Design activations; aspect → its planets; house → assigned
  returned planets.
- **Incoming cross-links:** Human Design gates → activating planet; constellation
  astrology node → system; system selection → all returned planets.
- **Provenance source:** returned ephemeris/calculation engine, house convention,
  confidence, validated birth input, and `birth-chart` report section.
- **Unavailable state:** missing/error astrology returns a text-only unavailable
  panel and no prior wheel; unknown-time values are withheld by the backend.
- **Screen-reader equivalent:** SVG description gives counts; every returned
  planet/cusp/aspect is a named keyboard target with inspector detail.
- **Print fallback:** bounded SVG and labels plus Research text and detailed
  birth-chart methods.

### Human Design bodygraph (`humanDesignBodygraph`)

- **Source response fields:** Human Design type, strategy, authority, profile,
  calculation/provenance fields; `centers[].{name,core_name,defined}`;
  `channels[].{name,gates,centers}`; `gates[]`; and personality/design activation
  records `gate`, `line`, `planet`.
- **Deterministic transformation:** place nine returned centers at fixed diagram
  coordinates; draw only returned complete channels between returned centers;
  group returned activation records by gate; render integers 1–64 and highlight
  only members of returned `gates`. JS does not resolve type, authority, channel
  completion, or center definition.
- **Visual marks:** nine center rectangles; one line per returned channel;
  returned summary labels; separate 64-button activation index. The index is not
  canonical spatial placement.
- **Selectable entities:** every center, returned complete channel, and gate 1–64.
- **Outgoing cross-links:** gate → containing returned channel and activating
  planets; channel → both gates/centers; center → returned channels naming it;
  system → all returned active gates.
- **Incoming cross-links:** astrology planet → same-planet activation; channel ↔
  gates/centers; constellation Human Design node → system.
- **Provenance source:** returned Human Design engine/standard and confidence
  note. Logical topology originates in `src/true_human_design/constants.py` and
  is serialized by the backend.
- **Unavailable state:** no exact-time result produces a text panel; no previous
  center, channel, or gate marks remain.
- **Screen-reader equivalent:** SVG description separates center/channel counts
  from the activation index; all entities have meaningful keyboard names and
  selection/relationship announcements.
- **Print fallback:** center/channel diagram, full index, Research limitation,
  text equivalent, and report methods.

### Tree of Life (`treeOfLife`)

- **Source response fields:** Tree data `total_value`, `reduced_value`,
  `dominant_sephirah`, `tree_depth`, `unique_paths` and envelope provenance.
  Reference nodes/paths mirror `SEPHIROTH` and `PATHS_22` in
  `src/encoders/kabbalah.py`, convention `ten-sephirot-and-22-paths-v1`.
- **Deterministic transformation:** draw ten fixed reference nodes and all 22
  configured path records; case-insensitively compare returned dominant name;
  only that node is active; link its returned reduced value by exact equality.
- **Visual marks:** ten circles, 22 path elements (two configured paths share
  9→10 endpoints), one response-specific highlight, four returned metrics.
- **Selectable entities:** ten Sephiroth. Reference paths are described but are
  not presented as response-specific activations.
- **Outgoing cross-links:** active Sephirah → exact numerology-value group;
  system → active Sephirah/value. Reference-only nodes have no numeric link.
- **Incoming cross-links:** matching numerology value → active Sephirah;
  constellation Tree node → system.
- **Provenance source:** encoder source IDs/convention and versioned backend
  `SEPHIROTH`/`PATHS_22`; `name-calculations` report section.
- **Unavailable state:** missing data produces a text panel with no empty tree or
  retained highlight.
- **Screen-reader equivalent:** SVG description states ten nodes, 22 reference
  paths, and the returned highlight; node names distinguish active/reference.
  Reference line elements are hidden from traversal so they do not become a
  meaningless path stream; the versioned endpoint map is documented above.
- **Print fallback:** tree, paths, active node, metrics, Research text, provenance.

### Numerology matrix (`numerologyMatrix`)

- **Source response fields:** Pythagorean `total` and
  `master_preserved|expression`; Chaldean `compound_number`, `name_number`;
  ordinal `ordinal_total`, `ordinal_reduced`; gematria `absolute_total`,
  `absolute_reduced`; isopsephy `total`, `reduced`.
- **Deterministic transformation:** select those returned input/result pairs and
  group rows by exact returned-result equality; no reduction is recomputed.
- **Visual marks:** one row per available system with input, presentation arrow,
  result, and method label.
- **Selectable entities:** every rendered row.
- **Outgoing cross-links:** row → constellation system, exact numeric-value
  group, and exact-equal peer rows.
- **Incoming cross-links:** Tree reduced value → matching group; fingerprint
  spoke and constellation numeric node → matching system row.
- **Provenance source:** versioned name encoder, normalized name, displayed
  reduction method, and `name-calculations` report section.
- **Unavailable state:** a row without a returned result is omitted; no previous
  value is reused.
- **Screen-reader equivalent:** native button names system/input/result; inspector
  explains exact equality and its non-validating limit.
- **Print fallback:** all rows/values/methods, equality limit, text equivalent,
  and detailed calculations.

### Identity fingerprint (`identityFingerprint`)

- **Source response fields:** `signature.fingerprint` fields `hash`, `symmetry`,
  `ring_pattern`, `spokes[].{encoder,value,hue}`.
- **Deterministic transformation:** the existing shared `signature-v2` renderer
  consumes the returned fingerprint. Atlas formats spoke values to four decimals
  for text only; it does not re-hash or recompute encoders.
- **Visual marks:** radial SVG, hash/symmetry/ring values, one returned spoke row
  per encoder.
- **Selectable entities:** full fingerprint and every spoke row.
- **Outgoing cross-links:** fingerprint → returned spoke systems; spoke → matching
  system and fingerprint.
- **Incoming cross-links:** constellation/numerology selections → same encoder.
- **Provenance source:** `signature-v2 identity_fingerprint`, returned parameters,
  and `overview` report section.
- **Unavailable state:** defensive empty-object rendering invents no spokes; the
  signature API contract is the primary guarantee that a fingerprint exists.
- **Screen-reader equivalent:** deterministic fingerprint button and inspector
  expose method/parameters and non-biometric/non-authentication limits; report
  includes a textual geometry alternative.
- **Print fallback:** SVG, parameters, spokes, algorithm note, disclosure, and
  provenance.

## Interaction contract

Selecting a visual object updates one shared inspector with:

- source;
- method;
- inputs;
- confidence category;
- interpretation type;
- limitations; and
- a supporting report-section link when applicable.

Selection uses native buttons or SVG elements with `role="button"`, `tabindex`,
Enter/Space handling, accessible names, and a polite live announcement. Linked
objects receive the same cross-highlight state. Motion is limited to focus,
highlight, and fade transitions and is disabled by the existing reduced-motion
contract.

## Modes

- **Explorer** is the default. It presents the six visual systems and keeps the
  long report folded behind a visible reference-layer heading.
- **Research** adds algorithm notes, the text equivalent, reproduction metadata,
  complete calculations, methods, limitations, and the existing report.

Switching modes never re-runs analysis and never changes the response.

## Responsive and print behavior

The desktop layout uses two visualization columns plus a sticky inspector.
Below 980 CSS pixels the inspector moves above the panels; below 720 pixels the
panels stack without removing any visualization. Every panel also has a native
fullscreen control with a fixed-position fallback for browsers that do not
support element fullscreen; both paths have keyboard exit and the fallback
returns focus to its control. Browser pinch zoom remains available. Dense SVGs
retain their complete accessible descriptions. Print removes
interaction controls and includes the visual panels, text equivalent, and
reference report.

## Known verification boundary

Static contracts, JavaScript parsing, server/API tests, and automated viewport
captures can verify structure and rendering. Physical-device VoiceOver,
TalkBack, iPhone Safari, and low-end Android Chrome checks remain separate
release gates until run on those devices.

The Human Design release choice and precise v1.1 acceptance criteria are in
`docs/HUMAN_DESIGN_TOPOLOGY_DECISION.md`.
