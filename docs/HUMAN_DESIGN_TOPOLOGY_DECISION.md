# Human Design topology release decision

Status: **Option C — ship the accurate v1.0 activation index and specify
canonical gate-on-channel topology for v1.1.**

## Evidence

- `src/true_human_design/constants.py` contains a complete 64-entry
  `GATE_TO_CENTER` map and 36 complete-channel gate pairs in `CHANNELS`.
- `src/true_human_design/topology.py` and the public adapter derive and return
  complete channels and defined centers. The v1.0 frontend consumes those
  returned results; it does not repeat this business logic.
- `src/hd_bodygraph.py` contains a separate spatial drawing helper, but its own
  comments call the channel coordinates approximate. Its `CHANNEL_LINES` map is
  incomplete and its active-gate offsets are generated arithmetically rather
  than stored as canonical endpoints. It therefore cannot authorize canonical
  placement for the public interface.
- The v1.0 Atlas accurately shows nine returned centers, returned center state,
  returned complete channels, all 64 numeric gate choices, returned active
  gates, planetary activation records, keyboard selection, provenance, and a
  text/print fallback. It now calls the numbered control an **activation index**
  and states that gates are not spatially placed at channel endpoints.

## Options considered

### Option A — retain the current bodygraph indefinitely

Rejected. The current view is accurate and usable, but canonical endpoint and
hanging-gate relationships would add explanatory value once an authoritative
spatial map and device evidence exist.

### Option B — add canonical gate placement before v1.0

Rejected for this release. The logical gate/center/channel topology is complete,
but the repository does not contain a complete authoritative spatial endpoint
map. Reusing the approximate legacy drawing would violate the no-guesswork
requirement. Building and validating a new primary-source map would expand the
accepted release candidate and physical-device QA scope.

### Option C — ship v1.0 and implement canonical topology in v1.1

Selected. It preserves an accurate response-driven v1.0 while making the
spatial limitation visible and testable.

## v1.1 implementation specification

The v1.1 work is complete only when all of the following are true:

1. Add a versioned reference module, separate from response data, containing
   nine canonical center shapes/coordinates, all 36 channel paths, both
   endpoint coordinates for every gate occurrence, all 64 gate-to-center
   assignments, and a primary-source citation plus convention/version ID.
2. Validate the reference: centers exactly nine, channels exactly 36, gates
   exactly 64, every channel endpoint resolves to its declared center, no
   unapproved duplicate endpoint, and map hash/version are stable.
3. Render all 36 channel beds. A returned complete channel is active only when
   the backend returns that gate pair. A returned single active gate is a
   hanging gate. Do not derive type, authority, or center definition in JS.
4. Use returned `personality_gates` and `design_gates` to distinguish
   personality-only, design-only, and dual activation with text as well as
   color/pattern. Do not invent semantics for inactive channels.
5. Gate selection highlights its endpoint, center, opposite gate, channel,
   returned activating planets, and inspector record. Channel selection
   highlights both gates, both centers, completeness, and provenance. Center
   selection highlights returned defining channels and active gates.
6. Provide an ordered text equivalent listing every returned active/hanging
   gate, activation side/planet/line, channel completion, center association,
   and defined-center result without requiring SVG path inspection.
7. At 320, 360, 390, 412, 768, and desktop widths, provide pinch zoom or focused
   panel mode, 44 CSS-pixel control targets, keyboard entry/exit, and legible
   print output.
8. Add deterministic fixtures for no active gates, one hanging gate, one
   complete channel, disconnected channels, personality-only, design-only,
   dual activation, all nine centers, and every gate at its versioned endpoint.
9. Run browser, TalkBack, physical Android, VoiceOver, physical iPhone, print,
   screenshot, and repeated-render checks for the new topology.

No item may use remembered coordinates, approximate legacy offsets, inferred
response relationships, or frontend duplication of the backend topology engine.
