# HA Panel enclosure rev F – Fusion build scripts (2026-11-03)

Fusion document: **HA Panel v5 - tapered** (cloud project *HA Touch Panel*, direct modelling). Start state: version v9
"rev E WIP 2026-11-01 b: slab restored, HOUSING_E rebuilt, boss/opening/pads, DOOR_plate (Claude)".
Scripts run through the Fusion MCP (`fusion_mcp_execute`, `featureType=script`), each `run(context)`, logging to
`~/Documents/v5f_log.json` (JSON array of `{t, script, step, data}`). MCP call timeout 60 s.

Brief: project doc `claude/brief-enclosure-design-2026-11-03.md`. Frames, helpers and the rev E build: `../revE/README.md`
and `claude/enclosure-v5-revE-handover-2026-11-01.md` §2–3.

| file | block | what it does | result |
|---|---|---|---|
| `v5f_b0_coupon.py` | 0 | K13/D20 coupon in a separate unsaved document: 60 × 60 × 2.5, R3 corners, 40 × 40 × 0.7 R1 fabric recess (1.8 under the cloth), 20 × 20 glue-patch zone marked by four L ticks (3 + 0.8 legs, 0.8 wide, 0.4 deep), modelled standing on a 60 mm edge (print orientation) → `~/Documents/HA_coupon_wall2p5.{3mf,stl}` | 7852.58 mm³ (8.2 g ASA, 9.8 g PETG); 9/9 probes |
| `v5f_b0_v8_lcd_standoff.py` | 0 | V8: imports `8inch-dsi-lcd_c_New.stp` into a separate unsaved document, probes the four LCD mounting points, closes it | standoff Ø5.5 × 1.5, plain Ø2.6 bore through standoff + PCB, LCD panel back 4.15–4.2 below the standoff face. Waveshare 2D drawing: standoffs **M3** ("4×M3.00 H1.5") → **M3 × 6 DIN912** (tip 2.2 past the boss face, ≈ 2.0 clear of the panel; × 8 touches the panel). Slab boss: Ø3.4 holes + Ø6.5 head pockets (Daniel 2026-11-03, option 4a); pocket depth 1.0, not 2.0, because the thread test can't be done on his panel, so an M3 × 6 stays in the 1.5 mm standoff (block 2) |
| `v5f_common.py` | – | shared header: frames, `Dw()`, `Ctx` (body/plane lookup, point probes, interference, world-aligned TemporaryBRep boxes/cylinders, combine), and since b1r `section_pts()` + `outline_body()` (the b1a door outline as a function). Pasted above the b0/b1 scripts; the **b1r scripts `exec()` a copy at `~/Documents/v5f_common.py`** (copy the repo file there first; the copy used on 2026-11-03 had md5 57f34421900f65a45dee733cf658fa3e) | – |
| `v5f_b1a_door.py` | 1 | DOOR_F from the outer generator's floor section (port of p18 `section_pts`) offset 3.5 (= wall 2.5 + D1 0.7 + gap 0.3), z 0–2.5, chin cut at y 4.0, front vertical fillets R8.5; DOOR_plate renamed DOOR_plate_revE and hidden | 34.61 cm³; front y 4.0, back y −81.49; interference 0 |
| `v5f_b1b_shell_bosses.py` | 1 | six M3 door bosses joined to HOUSING_E: Ø8, z 5.0–12.7, Ruthex M3 hole Ø4.0 × 6.7, 2.0 rib to the nearest inner wall (36 directions × 18 bisections at z 9); axes FL/FR (XC±88.5, −7.0), ML/MR (XC±75.5, −45.75), RL/RR (XC±44.0, −68.5) | HOUSING_E 246.44 → 248.68 cm³; ribs 8.35–8.6; interference 0 |
| `v5f_b1c_door_pads_pi_bosses.py` | 1 | door pads Ø11, z 2.0–5.0 under the six bosses; Pi bosses Ø7.6, z 2.0–7.5 + Ø6 land to z 8.0 at (−41.5, −54.5), (16.5, −54.5), (−41.5, −5.5), (16.5, −5.5) | DOOR_F 34.61 → 37.00 cm³ |
| `v5f_b1d_door_cuts.py` | 1 | per door screw Ø13 × 0.5 foot recess (SJ5012), Ø6.5 c-bore to z 3.5 (DIN912 M3 head 3.0), Ø3.4 through; Pi holes Ø4.0, z 0.8–8.5 (Ruthex M2.5); intake 10 × 10 × Ø2 at 3.0 pitch from (−16.1, −36.7) under the cooler | DOOR_F 34.78 cm³; 100/100 intake holes open, bars solid |
| `v5f_b1e1_pi5_step_import.py` | 1 | imports `RaspberryPi5.step` into a new unsaved document (left active) | 47 solids |
| `v5f_b1e_pi5.py` | 1 | copies the 47 solids at the K10 pose (PCB z 8.0–9.4) and unions them into PI5_F; PI5_F_cooler (official drawing, z 13.6–23.1), KO_K7_fan (hidden, fan footprint z 23.1–35.8), GPIO_plugA/B_env (2-row Dupont, z 11.9–32.0); closes the STEP document | PI5_F 17.93, cooler 25.64 cm³; 0 vs housing/door/slab/LCD; plug envelopes overlap the cooler / KO box by 0.4 mm in y (77.1 / 28.9 / 25.3 mm³, drawing tolerance at the header edge) |
| `v5f_b1f_feet_checks.py` | 1 | FOOT_* envelopes Ø12.7, z −3.0…0.5; bbox-prefiltered interference of the block-1 bodies vs housing, slab and every LCD_*; door-gap probes | 220 pairs, 11 overlapping bboxes checked, all 0; door vs feet 0; gap 0.99 (±x, y −7, z 1.25) |
| `v5f_b1g_renders.py` | 1 | renders `~/Documents/HA_v5f_b1_{front34,rear34,under,under_open}.png` (1600 × 1200, fit view; `under` orthographic) + 320 × 240 `_check.jpg`; `under_open` = TemporaryBRep copies of the door assembly dropped 70 mm, deleted after | – |
| `v5f_b1h_save.py` | 1 | body inventory to the log, f3d export, named version | 55 bodies; `revF-wip-b1.f3d` 12.2 MB; version "rev F WIP 2026-11-03 b1: …" saved |
| `v5f_b1r1_remove_bosses.py` | 1r | block-1 revision start (Daniel 2026-11-03 21:01): DOOR_F → DOOR_F_b1 and FOOT_* → FOOT_*_b1, hidden; the six b1 bosses cut from HOUSING_E with INNER_E ∩ (r 4.3 cylinders + 2.4 rib boxes), b1 rib directions recomputed | HOUSING_E 248.68 → 246.44 cm³ (−2.235 = the b1b addition); 24/24 probes |
| `v5f_b1r2_ring_cove.py` | 1r | floor ring: REF_E_outer ∩ z 0–2.5 minus TOOL_ring_opening_6p5 (outline offset 6.5, chin y 1.0, R5.5; kept hidden) → JOIN; **R3.5 inside radius** = fillet on the 4 concave ring-top edges, concentric with the outer R6 | ring 4.571 cm³; HOUSING_E 246.44 → 250.53 → 251.85; bend 2.497–2.503, wall at z 8 2.497–2.503 at side/chin/back; 36/36 probes |
| `v5f_b1r2b_cove_shell.py` | 1r | fallback for the inside radius (shell a z 0–6 slice of REF_E_outer 2.5 inward) — not needed, the fillet worked | – |
| `v5f_b1r3_door.py` | 1r | new DOOR_F = outline offset 6.8 (chin y 0.7, front corners R5.2), z 0–2.5 | 30.72 cm³; gap to the ring 0.300–0.301 on 5 rays; interference 0 |
| `v5f_b1r4_bosses.py` | 1r | six M3 bosses (as b1b) at FL/FR (XC±86.74, −7.66), ML/MR (XC±73.96, −45.63), RL/RR (XC±44.0, −66.74) = 6.0 from the door edge | ribs 9.91–10.19; HOUSING_E 251.85 → 254.22 cm³; interference 0 |
| `v5f_b1r5_pads_pi_bosses.py` | 1r | door pads Ø11 z 2.0–5.0 at the new axes; Pi bosses unchanged | DOOR_F 30.72 → 33.11 cm³ |
| `v5f_b1r6_door_cuts.py` | 1r | Ø6.5 c-bores z −0.5…3.5 + Ø3.4 through (screw heads 0.5 recessed, visible); SJ5012 recesses Ø13 × 0.5 at the feet FL/FR (XC±76, −6.9), RL/RR (XC±25, −69.4); Pi holes; intake | DOOR_F 30.92 cm³; 100/100 intake open; the "no recess at r 4.5" probe for FL/FR fell inside the foot recess (re-probed in r7) |
| `v5f_b1r7_feet_checks.py` | 1r | FOOT_FL/FR/RL/RR Ø12.7, z −3.0…0.5; bbox-prefiltered interference; foot clearances | 180 pairs, 9 overlapping bboxes, all 0; front feet 1.17 to the c-bore edge (web 1.02 at the recess), rear 9.59; 61 bodies |
| `v5f_b1r7b_section.py` | 1r | read-only section through the ML screw axis along its rib → SVG paths for the checkpoint diagram | – |
| `v5f_b1r7c_ring_scan.py` | 1r | read-only scan of 14 sites round the +x half: ring edge, door edge, gap, wall, bend thickness, measured from the actual outer surface (REF_E_outer at z 8) | 12 side/back sites: ring 6.19–6.48, door inset 6.49–6.78, gap 0.300, wall 2.497–2.514, bend 2.497–2.509, flat ring top 0.19–0.48. Front-corner site oblique (ring 7.95, gap 0.58 along the probe); y −8.27 wall reads 4.0 because the probe runs through the FL rib |
| `v5f_b1r8_renders.py` | 1r | renders `~/Documents/HA_v5f_b1r_{front34,rear34,under,under_open}.png` (as b1g; run twice, MODE 'outside' and 'open') | 4 PNG 1600 × 1200 |
| `v5f_b1r9_save.py` | 1r | inventory, f3d export, named version | 61 bodies (12 visible); `revF-wip-b1r.f3d` 12.6 MB; version "rev F WIP 2026-11-03 b1r: …" saved |
| `v5f_b2p_probe_interior.py` | 2 | read-only: INNER_E half-widths (±x from XC) at y 4/−10/−30/−45 for z 8/28/51/77, inner front y at x_rel 47.5/70.5/93.5, inner back at XC | half-width at y −10: 96.74 (z 8) … 93.96 (z 77); inner front y 5.0 to z 48, 4.49 at z 51, −1.04 at z 77; inner back y −82.47 (z 8) |
| `v5f_b2a_slab_boss_holes.py` | 2 | slab-boss LCD holes (option 4a): Ø3.4 through the boss (d 9.0 → 14.8) + Ø6.5 head pockets 1.0 deep (d 14.8 → 13.8) at design (±47.5, ZS ± 34), ZS −27.43; DIN912 M3 × 6 from the seat ends at d 7.8, inside the 1.5 standoff | HOUSING_E 254.224 → 254.050 cm³; 20/20 probes; interference 0 (19 bodies); intermediate version "…b2a: slab-boss holes…" |
| `v5f_b2b_ring_chambers.py` | 2 | floor ring narrowed from u 6.5 to u 5.6 along both chambers (x_rel ≥ 45.3 and ≤ −45.3, y ≥ −51.5; tool = outline offset 5.6 − TOOL_ring_opening_6p5, cut to z 2.6 so no cove sliver stays) → 1.2 door gap for the 2 mm CR foam on the door edge and a passage for the speaker frames; TOOL_ring_opening_5p6 kept hidden | tool 0.662 cm³; HOUSING_E 254.050 → 253.586; door untouched (gap 0.3 elsewhere) |
| `v5f_b2c_pi_shift.py` | 2 | Pi assembly moved 0.7 toward −x (stacks reached x_rel 45.85, the +x frame starts at 47.5): PI5_F, cooler, KO_K7_fan, GPIO plug envelopes; door Pi bosses, insert holes and the 10 × 10 intake field re-made 0.7 toward −x | stacks x_rel 45.15, microSD −44.85; DOOR_F 30.919 cm³; 100/100 intake holes open; moved bodies vs all others 0 |
| `v5f_b2d_partitions_ceilings.py` | 2 | chamber walls ∩ INNER_E: side partitions 1.5 (+x x_rel 45.4…46.9, −x −45.3…−46.8), back partitions y −51.6…−53.1 (behind the ML/MR boss pads), ceilings z 74.0…76.0, bottoms z 3.7 (door top 2.5 + 2 mm foam at 1.2); ring narrowing extended to y −53.1; Ø5 speaker-wire holes at x_rel ±75, z 18 | walls 27.622 cm³; HOUSING_E 253.576 → 281.098; interference 0 (25 bodies); line scans at 0.05 steps: partitions 1.40–1.50, back partitions 1.40–1.50, ceilings 1.90–2.00, partition bottoms at z 3.70–3.75 |
| `v5f_b2e_speakers_baffles.py` | 2 | SPK_L/R = DMA45-4 envelopes (frame 46 × 46 × 3 at y −3.0…0.0, basket Ø40 to y −29.1, axis XC ± 70.5, z 28); baffle blocks x_rel 47.5…93.5, z 5…51, y 0.7…chin ∩ INNER_E with a Ø40 bore, Ø2.5 pilots at ±17.75 (y 0.7 → 4.0) for M3 × 6 DIN912 self-tapping (2.3 engagement); 1 mm CR gasket y 0.0…0.7 | baffles 6.773 cm³; HOUSING_E 281.098 → 287.857; speakers 39.146 cm³ each; SPK vs HOUSING_E 0.40 mm³ (fixed in b2e2) |
| `v5f_b2e2_basket_clearance.py` | 2 | Ø40.6 cut over the basket length (y −3.0…−29.1): trims the FL/FR door-boss cap corners that sat in the basket envelope | 3.05 mm³ removed; SPK vs HOUSING_E 0; insert-hole walls intact |
| `v5f_b2f_lattice.py` | 2 | grille lattices through the chin: 199 × Ø1.9 on a 2.5 hex pitch inside Ø38 per speaker, y 4.5 → 8.0 | 564 mm² open per side (49.8 %); HOUSING_E 287.854 → 285.030; 199/199 open, bars solid, wall solid outside the field |
| `v5f_b2g_chamber_volume.py` | 2 | read-only: chamber air = box ∩ INNER_E − housing − door − front bore, minus the whole speaker envelope (lower bound) or the frame plate only (upper bound) | +x 125.89–158.69 cm³, −x 126.29–159.09 → Qtc 0.725–0.694, Fc 196–188 Hz, F3 191 Hz (Fs 151.4, Qts 0.56, Vas 0.085 L) |
| `v5f_b2h_touch_pcb.py` | 2 | TOUCH_PCB 90 × 44 × 1.6 (x_rel ±45, y 2.7…4.3, z 6…50) + KO_touch_back 2.9 zone; retention on the partition cavity faces: ledge z 5.0…6.0, lip z 6.0…6.8, top tab z 43.5…47.5 — fitted from behind (lift 0.9 behind the tabs, swing the bottom over the lips, drop onto the ledges), because the floor ring blocks insertion from below | retention 0.041 cm³; HOUSING_E 285.030 → 285.062; PCB and keep-out vs all bodies 0; 8/8 probes; slot-wall clearance 0.21 at the 0.9 lift |
| `v5f_b2i_k5_lanes.py` | 2 | KO_K5_LL/LR/UL/UR: Ø7 lanes from the key entry (head top, d 16.8): lower pair back and 13° up × 100, upper pair back and 37° down × 60 (brief K5) | **all four cross the back wall**: lower axes at t 62.5 / 64.75 (world y −64.6 / −66.8, z 93.8 / 94.3), upper at t 52.25 / 55.5 (y −59.5 / −62.1, z 114.8 / 112.8); 100.8–164.4 mm³ in HOUSING_E each, 0 with everything else |
| `v5f_b2q_probe_pi_ports.py` | 2 | read-only: PI5_F connector outlines from its vertices (+x end clustered by y, back edge by x) and the inner back wall behind the USB-C | USB stacks y −36.3…−21.6 / −18.3…−3.7, z 10.3–25.9, faces x_rel 45.1–45.2; USB-C x_rel −36.3…−27.6, z 9.4–12.6, face y −59.3; back wall y −79.3…−80.9 → 20.0–21.6 plug room |
| `v5f_b2r_probe_speaker_screws.py` | 2 | read-only: DIN912 M3 speaker-screw heads (Ø5.5 × 3 behind the flange) and straight Ø3 key paths back to the back partition vs HOUSING_E / DOOR_F; free run behind the outer heads | **lower-outer heads 37.97 mm³ inside the FL/FR door bosses** (free run 0); upper-outer heads clear, 27.5 free to the side wall; inboard heads and paths 0 (45.6 free) |
| `v5f_b2j_renders.py` | 2 | renders `~/Documents/HA_v5f_b2_{front34,cut,under_open,k5_section}.png`: closed front 3/4; housing cut at z 55 seen from behind/above; door assembly dropped 70; side section at world x 47.5 with the +x lanes in red (one MODE per run) | 4 PNG 1600 × 1200 |
| `v5f_b2s_split_concept_renders.py` | 2 | removable-back proposal renders (TemporaryBRep only, nothing saved): HOUSING_E split by the plane y −55 → `~/Documents/HA_panel_renders/HA_v5f_split_{rear34_exploded,rear_open}.png` (cover red, moved 80 back; cover off with speakers, touch PCB, Pi, LCD and lanes) | front 226.78 / cover 58.32 cm³ |
| `v5f_b2t_probe_split.py` | 2 | read-only removable-back study: opening section at y −55 / −60, cover volume, LCD-screw key entries at the plane | y −55: opening half-width 79.4 (z 3) → 21.7 (z 155), closed at z 160; cover 58.3 cm³ (61 g ASA); key entries z 91.6 / 118.2, 46.6–52.7 from the heads, all inside. y −60 fails the upper +x lane |
| `v5f_b2z_save.py` | 2 | inventory, f3d export, named version | 70 bodies (15 visible); `revF-wip-b2.f3d` 13.3 MB; version "rev F WIP 2026-11-03 b2: chambers, speakers + baffles, lattices, touch PCB retention, K5 lanes; USB pocket open (Claude)" |

## Lessons (new in rev F)
1. `importManager.importToNewDocument(createSTEPImportOptions(path))` on the 7.4 MB Waveshare STEP takes ≈ 11 s and returns
   the new document; `Document.close(False)` discards it and the previous document becomes active again (checked).
2. The Waveshare STEP frame: origin at the glass centre, long axis along Y (= design x, same sign), +Z toward the viewer,
   glass front at Z 4.8 → `d = 4.8 − Z`.
3. A coupon or test part can be built with `TemporaryBRepManager` (boxes + cylinders + booleans) and added to a fresh
   direct-modelling document with `bRepBodies.add()` — no sketches, exact volumes, exports via
   `createC3MFExportOptions` / `createSTLExportOptions`.
4. `importToNewDocument()` leaves the **new** document active; the next script must `activate()` the panel document
   before touching it (`Ctx()` checks the active document's name and raises otherwise).
5. Renders: set `camera.target/eye/upVector`, `isFitView = True`, assign `viewport.camera`, `refresh()`, then
   `saveAsImageFile(path, w, h)` — format by extension; a 320 × 240 JPEG (≈ 15 KB) is a cheap remote check of the framing.
6. A script that exceeds the 60 s MCP timeout keeps running in Fusion and completes; log before returning and read the
   result from `v5f_log.json`.
7. World-aligned boxes in the reclined design frame: `OrientedBoundingBox3D.create(Dw(centre), V3(1,0,0), WY, …)` with
   `WY = (0, C, −S)` (world +y in design coordinates).
8. Wall/gap probes by `pointContainment` bisection need a search window that starts outside counterbores and stays inside
   one wall; at the floor the R6 edge fillet thins the 2.5 wall to zero below z ≈ 1.1–1.2, so probes at z < 1.2 return
   the window size.
9. **REF_E_outer is not the analytic generator at the floor.** Measured from REF_E_outer at z 8, the rev E outer surface lies
   0.13–0.37 mm inside the analytic z-0 generator section (`section_pts` offset 0) along the sides and back corners
   (0.00 at the chin, 0.03 at the back centre). Anything placed from the generator (door, ring opening) is that much "wider" relative to the real surface:
   the ring is 6.19–6.48 instead of 6.5; the door-to-ring gap is unaffected (both from the generator, 0.300). Measure from
   REF_E_outer when the distance to the real outer surface matters (D1 recess, ports through the wall).
10. A concave edge loop between a planar face and the shell's inner surface (3 NURBS + 1 plane here) fillets in one
    `filletFeatures` call (R3.5, tangent chain, 0.1 s); select the edges by the neighbour face's `pointOnFace` height.
11. Probe placement: a fixed-offset probe near a screw can land in a neighbouring feature (r6 "no recess at r 4.5" hit the
    foot recess 10.77 away). Check probe points against every nearby cut before reading a `false` as a defect.
12. Probes that cross several features: scan intervals (`segs()`: step along a line, return the solid runs) instead of
    bisecting between assumed endpoints — b2b's first bisection probes read the wrong transition.
13. Exact connector outlines from a STEP-derived body: collect `body.vertices` beyond a plane and cluster them (PI5_F:
    USB stacks y −36.3…−21.6 / −18.3…−3.7, z 10.3–25.9, faces x_rel 45.1–45.2; RJ45 y −55.8…−39.8; USB-C x_rel −36.3…−27.6,
    z 9.4–12.6, face y −59.3). A point-probe grid misses 0.3 mm receptacle shells.
14. `readOnly: true` on `fusion_mcp_execute` for probe scripts (enforced; also runs with a dialog open).
15. The Filesystem MCP `read_media_file` returns the image **and** its base64 as text (≈ 6 k tokens for a 320 × 240 JPEG);
    check one render at most per block.

## Checkpoint 2 open items (2026-11-03)
Daniel 23:41: check that the unit can be assembled; a removable back would make assembly and service easier; print the
speaker enclosures separately and screw them in. Assembly check: the LCD screws and the speaker screws cannot be driven
with the floor door as the only access, and the top-mounted electronics of blocks 3–4 would have to be fitted 100–175 mm
up through the floor opening. Proposal: back cover split at y −55 (b2s/b2t), solid floor, separate speaker boxes.
1. ReSpeaker USB-A plug vs the +x speaker: the basket envelope (Ø40, y −3.0…−29.1) leaves 8.27 mm from the stack face
   (x_rel 45.15) at the lower port's top (z 17.6) and covers the front stack (y −18.3…−3.7) and the front half of the rear
   stack (y −29.1…−21.6). Pocket not built; options in the checkpoint report.
2. K5 lanes exit through the back wall (b2i) — the brief's zero-interference lanes are impossible without back-wall holes.
3. LCD screws are M3 DIN912 (2.5 hex): the A7 2.0 mm key does not fit; a 2.5 mm ball-end key ≥ 150 is needed.
4. Block 5: the D1 inner layer must not close the speaker bores or lattices.
5. Speaker screws (b2r): the lower-outer M3 heads sit inside the FL/FR door bosses, the upper-outer ones have 27.5 mm of
   straight room, and from the open chamber bottom no key reaches a horizontal screw (ball end ≤ ≈ 25° off-axis; an
   L-key's long leg meets the basket envelope or the walls). Fixing options in the checkpoint report; the FL/FR bosses
   also block a speaker insertion path at y −6…−3.66 (boss front face y −3.66).
