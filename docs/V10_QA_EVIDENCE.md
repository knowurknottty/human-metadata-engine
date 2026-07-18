# v1.0 release-candidate QA evidence

Date: 2026-07-18 (America/Chicago)

## Physical-device matrix

| Target | Detection evidence | Result |
| --- | --- | --- |
| Android / preferred Moto G Power 2022 | `adb devices -l` returned an empty device list; `adb mdns services` found no service. | **UNVERIFIED.** No physical Android Chrome flows or hardware-keyboard checks were possible. |
| TalkBack | Requires a connected Android device; none was available. | **UNVERIFIED.** No TalkBack interaction is claimed. |
| iPhone Safari | `devicectl` identified paired physical iPhone 17 Pro `WiFightIt`, iOS 26.5.2, but reported `tunnelState: unavailable`, `ddiServicesAvailable: false`, and “A connection to this device could not be established.” `xctrace` listed it offline. | **UNVERIFIED.** Registration/pairing is not a usable physical test connection. |
| VoiceOver | The paired iPhone could not be connected or controlled. | **UNVERIFIED.** No VoiceOver interaction is claimed. |

Because no usable physical device was connected, model, OS, browser version,
orientation, touch, virtual-keyboard, share-sheet, print destination, hardware
keyboard, TalkBack, and VoiceOver results remain release gates. Desktop/mobile
Chrome automation below is not counted as physical testing.

## Automated browser matrix

Command:

```bash
HME_RUN_NETWORK_QA=1 node tools/capture_atlas_baselines.mjs
```

Environment: Headless Chrome 150.0.0.0 on macOS, device scale factor 1. The
390 × 844 and other narrow-width checks use Chrome mobile metrics emulation.

| Flow/check | Result |
| --- | --- |
| Exact birth via real form/API with explicit IANA zone and coordinates | PASS |
| Name-only via real form/API | PASS |
| Unknown exact time | PASS — astrology remains, Human Design is explicitly unavailable, summary says Date only |
| Live ambiguous location (`Springfield`, Open-Meteo) | PASS — multiple keyboard-operable choices rendered |
| Hostile HTML-like name | PASS — rejected; no inserted element |
| Six surface count | PASS |
| Duplicate element IDs | PASS — none in the rendered exact-birth Atlas/report DOM |
| Constellation, astrology, center/gate, Tree, numerology, fingerprint selection | PASS — one current selection and inspector detail each |
| Chrome accessibility tree | PASS — 169 named buttons; calculated root, planets, centers, and gates exposed by name |
| Repeated Explorer/Research switching | PASS — presentation changes with zero fetch calls |
| Fullscreen fallback | PASS — opens, Escape closes, focus returns to the control |
| Horizontal overflow at 320/360/390/412/768 CSS px | PASS |
| Print media | PASS — gate index and Research text/provenance visible; inspector hidden |
| Print action | PASS |
| Markdown download | PASS — one `.md` file with expected report heading |
| Repeated exact fixture | PASS — Atlas DOM is byte-identical |
| Exact-birth → name-only replacement | PASS — planet/center marks removed; at least two unavailable panels |
| Start new analysis | PASS — prior dashboard becomes hidden |

The machine-readable capture hashes, widths, scroll positions, and individual
selection results are in `docs/assets/ui-v10/manifest.json`.

## Manual screenshot inspection

The nine committed sanitized PNGs were inspected for visible clipping, missing
glyph boxes, misleading stale data, and unavailable-state clarity. The focused
desktop and 390-pixel captures show the constellation, astrology symbols,
center/channel diagram, gate index, Research mode, and name-only unavailable
state. No user or personal-report fixture is present.

This inspection is evidence for the captured Chrome/font environment only. It
does not prove zodiac, planetary, I Ching, or Tree-of-Life font coverage on the
unavailable physical Android/iPhone targets.

## Release implication

Automated and static evidence is green, but the explicit physical Android,
TalkBack, iPhone Safari, and VoiceOver release gates in `RELEASE_GATES.md` are
open. The defensible public-release status is **NOT READY** until those required
device gates pass. The local implementation is otherwise a release candidate
with the documented v1.1 topology boundary.
