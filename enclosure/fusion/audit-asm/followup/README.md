# Assembly audit, follow-up (2026-11-13/14): the two flat leads, four open points, instructions, pictures

Brief `claude/brief-assembly-audit-followup-2026-11-13.md`. Report `claude/report-assembly-audit-followup-2026-11-13.md` (all numbers, findings F38 to F43).
Instructions `claude/assembly-instructions-2026-11-13.md` (new issue; the issue of 2026-11-12 stays). Model "HA Panel v5 - tapered" **version 62**: nothing was
changed or saved; after the picture calls the document shows as modified (templates added and deleted, visibility switched and put back).

## How it ran
- Every check ran through the Fusion connector's script call with `readOnly: true`, except the picture calls (below).
- The enclosure chat's files were loaded unchanged from commit `fafa8fd` under this audit's module names, each checked against its git blob hash:
  `v5f_k_lib.py` as `aud4k` (blob `ba85884`), `v5f_m_lib.py` as `aud4m` (blob `62790f5`; its line `k = sys.modules['v5f_k']` pointed at `aud4k`),
  `v5f_m1_behind_display.py` and `v5f_m2_rest.py` as namespaces (blobs `a64b8bf`, `da794a9`).
- `aud4_lib.py` (this folder, commit `2c8c9a0`, blob `181243c`) was loaded from that commit into `aud4` and ran as pushed. The one-off calls that used
  it are summarised below; they are not in the repo.
- Fusion had been restarted since the ribbon pass: the big bodies' slabs and the strip library's crops were rebuilt (about 40 s).
- The ribbon's faces were followed on an independent dry copy of the strip's frames (same S, B, F operations). It matches all 40 stations of
  `m_strips.json` exactly; the solids rebuilt by the enclosure chat's scripts equal `LEAD_DSI` and `LEAD_USB_RESP` to 0.000 mm3.

## Checks and results (report section)
| Check | How | Result |
|---|---|---|
| Preflight | body names, counts, version | 62 of 62, unmodified, 391 bodies, 95 in the unit, 36 visible, no `AUD_*` (block 0) |
| Ribbon's faces | frame normal n = d x w of the dry copy at the two ends; Pi body's faces at the port end | face A: board +w (toward the door) at the display, +x (Ethernet jack's face at x 44.85) at the Pi (5.1) |
| Ribbon's clearances | `sclear` per piece against every current body; face/edge from the gap vector and n | as the enclosure chat's figures; drop to the left box 8.10 (5.5) |
| Stiff end piece | ribbon rebuilt with `rs0` 3.3 and 3.8 | shell 2.80 / 2.30, sleeve 2.83 / 3.07, lower-left key path 2.70 / 2.63, arch 1.99 / 1.49 (5.2) |
| Cable's clearances | `sclear`; plug distances | as the enclosure chat's figures (5.6) |
| Left box sliding on | `slide`, 17 positions over 50, then without the plate | nothing touches but the plate under the floor; 0.49 nearest (5.6) |
| Ride-in | `ride`, 45 pieces x 23 positions, the enclosure chat's lead-part boxes | 0 mm3; ribbon 4.65, cable 1.22, plug 7.37 (5.7) |
| Display screws, left | key paths `KO_K5_UL`, `KO_K5_LL` as cylinders r 3.5 | cable 0.95 / 1.29 to the paths, about 3 to the key (5.6) |
| Left speaker plug | `reach` (fingertip 16, six directions) with leads; the finger's lumps in each ribbon piece; drops moved in x; sticks 6 and 4 across; pliers' jaws on the housing (top/bottom, ends) with a nose/joint/handle envelope; build order and service | fingertip 0 of 6; pliers 4 of 6; tweezers 4 across 5 of 6 (5.8.1) |
| USB-C plug in service | `jaws` on the sleeve's 7.4-across part, tips at the board's face (w 0); `service_fixed` with the plate unit 0, 20, 30 lower and 1.5 behind; pitch 30 to 55, yaw -25 to +15; plug 0, 3.6, 7.2 out; sight lines (needles 350 long) | shell seated: 30 to 35 deg below, 10 to 15 deg toward the middle, only the ribbon touched; end of travel free; sleeve visible (5.8.3) |
| The 25 cm spare | `roll(238, 250)`, `lanes3(238, 250)` as temporary strips; a re-laid speaker lead as a rope; fingertip at the spare and the anchor; the anchor's faces | roll fits both; three lanes into the shell at 250; lead through the roll 0.49 at 250 (5.8.4) |
| Ribbon's latch | tweezers (3 across for 40, then 6 across, 120 long) at both latch ends, door left out | door end 2 of 7; screen end under the cooler's envelope (5.5) |

## Picture calls (not read-only)
- Templates added, all deleted before the end: `AUD_usb_25cm_roll_250` (the cable rebuilt with Lc 250, blue), `AUD_spk_L_relaid` (green), `AUD_ribbon`
  (a copy of the rebuilt ribbon, yellow), `AUD_usbc_plug` (blue). The visibility set and the camera were stored first and put back.
- `step23_26_spare_lengths.png`: orthographic, eye (170, -400, 250), target (20, -45, 75), extents 20. `step22_notches.png`: along the screen's
  normal, target B(5, 0, -10), extents 14, up the screen.
- Saved at 1600 x 1200 in `~/Documents/HA_panel_renders/audit-followup/` on the Mac and taken with the connector's screenshot query.
- Closing state: version 62 of 62, 391 bodies, 36 visible (the same set as at the start), no `AUD_*`, modified: close without saving.

## Lessons (numbered on from the ribbon pass's 167)
- **168** Put a gripping tool on the part it grips. Jaws round the sleeve's narrow part (5.4 wide, tips 5 behind the board) said "not clean"; on the
  rigid 7.4-across part with the tips at the board's face, a line 30 to 35 deg below with a small yaw is clean where the standard's six were not.
- **169** A lead that hangs free below a crease is held at the crease. Before proposing "hold it aside", find where the finger meets it: here it was
  the held part and the drop's top, where the lead cannot move.
- **170** A strip's frame normal follows one physical face through bends and folds (a fold turns the frame 180 deg about the crease). Folding a
  crease over or under does not change which face ends up where; only a half twist does.
- **171** Rebuild a drawn lead from its author's scripts and compare it with the model body before using its labelled pieces for clearances.
- **172** `measureMinimumDistance` returns 0 and the origin as both points for bodies that intersect: read those rows as "inside", not as a place.
- **173** The connector's screenshot query leaves its PNG in the session's tool-results folder: copy it from there to deliver a picture.
- **174** Needle scans are slow against many pieces: 40 needles against 84 crop pieces took 72 s. Split them over calls.
