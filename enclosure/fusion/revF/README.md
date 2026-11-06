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
| `v5f_r1a_floor.py` | R1 | rework start (Daniel 2026-11-03 23:41 – 11-04 08:40: removable back, solid floor, magnets, USB-C at the bottom): HOUSING_F_wip = HOUSING_E − the six b1r4 door bosses (tool ∩ INNER_E, z 4.95–13.1 so the floor cove stays) + solid floor (REF_E_outer ∩ z ≤ 2.5) − Pi insert holes, 10 × 10 intake, 4 SJ5012 recesses (FL/FR x_rel ±84, y −6.5; RL/RR ±30, −69.0), 4 door-screw holes Ø3.4 + Ø6.5 × 1.0 at (±19, −74.5), (±50, −67.0); DOOR_F/FOOT_* → *_b2 hidden | 285.062 → 282.678 → 314.214 → 312.891 cm³; all probes true (floor solid, bosses gone, 100/100 intake, holes, recesses, cove kept) |
| `v5f_r1b1_inner_skins.py` | R1 | TOOL_inner_skin_1p2 / _1p4: INNER_E copies hollowed with `shellFeatures` (insideThickness) – the layers lie in the cavity along the inner surface | 112.71 / 131.09 cm³, 0.5 s each |
| `v5f_r1b2_split.py` | R1 | HOUSING_F_front = wip − (y < −55, z > 2.5) + lip + the 4 Pi bosses (from DOOR_F_b2); HOUSING_F_door = wip ∩ (y ≤ −55.3, z ≥ 2.8) [0.3 joint gap]; HOUSING_E, wip hidden | front 260.12, door 55.234 cm³; the "rebate" removed nothing (see lesson 16) |
| `v5f_r1b3a_lip_notch.py` | R1 | notch r 4.0 along the upper +x lane where it crossed the lip (32.86 mm³) + joint scans | front 260.051; scans showed the lip on the door's inner surface with no clearance |
| `v5f_r1b3b_lip_fix.py` | R1 | lip moved to the cavity layer 0.2…1.4 (0.2 clear of the door) | the cut separated the lip: "HOUSING_F_front" 2.452 + "HOUSING_F_front (1)" 257.629 |
| `v5f_r1b3c_lip_rejoin.py` | R1 | root band (skin 1.4 ∩ y −53.5…−55.0) + rejoin + both upper-lane notches | front 261.53 cm³, 1 lump; front ∩ door 0; lanes 0; lap clearance 0.32 in x at z 60 (0.2 normal) |
| `v5f_r1c1_lip_magnets.py` | R1 | lip extended to y −63; 10 magnet pairs Ø8 × 1.5 across the lap (z 25, 60, 95, 132, 150 per side): door pockets from the outside (under the cloth, 0.9 skin), lip pads Ø12 with pockets open to the cavity | front 265.558, door 54.414 cm³; magnet axes on the INNER_E normal (e.g. +x z 25: x_rel 74.16, n (0.692, −0.719, 0.067)) |
| `v5f_r1c2_bosses_usb.py` | R1 | lower-lane notches; door bosses Ø8 z 2.8–10.5 with Ruthex M3 holes + ribs (7.37–7.67); USB-C slot x ±10.5, z 12.7–19.2; PD_5807_env (flat 5807, socket centre z 17.2 on the centre line) + KO_5807_pigtail | front 265.519, door 55.484 cm³; boss/slot probes true; 5807 + pigtail vs front, door, Pi, cooler 0; front vs lanes 0 |
| `v5f_r1d_checks.py` | R1 | read-only: interference of front / door / PD_5807_env with every component (bbox-prefiltered, front also vs the 4 lanes); door copy moved straight back 1, 3, 10, 30, 80 mm vs front and 5807; joint scans at z 25 / 95 / 140, y −55.15 and −57.0; 5 probes per magnet pair | 45 pairs all 0; sweep 0 mm³ at every step; gap open at y −55.15 on all 6 lines; lip-to-door 0.4–0.9 in x at y −57 (0.2 normal); 10/10 pairs: door pocket open, 0.9 skin solid, lip pocket open, 0.3 pad skin solid, lap gap open |
| `v5f_r1e_renders_save.py` | R1 | renders (run with MODE 'renders'): rear 3/4 exploded (door copy 80 mm back, red), rear closed, underside (ortho), rear open (lanes red) → `~/Documents/HA_panel_renders/HA_v5f_r1_*.png` (+ 480 × 360 check JPEGs); guarded on the front/door volumes | 4 renders + 4 checks written, temporary bodies removed, visibility and visual style restored |
| `v5f_r1f_save.py` | R1 | the save run (R1e's save branch as sent): volume guard, inventory, f3d, named version | version "rev F WIP 2026-11-04 R1 …" saved; `HA Panel v5 - tapered revF-wip-r1.f3d` 17.8 MB; 82 bodies, 15 visible, no leftovers |
| `v5f_r2a_probe_box_space.py` | R2 | read-only pointContainment grid of the chamber space for the separate boxes | not run to the end: the first call timed out and the Fusion connector dropped (restarted by Daniel 21:08); replaced by boolean trials (lesson 20) |
| `v5f_r2b1_box_tools.py` | R2 | hidden tools: TOOL_inner_skin_2p7 (INNER_E copy, `shellFeatures` insideThickness 2.7); TOOL_cav_1p2_slide / _2p7_slide = (INNER_E − skin) ∩ (the same moved +1.0 in world y), restricted to the chamber zones x_rel ±40…±130, y −60…2, z 0…82: a box cut to it stays 1.2 (2.7) inside the wall at its final position and 1.0 behind it | 247.857 / 464.412 / 434.121 cm³, hidden |
| `v5f_r2b1b_step_tools.py` | R2 | the same for skins 4.7 and 6.2 (the 3.5 × 3.5 step along the floor cove) | skins 418.121 / 538.681, TOOL_cav_4p7_slide / _6p2_slide 386.506 / 351.406 cm³, hidden |
| `v5f_r2b2_trial_boxes.py` | R2 | read-only trial boxes (TemporaryBRep) vs the front shell after the planned wall cut, LCD + slab, lanes, speakers; air volume | floor-cove sliver 1.45 mm³ (more at 1.0 back) and contact with the z 25 / 60 magnet pads (reach y −53.2) at 1.0 back |
| `v5f_r2b3_locate.py` | R2 | read-only: lumps + world bounding boxes of the trial overlaps | located the cove sliver and the pads → 3.5 × 3.5 step, rear face y −52.5 → −52.0 |
| `v5f_r2b4_trial_path.py` | R2 | read-only: trial boxes with the fixes + insertion path (lift 6, in along −y at an inboard offset s, sideways out at 1.0 back, lower, forward), module = box ∪ speaker envelope ∪ stop pads | final 0; s 28 / 31 / 34 not clear, s 37 clear at u 10…70 (10 mm steps); earlier trials: s 22 without the lift hit the lip and back walls (138–254 mm³), the −x box slide hit the Pi floor bosses (tops z 8.0, R2h) → lift 6 (box bottom z 9.0) |
| `v5f_r2c_build_boxes.py` | R2 | shell: b2d side partitions removed for y ≤ 1.2 (cheeks y ≥ 1.2 keep the touch-PCB retention), back partitions and ceilings (∩ INNER_E); baffle stop pads Ø7.5 y 0.0…0.9 at the 4 frame corners; Ø2.5 pilots y −0.5…5.0 at the inboard corners (x_rel ±52.75, z 10.25 / 45.75) for M3 × 10 DIN912 self-tapping; outboard b2e pilots filled. Boxes SPKBOX_L / _R (see R2 checkpoint) | front 265.519 → 238.880 cm³, 1 lump; SPKBOX_L 25.321, SPKBOX_R 25.071 cm³; air 88.04–117.30 / 89.09–118.47 cm³; all probes true, no _tmp bodies |
| `v5f_r2d_checks.py` | R2 | read-only: interference of both boxes with every component, the front shell, the other box and the closed door; box path on the built bodies (5 mm steps); Pi path (PI5_F + cooler + GPIO plugs in from behind 1.0 above the seat); clamp-key paths Ø6.2 to y −90 | box ∩ speaker envelope SPKBOX_L 179.25, SPKBOX_R 66.98 mm³ (located in R2f), everything else 0 incl. the closed door and the other box; box path 0 except 0.5 mm³ at u 55 (both boxes); Pi path vs both boxes 0, vs the front shell 3.7 / 3.0 mm³ at 20 / 30 back (lift 1.0) – 14 min with the full PI5_F (lesson 24); key paths vs the front shell 0, bores open, tube walls and head seats solid |
| `v5f_r2f_locate_spk.py` | R2 | read-only: box ∩ speaker-envelope lumps; the u 55 path contact; the path again at 1 mm steps (lower, side, in) vs the front shell (cropped to the module's half); the Pi 25 back at lift 1.0 (lumps) | box ∩ envelope = pegs 2 × 22.52 + the basket envelope's rear end vs the outboard wall 22.06 / 21.94 (x_rel ±88.7…90.8, y −32.6…−21.6, z 20.7…37.2) + (+x) pocket vs basket 112.17 (x_rel 52.4…56.6, y −30.3…−18.3, z 11.6…21.4); u 55 contact = the box's top-outboard front corner (x_rel ±54.9…56.5, z 77.7…82.2) vs the lip's rear end (y −61.5…−64.4); 1 mm sweep: contact only at u 50…58 (max 0.93 mm³ at 57), lower and side 0; Pi 25 back: 5.6 mm³ on the rear −x Pi boss. Lump boxes are design boxes transformed to world, so y and z are inflated |
| `v5f_r2e_renders_save.py` | R2 | MODE 'renders': rear open (boxes blue), box path (+x box + speaker red at its entry pose), +x box front / rear 3/4 → `~/Documents/HA_panel_renders/HA_v5f_r2_*.png` (+ check JPEGs); MODE 'save': inventory, f3d, named version; guarded on the front / door / box volumes | 4 renders + 4 check JPEGs (entry pose 40 inboard), no leftovers |
| `v5f_r2g_path_offsets.py` | R2 | read-only: entry offset s 40 – sideways t 38…40 and in u 1…76 (1 mm) vs the front shell ∪ LCD + slab | all 0 (79 steps) for both boxes → entry offset 40 |
| `v5f_r2h_pi_lift.py` | R2 | read-only: lowest PI5_F vertex over each Pi boss's x band vs the boss tops → insertion lift; Pi below z 12 at that lift, u 0…70 (1 mm) vs the front shell (bosses, floor) | Pi underside z 6.56 over the −x bosses (microSD socket), boss tops 8.0 → need 1.44, lift 2.0; path 0; 6 s |
| `v5f_r2h2_pi_top.py` | R2 | read-only: the rest of the Pi (z ≥ 11) at lift 2.0, u 0…70 (1 mm) vs the front shell (x_rel ±60, z 9…60) ∪ both boxes | 0; 1.7 s |
| `v5f_r2i_save.py` | R2 | the save run (R2e with MODE 'save', as sent): volume guard, inventory, f3d, named version | version "rev F WIP 2026-11-04 R2: separate speaker boxes …" saved; `HA Panel v5 - tapered revF-wip-r2.f3d` 22.1 MB; 91 bodies, 17 visible, no leftovers |
| `v5f_b3a_probe_top_edge.py` | 3 | read-only, before D2: INNER_E − REF_E_outer; minimum distance from INNER_E's top-face edges (z 177.5, sharp: the p17 inner loft has no top fillet) to the outer faces above z 160; planar faces above z 175 | no hole at the top (the 14 962 mm³ lump is the inner loft's bottom below z 0, closed by the R1 floor); **minimum wall 0.08 mm** at the inner top corners next to the slot (x_rel ±74.0, y −22.4, z 177.5) against the R10 / R3 transition faces; outer top plane z 180.0, x_rel ±64.9, y −42.5…−22.8 |
| `v5f_b3b_ref_outer_r3.py` | 3 | D2: REF_F_outer (hidden) = the rev E p17 generator re-run as a new body (same sections, slab cut, chin cut, chin corners R12, floor R6; slab not moved, nothing deleted, sketches skF_*) with the top edge R3 all round (rear was R10); compared with REF_E_outer | REF_F_outer 1974.145 cm³, 20 faces, 5.1 s; F − E 1355.67 mm³ in one lump at the top edge (z > 165), E − F 0: the generator reproduces rev E exactly elsewhere |
| `v5f_b3c_apply_top_r3.py` | 3 | INNER_F (hidden) = INNER_E with its sharp top edges rounded R1.0; JOIN (F − E) ∪ (INNER_E − INNER_F) ∪ (front ∩ top band, for overlap) into HOUSING_F_front; minimum wall INNER_F ↔ REF_F_outer above z 160 | front 238.880 → 240.258 cm³, 1 lump; INNER_E − INNER_F 33.0 mm³ (B3d); minimum wall 1.77 at the inner top-front corners (x_rel ±74.5, y −22.2, z 176.7) → B3d; interference 0 (26 bodies) |
| `v5f_b3d_top_wall_fill.py` | 3 | TOOL_outer_skin_2p5_F (hidden) = REF_F_outer hollowed by `shellFeatures` insideThickness 2.5; deficit = (skin ∩ y ≥ −55.3, z 165…190) − front, joined | deficit 336.37 mm³ (the corners plus the upper back, where the horizontal 2.5 inset of the generator leaves ≈ 2.3 normal on the 23.7° lean) → 0; front 240.591 cm³; also filled the 0.3 joint gap at the back centre (1.4 mm³, z ≈ 165) → B3e |
| `v5f_b3e_joint_gap.py` | 3 | restores the front/door joint gap: CUT x_rel ±120, y −55.3…−55.0, z 163…190 | gap 1.399 → 0 mm³; top deficit (y ≥ −55.0) 0; front vs door 0; front 240.593 cm³ |
| `v5f_b3f_top_sensors.py` | 3 | hard top: port line y −26.5 (6.4 behind the slab's top-back edge y −20.1); strip pockets 30.4 × 6.4 × 0.8 at x_rel ±(7.3…37.7) (strips 30 × 6 × 0.8 at ±(7.5…37.5), mic 2.0 from the outboard end); mic ports Ø1.5 at ±35.5; heat-stake pins Ø1.8 × 3.5 below the pocket floor at ±11.5 / ±30.0; VEML6030 pocket 15.4 × 15.4 × 0.8 at x_rel 38.3…53.7, y −23.3…−38.7, lux port Ø2 at (46, −31.0) (provisional); envelopes MIC_strip_L/R_env, KO_mic_L/R_back, VEML_env | front 240.593 → 240.075 → 240.111 cm³, 1 lump; all probes true; designed contacts: pins in the strip envelopes 9.16 mm³ each and in the back keep-outs 8.65 each; VEML_env vs front 5.19 mm³ (B3g); envelopes vs LCD / slab / upper lanes 0 |
| `v5f_b3g_locate_veml.py` | 3 | read-only: VEML_env ∩ front; top deficit outside the B3f cuts (grown 0.3) | 5.186 mm³ at x_rel 49.5…54.0, y −40.8…−35.9, z 171.9…176.9: a 15 × 15 board's back-outboard corner (6 mm envelope incl. leads) against the upper back wall; deficit outside the cuts 0 |
| `v5f_b3h_probe_ld_corner.py` | 3 | read-only: plan rays at z 115 / 127.5 / 140 from (x_rel −60, y −25) to the viewer's-right front corner: inner hits, wall normals, wall along the ray; slab and LCD extents | the slot face (normal 0°) meets the side wall (normal 106–118°, 2.5–3.1 thick) in a sharp corner, apex ≈ (−89.6, −11.8) at z 127.5; no ≈ 40° surface; LCD_panel_body x ±92, slab ±105 |
| `v5f_b3i_ld2410c_cradle.py` | 3 | LD2410C cradle: board 16 × 22 × 3.0 (LD2410C_env_F, hidden) with its antenna normal on the corner bisector, 59° from +y toward −x, centre z 127.5; placed by bisection so the 2.0 air box in front clears both walls; frame ring 2.0 (0.15 clearance) 4.0 deep, stop lips 1.0 × 0.85, skirt to the walls (∩ cavity + the wall's own material for overlap); pushed in from inside. Run 1 at the brief's 40° stopped before any change: the air box still hit the side wall 20 mm back | antenna face centre (x_rel −72.53, y −22.05, z 127.5), 19.9 from the apex; front 240.111 → 242.831 cm³, 1 lump; board, core air (14.3 × 20.3 × 2.0) and insertion path vs front 0; cradle vs slab / LCD / lanes / boxes 0; rays from the antenna: −1° / 14° / 29° hit LCD_panel_body + LCD_glass after the wall, 44° / 59° pass housing + SLAB_frame only (≈ 16 mm of print at 59°), 74–119° the side wall only |
| `v5f_b3j_probe_ld_view.py` | 3 | read-only: plan rays at z 127.5 from three cavity points near the corner, 0…150° | 0–15°: wall then LCD_panel_body / LCD_glass; 30–60°: wall + SLAB_frame (printed); ≥ 60–75°: side wall only (≈ 3 mm along the ray) |
| `v5f_b3k_renders_save.py` | 3 | renders (MODE 'renders'): top 3/4 from the front-right, the top from below (cut body, strip envelopes red, VEML blue), the LD2410C corner from inside (cut body, board red) → `~/Documents/HA_panel_renders/HA_v5f_b3_*.png` + check JPEGs | 3 renders + 3 checks, no leftovers |
| `v5f_b3l_save.py` | 3 | the save run (B3k with MODE 'save', as sent) | version "rev F WIP 2026-11-04 b3: top edge R3 + top wall >= 2.5, mic strip pockets/pins/ports, VEML pocket (provisional), LD2410C cradle (Claude)" saved; `HA Panel v5 - tapered revF-wip-b3.f3d` 25.6 MB; 100 bodies, 17 visible, no leftovers |
| `v5f_b4a_probe_interior.py` | 4 | read-only: interior state for block 4 – component boxes, the rear opening's inner half-width at y −55.3 (z 10…150), the door's inner back wall y (x_rel −40…40, z 10…140), floor tops | opening half-width 76.9 (z 10) … 59.5 (z 100) … 17.3 (z 150); back wall inner y at x 0: −81.5 (z 35) … −72.6 (z 100), at x ±40: −77.1 (z 35), −70.5 (z 84); floor top z 2.5 |
| `v5f_b4b_main_board.py` | 4 | main board at candidate A (D21) on a separate bracket: MAIN_pcb (x_rel ±45, y −65.0…−63.4, z 34…84), MAIN_front_env (to y −33.4, z 35.8…84), MAIN_back_env (to y −68.5); MAIN_BRACKET (posts x_rel ±(46.5…52.5), y −62.5…−58.5, z 8…84; Ø8 bosses with Ruthex M2.5 Ø4.0 holes at (±41.5, z 37.5 / 80.5); foot tabs z 8–11 with Ø3.4); floor bosses Ø8 z 2–8 at (±49.5, −58.0), Ruthex M3 | bracket 4.9 cm³ (2 lumps = left/right prints); front 242.831 → 243.241 cm³; MAIN_front_env vs KO_K5_LR 3.08 mm³ (the env's top-left corner: B1 keeps x_rel < −41.45, y > −37 below z 83) and vs the bracket bosses (designed); door removal and Pi path (lift 2.0) 0 |
| `v5f_b4c_5807_cradle.py` | 4 | 5807 posts + rib on the front shell floor (superseded by B4d/B4g) | front 243.241 → 244.197; the posts sat in both speaker boxes' entry paths (36.8 / 41.0 mm³) |
| `v5f_b4d_5807_cradle_part.py` | 4 | B4c posts cut; separate CRADLE_5807 on floor bosses (±13.5, −64.5) (superseded by B4g: wrong hole end, see there) | front 244.197 → 243.241 → 243.65; box paths (s 40) and Pi path 0; cradle vs door 66.2 mm³ (plate end in the back wall) |
| `v5f_b4e_probe_world_boxes.py` | 4 | read-only: tight world boxes of every interior body (copy rotated +12° about x and lifted H, then `boundingBox`) | e.g. LCD_DSI_conn x_rel 41.85…46.75, z 103.3…126.0; LCD_Pi_standoff ×4 x_rel −19.2…−13.7 / 38.8…44.3; PD_5807_env y −84.6…−60.2, z 13.0…18.86 |
| `v5f_b4f_probe_disp_conn.py` | 4 | read-only: PI5_F lumps above the PCB near the CAM/DISP connectors, planar faces; PI5_F vs the cooler envelope | two connectors 2.95 × 15.5 × 4.05 at x_rel 4.1…7.05 / 10.3…13.25, y −57.3…−41.8, z 9.45…13.5, latch step on the +x side, solid top (vertical FPC entry, slot not modelled); 2 × 2 pin header x_rel 15.85…20.85 to z 17.9 inside the cooler box (12.75 mm³: the S-scaled cooler box, not the real cooler) |
| `v5f_b4g_5807_cradle_bezel.py` | 4 | 5807 holes corrected to the receptacle end (Eagle: 2.54 from the USB-C edge → x_rel +7.747 / −7.493, y −81.16, 1.2 in front of the door wall): door cutout x ±11.3, z 7.7–20.5 (was the R1 slot ±10.5 × 12.7–19.2); new CRADLE_5807 (B4d body → CRADLE_5807_b4d, hidden): plate z 8–11, posts Ø6 z 10.5–14 with Ruthex M2 Ø3.2 × 4.5, bezel x ±11.0, z 8–20.2, y −84.6…−81.6 filling the cutout with 0.3, PCB/screw-head pocket, receptacle window x ±4.67 × z 15.4–19.1, front pads; fixing 2 × M3 × 6 at (±5.5, −72.5) behind the main board; B4d floor bosses removed, new ones at (±5.5, −72.5) | door 55.484 → 55.102, front 243.65 (net), cradle 1.827 cm³, 1 lump each; 15/15 probes; cradle vs exact 5807 (PCB, receptacle, M2 heads, shanks) 0, vs PD_5807_env 70.7 (designed: underside keep-out + env box); door, front, Pi, main board, boxes 0; door removal 0.5…80 mm 0; slide-in from behind (lift 0.5) 0 |
| `v5f_b4h_respeaker_carrier.py` | 4 | ReSpeaker on RESP_CARRIER screwed to the LCD's four Pi standoffs (tips d 15.2 at x_rel −16.45 / 41.55, Z −2.93 / −51.93): plate x_rel −40.0…45.4, d 15.2–17.2, Z −56.9…2.2 (inside the boss opening, so LCD + carrier + ReSpeaker go in from the front); Ø2.9 for 4 × M2.5 × 5; notch over the LCD 2 × 2 header + pins; Ø6 × 5 bosses with Ruthex M2 holes at the ReSpeaker holes; zip-tie slot pairs 7.5 above each vacated mic pad (K14); envelopes RESP_pcb / _top_env / _mic_env / _usbc_plug_env (straight plug 12.4 × 6.6 × 32) | carrier 10.07 cm³; USB-C axis (45.28, −21.48, 122.13): the plug runs between the lower (top ≤ 87) and upper (bottom ≥ 139) +x lanes; U4 / U5 at (−32.11 / 38.89, −16.1, 112.27); all 0 vs LCD_*, slab, housing, door, lanes, boxes, main board, sensors; carrier vs RESP_mic_env 111.9 (bosses, designed); front-insertion sweep 2…30 mm vs housing + slab 0 |
| `v5f_b4i_spkbox_usb_slot.py` | 4 | SPKBOX_L: sealed USB-A pocket → slot along the plug's travel, open toward the Pi and through the rear face (V1 x_rel 44.0…55.65, y −36.95…−20.95; V2 44.0…57.15, y −53.0…−36.0; z 9.7…20.7; walls 1.5); SPKBOX_L_r2 kept hidden; envelopes USBA_plug_env, USBA_cable_env | box 25.321 → 25.623 cm³, 1 lump; chamber air −2.69 cm³ (+x 85.35–114.61); 9/9 probes; Pi + plug path (lift 2.0, 71 steps) and lowering 0; plug env vs SPK_L 20.8 and box vs SPK_L 266.3 mm³ (Ø40 basket envelope; clears if the real basket is ≤ Ø32 over its rear 10 mm, R2 open item 1) |
| `v5f_b4j_v11_options.py` | 4 | V11 envelopes at the Pi USB-C (hidden V11c_straight, V11a_up/_px/_mx, V11b_up/_px/_mx) and their overlaps | free length behind the receptacle 20.86 (door wall); c: door 74.8 mm³; a_up: main board 31.4 + back env 264.1; a_px: cradle 338.3, 5807 141.0, door (RR boss) 10.2, Pi 2.2; a_mx: door 260.9, bracket 143.1; b_up: back env 2.8 only; b_px: cradle 47.1; b_mx: door 46.3 |
| `v5f_b4k_probe_walls.py` | 4 | read-only rays: −x inner wall above the −x box (y −25…−62, z 80…110) and the back wall above the door joint (x_rel −40…40, z 160…178) | −x wall inner x −90.0 (y −25, z 80) … −72.7 (y −45, z 110), normal ≈ (0.75, 0.64, −0.15) at (y −45, z 92); back wall at x 0 inner y −52.2 (z 166) … −48.1 (z 176), 2.5 normal, front shell from z ≈ 165 up |
| `v5f_b4l_exhaust_bme_anchors.py` | 4 | exhaust: 2 slots 90 × 3 at x_rel ±45, z 167.0–170.0 / 171.5–174.5 through the back wall above the joint (540 mm², rev D start), TOOL_exhaust_slots kept for the block 5 re-cut; BME680_env (provisional 20 × 15 × 6) 1.5 off the back-right inner wall at (−76.82, −45, 92) + 2 slots 14 × 3 (TOOL_bme680_slots kept); zip-tie bridges on the floor at (±58.5, −56.5), top z 8.0 | front 243.65 → 242.162 → 241.952 → 242.147 cm³, 1 lump; 8/8 probes |
| `v5f_b4m_probe_lcd_dsi_conn.py` | 4 | read-only on the panel: imports Daniel's Waveshare STEP into a new document, intersects the merged PCBA body (2451 faces) with the DSI connector's region, lists the planar faces, closes the document | connector STEP Y 39.28…44.07 (x_rel 41.83…46.62), bottom face d 9.71; FPC slot 0.5 tall (d 8.4…8.9) with the side faces split at the slot on both long sides (±x) – entry side not decided by the model; +x assumed (short wrap to a back-mounted Pi in the stock kit) |
| `v5f_b4n_leads.py` | 4 | every lead as a hidden tube body LEAD_* along a polyline (Ø = bundle allowance), bbox-prefiltered booleans against 36 bodies + all LCD_*, PI5_F cropped to the lead's box | 13 leads in one run; lengths in the block 4 checkpoint; four routes touched something (MIC_R carrier boss 4.5, RADAR cradle ring 10.2, USB_RESP box edge 5.3, DSI MAIN_front_env 3.3 mm³) → B4o |
| `v5f_b4o_leads_fix.py` | 4 | the four routes re-done (old bodies → LEAD_*_b4n, hidden) | MIC_R 68.9, RADAR 70.8, USB_RESP 128.6, DSI 148.5 mm; all 0 |
| `v5f_b4p_renders_save.py` | 4 | renders (MODE 'renders'): rear open (leads red, envelopes blue), ReSpeaker carrier, inlet bezel, V11 envelopes → `~/Documents/HA_panel_renders/HA_v5f_b4_*.png` + check JPEGs; MODE 'save': inventory, f3d, named version | 4 renders + 4 checks, no leftovers; version "rev F WIP 2026-11-05 b4: …" saved; `HA Panel v5 - tapered revF-wip-b4.f3d` 26.0 MB; 142 bodies, 20 visible |
| `v5f_b5_common.py` | 5 | block-5 helpers (exec after `v5f_common.py`; on the Mac as `~/Documents/v5f_b5_common.py`): constants (fabric top z 175.3, top groove z 175.3–176.8, joint planes y −55.0 / −55.3, magnet tables MAG_D1 / MAG_R1, LCD-screw lane axes), TemporaryBRep helpers (tb_copy, inter, vol_x, lbox, dbox, mvw, wbb), ray helpers (ray_hits, solid_runs, magnet_point), slot masks (slot_in d < 15.6 / slot_out d < 13.0), build_layer() | – |
| `v5f_b5a_probe_fabric_zone.py` | 5 | read-only: REF_F_outer's 20 faces in world (type, area, box, normal); the joint faces of both parts | top plane z 180 (x ±73, y −47.1…−22.8); slot plane d 12.3, z 49.2–177.6; chin plane y 7.5, z 6.0–48.5; floor plane x ±93.7, y −79.0…1.5; door end face y −55.3 (z 2.8–165.1), front end face −55.0 (z 2.5–165.8), root band face −53.5 |
| `v5f_b5b_probe_sections.py` | 5 | read-only occupancy sections: chin top at x_rel 0 / 70, back top at x 0, bottom joint at x 0 | touch PCB y 2.75–4.25 (top z 50.0, 0.40 below the slot's inner surface at z 50); lattice holes through y 5.0–7.5; slab 0.3 off the slot face; exhaust slots open at x 0; door wall y −84.5…−82.3 near the floor, joint gap z 2.5–2.8 |
| `v5f_b5c1_inner_skins.py` | 5 | INNER_E copies shelled (insideThickness): TOOL_inner_skin_0p7 / _0p9 / _2p1 / _2p5, TOOL_inner_cup_2p1 (2.1 with the top cap z 177.5, 2649 mm², removed) | 66.220 / 84.908 / 194.500 / 230.089 / 190.136 cm³, 1 lump each, 0.4–2.4 s each |
| `v5f_b5c2_outer_skins_outlines.py` | 5 | REF_F_outer shells: TOOL_outer_skin_0p7 (whole), _2p7 (∩ z ≥ 160, cap removed), _3p2 (∩ z ≤ 20, cap removed); floor outlines from the rev E generator's z-0 section: TOOL_floor_off6 (z 2.0–3.3), TOOL_floor_off12 (z −1.0…0.75, sharp front corners) | 68.699 / 25.057 / 73.188 cm³; off6 x_rel ±93.72, chin y 1.5; off12 ±87.72, chin y −4.5 |
| `v5f_b5d_layer_conflicts.py` | 5 | read-only: the D1 layer (TemporaryBRep) against every part | front 25.24 cm³ (still with an LD2410C window), door 16.56; front ∩ TOUCH_PCB 3.16 mm³ (face contact); door ∩ K5 lanes 29–48 (the lanes run out through the door opening; door off), MAIN_back_env 0.74 (top corners), cradle bezel 96.6 / PD env 57.4 (inside the inlet cutout, re-cut in B5f), stale rev D BME680_env 73.1 (name clash, B5e-1); without exclusions VEML_env 5.1; no layer within 4.0 of the LD2410C face over 16 × 22 → window exclusion dropped |
| `v5f_b5e1_front_layer.py` | 5 | front: stale rev D BME680_env → `BME680_env_revD` (B4l's envelope had been auto-named `BME680_env (1)` → renamed `BME680_env`); R1 lip, root band and pads removed (TOOL_inner_skin_2p5 ∩ y −64.5…−53.4, z ≥ 6.0: 7.889 cm³); D1 layer joined (25.455 cm³) | front 242.147 → 234.257 → 254.941, 1 lump; chin layer y 4.65 solid / 4.15 air; +x side inner face at x_rel 89.0 with the layer behind it; touch PCB 3.16 mm³ (contact) |
| `v5f_b5e1b_pad_tips` (inline) | 5 | the eight R1 pad tips in front of the removal box (y −53.4…−52.2) had become bodies `HOUSING_F_front (1…8)` (25.8 mm³) at the JOIN → deleted | front 254.941 unchanged, no stray bodies |
| `v5f_b5e2_lip_d1.py` | 5 | lap joint for D1 = 0.7: lip s −0.9…−2.1 (y −63.5…−53.5, z ≥ 6.5), root s 0…−2.1 (y −55.0…−53.5), 10 pads Ø12 s −0.9…−3.0 with Ø8.3 lip pockets s −1.2…−3.1, lane notches r 4.0; magnet points by ray on INNER_E at MAG_D1 (z 25 / 60 / 95 / 132 / 150 at y −59.7 / −59.5 / −59.0 / −58.0 / −57.5; x_rel ±73.42 / 68.58 / 59.8 / 41.1 / 16.7) | tool 9.018 cm³, 0 against door, boxes, main board, cradle, lanes, BME680, LD2410C; front 254.941 → 263.238, 1 lump; boxes at the sideways insertion pose (−1.0) 0 |
| `v5f_b5e3_front_recut.py` | 5 | re-cut what the layer closed: lattices 2 × 199 Ø1.9 (y 3.5 → 8.0), 4 pilots Ø2.5 (y −0.5 → 5.0), exhaust and BME680 slots (kept B4l tools) | front 263.238 → 261.960; 199/199 holes open and bars solid at y 4.6 per side; pilots open |
| `v5f_b5f_door_layer.py` | 5 | door: D1 layer (16.562 cm³); R1 pockets filled (r 4.25, s 0.85…2.5); new pockets Ø8.3 from s +0.2 at MAG_D1; inlet cutout x ±12.2, z 6.8–21.4 for the grommet sleeve; 2 × Ø2.1 pin holes at (x_rel ±13.6, z 14.1); door-boss insert holes Ø4.0 z 2.3–9.5 re-cut | door 55.102 → 69.941 → 70.767 → 69.136, 1 lump; 10/10 pockets open, 0.9 skin, lap gap open; back wall at x 0, z 60: y −81.78…−78.58 (3.2 before the recess); door vs front, cradle, PD env, bracket, boxes 0; MAIN_back_env 0.74 |
| `v5f_b5g_recess_feet.py` | 5 | front feet SJ5012 → (x_rel ±80.0, y −11.5) (old Ø13 × 0.5 recesses filled, FOOT_FL / FOOT_FR moved); front Pi insert holes' bottoms z 0.8 → 1.5; 0.7 recess = TOOL_outer_skin_0p7 ∩ z ≤ 175.3 − slot_out − TOOL_floor_off12 − floor rim behind the joint (y < −55.0, z < 2.65) | recess tool 41.174 cm³ (front 23.53, door 15.57); front 261.960 → 238.398, door 69.136 → 53.572, 1 lump each; along rays (recess / solid): chin 0.7 / 2.5, sides 0.74–0.77 / 2.64–2.76 (along x), door back 0.7 / 2.5, back above the door 0.81 / 2.73 (along y), underside strip 0.7 / 1.8, floor inside 0 / 2.5, rim behind the joint 0 / 2.41 |
| `v5f_b5h_grooves.py` | 5 | rail TOOL_inner_cup_2p1 ∩ z 173.8–177.6 − slot zone (d < 17.5) − VEML_env + 0.5 (1.192 cm³); top groove TOOL_outer_skin_2p7 ∩ z 175.3–176.8 ∩ y < −22.5 (0.714 cm³); under-slab groove design Z −93.43…−91.93, x_rel ±93.5: d 12.3 → 15.0 at \|x_rel\| ≥ 48 (baffle blocks behind), → 14.3 across the touch PCB; exhaust slots re-cut after the rail | front 238.398 → 239.407 → 237.918, 1 lump; back groove 3.0 deep along y with a 1.9 floor; hard band at z 177.3 unrecessed; under-slab: deep sections end in the baffle, shallow 0.5 floor, slot face hard above; rail vs parts 0; designed contacts unchanged (strip pins 9.16 / 8.65 mm³), VEML_env 2.04 (was 5.19) |
| `v5f_b5i_grommet.py` + `v5f_b5i2` (inline) | 5 | GROMMET_usbc_F: flange 1.0 on the cloth face (REF_F_outer moved −1.0 in y minus REF_F_outer, x ±15.1, z 4.7–23.5, R2), sleeve 0.8 (bore x ±11.3, z 7.7–20.5 = bezel + 0.3) through cloth + wall to the door's inner surface, 2 × Ø1.8 heat-stake pins 1.5 proud inside; B5i-2 opened the flange over the bore (B5i had cut the bore from the sleeve only) | 0.778 → 0.488 cm³, 1 lump; vs door, front, cradle, PD env, pigtail, feet 0; door + grommet pulled straight back 1 / 3 / 10 / 30 / 80: 0 |
| `v5f_b5j1_checks.py` | 5 | read-only: front / door / grommet against all 73 current parts (bbox pre-filter, PI5_F cropped) and each other; walls along rays (REF entry = cloth face, both parts' runs); slot-face probes; joint gap; magnets; LD2410C air; touch PCB lifted 0.9 | front ∩ door 0, grommet ∩ front / door 0; front: TOUCH_PCB 3.16 (face contact with the D1 layer), strip pins 9.16 ×2 / 8.65 ×2 (designed, unchanged), VEML_env 2.04 and BME680_env 0.08 (provisional boards); door: K5 lanes 101–167 (lanes run out through the door opening, used with the door off), MAIN_back_env 0.74 (top corners); grommet all 0; walls 2.5–2.9 under 0.7–0.8 recess (chin, sides, rear corner, bends); slot face hard at Z 36 and −91; 10/10 magnets (pocket open, 0.9 skin, lap gap, 0.3 pad skin, lip pocket open); LD2410C 19.6 to the wall along the antenna axis (no layer within 4.0 of the face, B5d); touch PCB lifted 0.9: 3.09 (the same face contact) |
| `v5f_b5j2_box_paths.py` | 5 | read-only: R2 box insertion path against the rebuilt lip and the D1 layer (front shell cropped per box): +y travel at 40 inboard (lift 6), sideways at dy −1.0 (lift 6), lowering at the final x | both boxes: +y travel brushes the lip's rear end at dy −59…−54 (≤ 0.23 mm³); at the final x lifted ≥ 4 the box's top-outboard edge meets the D1 layer on the leaning side wall (lift 4 / 5 / 6: 2.6–3.0 / 36 / 112 mm³), 1 mm inboard 0 → path re-ordered in B5j-3 |
| `v5f_b5j3_box_paths2.py` | 5 | read-only: re-ordered box insertion path per box (front shell cropped): lift 6 → +y travel at 42 inboard (dy −70…−40, 1 mm steps) → sideways to 1 mm inboard of the final x (dy −1.0, lift 6) → lower 6 → 0 (0.5 steps) → last 1 mm outboard on the floor (0.25 steps) → push dy −1.0 → 0 (0.25 steps) | both boxes: every step 0 mm³ → assembly order changes (R2 note): the box goes in high and far inboard, then sideways, then down |
| `v5f_b5k_renders_save.py` | 5 | MODE 'renders': temporary RENDER_tmp_CLOTH (TOOL_outer_skin_0p7 ∩ z ≤ 175.3 − slot_out − TOOL_floor_off12 − rim behind the joint − sleeve opening − joint gap) in grey → `HA_v5f_b5_{rear34,front34,under,lap,topgroove}.png` + check JPEGs; MODE 'save': inventory, f3d, named version | cloth 40.780 cm³, deleted after the shots, no leftovers; version "rev F WIP 2026-11-05 b5: …" saved; `HA Panel v5 - tapered revF-wip-b5.f3d` 35.6 MB; 153 bodies, 21 visible |
| `v5f_b5k2_closeups.py` | 5 | close-ups at a fixed camera distance (isFitView False): top groove + hard band at the +x rear corner (150 mm, replaces B5k's fitted shot), grommet flange on the door (140 mm); + 240 × 180 previews | 2 renders, no leftovers |
| `v5f_b6a_matrix.py` | 6 | read-only: full interference matrix before the V11 / seam work (bbox-overlapping pairs, both bodies cropped to the boxes' intersection + 0.1, intersected) | 76 parts, 340 pairs, 70 non-zero, 0 failures – all designed or known (listed in the block 6 section with B6m) |
| `v5f_b6v1_v11_option1.py` | 6 | V11 option 1 (Daniel 2026-11-05 09:16): 5807 + cradle + envelopes + pigtail up 6.5 (old → `*_b5`, hidden); door inlet cutout re-cut at x ±12.2, z 13.3–27.9 (old one filled with the wall profile), grommet pin holes Ø2.1 at (±13.6, z 20.6); door RR boss moved from (x_rel −19, y −74.5) to (−19, −77.0) (Ø8 z 2.8–10.5, Ruthex M3, rib by ray), floor screw hole + c-bore with it; cradle legs Ø8 z 8.0–14.6 on floor bosses at (±3.8, −76.0) | front 237.918 → 237.926, door 53.572 → 53.536, cradle 1.827 → 1.598 cm³; pigtail 19.4 mm |
| `v5f_b6v2_v11_grommet_route.py` | 6 | GROMMET_usbc_F rebuilt at the raised inlet (B5i geometry at z 20.6; old → `_b5`); PIPWR_a_env (90° adapter + straight plug at the Pi, plug under the main board's USB4105 at x_rel 18.8…31.2, z 14.0–33.9) and LEAD_PI_POWER Ø5 (floor run + R8.5 up into the plug), both hidden; checks | grommet 0.489 cm³; cable route 25.3, plug tip to plug tip 77.3 → **122.7 mm slack** on the 0.2 m cable; door sweep 0 except 0.01 at 1 mm; **front ∩ door 3.36 mm³** (B6V-1's cradle floor bosses reach the door's floor cove) → B6V-3 |
| `v5f_b6v3_cradle_bosses.py` | 6 | floor bosses moved to (x_rel +6.5, y −72.5) / (−1.5, −72.5) (Ø8 z 2.0–8.0, Ruthex M3 Ø4.0 z 2.3–8.0; the −x one 0.2 clear of the plug box), B6V-1 bosses removed and dimples filled; new CRADLE_5807 (B6V-1's → `_b6v1`, hidden): plate front restored for x_rel > −5.2, old legs and holes filled, legs Ø8 z 8.0–14.6, Ø3.4, c-bore Ø6.5 × 1.5 (M3 × 12 DIN912) | front 237.926 → 237.930, cradle 1.598 → 2.156 cm³; **front ∩ door 0**; cradle vs PD_5807_env 64.71 (designed); door sweep 1…80 mm 0; 11/11 probes |
| `v5f_b6s1_seam_probe.py` | 6 | read-only: seam option (b) quantified – stations on the old joint plane y −55.0 (rays from (XC, −55, 2.9)), wall normal n, u = t × n; options I (inner edge kept), O (seam kept), M (mid-wall pivot); door magnet pocket rims vs the new door face | lean of the joint plane off the wall normal 40.3° (floor) … 69.2° (arch top); I: seam 2.57–3.14 back in y (2.87–8.30 along the surface), lip and boxes unchanged, pocket rims −0.66…+0.16 from D; O: lip root 2.57–3.14 forward → 1.6–1.8 into both speaker boxes (2.6–2.8 at their insertion pose); M: seam 1.8–2.0 back, root band 0.1 clear of the fitted boxes, 0.9 into the insertion pose |
| `v5f_b6s2_seam_stations.py` | 6 | read-only: 180 stations (P, n on INNER_E; A, Q, B on the s −0.7 / 1.8 / 2.5 surfaces) → `~/Documents/v5f_seam_I.json` (not in the repo; B6s-2 re-creates it from the model); magnets moved along u until the door pocket rim is ≥ 1.05 from A + 1.7 u | 229 s for the rays (lesson 30); moves 0.95 (z 25) … 1.70 (z 150) |
| `v5f_b6s3_seam_faces.py` | 6 | option I: TOOL_seam_RF / _RD = unions of oriented half-space boxes per station (138, ≥ 2.0 apart) in front of the planes through A / A + 1.7 u with normal u; TOOL_seam_wall = the D1 wall profile near the joint; door − RD, front + (wall ∩ RF ∩ y < −55.0). Run 1: t' came out as −t → swapped box extents, 3 lumps → ASM_INCONS_FACE (tools → `*_fail1`, parts untouched); run 2: knife edge (lesson 41) → ASM_INCONS_FACE; run 3 (gain box to y −54.9): door cut done, front JOIN failed (ASM_BAD_CONTAINMENT) | wall profile = door ± 0.00 mm³ in a test slab; door 53.536 → 50.799 cm³ (1 lump); gain leftover → TOOL_seam_gain_fail3 (hidden) |
| `v5f_b6s3b_seam_faces.py` | 6 | completes B6s-3: front face F = A + 0.2 u (meets y −55.0 inside the cavity: no zero-thickness wedge), door face D = A + 1.9 u (gap 1.7 kept, 0.2 slice off the door); the gain touches the front's end face y −55.0 face to face and overlaps the floor rim by 0.1; union tried as TemporaryBRep first (fallback: replace the body) | RF / RD 1 lump; gain 1.875 cm³; front 237.930 → 239.800 (combine), door 50.799 → 50.601; front ∩ door 0; gap 0.85 + 0.85 at 10 stations, face normals 0.0° off u; door sweep 0 |
| `v5f_b6s4_seam_magnets.py` | 6 | 10 magnet pairs moved a further 0.2 along u (D at A + 1.9 u) and projected onto INNER_E; door: old pockets filled (Ø8.5 ∩ wall − RD), new Ø8.3 pockets from s +0.2; front: old pads outside the lip removed, old lip pockets refilled, new pads Ø12 s −0.9…−3.0 and lip pockets Ø8.3 s −1.2…−3.1, lane notches kept; temp result first, then combines | magnets +x (x_rel, y, z): (72.59, −60.47, 24.92), (67.74, −60.20, 59.85), (58.87, −59.66, 94.70), (39.89, −58.68, 131.11), (16.04, −58.15, 148.35), −x mirrored within 0.04; moved 1.10–1.89 from MAG_D1; rim to D 1.05; removed 477.09 mm³ = expected 477.12; front 239.797, door 50.601 cm³; 10/10 magnet probes; front ∩ door 0; interference designed only |
| `v5f_b6s5_save.py` | 6 | intermediate named version | "rev F WIP 2026-11-05 b6a: V11 option 1 (…) + joint faces normal to the wall, magnets moved (Claude)", 171 bodies |
| `v5f_b6s6_cleanup.py` | 6 | B6s-4's door combine had left `HOUSING_F_door (1)` (7.8e-9 cm³, a 0.1 mm speck beside the old −x z 95 pocket) → deleted (lesson 43) | front / door unchanged, 1 lump each; 170 bodies |
| `v5f_b6i_inventory.py` | 6 | read-only: every body with visibility, volume, lumps, tight world box and centroid → log | 171 bodies (22 visible incl. the speck), 92.5 s |
| `v5f_b6p_probes.py` | 6 | probes with a temporary PROBE_tmp_OUT (air + cloth recess): wall = minimum distance from the inner-surface point (ray) to it, top-front roll, speaker-box walls, lane clearances, front–door distance, floor-rim gap, slab gaps, joint gap/face angle, old z 132/150 door pockets filled | walls 2.50 chin / 2.49 +x side z 60 / 2.46 −x side z 120 / 2.49 door rear corner z 40 / 2.48 door back z 60 / 2.44 door side z 100 / 2.50 top / 2.50 bottom fillet / **2.32 back band z 165**; roll 2.50; box walls 1.50–1.58; lanes ≥ 0.31 (KO_K5_LR vs MAIN_front_env 0.0 = the B1 keep-out corner); front–door 0.20 (lap); rim gap 0.30 ×3; joint 0.85 + 0.85, faces 0.0–0.5° off u; pockets filled 4/4 |
| `v5f_b6p2_probes.py` | 6 | follow-up: back band at x ±45 (outside the slot field), the top-front roll aimed at the inner corner (4 directions), slab ring gaps | back band 2.35 / 2.35 (z 165), 2.34 (z 170): the rev E inner loft is a 2.5 **plan** offset, normal wall 2.5·cos(lean) (lesson 45); roll 2.50–2.64; slab ↔ front min 0.0 (bears on the boss, designed), top ring 0.30 at x 0 / 70, bottom ring rays fall into the under-slab groove (2.3 / 3.0) |
| `v5f_b6n_mass_tip.py` | 6 | read-only: printed parts × 1.05 / 1.27 g/cm³ with centroids, component masses (sheet or flagged estimates) at their envelopes' centroids, CoG, tipping force about the rear feet | ASA 1079 g (printed 443), CoG (0.2, −18.7, 76.6); PETG 1172 g (printed 536), CoG (0.1, −19.1, 77.0); about the rear foot centres (y −69, z −3): 3.00 N ASA / 3.23 N PETG horizontal at the glass top edge (lever 177.7), 3.31 / 3.57 N normal to the glass; about the contact patches' rear edge (y −75.35): 3.38 / 3.64 N |
| `v5f_b6o_print_orient.py` | 6 | read-only: each printed part meshed; support area (faces > 45° down, bed faces excluded), bed contact, height and 256³ fit for 8 build directions | front +z (floor down) 12 730 mm² of overhang (best of 8); door +z 208; slab on its side 2 392 / glass side down 4 761 (bed 1 173); boxes rear face down 1 820–1 943; bracket +z 251; ReSpeaker carrier plate down 0; cradle rear face down 169; grommet flange down 200 (on its side 114); all fit 256³ |
| `v5f_b6r_renders.py` | 6 | final renders with a temporary cloth body that wraps the new joint faces (0.3 cloth gap) → `~/Documents/HA_v5f_final_{front34,side,rear34,under,under_open,interior}.png` (+ check / tiny JPEGs); under_open = door + grommet pulled back 70 (its removal direction) | 6 PNG 1600 × 1200; cloth 42.14 cm³; no leftovers |
| `v5f_b6m_matrix_final.py` | 6 | read-only: B6a's matrix on the final state (filters extended by `_b5`, `_b6v1`, `_b6s3`, `_r3`, `_fail*`) | 78 parts, 354 pairs, 72 non-zero, 0 failures, 82 s – all designed or known (block 6 section) |
| `v5f_b6x_final_save_export.py` | 6 | guards, inventory, named version, f3d, STEP per printed part (TemporaryBRep copy → world frame → new direct-modelling document → STEP → closed) | version "rev F 2026-11-03 final (Claude)" saved; `HA Panel v5 - tapered revF-final.f3d` 41.1 MB; 170 bodies, 21 visible; 9 STEP files `~/Documents/HA_v5f_{front,door,slab,spkbox_L,spkbox_R,main_bracket,resp_carrier,cradle_5807,grommet_usbc}.step` (5.10 MB … 0.06 MB; main_bracket 2 lumps = the L/R prints); 66 s |
| `v5f_b6w1_skin3p2.py` | 6 | decision 1 (a), first tool: REF_F_outer ∩ z ≤ 176 shelled 3.2 with the z-176 cap removed (hidden) | TOOL_outer_skin_3p2_F 293.076 cm³, 1 lump, 26 faces, probes (door back, chin) ok; 13 s |
| `v5f_b6w2a_fill_probe.py` | 6 | read-only: fill = 3.2 skin ∩ (INNER_E − TOOL_inner_skin_0p7) ∩ z 6.5–175.3 − slot zone − VEML / LD windows − lap band (TOOL_inner_skin_2p1 ∩ y −67…−52.5) − speaker bores (r 20.5) − pilots (r 1.6); split, crossings, fill ∩ parts | raw 1869.9 mm³ (1 lump, 16 faces); lap band takes 690.9; fill 1161.6 mm³ = front 877.6 + door 283.7; crosses exhaust 107.9, BME680 0.48, inlet 1.91, pins 0.07, grommet 0.05; ∩ parts: BME680_env 0.03, KO_K5_LR 0.10, MAIN_back_env 0.19 + the 5807 / cradle / grommet inside the inlet |
| `v5f_b6w2_wall_fill.py` | 6 | first apply: openings taken out of the fill, gates (fill ∩ parts except the three pairs already non-zero in B6m, cross volumes, TemporaryBRep union = 1 lump), JOIN | gates passed (5807 / cradle / grommet gone with the inlet cut); front's temp union **ASM_INCONS_FACE → nothing joined** |
| `v5f_b6w2_fill.py` | 6 | shared fill definition (3.2 skin) for B6w-2b, copy in `~/Documents/` | – |
| `v5f_b6w2b_union_diag.py` | 6 | read-only: union per part and per region (body and fill cropped to region boxes) | door whole ok (50.889 cm³); front fails at the chin (y > −3: 3.36 mm³ over ≈ 14 000 mm², a sheet ≈ 0.0002 thick) and z 60–160 (464.4 mm³); z < 60 and z > 160 join |
| `v5f_b6w2c_union_diag2.py` | 6 | read-only: V2 = fill boundaries moved off the planes of earlier cuts (slot zone, VEML, exhaust / BME680 slots grown 0.05; top z 175.2) + chin masked | z 60–160 now joins; whole front **ASM_BODY_VERTEX_CRUMBLE** (thin sheet's cut edges); 206 s |
| `v5f_b6w1c_skin3p22.py` | 6 | second tool: the same shell at 3.22 (wall 2.52 normal) so the fill is ≥ 0.02 thick wherever it exists | TOOL_outer_skin_3p22_F 294.822 cm³, 1 lump, 26 faces; 17 s |
| `v5f_b6w2d_fill.py` | 6 | fill V3 (copy in `~/Documents/`): 3.22 skin, V2 offsets, chin masked, front = y ≥ −52.5, door = y ≤ −67 (nothing of the fill lies between), openings out of the fill (inlet x ±12.25, z 13.25–27.95, pins r 1.10) | – |
| `v5f_b6w2d_wall_fill.py` | 6 | apply V3 with the B6w-2 gates, JOIN (fallback replace), checks with a temporary PROBE_tmp_OUT | fill 1765.1 mm³ (front 1119.2, door 509.9, between 0); ∩ parts only BME680_env 0.09, KO_K5_LR 0.13, MAIN_back_env 0.30; **JOIN both**: front 239.797 → 240.888, door 50.601 → 51.101 cm³, 1 lump each; front ∩ door 0, minimum 0.20; walls 2.52 (sides z 60–150, door back z 60 / 110, door sides, back band z 165 x 0 / ±45), chin / top 2.50; lap band (door) 2.35–2.49; exhaust / BME680 / inlet / pins clear (web 2.52), inserts open, lanes 0.497, door sweep 0; 77 s |
| `v5f_b6w3_checks.py` | 6 | read-only: B6m matrix on the new state (filters + `_b6w`, `_fail`, `PROBE_`, `B6W2`) compared with B6m; speaker-box insertion path (B5j3 method) | 78 parts, 354 pairs, 72 non-zero (same pairs), 0 failures; changed: door ∩ MAIN_back_env 0.74 → 1.04, BME680_env ∩ front 0.08 → 0.16, door ∩ K5 LL / LR −0.06 / −0.03 (noise); box paths a–e all 0, final pose 0, boxes 0.20 from the front (at a baffle stop pad, B6w-6) |
| `v5f_b6w4_wall_scan.py` | 6 | normal-wall scan with a temporary PROBE_tmp_OUT: plan rays every 15° from (x_rel 0, y −38) at 15 heights z 10–174 to the first front / door face, classed lap / chin / slot / cove / fill | 317 hits; fill zone 140: 122 at 2.50–2.60; below 2.50 only at opening edges (exhaust slot top edge z 170: 2.31–2.32, inside the 0.05 band; inlet cutout sides 0.24 / 0.25: ray grazing the cut) and in the VEML window (1.80: provisional envelope, no D1 there since block 5); above 2.60: door bosses 9.33, LD2410C cradle 8.07, rail 3.74; 436 s |
| `v5f_b6w6_probes.py` | 6 | follow-up with PROBE_tmp_OUT: where the boxes are 0.20 from the front; back band off the slot edges; lap band with door-only rays (the scan's rays hit the lip first there) | boxes 0.20 from a baffle stop pad (x_rel 89.85 / −86.65, y 0.0, z 10.25; chin, not touched by B6w); back band 2.52 at z 166 and on the slot web z 170.75 (x 0, ±20, ±40), 3.70–3.73 at z 175 (rail); lap band 2.345 (door top, x 0, z 155) … 2.487; 115 s |
| `v5f_b6n_mass_tip.py` (re-run after B6w) | 6 | as above on the r2 state | printed ASA 444.4 / PETG 537.5 g, total 1080.9 / 1174.0 g; CoG (0.18, −18.73, 76.61) / (0.13, −19.12, 77.02); tipping 3.00 / 3.23 N, unchanged |
| `v5f_b6w5_save_export.py` | 6 | guards (front 240.888, door 51.101; no leftovers), inventory, named version, f3d, STEP for the two changed parts | version "rev F 2026-11-03 final r2 (Claude)" saved; `HA Panel v5 - tapered revF-final-r2.f3d` 43.7 MB (revF-final.f3d kept); 172 bodies (+ TOOL_outer_skin_3p2_F / _3p22_F, hidden), 21 visible; `HA_v5f_front.step` 5.95 MB and `HA_v5f_door.step` 1.97 MB re-exported (1 lump each), the other seven unchanged; 93 s |
| `v5f_b6f_fabric_view.py` | 6 | Daniel 12:51 "I want to see the model with the fabric on": B6r's cloth (0.7 recess, seam (b) wrap, 0.3 cloth gap) as two visible non-printed bodies RENDER_FABRIC_front / RENDER_FABRIC_door ('Fabric (Grey)'); pictures of the r2 state; door and glass shown in the viewport; **not saved as a version** | front cloth 26.781 cm³ (1 lump), door cloth 15.358 cm³ (3 lumps); 0 overlap with front / door / each other, door cloth ∩ grommet 3.57 mm³ (the two Ø1.8 heat-stake pins through the cloth); `~/Documents/HA_panel_renders/HA_v5f_r2_fabric_{front34,side,rear34,seam,under}.png`; 53 s |
| `v5f_c1a_probe_top.py` | c1 | read-only: the top region before the cap split (REF top profile, front strip, back / side wall rays z 150–180, bodies above z 160) | top flat z 180 (x 0 y −23…−46, at y −45 only x ±24.4); inner top 177.5; rail z 173.8–177.6; exhaust rows x ±45, z 167–170 / 171.5–174.5; front bar behind the slab (back face 12°, y −19.3 at z 163 … −22.3 at 177); mic strips, VEML, leads; 94 s |
| `v5f_c1b_cap_tools.py` | c1 | offset bands TOOL_cap_off<t> = REF_F_outer ∩ z 160–177.2 shelled t (crop faces removed); hang check below the split | made, but REF's front face (slot-face plane) lies behind the y −15 crop, so every band also ran behind the slot face (lesson 51) → renamed `TOOL_cap_off*_v1`, hidden; below the split only the four mic heat-stake pins (z 174.8) |
| `v5f_c1b2_cap_tools.py` | c1 | bands rebuilt from REF ∩ z 160–177.2 ∩ design Y ≤ −13.9 (crop face removed): t 0.72 / 4.1 / 4.7 / 5.0 / 5.9 / 6.1 / 7.3 | attempt 1 (front plane passed as a removed face) SHELL_GENERIC_FAILURE – the plane is tangent to the corner blends; 1.9 and 1.95 failed with the −13.9 crop (lesson 52); failed copies hidden as `*_fail` |
| `v5f_c1b3_ref_faces.py`, `v5f_c1b4_corner_faces.py` | c1 | read-only: REF crop face list; extent of the two front-corner blend faces | front plane + 2 NURBS blends (y −18.7…−24.6, x ±73…±84) + one side/back NURBS |
| `v5f_c1b5_off1p9.py` | c1 | the 1.9 band with crop design Y −14.6 | TOOL_cap_off1p9 6.193 cm³ |
| `v5f_c1c_probe_posts.py` | c1 | read-only: post candidates – plate underside, top flatness under the head (r 3.6), body conflicts, cap notch vs the groove cover, front bar back face, back wall, exhaust zone, joint sliver | plate underside 177.5 and flat z 180 under all heads; (±62, −27) notch cut the groove cover (21.9 mm³), (±28, −38.6) 0.78 mm³; 212 s (lesson 53) |
| `v5f_c1d_cap_build.py` | c1 | split + ledge + flange steps + groove + exhaust row + posts; cap rim / lip / notches / countersinks; TemporaryBRep gates; commit (old front → HOUSING_F_front_c0, hidden) | committed (front 235.659, cap 8.910 cm³) but the groove was cut before the posts – superseded by c1d2 (bodies kept hidden as `_c1v1`) |
| `v5f_c1e_fillet_checks.py`, `v5f_c1e2_groove_edge.py`, `v5f_c1e3_groove_recut.py` | c1 | R0.8 on the ledge edge (its filter also took the groove's inner edge), R0.3 on the groove's outer edge, groove re-cut after the posts | on the c1v1 bodies; sections (c1f run 3) then showed the FL/FR posts overhanging the groove → rebuild |
| `v5f_c1d2_cap_rebuild.py` | c1 | rebuild from HOUSING_F_front_c0: FL/FR moved to (±58.4, −27.0) (post 0.25 inside the groove's inner edge), groove cut after posts and webs; same gates | front 235.6726, cap 8.9419 cm³, 1 lump each; front ∩ cap / door, cap ∩ door 0; groove ∩ posts 13.5 mm³ removed (BL/BR webs); 69 s |
| `v5f_c1e4_fillets_checks.py` | c1 | fillets with explicit edge classes: ledge outer edge R0.8, both groove top edges R0.3 (one feature); checks | front 235.6548 cm³; post tops 177.5 = cap plate underside at all four; intersections 0 |
| `v5f_c1f_sections.py` | c1 | read-only: section loops S1 x 0, S2 x 28 (BL), S3 x 58.4 (FL), S4 y −30.05 → `HA_panel_renders/c1_sections.json`, plotted off-line | run 4 = final state |
| `v5f_c1g_renders.py`, `v5f_c1g2_renders_close.py` | c1 | checkpoint renders (exploded, assembled, top; orthographic close-ups with explicit viewExtents, lesson 54) | `~/Documents/HA_panel_renders/HA_v5f_c1_*.png` |
| `v5f_c1h_save.py` | c1 | guards, named WIP version | "rev F WIP 2026-11-05 c1 step 1: …" saved, 200 bodies |
| `v5f_c1z_logread.py` | – | read-only helper: print parts of a log entry (lesson 30) | – |
| `v5f_c2a_key_lanes.py` | c2 | read-only: key lanes (Ø5 for a 2.5 ball-end key) for cap screws driven from inside, from candidate axes on the lip ring to targets behind the unit (door off), against every part (pre-cap front shell), leads separately | with the cap on only the back is reachable (x ≤ ±31, y −42…−38: 23–25°); (46, −33) only through leads – c2a2 (inline): LEAD_VEML alone (51–67 mm³); 70.6 s |
| `v5f_c2b0_probe.py` | c2 | read-only: bodies near the top; boss axes tangent to the lip (Ø8, d ≥ 6.1 at z 172.5–175.8, bisection along the plan normal); lanes for BL/BR/SL/SR without VEML_env / LEAD_VEML; cap pocket map (containment at z 177.9 / 179.5); bar back face | BL/BR (±25.91, −37.80), SL/SR (±43.36, −32.85); best clear lanes 24.6° (back) / 27.6° (rear corners), no lead in the way; mic pockets x ±(7.3…37.7), old VEML pocket x 38.3–53.7, pins to z 174.9; bar back face −22.34 at z 177, joint plane from z ≈ 177.3; 70.6 s |
| `v5f_c2c_cap_hidden_screws.py` | c2 | rebuild from HOUSING_F_front_c0: cap without posts / notches / countersinks + four Ø8 bosses (Ruthex hole Ø4.0 × 6.0 from below); front shell pads z 169.5–172.5 (Ø3.4) + two 2.0 ribs per pad along the key lane; shelf under the cap's front edge; VEML to the centre (old pocket + port filled), mic strips 29 long; LEAD_VEML re-routed; KO_capkey_* lanes; gates; old bodies → `*_c1` (hidden) | run 1 front ∩ cap 1.04 mm³ (c0's corner fillet under the cap's front edge on the shelf → squared off); runs 1–3 VEML 0.33 / 0.95 / 0.997 from the cap ring → 0.8 forward of the proposal; run 4 committed: front 237.2926, cap 9.931 cm³; lanes clear; 75 s |
| `v5f_c2d_fillets_checks.py` | c2 | c1e4's classified fillets (A 3 edges R0.8, B 3 R0.3, C 1 R0.3, one feature) + checks; exhaust open length at mid-wall (containment) | run 1 on c2c's front (237.2748; exhaust by rays from inside, superseded); run 2 on c2i's front: 236.6852 cm³, 1 lump each; front ∩ cap / door, cap ∩ door 0; pad 169.5 / 172.5 = boss bottom at all four; axis open to the insert hole end 178.5, top 180.0 above; KO_capkey_* ∩ every part and lead 0; exhaust 81.75 / 82.25 of 90 mm open → 492 mm²; 142 s |
| `v5f_c2d2_exhaust_wall.py` | c2 | read-only: exhaust open length at mid-wall (REF hit along −y, point 2.4 inside along its normal, containment), 0.25 steps | on c2c's front 468.7 mm² (incl. the SL/SR lane ribs near x ±43); 722 rays 370 s (lesson 59) – c2d run 2 does it by containment |
| `v5f_c2e_sections.py` | c2 | read-only: section loops S1 x 0, S2 x 25.91 (BL), S3 x 43.36 (SL), S4 plan z 165, S5 plan z 177.9 → `HA_panel_renders/c2_sections.json`, plotted off-line | run 1 had S4 at z 168 (above the lanes' start); its z 165 plan showed SL/SR's inner rib not reaching the back wall → c2i; final run after c2d run 2 |
| `v5f_c2f_renders.py`, `v5f_c2f2_renders_ortho.py` | c2 | checkpoint renders (assembled, exploded, cap underside, pads from above, inside views with and without the key lanes, top) | c2f's first orthographic shot after a perspective one came out at the wrong scale (lesson 54 amended); c2f2 applies the camera twice; `~/Documents/HA_panel_renders/HA_v5f_c2_*.png` |
| `v5f_c2g_save.py` | c2 | guards, named WIP version | "rev F WIP 2026-11-05 c2: …" saved, 214 bodies |
| `v5f_c2h_lip_vertical.py` | c2 | the cap's lip (c1's d-band, leaning with the walls) made vertical: top slice z 175.3–175.85 copied down in 0.5 steps to z 173.3; insertion sweep gate | before: cap lifted 0.75–1.75 ∩ front 13–29 mm³ (the cap could not go on – also true in c1); after 0 at every h 0.1–4.0; cap 9.931 → 9.9147 cm³ (old → `HOUSING_F_cap_c2a`) |
| `v5f_c2i_front_ribs.py` | c2 | front shell rebuilt from c0 as c2c but SL/SR with one rib along the wall normal on the outer side (the inner lane-aligned rib hung free below z ≈ 167); rib rooting gate; insertion sweep | front 236.7029 (old → `HOUSING_F_front_c2a`); every rib rooted in the wall (16.6–17.8 mm³ below z 166); 107 s |
| `v5f_x1_exploded_doc.py` | x | separate document **"HA Panel v5 - exploded view (rev F c2)"** (same project folder): 19 components (one per part group), bodies copied at their true positions, explode offsets in the occurrence transforms (cap up 85, display stack along the slab normal 60 / 95 / 135, boxes ±95, speakers ±95 / +60, door −150, grommet −185, 5807 −105, main board and BME680 −60, Pi −85 / −35, feet −25, radar 50 along its normal); colours printed blue-grey, cap orange, boards green, LCD / speakers / feet dark; renders `HA_v5f_c2_exploded_{rear34,front34}.png` | saved; the design model is only read (cloth, leads, keep-outs, tools not copied) |
| `v5f_d0_sections.py` | d | read-only: section loops for the d-round pictures (PLANES / OUT set per step; variants `v5f_d3c_boxR_sections.py`, `v5f_d4a_inlet_sections.py`) | JSON → plotted off-line |
| `v5f_d1_bracket_feet.py`, `v5f_d1b_bracket_merge.py` | d | audit 22: bracket screwed from below – front floor bosses at (±49.5, −58.0) removed, Ø3.4 + Ø6.5 × 1.0 c-bore through the floor; MAIN_BRACKET foot bosses Ø8 z 2.5–8.6 with Ruthex M3 holes Ø4.0 z 2.4–9.5, old tab holes plugged; d1b rebuilt the bracket from the pieces the combine had split | front 236.6852 → 236.1819, bracket 4.9002 → 5.3418 cm³ (2 lumps = the L/R prints); bracket halves sweep 0; old → `*_d0`, split pieces → `MAIN_BRACKET_d1split_*` (hidden) |
| `v5f_d2_boxL_bore.py` | d | audit 27: SPKBOX_L lower screw bore Ø6.2 re-cut y −53…−19 through the B4i USB slot's walls | box 25.6228 → 25.3206; tool line clear 130 mm |
| `v5f_d3_touch_clips_deflector.py` (+ `d3b`, `d3e`, `d3f`, read-only `d3d` / `d3d2`) | d | audit 24 / Daniel 2a: TOUCH_CLIP_L / R (0.4896 cm³ each) screwed to blocks on the boxes (M3 × 8 self-tapping into Ø2.5 pilots), front tabs / lips cut; audit 36 / 1a: cooler-exhaust deflector pocket on SPKBOX_R's inboard wall (stepped 0.5 ledges, z 13–26.5), its wall closed at the edges (d3e), lower bore re-cut twice (d3b / d3f) | touch PCB tilt-in only the designed seat face; clip paths 0; box chambers L 117.69 / 86.10, R 118.13 / 86.24 cm³ sealed (R lost 2.9: 121.05 / 89.16 before); box paths 0 |
| `v5f_d4b1_probe.py`, `v5f_d4b2_probe.py` | d | read-only: door / grommet / cradle geometry and trial booleans (stub 7.4 mm³, flange add 61.9 mm³, pin fill = hole 8.62 mm³, web after 0.80) | inputs for d4c |
| `v5f_d4c_door_grommet_cradle.py` | d | audit 7 (flange 0.4 → 0.85 by lifted slice copies), 8 (RR stub cut, cradle leftover hole filled), 9 (pin holes Ø1.7 at ±13.85, old Ø2.1 filled with the wall profile; grommet pins Ø1.5), 33 (grommet rebuilt: opening to z 30.1 outside the door's outer face, 0.8 collar in the cloth layer, flange to z 33.1), 2 (webs 4 wide between the tangent cradle legs / floor bosses); the door bosses to z 2.5 (undone in d4e) | door 51.101 → 51.2068, grommet 0.4889 → 0.5062, cradle 2.1564 → 2.1709, front → 236.1755; 22 probes ok |
| `v5f_d4e_boss_pads.py` | d | audit 32 done printably: the door prints on its bottom edge, so the bosses back to z 2.8 and Ø8 × 0.3 pads (z 2.5–2.8) on the floor under them | door 51.1616, front 236.2249; door ∩ front 0 |
| `v5f_d4f_checks.py`, `v5f_d4g_pin_dimple.py`, `v5f_d4h_save.py` | d | checks (overlaps of every changed region 0; cradle ∩ PD_5807_env 64.71 unchanged); two orphan Ø2.2 × 0.03 recesses removed with DeleteFace (wall + floor) on a copy that then became HOUSING_F_door; version | door 51.1617; grommet / door-band sweeps 30 mm in 0.5: 0 hits; "rev F WIP 2026-11-06 d4" |
| `v5f_d5a_probe.py`, `v5f_d5c_probe.py`, `v5f_d5d_probe.py` | d | read-only: voids, magnet pockets, Pi bosses, sections (shelf, exhaust rows, floor, door, lip end, BME680 / LD2410C corners), shelf tip extent, lip lower edge per x | inputs for d5b / d5e / d5g |
| `v5f_d5b_front_small.py` | d | audit 1 (two speaker-bore voids filled exactly), 3 (10 magnet pocket floors +0.2: skin 0.49 on the axis, pocket 1.6), 14 (Pi seats Ø6.8, rear hole skins 1.5) | front 236.2249 → 236.3673; seats ∩ Pi 0 |
| `v5f_d5e_vents_posts_shelf.py`, `v5f_d5f_save.py` | d | audit 35 / Daniel 1a: intake 100 → 475 × Ø2 on the same grid (1 492 mm²); door: 12 vertical slots 3.0 wide, x_rel −24…42, z 66 to min(110, lip − 6) (1 504 mm²); audit 10: two 1.2 posts per exhaust row (wall profile); audit 6: shelf 0.4 land | front 233.5171, door 47.2694 cm³; hole cut volume exact (375 × 7.854); "rev F WIP 2026-11-06 d5" |
| `v5f_d5g_ld_ribs.py` | d | audit 40: two heat-stake ribs 1.2 × 6.0 behind the LD2410C's short edges (0.1 clear), staked over its back edges | front 233.5399; module path 4 mm inward 0; ribs ∩ parts 0 |
| `v5f_d5h_root_fillets.py` | d | audit 13, load-bearing roots: cradle floor bosses R0.8, Pi bosses R0.5, cradle legs R0.8, 5807 posts R0.5, bracket feet R0.8; door boss junctions failed (ASM_ABL_CAP_COMPLEX where they run into the cove) – door unchanged | front 233.5514, cradle 2.1775, bracket 5.3431 |
| `v5f_d6a_cap_probe.py`, `v5f_d6b_cap_fixes.py`, `v5f_d6c_save.py` | d | audit 1 (cap void filled), 38 (4 seat pads per strip pocket, 0.7 under the plate: gasket 1.0 → 0.7); MIC strip envelopes split strip / gasket | cap 9.9147 → 9.9227; envelopes ∩ cap 7.63 = the pins; "rev F WIP 2026-11-06 d6" |
| `v5f_d7a_matrix.py` | d | read-only: full matrix on the audit's 83-part list + the two clips (433 pairs) | 76 non-zero: 70 as in the audit, 6 changed by design (pins in the thinner strip envelopes; door ∩ KO_capkey_* smaller where the vent slots cut the door), 0 new, 0 gone |
| `v5f_d_sweep.py`, `v5f_d_tools.py`, `v5f_d_box_air.py` | d | the audit's a3a / a3b / a5a with a volume guard in place of the audited state | d-round sweeps all 0 (boxes, bracket halves, clips, touch tilt-in, grommet, door band, cradle, cap, LD2410C); strips into the cap: the pins through the strip holes only (as in the audit) |
| `v5f_d7c_export.py` | d | RENDER_FABRIC_front hidden; version; f3d; STEP per printed part incl. the cap and the clips | see the d-round checkpoint |
| `v5f_d8a_veml_probe.py`, `v5f_d8b_veml_pins.py` | d | audit 40, Daniel's caliper (board 15.26 × 15.20, Ø2.1 holes 11.0 apart): two Ø1.8 heat-stake pins at x_rel ±5.5, y −28.23 (hole inset 2.13 assumed) inside 1.0 stand-off collars Ø3.2, two 1.0 seat pads at the header-edge corners; board top 1.0 under the pocket ceiling (sensor 0.85), centred on the lux port; VEML_env rebuilt (board 1.6 assumed + sensor + 4 mm jumper band), LEAD_VEML extended to the board | cap 9.9227 → 9.9591; env ∩ cap 0; board up into the cap 0 |
| `v5f_d9a_bme_probe.py`, `v5f_d9b_lead_probe.py`, `v5f_d9c_bme_cup.py`, `v5f_d9e_bme_tilt_sweep.py` | d | audit 37, decision 1 b (20 × 15 × 6 placeholder): first form, an open-top cup with a lid – the board could not drop in (the wall leans in above the cup; tilted, its face hit the cup's back wall) → replaced, kept hidden (`*_d9c`) | sweeps: straight down 79.9 mm³, tilted 0.5–133 mm³ |
| `v5f_d9f_bme_tray_hood.py`, `v5f_d9g_bme_groove_hood.py` | d | second form: tray moulded to the wall (floor + 45° underside, side walls 2.4, corner pads, lead slot, pins) + separate hood (back + top plate) | board in along −w 0; hood on 0 against the shell |
| `v5f_d10a_lip_probe.py`, `v5f_d10b_lip_stations.py`, `v5f_d10c_lip_square_end.py`, `v5f_d10d_lip_end_loft.py` | d | audit 4, decision 2 a: the end curve of the lip's outer face swept along d = (0, 0.957, −0.289) (the band's normal at the top) as a loft tool TOOL_lip_end (kept hidden); only the inner face's overhang goes, the outer lap face keeps its length | knife edges < 30° at the end 1 → 0 (min 58.8°); front −0.548 cm³; d10c (union of 300 station boxes) failed – lesson 69 |
| `v5f_d11a_sd_probe.py`, `v5f_d11b_sd_space.py` | d | read-only: microSD extender (decision 3 A) – card end, right box, the space behind it | no extender route fits as decided (1.15 to the box wall; the plug rides in with the Pi) – superseded by d13a |
| `v5f_d12a_bme_up.py` | d | the BME680 tray sat in the right box's B5j-3 path (sideways at lift 6, 72.5 mm³): everything 6 mm further up the wall (+10 from the original), underside clipped at z 83 (1.0 over the box's top in the path), board 0.6 further from the wall; front rebuilt from `_d9` and the lip-end cut re-applied; foam envelopes A13 behind the board, A12 under the hood's top | front 235.3238, BME_HOOD 0.8029 cm³; right box B5j-3 path 0; board in 0 (LEAD_RADAR crosses its path: BME680 first); hood on 0; cap 4 mm down 0; VEML up 0 |
| `v5f_d12b_matrix.py` | d | read-only: d7a's matrix on the pairs with a changed body (d7's list + BME_HOOD and the two foam envelopes) | 140 pairs, 13 non-zero: as in d7 except 3 designed (foam ∩ top foam 19.95, front ∩ top foam 1.16, VEML_env ∩ LEAD_VEML 15.55 → 18.73) and 2 gone (BME680_env ∩ LEAD_BME680 2.22, BME680_env ∩ front 0.16) |
| `v5f_d12c_save_export.py` | d | version, f3d, STEP of the changed parts (front, cap) and the new BME_HOOD (d7d's method) | "rev F WIP 2026-11-06 d12 …" saved; `revF-d12.f3d` 82.8 MB; STEP front / cap / bme_hood, 1 lump each |
| `v5f_d13a_sd_options.py` | d | read-only: microSD access (Daniel 18:00: required) – card geometry, both chambers, trial regions vs the part list and the chamber air: floor hatch, rear tunnel, extender channel, socket / reader zones, a second USB-A plug | card x_rel −44.85…−29.45, z 6.71–7.41 (grip end 6.41–7.41 over the outer 1.72, nothing below it); chamber air lost (R lower bound 86.24): hatch pocket 0.71, rear tunnel 1.29, extender channel 3.65 (+ basket envelope 97 mm³); rear exit blocked by the bracket foot (37.7 mm³) and the tie bridge (22.7); second USB-A plug ∩ +x box 461, ∩ basket envelope 191 |
| `v5f_d13b_pi_upright.py` | d | read-only: Daniel 19:08 – the Pi stood on its short edge against either box (envelope 90 × 58 × 20 from PI5_F) | needs z 3–93, the ReSpeaker carrier starts at z 84; overlaps MAIN_front_env by 24.5 cm³ on either side, plus a touch clip, the LCD lane keep-out (right) and the DSI / GPIO / sensor leads; the cooler blows out of the SD end – into the ReSpeaker (card up) or the floor 3 mm away (card down). Not taken |
| `v5f_d14a_sd_hatch.py` | d | microSD floor hatch (option 1, Daniel 19:22): SPKBOX_R + walls (1.5, inside the old chamber air, r 3.15 kept clear round the lower bore) − pocket x_rel −61.0…−45.9, y −36.2…−23.6, z 3.0…8.0 (open toward the Pi and downward; opens the bore's bottom: a 4.3 slot at z 8.0, the Ø5.5 head can't drop in); front − 17.7 × 13.0 slot through the floor − 0.8 underside rebate; HATCH_COVER (flange flush with the underside, plug, two 10 mm side beams with 45° / 45° catches seating on the floor's top in the 1.2 gap under the box, fingernail notch); SD_SLED (hidden service tool: shoulder on the underside, stem, platform at z 6.41, back-stop) | SPKBOX_R 25.6435 → 25.5694, front 235.3238 → 234.7010 (−622.8 mm³ = slot + rebate, floor solid there), cover 0.5860, sled 1.1956 cm³; 1 lump each; 14 / 14 probes; old → `*_d14`, tools `TOOL_sd_*` hidden |
| `v5f_d14b_hatch_checks.py` | d | read-only: box air, SPKBOX_R's added material vs its old chamber air, the bore's head path, the card's way out and back, the tweezers' zones, the sled's path | chambers R 117.424 / 85.527 (was 118.131 / 86.235), L 117.690 / 86.099, both sealed; added 333.37 mm³, 0.0 outside the old chamber air (outer shape and insertion path unchanged); Ø5.5 head path 0; card out sideways and down: only the cover (404.8 mm³, it closes the slot); tweezers zones free; sled + card (up 8, push 14.75) 0 except the sled's 0.35 over-travel into the seated card (2.49 mm³ at 14.75) |
| `v5f_d14c_matrix.py` | d | read-only: d7a's matrix on the pairs with SPKBOX_R, the front or HATCH_COVER (d12's list + the cover) | 102 pairs, 4 non-zero, all as in d7 / d12 (SPK_R ∩ box 66.99, touch PCB ∩ front 3.16, box ∩ LEAD_SPK_R 0.97, front ∩ top foam 1.16); the cover 0 with every part |
| `v5f_d14d_save_export.py` | d | version, f3d, STEP of the changed parts (front, SPKBOX_R) and the new cover and sled | "rev F WIP 2026-11-06 d14 …" saved; `revF-d14.f3d`; STEP front / spkbox_R / hatch_cover / sd_sled |
| `v5f_d15a_ext_probe.py` | d | read-only: Daniel 19:44 (the hatch is not usable): extender route to a fingertip push-push socket – plug pocket widened for an 8 × 18 stiffener, flex under / behind the right box, socket zones at the back | plug pocket +0.87 cm³ chamber air, Ø40 basket envelope 45 mm³; flex under the box free; the back-right corner is too tight for a socket (door wall 8–14 behind the box) and the back face at floor level is full (bracket feet, Pi power plug, cradle, door bosses). Not taken |
| `v5f_d16a_finger_notch.py`, `v5f_d16d_box_reraise.py` | d | Daniel 19:52 / 19:58: finger notch, no extender, the box made taller. SPKBOX_R rebuilt from `SPKBOX_R_d14`: finger channel x_rel −64.0…−45.9 from the rear face to y −31.0, up to z 16.0, open at the bottom and toward the Pi, + card slot x_rel −61.3…−45.9, y −36.2…−23.6, to z 8.5 (walls 1.5 = W ∩ the old chamber air; the lower bore a sealed tube from y −31 forward); top +6 mm (copies of the top 6 mm, outer and air, clipped to TOOL_cav_1p2 / _2p7_slide) except over x_rel ≤ −56.9 at y −60…−24, the LCD lane strip and y > −10 – d16a's wider raise hit RESP_CARRIER (42 inboard, lift 6) and the BME680 tray (sideways move) in the B5j-3 sweep; d16d with the channel ending at y −30 touched the Ø40 basket envelope by 42 mm³, so it ends at y −31. Front back to `HOUSING_F_front_d14` without the right floor tie bridge (in the finger's way); HATCH_COVER, SD_SLED → `*_d16` | SPKBOX_R 25.6435 → 26.3874 cm³ (old states `SPKBOX_R_d16`, `_d16a`, `_d16d`), front 235.3238 → 235.2295 (bridge −94.3 mm³); chamber R 118.066 / 86.171 (was 118.131 / 86.235), sealed; Ø5.5 head path 0; 10 / 10 probes |
| `v5f_d16b_notch_checks.py`, `v5f_d16c_matrix.py` | d | read-only: the finger's way in (between the bracket post and the lip, along the channel to its front wall `CY1`, at the card's end), its clear width (rays along ±x from x_rel −61 at 7 stations behind the box × 8 heights, every part but the door), the card's way out, the cooler exhaust window; changed-pairs matrix; B5j-3 sweep with `v5f_d_sweep.py` | way in 15.0–16.1 wide at y −62.3 between the shell's back corner and the bracket column (z 8.5–25), 17.7–19.6 at y −59, ≥ 21 from y −56.5 in; the column and foot stand behind the channel's inboard half (d16 checkpoint, Blocked); channel and grip-end zones free; card out free; exhaust window ∩ box 0; B5j-3 237 steps 0; matrix 99 pairs, 4 non-zero: 3 as in d7 / d12, SPK_R ∩ box 66.99 → 68.66 (the card slot's wall corner vs the Ø40 envelope) |
| `v5f_d16e_save_export.py` | d | version, f3d, STEP front / spkbox_R | see the d16 checkpoint |
| `v5f_d16f_bridge_fin.py` | d | d16b's entry zone found a 0.1 × 4.0 × 5.4 fin on the floor: d16a cut the tie bridge to x_rel −61.7, it ran to −61.8 (d14: x −61.8…−55.2). Front minus x −62.0…−61.5 over the bridge's y / z; old state → `HOUSING_F_front_d16f` | front 235.2295 → 235.2273 (−2.18 mm³), 1 lump; no lump above the floor round the bridge; 4 / 4 probes |
| `v5f_d16g_save_export.py` | d | version d16f, f3d (replaces revF-d16.f3d), STEP front | see the d16 checkpoint |
| `v5f_d0_sections.py` (d16h: planes set by the loader) | d | read-only: plans z 7 / 12 / 16, sections x_rel −55, y −33 / −58 / −62.3; floor plans z 0.3 / 1.2 / 4 and z 30 / 38 round the right-back corner | the bracket's right column and foot stand behind the channel's inboard half (d16 checkpoint, Blocked); floor solid, no holes, at (−66, −57.5); the speaker lead runs at z 28–41 |
| `v5f_d17a_bracket_probe.py` | d | read-only: Daniel 21:00 – crank the bracket column. The right bracket half per height; the floor round the old foot and the new spot; the shell's and the door's inner faces round the new foot, leg and knee (bars on cropped bodies, not rays: d16b's 112 rays took 10 min) | right half: foot boss Ø8 z 2.5–8.6, tab x −53.5…−46.5 z 8–11, column x −52.5…−46.5 / y −62.5…−58.5 to z 84.5, board-boss arms z 33.5–41.5 and 76.5–84.5; floor top z 2.5 at both feet, 2.55 on the tie bridge's footprint; shell's inner face x −69.0…−66.9 at y −62.5 and −72.9…−69.7 at y −58.5 (z 8–30); the door's bottom flange reaches y −61.4 at x −68 |
| `v5f_d17b_bracket_crank.py` | d | MAIN_BRACKET's right half: foot, tab and column below z 21 cut (x −54.5…−44.5); new foot boss Ø8 z 2.5–11 with the Ruthex M3 hole Ø4.0 z 2.4–9.5 at (−65.0, −57.0); leg x −67.5…−62.0, y −59.5…−55.0 to z 27; knee x −66.0…−46.5, y −62.5…−55.0, z 21–27 (to −67.5 over the leg); 45° gusset under the knee at the leg (x −62…−58, z 17–21). Front: the old Ø3.4 + Ø6.5 × 1.0 c-bore filled, the same cut at the new axis, the tie bridge's 0.05 base layer cut (d16a / d16f cut from z 2.55; the floor's top is 2.5). At x −65.5 the new c-bore met the joint's underside relief by 0.49 mm³, at −65.0 by 0.26 (below the head's seat) | bracket 5.3431 → 6.1301 cm³, 2 lumps; front 235.2273 → 235.2269 (fill +46.8, hole −46.5, base layer −0.72 mm³), 1 lump; bracket ∩ every part 0 except MAIN_front_env 724.91 (designed, unchanged); 17 / 17 probes |
| `v5f_d17c_finger_check.py` | d | read-only, lesson 76: a straight finger on the floor (bottom z 2.9), tip at y −33.5 with its inboard edge at x −45.5, stadium sections 13.5 × 11 / 14.5 × 12 / 16 × 13 / 17 × 14 back to y −95, vs every part but the door; the right box's lower-screw driver (Ø6 along y from behind to the bore's mouth) and the new foot screw's driver (Ø6 from below) | before d17b (control): finger ∩ MAIN_BRACKET 445.06 mm³ (foot + column), box driver ∩ bracket 108.9; after d17b and after d17e: 0, 0, 0 |
| `v5f_d17d_matrix.py` | d | read-only: changed-pairs matrix for MAIN_BRACKET and the front (d16c's method; run on d17b and on d17e); right-half and door sweeps with `v5f_d_sweep.py` (the audit's runs 18 and 31: the half from 30 back at 1.5 inboard, lift 0.5; the door from 80 back, cropped to the right-back corner) | 111 pairs, 3 non-zero, all as before (TOUCH_PCB ∩ front 3.16, MAIN_front_env ∩ bracket 724.91, front ∩ FOAM_bme_top_env 1.16); right half 65 steps 0; door 161 steps 0 |
| `v5f_d17e_leg.py` | d | the leg 5.5 × 4.5 → 5.5 × 6.5 (y −60.5…−54.0) over z 10.5–21: twice the old column's bending section about x | bracket 6.1301 → 6.2403 cm³; 2.0 behind the box's rear face; ∩ parts unchanged; d17c, the sweeps and the matrix re-run on it |
| `v5f_d17g_save_export.py` | d | version d17, f3d, STEP front / main_bracket | see the d17 checkpoint |
| `v5f_d18a_exploded_prints.py` | d | read-only (a temporary document, closed unsaved): Daniel 21:33 "exploded view of the individual prints" – the 14 printed parts as of d17 (the bracket halves separate) exploded along y in assembly order, offsets picked with a bounding-box occlusion check so none hides another from 15° behind the right side, 35° up; rendered at twice the viewport with each print's centroid and projected box for the labels, then each print alone (fit view). Labels and the parts sheet composed off-line | `~/Documents/HA_panel_renders/HA_v5f_d17_prints_{exploded,sheet}.png`; 14 prints, 450 g of ASA as solid volume |
| `v5f_d19a_print_assess.py` | d | read-only: Daniel 21:49 "assess these parts for printability". B6o's method for the 14 prints (the bracket halves split by x) over 8 build directions: faces more than 45° down need support, the bed's own faces excluded; flat ceilings (within 11° of down); for the best and the +z direction the support faces joined into regions (shared mesh nodes) with area, world box and mean angle. Re-run after d19d | in each print's B6o orientation (mm²): front 11 506, cap 295 (top face down; 3 060 as fitted), slab 2 392 (on its side), carrier 0, door 285, grommet 241, 5807 cradle 170, bracket L 152 → 122 and R 278 → 245 after d19d, BME680 hood 34, boxes L 1 975 / R 2 592, clips 8 |
| `v5f_d19b_fix_probe.py` | d | read-only: room under the LD2410C cradle's floor and under the bracket's lower arms – candidate boxes vs every part (the door included), the right box's B5j-3 path inside the cradle's box; the front sliced round the cradle | under the cradle only the BME680 items (y ≤ −25.37); under the arms only the bracket; the right box's path stays out of the cradle's box. The slices failed (ASM_BODY_VERTEX_CRUMBLE on 0.1 slices of the cropped front) |
| `v5f_d19c_fix_probe2.py` | d | read-only: two rib slabs under the cradle's floor (y −24.5…−22.5, −11…−9) vs every part and keep-out, the side wall's inner face in them per height; the bracket's gusset boxes vs every part; the cap top face down by region | rib slabs free; inner face x −88.83 at z 86 to −85.41 at z 114.1 (y −23.5); gusset boxes meet only the bracket's own arm (64.47 mm³); cap: one 163 mm² region (the top face's edge round, its first 0.9 mm) and pocket steps of ≤ 10 mm² |
| `v5f_d19d_print_fixes.py` | d | (A, checked, not applied) a 2.0 rib with a 46° underside under the cradle's floor, from the side wall (1.0 into it, plane fitted to the measured inner face) to the floor's free edge, at y0 −24.5…−17.0, vs every part and keep-out, the BME680 board's and hood's paths (along −w, here from 14 out), the LD2410C's (run 26) and the right box's top on B5j-3. (B, applied) a 46° gusset under each lower board-boss arm (z 33.5) over the column's y range −62.5…−58.5, from 0.5 inside the column to x ±38.0, up to z 35.7 (MAIN_front_env starts at 35.8), minus the Ø4.0 insert hole; the added material (new minus old) checked at rest, on the half's own path (runs 17 / 18), the main board's (19), the Pi adapter's (27) and the door's (31) | A: the floor is a pad turned 31° with the module, joined to the side wall only at y −26.5…−21 and to the front wall at its front corner; ribs at y0 −24.5 / −23.0 / −21.5 meet BME_HOOD on its way in from 1.0 / 3.5 / 6.0 mm out (≤ 2.89 mm³); −20.0 and −18.5 clear everything but leave the floor's back half (≈ 160 mm²) and its tall support: not applied. B: +158.0 mm³ a side, 1 lump each, 0 with every part and on every path (the door never reaches them); MAIN_BRACKET 6.2403 → 6.5563 cm³, 2 lumps; old → `MAIN_BRACKET_d19`; 16 / 16 probes |
| `v5f_d19e_front_regions.py`, `v5f_d0_sections.py` (d19f planes) | d | read-only: every support region (≥ 2 mm²) of the front floor down and of the cap, door, 5807 cradle, boxes, carrier and hood in their orientations; sections and plans round the cap seat (z 150–182), the LD2410C cradle and the front's bottom edge | front: 550 regions, 11 497 mm²; 49 of ≥ 30 mm² hold 9 610: cloth recess 1 757, bottom edge 725 + 2 × 231 + 2 × 55, under-slab groove 659 + 426, slab ledges 499 + 468 + 107 + 49, rear rim 647, cradle floor 329, BME680 tray 305 + 32 (45° faces and the 1.2 flat at the wall's foot), cap seat, its four screw lobes and the vent bars (z 160–172) ≈ 1 400 – ledges on the back wall's top and bridges of 9–17 mm between the vent ribs –, four Ø13 recesses at z 0.5 (4 × 129); 501 regions under 30 mm² hold 1 887 |
| `v5f_d19g_save_export.py` | d | version d19, f3d, STEP main_bracket | see the d19 checkpoint |
| `v5f_d20a_exploded_doc.py` | d | Daniel 23:20 "an exploded view of the model in Fusion so I can inspect the parts": the 14 prints as of d19 copied into a new direct-design document, one component per print, world frame (z up, x centred), each occurrence moved by d18a's offset; d18a's three colours; saved next to the design model; the design model only read | "HA Panel v5 - exploded prints (d19)", version 1, 14 components, volumes as the copies; materials Steel as in the design model (no masses from it) |

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
16. `shellFeatures` with `insideThickness` on a copy of INNER_E makes the layer **inside the cavity** along the inner
    surface. A lip cut from it touches the other part's inner surface (zero clearance) and joins its own wall only along an
    edge; use an offset layer (0.2…1.4) and give it a root band on its own wall, or a later cut splits it off.
17. A combine that disconnects a body leaves several bodies, and the original name can land on the small piece (here the
    lip kept "HOUSING_F_front" and the shell became "HOUSING_F_front (1)"). Check names and `lumps` after every combine.
18. Surface normals for oriented pockets: `comp.findBRepUsingPoint(p, BRepFaceEntityType, 0.005, False)` → the INNER_E face
    → `face.evaluator.getNormalAtPoint(p)` (outward = into the wall).
19. While a long script keeps Fusion busy, MCP calls to Fusion time out, but the Filesystem MCP still answers: read the
    result with `read_text_file(~/Documents/v5f_log.json, tail=N)` instead of a Fusion read script.
20. `pointContainment` on INNER_E is slow (seconds per point): a probe grid over a chamber cannot finish inside the MCP
    timeout. Test fits with TemporaryBRep booleans against tool bodies made once and stored hidden (offset cavities from
    `shellFeatures`, ∩ a copy moved along the assembly path) and read volumes: 0.3–1 s per boolean on these bodies.
21. After a timed-out call the Fusion connector can stay "failed" ("Version negotiation failed …"); it does not recover by
    itself. Check with `get_device_info`; the connection has to be restarted on the Mac.
22. To find an unexpected overlap, intersect the two bodies and list the result's `lumps` with world bounding boxes
    (R2b-3, R2f): one call instead of a probe search.
23. Path checks need steps shorter than the thinnest feature passed: R2d's 5 mm steps found a 0.5 mm³ contact at u 55 that
    R2b-4's 10 mm steps had stepped over; at 1 mm it spans u 50…58.
24. Booleans with the 47-solid PI5_F union take ≈ 30 s each against the full front shell (R2d's Pi path: 14 min for 30, Fusion
    blocked meanwhile). Crop both bodies to the region and z band that matter first (R2h: 71 steps in 6 s), and get
    clearances from vertices (lowest PI5_F vertex over each boss) before sweeping.
25. A rev E generator step can be re-run as a NEW body with one parameter changed and diffed against REF_E_outer
    (B3b: F − E only at the edited edge, E − F = 0); applying only the difference keeps every later block's work. The p17
    `build()` deletes BODY_E / INNER_E / HOUSING_E and `moveslab()` moves the slab – copy the loft / cut / fillet code
    only.
26. Wall check: `shellFeatures` insideThickness t on a copy of the OUTER reference gives the t-layer inside the outer
    surface; (layer ∩ region) − body = every place thinner than t (normal), and it can be joined as the fix (B3d).
    `measureManager.measureMinimumDistance(face, face)` gives the point pair for a single spot (B3a, B3c).
27. `comp.findBRepUsingRay(origin, dir, BRepFaceEntityType, -1, visibleOnly, hitPoints)` returns every face crossed with its
    hit point: wall thickness along a line, surface normals (face.evaluator), and line-of-sight checks through hidden
    bodies (visibleOnly False) – B3h, B3j.
28. Tight world bounding boxes: copy the body, transform the copy with the design → world matrix (rotation +12° about x,
    translation H in z: cells (1,1)=C, (1,2)=−S, (2,1)=S, (2,2)=C, (2,3)=H/10) and read `boundingBox` (B4e). Design boxes
    converted corner by corner are inflated by the tilt (a 22 mm tall LCD part gains 4.8 mm in y).
29. Parts parallel to the LCD are easiest in design coordinates: boxes with axes (1,0,0)/(0,1,0) and cylinders along design Y,
    positions as (x_rel, d = −Y, Z) (B4h carrier, the LCD's own standoffs give d and Z directly).
30. Long ray probes over the whole component are slow (126 `findBRepUsingRay` calls with ~140 bodies > 60 s, B4k). Read a
    large log entry with a small read-only script that loads `v5f_log.json` and prints compact text, instead of tailing
    thousands of JSON lines.
31. Re-derive hole positions from the source frame before modelling: B4c/B4d placed the 5807 posts at the wrong edge; the
    Eagle frame (Y toward the USB-C edge, top view) mapped onto the pose (Y → −y, top up) gives X → −x (B4g).
32. Leads as tube bodies: TemporaryBRep cylinders per segment + spheres at the joints, bbox pre-filter on the obstacles, PI5_F
    cropped to the lead's box before the boolean (13 leads in one call, B4n). Cylinder ends are flat, so a lead ending at a
    connector face does not register as an overlap.
33. A STEP whose parts are merged into one body (Waveshare PCBA, 2451 faces): intersect it with a region box and list the
    region's planar faces (normal, area, point) to find a connector's FPC slot (B4m).
34. A shell input of faces instead of the body removes those faces: an INNER_E copy shelled 2.1 with its top cap removed gives
    the wall band without the cap's layer (TOOL_inner_cup_2p1, B5c-1, 0.5 s).
35. An inward shell thicker than a convex fillet radius would degenerate (REF_F_outer's R3 top edges vs 3.2): crop the
    reference first (∩ z ≤ 20 or ∩ z ≥ 160) and pass the crop's cap face to the shell so the cut is not lined (B5c-2).
36. A skin ∩ box removal leaves the feature's parts outside the box as loose lumps; the next combine JOIN makes each of them
    a body `name (n)`. Size removal boxes to the feature's full extent and list `name (n)` bodies after every combine
    (B5e-1: eight R1 pad tips, deleted in B5e-1b).
37. A body added under an existing name becomes `name (1)`; name lookups then return the older body. The stale rev D
    `BME680_env` shadowed B4l's envelope, so the B4l–B4o checks by name used the wrong body; B5e-1 renamed both.
38. `findBRepUsingRay` from inside a hidden reference body returns the surface point and its face in one call: magnet points
    on INNER_E by ray (B5e-2) reproduce R1's 26-step containment bisection (x_rel 59.82 / 41.07 at z 95 / 132) instantly.
39. `camera.isFitView = True` refits to all visible bodies and ignores the eye distance, so a "close-up" comes out as the
    whole housing. For a close-up set `isFitView = False` and place the eye at a fixed distance from the target (B5k-2). A
    480 × 360 check JPEG read through `read_media_file` costs ≥ 25 k tokens (output truncated); a 240 × 180 preview is enough
    to check the framing.
40. Faces normal to a curved wall (ruled surfaces) from TemporaryBRep: one oriented box per station (rays on the old joint
    plane, stations ≥ 2 mm apart), each the half-space in front of the plane through the station point with normal
    u = t × n, unioned in balanced pairs (138 boxes in 6 s). Align t' = n × u with the chord (it came out as −t and swapped
    each box's extents → gaps, 3 lumps) and alternate the non-functional extents between neighbours (20 / 21 deep, s ± 0.4)
    so no side faces are nearly coincident. The faces measured 0.0–0.5° off the wall normal (B6s-3b, B6p).
41. A boolean in which three surfaces meet in one curve fails: the new face pivoting about the old inner edge met the old
    end-face plane and the inner surface there (ASM_INCONS_FACE), and a 0.1 overlap sharing the wall's inner and outer
    surfaces with the target gave ASM_BAD_CONTAINMENT. With the pivot moved 0.2 along u the added wedge has a thickness at
    the inner surface, touches the target face to face on its planar end face and overlaps the floor rim fully – the
    JOIN went through (B6s-3b).
42. Before a risky JOIN / CUT on a main body run the same booleans on a TemporaryBRep copy; if the combine still fails, the
    copy can replace the body (old body hidden, appearance and material copied). Not needed in B6s-3b / B6s-4.
43. A JOIN + CUT of overlapping cylinders left `HOUSING_F_door (1)` with 7.8e-9 cm³ while the door itself stayed 1 lump
    (B6s-4): the target's lump count does not catch it – list `name (n)` bodies after every combine (lesson 36).
44. Normal wall in one call: a hidden "outside" body ((box − REF_F_outer) ∪ (cloth skin − parts)), the inner-surface point
    from a ray, then `measureManager.measureMinimumDistance(point, body)` (B6p). Read the ray's hit point first: a ray from
    the cavity can land on the lip, a pocket or a slot edge.
45. The rev E inner loft is a 2.5 **plan** offset, so the normal wall is 2.5·cos(lean): 2.32–2.35 on the back band above the
    door (lean ≈ 22°), 2.44–2.48 on the door. B3d had filled the band above z 165 to 2.5 normal; block 5 took the D1 layer
    from INNER_E and the recess from REF_F_outer, which put the band back to 2.5·cos(lean). A layer derived from a
    reference inherits the reference's error – check the normal wall after every layer.
46. Overhang numbers per print orientation: `meshManager.createMeshCalculator()` (normal quality), triangle normal × area
    against each candidate build direction; nine parts × 8 directions in 1.4 s (B6o).
47. Extend the matrix filters with each step's hidden copies (`_b5`, `_b6v1`, `_fail1`, …): a copy left in reads as a large
    "interference" with its successor (CRADLE_5807 vs CRADLE_5807_b6v1 1190.67 mm³ in B6V-3's check).
48. A fill bounded by an offset of the outer surface that coincides with an existing inner face is a near-zero sheet where
    the two meet: the 3.2 skin and the D1 surface coincide on the vertical chin (sheet ≈ 0.0002 thick) and the front's union
    failed (ASM_INCONS_FACE; after the fixes of lesson 49, ASM_BODY_VERTEX_CRUMBLE at the sheet's cut edges). Over-target
    by 0.02 (3.22: 2 000 × the modelling tolerance, far below print resolution) so the fill is ≥ 0.02 thick wherever it
    exists, and mask regions that need nothing (B6w-2b…2d).
49. Do not bound a fill with the planes / tools that already cut the same part (slot zone, sensor windows, slots): a fill
    face lying in a part face plus the shared edge fails like lesson 41. Grow those exclusions 0.05 (B6w-2c fixed z 60–160).
50. Take the openings out of the fill before the join (one JOIN per part, nothing re-cut), gate the JOIN on fill ∩ every
    part and a TemporaryBRep union = 1 lump, and bisect a failing union by cropping body and fill to region boxes (B6w-2b).
51. REF_F_outer's front face in the top band is the slot-face plane (design Y −12.4; world y −16.1 at z 160 … −19.8 at
    z 177.2): a world-y crop at −15 missed it and the shell also made a band behind the slot face (c1b). The plane is
    tangent to the two front-corner blends, so passing it to the shell as a removed face fails (SHELL_GENERIC_FAILURE).
    Crop 1.5 behind it with a design-Y box (the crop face cuts the blends at ≈ 45°) and remove the crop face (c1b2).
52. The same shell can fail at one thickness and work at others: crop −13.9 failed at 1.9 and 1.95 and worked at 0.72 and
    4.1…7.3; crop −14.6 worked at 1.9 (c1b5). Move the crop or the thickness before changing the design.
53. 85 TemporaryBRep booleans against big bodies (LCD STEP, door) + 180 rays took 212 s (c1c); bbox-prefilter (lesson 32).
54. After an orthographic shot, a perspective close-up with isFitView False kept the old extents and came out empty
    (c1g); for close-ups use an orthographic camera and set `camera.viewExtents` explicitly (c1g2: 11 ≈ 100 mm wide).
    Amended (c2f2): set the type / eye / target first, assign `viewport.camera`, re-read it, then set `viewExtents` and
    assign again – set in one go, the first orthographic shot after a perspective one comes out at the wrong scale.
55. Order matters when a cut and an addition overlap: c1d cut the spline groove before adding the posts, so the post webs
    partly filled it. Cut functional voids last, and look at sections through every added feature before the fillets –
    a 2-D check of four planes (c1f) found what the volume gates could not.
56. Edge selection by "neighbour face leans outward" also matched the groove's inner wall (it leans with the outer wall):
    classify fillet edges by position as well (point containment in an offset band, c1e4).
57. Check the assembly motion, not only the closed fit. A hook that swings into a slot behind a flush butt joint can't go
    in: every point of the cap face above the pivot moves into the bar when the far end is lifted (Δy = height above the
    pivot × tilt). And a skirt built as an offset band of a leaning wall leans with it: lowered straight down, its bottom
    edge meets the mating flange's top edge (c1/c2 lip, 0.55 interference; fixed in c2h with a vertical skirt). Gate every
    part that is put on with an insertion sweep (part moved back along its path in steps ∩ mating part = 0).
58. A clearance gate made of an offset box ∩ part reports mm³ rounded to 0.01: 0.997 mm of clearance read 0.01 and failed
    a "< 0.01" gate (c2c run 3). Give such gates a stated tolerance and the clearance it stands for.
59. `findBRepUsingRay` is component-wide: ≈ 0.35–0.5 s per ray with ≈ 210 bodies (c2d 362 rays 126 s, c2d2 722 rays 370 s).
    For dense sample grids use `pointContainment` on the one body instead.
60. A part rebuilt from an earlier body brings that body's small features along (c0's inner corner fillet under the cap's
    front edge, to z ≈ 177.3, hit the new shelf in c2c run 1): probe a containment grid next to new mating faces first.
61. Oblique ribs in front of a slot look worse from inside than at the wall: measure an opening where it is (mid-wall
    point 2.4 inside REF – REF surface found by containment bisection, c2d run 2), not by rays from the interior (c2d run 1).
62. Fusion's Python globals persist between MCP runs, `run` included: a snippet that defines no `run()` re-runs the
    previous script's (d4e ran twice; only its guard stopped the second run). Every snippet defines its own `run()`.
    A loader that execs a script into its own dict and calls it there still defines no global `run()`, so the MCP ran
    the last global one after it (d12b re-ran after d13a and d13b): the loader's own `run()` execs and calls the script.
63. Never bind v5f_common's constants (`C`, `S`, `T`, `H`, `XC`) to anything else: d5h's `C = 'CRADLE_5807'` made
    `wy()` / `Dw()` raise, so every edge filter silently found nothing.
64. The MCP call waits 60 s; a longer script keeps running and finishes. Read its result from the log with a read-only
    snippet (with its own `run()`, lesson 62); never re-send the script.
65. Concave-edge test: both points p ± 0.03 along (n1 − n2) inside the body. The outward bisector points into air for
    concave and convex edges alike.
66. `deleteFaceFeatures` heals a shallow recess only when its floor goes with its wall (wall only →
    DELETE_FACES_FAILED_TO_FILL_GAP). Try it on a copy, then swap names.
67. Lengthening a feature below a part's bed face breaks its print orientation (d4c's door bosses): put the extra on the
    mating part instead (d4e's floor pads). Check B6o's orientation before any change at a bed face.
68. Fillets whose edges run into a cove or a tangent-blended region fail with ASM_ABL_CAP_COMPLEX (the door boss / rib /
    wall junctions); boss roots on flat floors and plate undersides work (d5h groups A–E).
69. A union of hundreds of slightly rotated station boxes (d10c, 300 boxes, tree-wise) ran 7 min and failed with
    ASM_INCONS_REL. For a swept end face use one loft between two sketch profiles (d10d: 34 s) and keep the tool's faces
    off the part's existing faces.
70. A TemporaryBRep boolean with a tool face lying on a part face (d10d's first loft started in the lip's end plane) fails
    with ASM_INCONS_REL; start the tool 0.5 behind the plane.
71. A CombineFeature cut can split a sliver off the target as a new visible body `<name> (1)` (d10d: 0.0003 mm³ at the
    lip's foot). After every combine, list the bodies named `<target> (n)` and hide / rename them.
72. `device_commit_files` straight after an edit can upload the previous content (d10d ran the old file twice; the Mac's
    d10b / d10c copies were still the first drafts at close-out): compare the Mac file's size with the local one before running.
73. A part added to a wall must clear the other parts' insertion paths, not only their installed state: the BME680 tray
    passed the matrix but sat in the right box's B5j-3 path (lift 6).
74. Cut a feature away with a box taken from the feature's own bounding box in the old body, grown 0.2, then list the
    region's lumps: d16a's hand-placed box stopped 0.1 short of the floor tie bridge's end and left a 0.1 mm fin, and its
    bottom at z 2.55 left a 0.05 layer (the floor's top is 2.5 there; d17a measured it).
75. A script's module-level names share the helpers' namespace: d16b's station list `WY` replaced v5f_common's world +y
    vector and every box failed. Keep WX / WY / WZ, C, S, H, XC and the helper names free.
76. Empty zones are not a path. d16b's finger zones (way in, channel, grip end) were each clear, but no straight finger
    joins them: the bracket column stands behind the channel's inboard half. Check access with the finger's (or tool's)
    own solid along its line, and look at a plan section before calling a way in usable.
77. Loaders read scripts with `open(path, encoding='utf-8')`: a plain `open()` failed on the en dash in v5f_d_sweep.py's
    header (ascii codec) in the MCP's Python although other scripts with non-ASCII comments had passed.
78. A face drawn at exactly 45° sits on the support test's threshold (n·U = −0.7071): mesh normals fall on both sides of
    it and the count depends on noise. Draw faces meant to print without support at 46°.
79. A sweep's MOVE_CROP must still hold the whole moving piece after its shape changes: run 18's crop (x_rel −60…−30) cut
    off d17's leg (to −69) and the right box and the Pi dropped out of the swept region. Crop the right half at −72…−30
    and compare `fixed_in_region` with the last run's.

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
   (Superseded by R1: with the back off the key goes straight in along the lanes; ≥ 75 mm of shaft, deepest head 53 mm in.)
4. Block 5: the D1 inner layer must not close the speaker bores or lattices.
5. Speaker screws (b2r): the lower-outer M3 heads sit inside the FL/FR door bosses, the upper-outer ones have 27.5 mm of
   straight room, and from the open chamber bottom no key reaches a horizontal screw (ball end ≤ ≈ 25° off-axis; an
   L-key's long leg meets the basket envelope or the walls). Fixing options in the checkpoint report; the FL/FR bosses
   also block a speaker insertion path at y −6…−3.66 (boss front face y −3.66).

## R1 checkpoint (2026-11-04)
Rear door split at y −55 with a solid floor (Daniel 2026-11-03 23:41 – 11-04 08:40). Built and checked in R1a–R1e.
- Door: HOUSING_F_door 55.484 cm³, removal straight back (−y), clear of the front shell and the 5807 from 1 to 80 mm.
- Joint: 0.3 gap at the plane and above the floor; the front shell's lip (cavity layer 0.2…1.4, y −53.5…−63) under the door
  wall, 0.2 normal clearance; r 4.0 notches along all four LCD-screw lanes.
- Magnets: 10 pairs Ø8 × 1.5 N52 across the lap, axis on the INNER_E normal, at (z, y) (25, −59) (60, −59) (95, −59)
  (132, −58) (150, −56.5) per side. Faces 1.4 apart (0.9 door skin + 0.2 lap + 0.3 lip skin). Pull per pair, surface-charge
  model, uniform magnetisation: 3.8 N (Br 1.42 T) – 4.1 N (Br 1.48 T) at 1.4 mm; 2.8–3.0 N at 2.0; ideal values, real
  magnets lower. The pull seats each magnet on its pocket floor; with the door off the lip magnets rest in pockets open to
  the cavity (retention open item).
- Screws: 4 × DIN912 M3 × 6 from below at x_rel ±19 (y −74.5) and ±50 (y −67.0), Ø3.4 + Ø6.5 × 1.0 counterbore in the
  floor, Ruthex M3 in Ø8 door bosses (z 2.8–10.5, hole Ø4.0 to z 9.5), 4.2 mm thread engagement.
- USB-C: Adafruit 5807 flat on the door centre line, PCB z 14.0–15.6, socket centre z 17.2, receptacle face y −84.6; door
  slot x ±10.5, z 12.7–19.2 (bezel in block 4). The board fills the 7.5 mm reservation behind the Pi edge: the display
  ribbon has to leave the Pi upward/forward.
- Feet SJ5012: FL/FR x_rel ±84, y −6.5; RL/RR ±30, −69.0.
Open from R1: magnet retention with the door off; D1 = 0.7 re-run of the lip and magnets in block 5; 5807 cradle + bezel,
main-board floor bracket (block 4); R2 speaker boxes and the USB-plug pocket.

## R2 checkpoint (2026-11-04)
Separate speaker boxes, fitted from the back before the Pi (plan accepted 2026-11-03 22:54; magnets Ø8 × 1.5 N52 × 10 pairs
kept, lip magnets with a drop of CA – Daniel 2026-11-04 20:31). Built in R2c, checked in R2d / R2f.
- Shell (HOUSING_F_front 265.519 → 238.880 cm³, 1 lump): b2d chamber partitions removed for y ≤ 1.2, back partitions and
  ceilings removed (all ∩ INNER_E); the cheeks y ≥ 1.2 keep the touch-PCB retention. Baffle stop pads Ø7.5, y 0.0…0.9, at
  the 4 frame corners (x_rel ±52.75 / ±88.25, z 10.25 / 45.75). Ø2.5 pilots y −0.5…5.0 at the inboard corners for
  M3 × 10 DIN912 self-tapping (tip y 4.3, 4.3 mm engagement, 1.8 skin in front after the D1 recess); outboard b2e pilots filled.
- Boxes SPKBOX_L (+x) 25.321 cm³, SPKBOX_R (−x) 25.071 cm³ (≈ 26 g ASA solid each): outer x_rel ±46.0…wall,
  y −52.0…−3.7, z 3.0…76.0, ∩ (INNER_E − 1.2) at the final pose and 1.0 behind it (sideways slide); walls 1.5, front wall
  2.0 (y −5.7…−3.7); 3.5 × 3.5 step along the bottom-outboard edge (floor cove R3.5 + D1); basket hole Ø40.6; box stop pads
  Ø7.5 y −3.9…−3.0 at the 4 frame corners (rings Ø7.5 / Ø3.4 inboard, discs outboard); pegs Ø3.2 y −3.7…−0.2 in the
  outboard frame holes; clamp holes Ø3.4 at the inboard frame holes; tubes Ø8 / bore Ø6.2 from the front wall back through
  the rear wall; wire hole Ø3 at (x_rel ±62, z 30). +x box only: sealed USB-A plug pocket, void x_rel 44…55.15,
  y −36.95…−20.95, z 9.95…17.95 (walls 1.5) – fits only if the real basket is ≤ Ø32 over its rear 10 mm (bench check).
- Stack at the frame corners: box front wall → 0.7 (rear foam, set by the box pads) → frame 3.0 → 0.7 (front gasket, set by
  the baffle pads) → baffle. Foam: 1 mm closed-cell, compressed to 0.7.
- Fixing: speaker on the box on the bench (2 pegs locate the outboard holes); in the housing 2 × M3 × 10 DIN912 per box
  through the tubes and the inboard frame holes into the baffle pilots (head seat y −5.7, socket top y −8.7: 43.3 mm in
  from the box's rear face); the 2.5 mm ball-end key ≥ 75 mm of the LCD screws fits. Self-tapping instead of Ruthex
  accepted by Daniel (2026-11-04 21:58): an insert hole would leave ≈ 0.1 mm of chin skin (0.8 after D1).
- Air (net of tubes and pocket): +x 88.04–117.30, −x 89.09–118.47 cm³ (lower value = the whole Ø40 basket envelope
  subtracted). DMA45-4 closed box (Fs 151.4 Hz, Qts 0.56, Vas 85 cm³): Qtc 0.785 / F3 193 Hz at 88 cm³, 0.735 / 191 Hz at
  117 cm³.
- Insertion (each box with its speaker): lift 6 (box bottom z 9.0 > Pi boss tops 8.0), in along +y at 40 mm inboard,
  sideways out to the final x 1.0 behind the final pose, lower 6, push 1.0 forward onto the gasket, 2 screws from behind.
  At 37 inboard the box's top-outboard front corner touches the lip's rear end (≤ 0.93 mm³, R2f).
- Pi (after the boxes): in from behind 2.0 above its seat, then lowered (at 1.0 the microSD socket, underside z 6.56,
  hits the rear −x Pi boss, top 8.0).
- Assembly order: LCD (screws via the lanes) → speaker boxes → touch PCB → main board / ReSpeaker / sensors / USB-C → Pi →
  cables → door.
- Checks (R2d, R2f–R2h): boxes vs every other part, the front shell, the other box and the closed door 0. Box ∩ speaker
  envelope = the pegs (2 × 22.5 mm³, by design: the envelope has no holes) + the basket envelope's rear end vs the outboard
  wall (≈ 22 mm³ per side, y −21.6…−29.1) + on +x the pocket vs the basket envelope (112 mm³, y −19.45…−29.1); both lie in
  the rear 10 mm of the basket and clear if the real basket is ≤ Ø32 there. Box paths at 1 mm steps 0 with the 40 entry
  offset; Pi path at 1 mm steps 0 with the 2.0 lift (vs bosses, floor, front shell, both boxes); clamp-key paths Ø6.2 from
  the box rear face to y −90 vs the front shell 0, bores open.
Open from R2:
1. Bench: DMA45-4 basket ≤ Ø32 over its rear 10 mm (plug pocket and outboard walls); otherwise relieve the outboard wall
   locally and rework the pocket.
2. Block 4: the ReSpeaker's USB-A plug cannot be pushed into the Pi with the +x box fitted (the pocket gives 10 mm in front
   of the port, the inserted plug's length, with no room for its insertion travel). Decided (Daniel 2026-11-04 21:58):
   side-exit right-angle USB-A plug, plugged into the Pi before the Pi goes in; the +x box pocket becomes a sealed channel
   to the box's rear face (≈ 3 cm³ less air). Model and check in block 4.
3. Block 4: re-check the Pi path (2.0 lift) against the main board, ReSpeaker, sensors and 5807 fitted before it.
4. Bench: M3 × 10 self-tapping into the ASA Ø2.5 pilots, 5 drive cycles.
5. Block 5: D1 = 0.7 re-run (lip, magnets); the boxes' 1.2 wall clearance already includes D1 0.7 + 0.5.

## Block 3 checkpoint (2026-11-04)
Daniel 2026-11-04 22:07: continue without the time stop; R3 and the local top-edge rebuild taken as recommended.
- D2: top edge R3 all round (rear was R10, front already R3) via REF_F_outer and the difference only (B3b/B3c); the rev E
  sharp inner top edge rounded R1.0 (INNER_F); wall ≥ 2.5 (normal) everywhere above z 165 (B3d, checked with the 2.5 skin of
  REF_F_outer). Fixes the 0.08 mm wall found at the inner top-front corners (B3a). Hard band to the groove's upper edge
  (block 5, groove ≥ 0.5 below the R3 tangent): 3.2 on the sides, 2.3 at the back. Front shell 238.880 → 240.593 cm³.
- Top sensors (B3f): port line y −26.5 (brief ≈ 5 behind the slab's top edge; the inner top's front round ends at y −23.4,
  6.4 is the closest a 6-wide strip fits). Mic strips 30 × 6 × 0.8 at x_rel ±(7.5…37.5), mic 2.0 from the outboard end under
  Ø1.5 ports at ±35.5; pockets 30.4 × 6.4 × 0.8 (1.7 wall above); stack gasket 1.0 + strip 0.8 → strip back at z 176.5,
  back parts ≤ 4.9, cable bend ≥ 10 (keep-outs modelled). Heat-stake pins Ø1.8 × 3.5 at ±11.5 / ±30.0 (B1 lays the
  strip around them; the gasket needs Ø2.2 holes there). Deviation from rev D: rev D's strips ±(22…52) with pins ±27 / ±49.5
  carried the lux sensor on the strip; the separate VEML6030 breakout under the Ø2 port at +46 sits where rev D's +x strip was.
- VEML6030 (provisional, E0 issue 8 – outline, holes and chip position unmeasured): pocket 15.4 × 15.4 × 0.8, lux port Ø2 at
  (x_rel 46, y −31.0) on the assumption the chip is at the board centre; a 15 × 15 board with its leads (6 mm envelope)
  touches the upper back wall at its back-outboard corner (5.2 mm³) – a 13 × 13 board clears. Retention after the caliper
  measurement.
- LD2410C (B3h–B3j): at z 115–140 there is no ≈ 40° corner surface – the slot face meets the side wall in a sharp ≈ 63° inner
  corner, and the brief's 40° board does not fit there with 2.0 air. Built on the corner bisector, 59° from +y toward −x
  (antenna face centre x_rel −72.5, y −22.1, z 127.5; 2.0 air; cradle with lips and a skirt to the walls). Line of sight
  from the antenna: < ≈ 30° from +y the LCD panel (metal) and glass, 30–65° the housing corner + the slab's printed border
  (≈ 16 mm of print at 59°), > 65° the side wall only. Decision needed (open item 1).
- Checks: front vs slab, glass, all LCD_*, door, both boxes, the four lanes: 0; designed contacts only (pins in the strip
  envelopes and keep-outs); front vs door 0 with the joint gap restored.
- Version "rev F WIP 2026-11-04 b3 …" saved; `HA Panel v5 - tapered revF-wip-b3.f3d` 25.6 MB; renders HA_v5f_b3_*.
Open from block 3:
1. LD2410C direction (Daniel): keep the corner at 59° (LCD shadows the front sector below ≈ 30°), face it along the side wall
   (≈ 110°, 2.5 wall + 2.0 air, sees 50–170°), or move it to a place with a clear forward view.
2. VEML6030 board measurement (outline, holes, chip position) → pocket, port position and retention.
3. Mic cable path to the ReSpeaker (block 4, with the ReSpeaker placement); strip PCB layout (B1) around the pins.
4. Top groove + rail (block 5) at ≥ 0.5 below the R3 tangent (sides z ≤ 176.8, back ≤ 177.7).

## Block 4 checkpoint (2026-11-05)
Electronics mounts and cables. Daniel 2026-11-04 21:58: side-exit right-angle USB-A plug pre-plugged into the Pi, +x box
pocket → channel to the box's rear face; M3 × 10 self-tapping speaker clamps. Built in B4b–B4o, saved as "rev F WIP
2026-11-05 b4 …" (`revF-wip-b4.f3d`, 26.0 MB, 142 bodies).
- Main board (D21, candidate A): MAIN_pcb x_rel ±45, y −65.0…−63.4, z 34–84 on MAIN_BRACKET (two printed L/R halves, posts
  x_rel ±(46.5…52.5), Ruthex M2.5 bosses at (±41.5, z 37.5 / 80.5), tabs on floor bosses (±49.5, −58.0), M3 × 6).
- 5807 inlet (K17): the R1 premise was wrong – the Pi 5's CAM/DISP connectors are vertical-entry at y −57.3…−41.8 in front
  of the rear edge (B4f), so the DSI FPC leaves upward and the 5807 behind the edge is clear of it. Holes corrected to the
  receptacle end (B4g): door inlet cutout x ±11.3, z 7.7–20.5; CRADLE_5807 with a bezel filling the cutout (0.3 gap,
  receptacle window x ±4.67, face flush at y −84.6, so any overmould stays outside); 2 × M2 × 6 into Ruthex M2 posts;
  cradle fixed by 2 × M3 × 6 at (±5.5, −72.5) behind the main board. Pigtail 25 mm up to an XH near the main board's bottom
  edge.
- ReSpeaker (K14): RESP_CARRIER on the LCD's four Pi standoffs (4 × M2.5 × 5), board behind the LCD between the K5 lane pairs,
  mic side toward the carrier, USB-C at the +x end: straight plug (12.4 × 6.6 × 32 allowance) between the lower and upper
  +x lanes with ≥ 10 mm to both. Zip-tie slots 7.5 above each vacated mic pad. LCD + carrier + ReSpeaker go in from the front
  as one module (sweep 2…30 mm through the boss opening and the slab window: 0).
- +x box: slot along the USB-A plug's travel (Pi in from behind at lift 2.0), open toward the Pi and through the rear face;
  air −2.69 cm³ (+x 85.35–114.61 cm³). Pi + plug path 0.
- BME680 (K15, provisional 20 × 15 × 6): back-right corner above the −x box at (−76.82, −45, 92), two 14 × 3 slots behind the
  cloth. Exhaust (K18): 2 × 90 × 3 slots above the door joint (z 167–170 / 171.5–174.5), 540 mm² (rev D start); slot tools
  kept for the re-cut after the D1 layer (block 5). Floor tie anchors at (±58.5, −56.5) (2 of 3; the third on the V11 run).
- V11 (B4j, overlaps in mm³): straight plug – 20.86 mm to the door wall, 74.8 into it; adapter up – main board PCB 31.4 + back
  envelope 264.1; adapter +x – cradle 338.3, 5807 141.0, RR door boss 10.2; adapter −x – door 260.9, bracket 143.1; elbow up –
  back envelope 2.8 (0.2 mm); elbow ±x – cradle 47.1 / door 46.3. Decision needed (open item 1).

Routed lengths (centreline, B4n/B4o; K11 slack ≥ 50 on top):
| Lead | routed mm | cable | to buy / cut |
|---|---|---|---|
| GPIO plug A (9) / B (4) | 49 / 50 to a nominal landing at x_rel −20…0, z 45–50 inside MAIN_front_env | pre-crimped F-F | 15 cm leads (20 cm leave 150) |
| LCD 5 V + GND (LCD's own lead, 2 terminals in plug A) | 141 + 14 housing = 155 | owned 4-pin lead, unmeasured | needs ≥ 205 (Measure 2) |
| Mic L / R | 71 / 69 | JST SR 305 | cut to ≈ 120 |
| Speaker L / R | 28 outside + ≈ 25 in the box | XH 2P 300 | cut to ≈ 105 |
| Radar | 71 | XH 4P 300 | cut to ≈ 120 |
| Touch | 54 | XH 4P 300 | cut to ≈ 105 |
| VEML6030 / BME680 | 138 / 96 | Dupont 300 | cut to ≈ 190 / 150 |
| 20 V pigtail | 25 | XH 2P 300 | cut to ≈ 75 |
| ReSpeaker USB (A side-exit → C straight) | 129 outside + 18.5 slot + plugs ≈ 47 = 194 receptacle to receptacle | angled A-to-C | 0.25 m (56 slack) |
| DSI FPC (22 → 15) | 149 + folds | 300 | 300 (Daniel's 200: ≈ 40 slack, too short) |
| Pi power (V11) | a ≈ 90 / b ≈ 140 | 0.2 m + adapter / 0.5 m elbow | a ≈ 110 / b ≈ 360 slack |

Assembly order: LCD + carrier + ReSpeaker (mic cables soldered and tied, DSI FPC and LCD lead on the LCD) from the front,
4 × M3 × 6 via the K5 lanes → mic strips (SR plugs) → speaker boxes → touch PCB (+ BME680 / VEML6030 leads) → main board +
bracket → Pi from behind (GPIO plugs A/B on the header, USB-A plug in the box slot) → Pi power (V11) → 5807 cradle + 5807 →
cables → door.
Open from block 4:
1. V11 (Daniel): (a) adapter (female toward +x) + 0.2 m straight cable along the floor behind the Pi to a USB4105 on the main
   board's bottom edge facing down at x_rel ≈ +25; needs the 5807 raised 6.5 (receptacle centre z 23.7, cradle on legs behind
   the cable), the RR door boss moved 2.5 back (y −77.0) – ≈ 110 slack, one extra contact pair (bench 2.7); (b) 0.5 m elbow
   (up-bending), fits as built, ≈ 360 mm stowed above the main board.
2. LD2410C direction (from block 3, Daniel).
3. LCD DSI connector entry side (STEP slot open on both sides; +x assumed) and the real Active Cooler around CAM/DISP 1 (the
   S-scaled cooler box covers y ≥ −50.1 above the connector) – bench.
4. LCD 4-pin lead length (≥ 205 needed); the LCD lead's terminals ride in plug A, which goes in with the Pi (≈ 70 mm travel) –
   or fit plug A after the Pi – bench.
5. BME680 / VEML6030 outlines (caliper) → retention; DMA45-4 basket ≤ Ø32 over its rear 10 mm (slot walls now 266 mm³ inside
   the Ø40 envelope).
6. B1 keep-outs: MAIN_front_env top-left corner (x_rel < −41.45, y > −37) below z 83 (−x lower lane); the four bracket bosses
   (Ø8, y −63.4…−57.7); connector positions used for the routes (GPIO landing x −20…0, z 45–50; XH speaker x ±40, z 40;
   radar x −37, z 80; touch x 4, z 60; pigtail x 0, z 37.5); Pi-power USB4105 per V11.
7. LCD Pi standoffs: M2.5 thread depth unknown (M2.5 × 5 assumed); USB plug overmoulds unmeasured (allowances above).
8. Block 5: re-cut the exhaust and BME680 slots after the D1 inner layer (TOOL_exhaust_slots, TOOL_bme680_slots).

## Block 5 checkpoint (2026-11-05)
Fabric (D1, D2). Built in B5c–B5i on the block 4 state, checked in B5j, saved as "rev F WIP 2026-11-05 b5 …"
(`revF-wip-b5.f3d`, 35.6 MB, 153 bodies: + 10 hidden tool bodies, + GROMMET_usbc_F). Renders `HA_v5f_b5_{rear34,front34,
under,lap,topgroove,grommet}.png`.
- Wall under the cloth (D1): 0.7 inner layer (TOOL_inner_skin_0p7 ∩ z 2.5–175.3, thickened floor cove R2.8 concentric with
  the R6 edge fillet) on both parts, then the 0.7 recess (TOOL_outer_skin_0p7 ∩ z ≤ 175.3): the wall moves 0.7 inward and stays
  2.5, the cloth face is the rev F outer surface. Measured along rays: 0.7–0.8 recess over 2.5–2.9 plastic (chin, sides, rear
  corners, door back, back above the door, bottom bend). Exceptions: none behind the slot face / boss; none on the flat floor
  (the 6 mm underside strip sits on 1.8 plastic – the speaker boxes stand 0.5 above the floor, so a flat-floor layer would hit
  them); at the VEML6030 envelope (provisional 15 × 15 board) a local 1.8 wall and a notch in the rail (a 13 × 13 board clears
  both).
- Fabric zone: chin band (to the under-slab groove), both sides, rear corners, door, the back band above the door, bottom
  fillet + 6 mm underside strip forward of the joint. Hard: top band (3.2 above the top groove), slot face / boss, underside
  inside the strip, floor rim behind the joint (z 0–2.5; the door's 2.8 bottom edge sits above it).
- Top groove (D2): constant z 175.3–176.8 (upper edge 0.5 below the R3 tangent on the sides, 0.9 at the back; hard band 3.2),
  2.0 deep below the recessed surface (2.7 below the cloth face), round the sides, rear corners and back (y < −22.5); rail
  2.1 behind it (z 173.8–177.6) → groove floor 1.9–2.0. Exhaust slots re-cut through the rail's lower 0.7.
- Under-slab groove: rev D position relative to the slab (design Z −93.43…−91.93, 1.5–3.0 above the slab's bottom edge,
  hidden), x_rel ±93.5, depths below the recessed surface: 2.0 where the speaker baffles back it (|x_rel| ≥ 48); 1.3 over a
  0.5 floor across the touch PCB (|x_rel| < 48: its top edge is right behind the groove, no room for a rail).
- Lap joint at D1 (R1/R2 open item): lip s −0.9…−2.1 (0.2 under the door's new inner surface), root band to y −53.5, pads
  s −0.9…−3.0, door pockets from s +0.2 (0.9 skin), magnet faces 1.4 apart as in R1. Magnets z 25 / 60 moved back to
  y −59.7 / −59.5 (thicker pads vs the boxes' insertion pose), z 150 to y −57.5 (the door pocket was 0.94 inside the door's
  end face). Lip extended to y −63.5.
- USB-C grommet: GROMMET_usbc_F (0.49 cm³) – flange 1.0 on the cloth face (x ±15.1, z 4.7–23.5, R2) covering the cloth's cut
  edge by ≥ 2.2, sleeve 0.8 through cloth + wall round the cradle bezel (0.3), 2 × Ø1.8 heat-stake pins through the door;
  door cutout x ±12.2, z 6.8–21.4. Door + grommet come off together over the bezel (0 at 1…80 mm).
- Feet: front SJ5012 moved from (x_rel ±84, y −6.5) to (±80, −11.5), clear of the strip; front Pi insert holes' bottoms
  z 0.8 → 1.5.
- Housekeeping: the stale rev D `BME680_env` had shadowed B4l's envelope (`BME680_env (1)`); renamed (B5e-1). R1 pad tips
  deleted (B5e-1b).
- Volumes: front 242.147 → 237.918 cm³, door 55.102 → 53.572, grommet 0.488.
- Checks (B5j-1): front ∩ door 0; grommet ∩ front / door 0. Front: TOUCH_PCB 3.16 mm³ (face contact with the D1 layer), strip
  pins 9.16 × 2 / 8.65 × 2 (designed, unchanged), VEML_env 2.04 and BME680_env 0.08 (provisional boards). Door: K5 lanes
  101–167 (the lanes run out through the door opening and are used with the door off), MAIN_back_env 0.74 (top corners,
  B1 keep-out). Slot face hard at Z 36 and −91; 10/10 magnets (pocket open, 0.9 skin, lap gap, 0.3 pad skin); LD2410C: no
  layer within 4.0 of the antenna face.
- Speaker boxes: R2's insertion path now brushes the rebuilt lip's rear end (≤ 0.23 mm³) and, lifted ≥ 4 at the final x, the
  D1 layer on the leaning side wall (2.6–112 mm³) (B5j-2). New path, 0 at every step (B5j-3): lift 6 → slide in at 42
  inboard → sideways to 1 inboard, 1.0 behind the final y → lower → last 1 mm outboard on the floor → push 1.0 forward.
- Cloth pieces: front belt (chin band, sides, rear corners, back band above the door; its ends meet in one ≈ 10 mm butt seam
  at the back centre above the arch) and door panel. No seam termination was chosen at checkpoint 1, so both cloth ends are
  flush-cut at the joint as built; along the arch the door's end face meets its cloth face at 22–44°.

Open from block 5:
1. Seam termination at the joint (Daniel): (a) flush-cut as built – the cut ends sit at the 0.3 joint line, the door's edge
   along the arch is acute (22–44°); (b) re-cut both joint faces normal to the wall and wrap the cloth round them (lip, pads
   and magnet pockets rebuilt); (c) a spline groove along both joint edges (a hard band on each side, like the top).
   Recommended (a); (c) if the bench cloth sample lifts at the arch.
2. V11 (from block 4) and the LD2410C direction (from block 3) – Daniel.
3. Under-slab groove: the middle 96 mm (|x_rel| < 48) is 1.3 deep over a 0.5 floor with no rail (the brief asked for a rail):
   cloth tucked + contact adhesive there.
4. Underside strip: 1.8 plastic under the cloth (2.5 everywhere else).
5. Assembly order: speaker boxes by the B5j-3 path; grommet pins heat-staked to the door at assembly; the grommet moves
   + 6.5 with the 5807 if V11 (a).
6. VEML6030 / BME680 outlines (caliper) → retention and the VEML pocket wall; MAIN_back_env top corners (B1 keep-out).

## Block 6 (2026-11-05)
Daniel 2026-11-05 09:16: seam (b), V11 option 1, LD2410C kept at 59°. Built in B6V-1…3 and B6s-1…4, verified in B6p, B6p2
and B6m, saved as "rev F 2026-11-03 final (Claude)" (`HA Panel v5 - tapered revF-final.f3d`, 41.1 MB, 170 bodies, 21 visible),
STEP per printed part `~/Documents/HA_v5f_<part>.step` (world frame), renders `~/Documents/HA_v5f_final_*.png`.
- V11 option 1: 90° adapter on the Pi's USB-C + 0.2 m straight cable along the floor to a USB4105 on the main board's bottom
  edge (plug x_rel 18.8…31.2, z 14.0–33.9): route 25.3, plug tip to plug tip 77.3, **122.7 mm slack**. 5807, cradle, envelopes
  and pigtail up 6.5 (receptacle centre z 23.7, pigtail 19.4 mm); door inlet x ±12.2, z 13.3–27.9; grommet rebuilt at z 20.6;
  door RR boss at (x_rel −19, y −77.0); cradle legs Ø8 z 8.0–14.6 on floor bosses at (+6.5, −72.5) / (−1.5, −72.5), M3 × 12
  DIN912 into Ruthex M3.
- Seam (b), option I (inner edges kept; the joint plane meets the wall 40–69° off normal, B6s-1): front face through the old
  inner edge + 0.2 along u, door face 1.7 behind it, both containing the wall normal → 0.7 cloth wrapped on each face, 0.3
  between the cloths. The visible seam moved 2.6–3.1 mm back in y (to y −57.7…−58.3, near-planar), lip / root band /
  speaker boxes unchanged; 10 magnet pairs moved 1.10–1.89 along the surface (door pocket rim 1.05 from the door face),
  pads and lip pockets with them. Front 237.930 → 239.797, door 53.536 → 50.601 cm³.
- Interference (B6m, 78 parts, 354 pairs, 0 failures): 72 non-zero pairs, all designed or known –
  front: TOUCH_PCB 3.16 (face contact with the D1 layer), strip pins in MIC_strip_L/R_env 9.16 × 2 and KO_mic_L/R_back
  8.65 × 2, VEML_env 2.04 / BME680_env 0.08 (provisional boards); door: K5 lanes 100.9–166.4 (the lanes leave through the
  door opening, used with the door off), MAIN_back_env 0.74 (B1 keep-out); front ∩ door 0, grommet 0;
  CRADLE_5807 ∩ PD_5807_env 64.71 (underside keep-out); speaker boxes vs the Ø40 basket envelope 266.28 / 66.99 and
  SPK_L ∩ USBA_plug_env 20.8 (clear if the real basket is ≤ Ø32 over its rear 10 mm – bench); MAIN_front_env vs the bracket
  724.91 and the leads ending at its connectors (GPIO A 252.72, B 128.22, touch 58.38, speakers 46.81 × 2, pigtail 29.30,
  radar 22.90); KO_K5_LR ∩ MAIN_front_env 3.08 (B1 keep-out); Pi: GPIO plug envelopes on the header (PI5_F 77.96 / 28.75,
  cooler box 77.14 / 28.88, KO_K7_fan ∩ plug B 25.28 – header-edge drawing tolerance), PI5_F ∩ cooler box 12.75 (2 × 2
  header), cooler box ∩ LEAD_DSI 47.65 (S-scaled box above CAM/DISP – bench), PIPWR_a_env ∩ PI5_F 2.17 and ∩ LEAD_PI_POWER
  10.51; ReSpeaker: carrier bosses in RESP_mic_env 111.91, own envelopes 146.85 / 11.69, mic leads at the pads 43.35 /
  44.08, USB plug ∩ lead 0.38; leads at their ends (DSI at the LCD 0.01 / 0.20 / 11.78, touch cluster 18.87–27.03 and
  1.03–1.86, BME680 2.22, pigtail 5.83 / 0.25, mic strips 16.02 / 16.04, speaker wires through the box holes 0.97 × 2,
  USB_RESP in its cable envelope 6.90); lead crossings SPK_L × USB_RESP 23.26, VEML × DSI 22.27 (dressed at assembly);
  LCD vendor envelopes vs their own connectors / standoffs / headers 33.26–196.35.
- Probes (B6p, B6p2): normal wall chin 2.50, +x side z 60 2.49, −x side z 120 2.46, door rear corner 2.49, door back z 60
  2.48, door side z 100 2.44, top 2.50, bottom fillet 2.50, **back band above the door z 165–170 2.32–2.35** (lesson 45);
  top-front roll 2.50 (inner corner 2.50–2.64); speaker-box walls 1.50–1.58; K5 lanes ≥ 0.31 to every part but the door
  and the B1 keep-out corner (front shell 0.50, boxes 0.31 / 0.45, ReSpeaker carrier 2.50–2.82); front–door minimum 0.20
  (lap), floor-rim gap 0.30 (x 0 / ±40), joint 0.85 + 0.85 (faces 0.0–0.5° off the wall normal); slab on the boss (contact,
  designed), top ring gap 0.30.
- Masses and tipping (B6n): printed ASA 442.7 g / PETG 535.5 g; total 1079.2 / 1172.0 g (components: sheet masses where
  given; Pi + cooler 75, ReSpeaker 12, LD2410C 2, LCD module 254, harness + screws 40, cloth + spline 25 are estimates);
  CoG (x_rel 0.2, y −18.7, z 76.6) / (0.1, −19.1, 77.0). About the rear feet (SJ5012 at (±30, −69.0), contact z −3.0):
  horizontal push at the glass top edge (y −6.67, z 174.67) **3.00 N ASA / 3.23 N PETG** (lever 177.7), 3.38 / 3.64 about
  the contact patches' rear edge (y −75.35); normal to the glass 3.31 / 3.57 (lever 160.8); normal at the screen centre
  5.26 / 5.67. Rev D quoted 2.3 N with a 0.21 m lever; the same convention gives 2.54 N here.
- Print orientation (B6o; support area = faces more than 45° down, bed excluded): front floor down 12 730 mm² (the best of 8;
  roof, slot face, lip and pads, 180 tall); door bottom edge down 208 (154 tall); slab glass side down 4 761 (bed 1 173 –
  the rebate floor bridges 1.2 above the bed) or on its side 2 392 (210 tall); speaker boxes rear face down 1 820–1 943;
  main bracket as installed 251 (2 pieces); ReSpeaker carrier plate down 0; cradle rear face down 169; grommet flange down
  200 (pins up). All fit 256 × 256 × 256. Shrinkage: per-filament Shrinkage % in Bambu Studio (measured ÷ designed × 100
  from one calibration print per material), X-Y hole compensation 0.1 to start – the model stays at nominal size
  (E0-consumables §6a).

Decisions (Daniel 2026-11-05 11:18, "1. a 2. a 3. a"):
1. (a) Wall to 2.5 normal where the shell leans, outside the lap – applied in B6w (below).
2. (a) Seam option I kept as built (visible seam 2.6–3.1 mm back, y −57.7…−58.3; speaker boxes unchanged).
3. (a) Fabric dark grey (F1 knit, as rendered).

B6w (decision 1 a), saved as "rev F 2026-11-03 final r2 (Claude)" (`HA Panel v5 - tapered revF-final-r2.f3d`, 43.7 MB;
`HA_v5f_front.step` / `HA_v5f_door.step` re-exported):
- Fill = plastic down to 3.22 below the cloth face (TOOL_outer_skin_3p22_F) inside the D1 surface, z 6.5–175.2, minus the
  slot zone (d < 15.65 above Z −94.35), the VEML / LD2410C windows, the lap band (TOOL_inner_skin_2p1 ∩ y −67…−52.5: the
  door keeps its 0.2 gap over the lip and pads), the speaker bores / lattices (r 20.5), the clamp pilots (r 1.6) and the chin
  (y > −3: vertical, already 2.50, the touch PCB lies on it). The exhaust / BME680 slots, the inlet cutout and the pin holes
  are taken out of the fill (tools grown 0.05), so each part got one JOIN and no opening changed.
- 3.22, not 3.2: with the exact 3.2 skin the fill is a sheet ≈ 0.0002 thick wherever the wall already is 2.50, and the
  front's union failed (B6w-2, -2b, -2c; lessons 48–50). At 3.22 the sheet is ≥ 0.02 thick → the filled walls are 2.52.
- Front 239.797 → 240.888 cm³ (+1.090), door 50.601 → 51.101 (+0.500), 1 lump each (JOIN, no fallback). Fill ∩ parts:
  only the three pairs already non-zero in B6m. Matrix (B6w-3): 72 non-zero pairs, the same as B6m; door ∩ MAIN_back_env
  0.74 → 1.04, BME680_env ∩ front 0.08 → 0.16. Front ∩ door 0, front–door minimum 0.20, door sweep 0, speaker-box
  insertion path 0 at every step, K5 lanes 0.497 to the front.
- Walls (B6w-2d probes, B6w-4 scan of 317 plan rays, B6w-6): 2.52 wherever filled – sides z 60–150, door back and sides,
  back band z 165–166 and on the slot web z 170.75 (x 0, ±20, ±40); chin and top 2.50; rail 3.70–3.74. Below 2.50 only at
  opening edges (within the 0.05 band the fill keeps from the exhaust / BME680 slots and the inlet: 2.31–2.34 on the slot
  edges), in the VEML window (1.80, provisional envelope, unchanged since block 5) and in the lap band (door over the lip
  2.345–2.487). Masses (B6n re-run): printed ASA 444.4 / PETG 537.5 g (+1.7 / +2.0), total 1080.9 / 1174.0 g; tipping
  3.00 / 3.23 N, unchanged.

Open from block 6 (after B6w):
1. Lap band, left by decision 1 (a): the door's wall over the lip stays 2.35–2.49 normal (2.354 at the door top z 150,
   2.375–2.385 at z 135–140, 2.441–2.446 on the sides at z 100, 2.487 at the rear corner z 40); the 1.2 lip lies 0.2 inside
   it, so the closed joint has 3.55–3.69 of plastic. To reach 2.52 there: thicken the door inward and thin the lip by the
   same amount (≤ 0.17) so the gap stays 0.2. Within 0.05 of the exhaust / BME680 slot edges and the inlet the wall keeps
   its old value (2.34 at the slot corner x 45, z 170).
2. Bench: DMA45-4 basket ≤ Ø32 over its rear 10 mm; Active Cooler around CAM/DISP; LCD DSI entry side; LCD 4-pin lead
   length; BME680 / VEML6030 outlines; M3 × 10 self-tapping into the ASA pilots; magnet pull across 1.4 mm; cloth thickness
   (0.7 assumed – it sets the 1.7 face gap); weigh the estimated components (tipping moves with them).
3. Cloth: dark grey F1 knit; contact adhesive on the wrapped end faces; at the floor the front cloth ends on the hard rim
   behind the joint.

## Cap block c1 – step 1 checkpoint (2026-11-05)
Daniel 13:31: "Make the top piece a cap that gets screwed onto the top so it acts as a clamp for the fabric so it can be
pulled tight. There should be a way to hold the fabric in place while the cap is being tightened down"; 13:51 "1. A 2. A
3. a": spline groove in the ledge (1 A), countersunk M3 from the top (2 A), joint ≈ 3 mm behind the display's top-back
edge, slot face and display ring on the front shell (3 a). Step 1 (this) = split, ledge, holding feature, lip, posts,
screws; step 2 = sensors into the cap, checks, renders, version, STEP. Saved as "rev F WIP 2026-11-05 c1 step 1: …".
- Joint: the front shell keeps y ≥ −22.5 above z 175.3 (3.0 behind the slab's back face y −19.5, where the old top
  groove ended); cap face y −22.6 (0.1 gap). Split at z 175.3 within 7.3 of the outer surface, at z 174.0 further in (the
  four mic heat-stake pins, down to z 174.8, stay on the cap).
- Ledge (front shell): top z 175.3 from the cloth surface (0.7 inside the outer surface) to 5.2 inward; flange 0.72…5.9
  inside the outer surface, z 171.8–175.3, two 0.9 steps under it (5.0 at z 170.95–171.8, 4.1 at z 170.1–170.95, ≈ 45°).
  Outer edge R0.8 (the cloth turns over it), clamp strip 1.2 wide with 0.32 flat at the back.
- Spline groove: 1.2…4.0 inside the cloth surface (2.8 wide), floor z 172.8 (2.5 deep), walls parallel to the outer wall
  (≈ 22° lean at the back), both top edges R0.3, y < −22.5 (ends closed by the front shell). Ø1.8 TPU 95A spline: 0.7 cloth
  each side leaves 1.4 → 0.4 interference.
- Cap (HOUSING_F_cap, 8.94 cm³): the old top above the split; within 7.3 of the outer surface below z 177.2 rebuilt from
  REF (bottom face z 175.8 = 0.5 over the ledge: 0.7 cloth squeezed to 0.5; old groove filled); lip 6.1…7.3 inside the
  outer surface (1.2 thick, 0.2 off the flange), z 173.3–175.8; notch r 4.2 round each post.
- Screws: 4 × ISO 10642 M3 × 8 from the top, Ø3.4 + 90° countersink Ø6.9 (head dk ≤ 6.72 → ≥ 0.09 below flush on the flat
  top z 180), Ruthex M3 in Ø4.0 × 6.0 holes, 5.5 mm of thread in the insert (tip z 172.0, hole floor 171.5). Posts Ø8
  z 170.5–177.5 (top = cap plate underside, so the posts set the 0.5 clamp gap), 45° cone to Ø2 at z 167.5, rib 2.0 with
  a 55° lower edge: FL/FR (±58.4, −27.0) into the front bar (ends z 162.8) with a web z 170.5–173.1; BL/BR (±28.0, −38.1)
  to the back wall (ends z 158.9) with a web to the flange z 171.8–173.1, under the lip.
- Exhaust: the upper row (z 171.5–174.5) sat where the ledge goes – filled by the flange (0.02 left at its outer face);
  new row z 162.5–165.5 (x ±45; 1.16 above the root band at x 0). Lower row z 167.0–170.0 unchanged. 540 mm² less the two
  BL/BR ribs crossing both rows (4 × 2.0 × 3 = 24 mm²) → 516 mm².
- Volumes: front 240.888 → 235.655 cm³, cap 8.942, together +3.709 (flange, posts, rim, lip − groove). Printed parts ASA
  1.05 / PETG 1.27: front 247.4 / 299.3 g, cap 9.4 / 11.4 g.
- Checks: 1 lump each, no duplicate names; front ∩ cap, front ∩ door, cap ∩ door 0; post tops 177.5 = cap plate underside
  at all four; sections S1–S4 (c1f) as drawn in the checkpoint pictures.
- Open for step 2: VEML_env (x 38.5–53.5, y −23.5…−38.5, z 172.3–178.3) intersects the cap's rim / lip (164.8 mm³) and the
  front flange (43.7 mm³) in the +x rear corner – move it; mic pockets start 0.7 behind the cap face (y −23.3); sensor
  pockets / ports / pins on the cap, leads with the cap off; cloth bodies for the new top edge; full matrix, renders,
  version, STEP. MIC strips / KO_mic ∩ cap 9.16 / 8.65 mm³ are the pocket overlaps the front shell had before.

## Cap block c2 – hidden screws checkpoint (2026-11-05)
Daniel 15:26: "That's not quite right because the fastners will be visable from the outside. The lid should have the screw
bosses with the threaded inserts and the screws should come up from the shell into the lid"; answers: front "Hooks into
the bar (Recommended)", VEML6030 "Centre, as proposed (Recommended)". The hook turned out not to be assemblable (below);
15:57 message: option A (two more hidden screws + a shelf) unless Daniel says otherwise. Saved as "rev F WIP 2026-11-05
c2: …".
- Why not the hook: the cap's front face (z 177.5–180) sits 0.1 behind the bar's joint face, above any hook pivot inside
  (z ≈ 174.5). Lifting the cap's back by α moves that face forward by (height above the pivot) · α = 3…5.5 · α: contact
  after 1–2°; pushing a lip 1 mm into a slot with the cap level is blocked by the same face.
- Key lanes (c2a/c2b0, door off, Ø5 for a 2.5 ball-end key): from the cap's lip ring only the back (x ≤ ±31) and, once
  the VEML lead is gone, the rear corners (±43.4, −32.9) are reachable; further forward everything hits the side walls,
  the bar or leads.
- Screws: 4 × DIN912 M3 × 8 from below; Ruthex M3 in Ø8 cap bosses (hole Ø4.0 × 6.0, z 172.5–178.5, 1.5 under the top
  z 180), bosses tangent to the lip's outer face (d 6.1 at z 175.8): BL/BR (±25.91, −37.80), SL/SR (±43.36, −32.85).
  Front-shell pads z 169.5–172.5 (Ø3.4; disk r 5.5 + a strip along the lane, d ≥ 4.1 so they join the flange steps and
  stay off the exhaust slots). Ribs 2.0 with a 55° lower edge, rooted in the wall at d ≥ 1.9: BL/BR two each at ±4.5
  either side of the lane (along the lane); SL/SR one each along the wall normal, 4.5 outboard (c2i: an inboard rib along
  the lane would hang free below z ≈ 167 or cross the exhaust rows). Head z 166.5–169.5, tip z 177.5 (5.0 in the insert).
  Boss bottom on the pad top = the 0.5 clamp gap.
- Lanes (hidden KO_capkey_*): BL → (20, −100, 30) 24.6°, BR mirrored; SL → (20, −100, 30) 27.6°, SR mirrored; ≈ 97 / 102
  inside the unit; clear of every part and lead (c2d). Key reach ≥ 120.
- Front edge: SL/SR are 10.4 behind the joint; a 45° shelf on the bar's back face, top z 177.4 (0.1 under the cap), to
  y −23.3 (0.2 in front of the mic strips), x ±60, keeps the cap's front edge from being pushed down. c0's corner fillet
  under the cap's front edge (to z ≈ 177.3) was squared off for it.
- Lip made vertical (c2h): c1's lip was a d-band and leaned with the walls (0.38 mm/mm at the back), so its bottom edge
  was 0.55 outside the flange's top edge when lowered: the cap could not go on (also in c1). Now the band's top slice
  (z 175.3–175.85) stepped straight down to z 173.3: 0.2 off the flange at z 175.3, ≈ 1.0 at z 173.3; the cap moved up
  0.1–4.0 ∩ front shell = 0 at every step. The skirt's faces are stepped 0.19 per 0.5 (construction; inside, not seen).
- VEML6030 at x −7.5…7.5, y −41.2…−26.2 (0.8 forward of the proposed y −42…−27: the cap ring's inner face leans forward to
  y −42.33 at z 177.2), pocket 15.4 × 15.4 × 0.8, lux port Ø2 at (0, −33.7); old pocket / port filled. Mic strips 29 long
  (x ±8.5…37.5; ports, pins, 71.0 spacing unchanged) so the 15 × 15 VEML envelope keeps 1.0 to them; pockets 0.6 apart.
  LEAD_VEML down the centre, joining the old route at (40, −35, 130): 159.8 routed (was 138); it crosses LEAD_DSI at
  z 86–95 on that old route (22.3 mm³, unchanged; flexible leads).
- Exhaust: 492 mm² open at mid-wall (81.75 / 82.25 of 90 mm; the four BL/BR ribs cross both rows) – c1 by arithmetic 516,
  start 540; intake 314 (100 × Ø2).
- Volumes: front 235.655 → 236.685 cm³, cap 8.942 → 9.915 cm³. ASA 1.05 / PETG 1.27: front 248.5 / 300.6 g, cap
  10.4 / 12.6 g.
- Checks: 1 lump each; front ∩ cap / door, cap ∩ door 0; pad top 172.5 = boss bottom at all four; axis open to 178.5 with
  1.5 above; insertion sweep 0; KO_capkey_* ∩ every part and lead 0; VEML / mic / leads ∩ cap and front 0 apart from the
  pins in the strip envelopes (9.16 / 8.65 mm³ by design).
- Bodies: c1 versions hidden as `*_c1` (front, cap, VEML_env, LEAD_VEML, MIC_strip_*_env, KO_mic_*_back), c2c's as
  `HOUSING_F_front_c2a` / `HOUSING_F_cap_c2a`.
- Open (step 2): cloth bodies for the new top edge, full interference matrix, STEP export; VEML board size (caliper) – if
  ≤ 13 mm the mic strips can stay 30 long.

## Audit response – d-round (2026-11-06)
Input: `claude/report-model-audit-2026-11-05.md` (43 findings). Daniel 10:27: decision 1 a (vents ≈ 5× at the floor intake and
behind the cloth, cooler-exhaust deflector, BME680 in a pocket sealed from the interior air, ASA until a soak test on the
finished unit passes), 2 a (the speaker boxes hold the touch PCB → two clips screwed to the boxes), 3 (cap SL / SR lanes stay
at 27.6°, no test: ball-end sockets owned). Versions "rev F WIP 2026-11-06 d3f / d4 / d5 / d6 / d7".
- Done (finding → change): 1 voids filled (front ×2, cap); 2 webs 4 wide between the tangent cradle legs and floor bosses;
  3 magnet pocket floors +0.2 (skin 0.49 on the axis, pocket 1.6, faces 1.4 → 1.6); 6 shelf 0.4 land; 7 door flange 0.85;
  8 RR stub cut, cradle leftover hole filled; 9 grommet pins Ø1.5 in Ø1.7 holes at ±13.85 (web 0.80); 10 two posts per
  exhaust row (spans 13.0 / 12.4 / 13.0); 13 root fillets at the load-bearing roots (cradle bosses / legs R0.8, Pi bosses
  R0.5, 5807 posts R0.5, bracket feet R0.8 – door boss junctions not possible, lesson 68); 14 Pi seats Ø6.8, rear hole
  skins 1.5; 22 bracket screwed from below (ISO 7380 M3 × 8 into Ruthex M3 in new foot bosses); 24 touch-PCB clips;
  27 +x box lower bore re-cut through the USB slot; 32 0.3 floor pads under the door bosses (not longer bosses, lesson 67);
  33 grommet opening to z 30.1 (overmold ≤ 12.8 centred, was 6.6) with a cloth collar, flange to z 33.1; 35 intake
  314 → 1 492 mm², door slots +1 504 mm² (exhaust 492 → ≈ 1 980 mm²: rows 478 after the posts + slots); 36 deflector on SPKBOX_R (chambers 118.13 / 86.24 cm³,
  sealed); 38 strip seat pads (gasket 1.0 → 0.7); 40 LD2410C heat-stake ribs; 42 RENDER_FABRIC_front hidden, STEP / f3d
  re-exported (12 parts incl. cap and clips).
- Thermal re-estimate (audit model, two outlets at z 166 / 88): interior rise 21–26 K with the cloth passing the slot area,
  24–30 K at half (was 31–43 K); the walls carry about half the 14 W. ASA until the soak test (decision 1 a).
- Checks: matrix 433 pairs (audit's 83 parts + clips) – 76 non-zero, 70 identical to the audit, 6 changed by design, 0 new,
  0 gone; sweeps 0: boxes L / R (B5j-3, with the touch PCB and KO), bracket halves, clips, touch tilt-in (seat face only),
  grommet and door bottom band 30 mm back, cradle, cap 4 mm down, LD2410C 4 mm in; strips into the cap: pins through the
  strip holes only; tool lines: clip screws 60 free, all four box bores 130 free; box-air seals L 117.69 / 86.10,
  R 118.13 / 86.24 cm³.
- Volumes (cm³): front 233.5514, door 47.2694, cap 9.9227, SPKBOX_L 25.6082, SPKBOX_R 25.6435, MAIN_BRACKET 5.3431,
  CRADLE_5807 2.1775, GROMMET_usbc_F 0.5062, TOUCH_CLIP_L / R 0.4896, SLAB_frame 62.9324, RESP_CARRIER 10.0716.
- Exports: `~/Documents/HA_v5f_{front,door,cap,slab,spkbox_L,spkbox_R,main_bracket,resp_carrier,cradle_5807,grommet_usbc,
  touch_clip_L,touch_clip_R}.step` (world frame), `~/Documents/HA Panel v5 - tapered revF-d7.f3d` (75.6 MB).
- Fasteners changed: door 4 × ISO 7380 M3 × 8 from below (heads 0.65 proud, 5.7 in the insert, tip 0.5 short); bracket
  2 × ISO 7380 M3 × 8 from below; clips 2 × M3 × 8 self-tapping into Ø2.5 pilots; Pi 4 × M2.5 × 6; main board 4 × M2.5 × 6;
  5807 and ReSpeaker M2 × 5; M2 inserts → Ruthex M2 × 4 (the XIXIAN OD3.2 don't bite in the Ø3.2 holes); leads cut: mic
  L / R ≥ 175, VEML ≥ 260, radar ≥ 125.
- Open, Daniel: BME680 pocket (CJMCU-680 outline / holes unpublished – caliper, or build to the 20 × 15 × 6 placeholder;
  sensor + slots 4 mm up the wall); lip feather end (station-built end faces, or deburr); microSD extender on the Pi 5 (short
  extender + bench test / card non-service / box wall outboard); VEML retention (board size). Bench: soak test; staking
  (grommet pins, LD ribs, strips onto the pads); self-tapping pilots (clips, boxes); K13 path for the LD2410C; cap-insert
  coupon (finding 34).
- Hidden copies of every replaced state: `*_d0`, `*_d2`, `*_d4`, `*_d4c`, `*_d4e`, `*_d5a`, `*_d5b`, `*_d5e`, `*_d5h0`,
  `*_d6`, `MAIN_BRACKET_d1split_*`; nothing deleted except temporary `D*_tmp` tools.

## Audit response – d8 to d13 (2026-11-06)
Daniel 16:35: VEML6030 by caliper 15.26 × 15.20, Ø2.1 holes 11 mm apart (no tolerance added); 1 b (BME680 to the
20 × 15 × 6 placeholder); 2 a (square lip end – feather edges do not print well); 3 A (short microSD extender, as in the
watch winder). 18:00: card access is a requirement (V1 needs a full strip-down to reach it); three options asked. Version
"rev F WIP 2026-11-06 d12 …".
- Done (finding → change): 40 VEML6030: two Ø1.8 heat-stake pins in Ø3.2 × 1.0 stand-off collars + two 1.0 seat pads,
  board 1.0 under the pocket ceiling, centred on the lux port; 37 BME680: tray moulded to the back-right wall 10 mm up
  the wall from the placeholder's first spot (underside clipped at z 83, 1.0 over the right box's B5j-3 path) + separate
  BME_HOOD (back + top plate, Ø2.4 holes over the pins), A13 foam behind the board and A12 under the hood's top, slots
  moved with it; 4 lip end squared by TOOL_lip_end (the inner face's overhang only, knife edges 1 → 0, min 58.8°).
- Assembly: the BME680 board and hood before the LD2410C lead is dressed (LEAD_RADAR crosses the board's path); the hood
  is staked on the tray's pins. VEML6030 onto its two pins in the cap and staked.
- Checks: right box B5j-3 path 0 (72.5 mm³ with the d9 tray); BME680 board in along −w 0; hood on 0; cap 4 mm down 0;
  VEML board up 0; changed-pairs matrix 140 pairs, 13 non-zero = d7's except 3 designed and 2 gone (d12b row).
- Volumes (cm³): front 235.3238, cap 9.9591, BME_HOOD 0.8029; the rest as in the d-round.
- Exports: `~/Documents/HA_v5f_{front,cap,bme_hood}.step` (world frame; the other parts unchanged since d7),
  `~/Documents/HA Panel v5 - tapered revF-d12.f3d` (82.8 MB).
- Lead: BME680 routed 110, cut ≥ 165.
- Open, Daniel: microSD access (d13a; card in the Pi's slot 1.15 from SPKBOX_R's inboard wall, the slot facing the box):
  1 floor hatch – pocket in SPKBOX_R's inboard-bottom corner open downward (x_rel −61.0…−46.0, y −36.2…−23.6, to z 8.0,
  1.5 walls, joins the lower bore) + 17.7 × 13.0 floor slot with a flush cover; the card is pulled 15.4 toward −x and
  drops out below, door on; chamber R lower bound 86.24 → 85.53. 2 rear tunnel to the box's rear face (→ 84.95), door
  off; the bracket's right foot and the tie bridge move. 3 extender channel along the Pi's slide (→ 82.59), door off,
  push-push socket on the box's rear face; the channel's fold corner meets the basket envelope (97 mm³); High Speed only
  unless the bench shows more. Dropped: USB card reader (a second side-exit USB-A plug meets the +x box and its basket
  envelope). Bench: VEML pin staking; BME680 real board vs the placeholder; hood fit.
- Hidden copies: `*_d8`, `*_d9`, `*_d9c`, `*_d9f`, `*_d10`, `*_d12`, `HOUSING_F_front_d12a`; TOOL_lip_end kept hidden.

## microSD floor hatch – d14 (2026-11-06)
Daniel 18:00: card access is a requirement (V1 needs a full strip-down). 19:22: option 1 as proposed (floor hatch; rear
tunnel and extender channel not taken, the Pi on its edge does not fit – d13b). Version "rev F WIP 2026-11-06 d14 …".
- Service: lift the panel or lay it on its side, unclip HATCH_COVER (fingernail notch), grip the card's 1.0 grip end
  (x_rel −44.85…−43.13; free above and below) with angled tweezers, pull it 15.4 toward −x into the pocket; it drops out
  through the slot. Refit: card on SD_SLED (platform at the socket's height), up through the slot until the shoulder sits
  on the underside, push 14.4 toward +x (the stem stops at the slot's edge 0.35 later), cover back on.
- Changed: SPKBOX_R (pocket + walls), front (slot + rebate); new HATCH_COVER (printed, flange down), SD_SLED (printed tool).
  Door, Pi, boxes' paths, software and the card's speed unchanged.
- Checks: d14b / d14c rows; chamber R lower bound 85.527 cm³ (floor 81.6).
- Volumes (cm³): front 234.7010, SPKBOX_R 25.5694, HATCH_COVER 0.5860, SD_SLED 1.1956; the rest as in d12.
- Exports: `~/Documents/HA_v5f_{front,spkbox_R,hatch_cover,sd_sled}.step` (world frame),
  `~/Documents/HA Panel v5 - tapered revF-d14.f3d`.
- Bench: card out with tweezers in one pull 5 / 5; sled refit seats and boots 5 / 5; the cover's catches hold it and it
  comes off by the notch 5 / 5 (beams 0.7 × 10, catch 0.25 over the floor's edge – trim on the print if needed).
- Hidden copies: `SPKBOX_R_d14`, `HOUSING_F_front_d14`; tools `TOOL_sd_walls`, `TOOL_sd_pocket`, `TOOL_sd_slot`.

## microSD finger notch – d16 (2026-11-06)
Daniel 19:44: the floor hatch (d14) is not usable in practice – removed. 19:52: make the speaker box taller to win back the
air; 19:58: finger notch, no extender. Versions "rev F WIP 2026-11-06 d16 …" and "… d16f …" (the bridge's fin).
- Intended service (does not work as built, see Blocked): door off (4 × M3 from below); a finger in behind the right box,
  along the channel to the card's end (17 mm in from the box's rear face); hook the card's 1.0 grip end with a fingernail
  and pull it 15.4 toward −x into the card slot; draw it back through the channel. Refit: lay the card in the slot and
  push it home with a fingertip. Full card speed, no extender.
- SPKBOX_R: channel + card slot in its inboard-bottom-rear corner; top +6 mm outside the BME680 tray's path, the LCD lane
  strip and the front 10 mm; chamber R lower bound 86.171 cm³ (was 86.235; floor 81.6). The lower screw is driven through
  the channel into the bore's mouth at y −31. The cooler exhaust window (z 13.6–23.1) now partly faces the channel
  (open to the back) below z 16.
- **Blocked (d16b re-run, d16h sections):** the main-board bracket's right column (x_rel −53.5…−47.5, y −62.5…−58.5,
  z 8–84.5) and foot (Ø8 at −49.5 / −58.0, z 2.5–11) stand behind the channel's inboard half. A straight finger must pass
  outboard of them (15.0–16.1 to the shell's back corner at y −62.3, z 8.5–25) and then reach x −45.5 at y −33 inside the
  18.1-wide channel: no finger 12 wide or more can do both. Open: Daniel to choose – crank the column (foot screw to
  about (−66, −57.5), lower column outboard, back to the column above z 17), re-image in place over USB-C (RPIBOOT), or both.
  Fixed in d17 (Daniel 21:00: crank the column).
- Front: solid floor again; the right floor tie bridge is gone (it stood in the finger's way; d16f took its last 0.1 mm)
  – re-place it only if a lead needs it.
- Checks: d16b / d16c rows; B5j-3 path 0; matrix as before except SPK_R ∩ box +1.67 mm³.
- Volumes (cm³): front 235.2273, SPKBOX_R 26.3874; the rest as in d12. HATCH_COVER / SD_SLED hidden (`*_d16`); their
  d14 STEP files are obsolete.
- Exports: `~/Documents/HA_v5f_spkbox_R.step` (d16), `HA_v5f_front.step` (d16f), world frame; `~/Documents/HA Panel v5 -
  tapered revF-d16.f3d` (d16f).
- Hidden copies: `SPKBOX_R_d16`, `_d16a`, `_d16d`; `HOUSING_F_front_d16`, `_d16f`; `HATCH_COVER_d16`, `SD_SLED_d16`.
- Bench: see d17.

## microSD way in – d17 (2026-11-06)
Daniel 21:00: crank the main-board bracket's right column (d16's finger channel was blocked by it). Version "rev F WIP
2026-11-06 d17 …".
- MAIN_BRACKET, right half: the foot screw moves to (−65.0, −57.0), 15.5 outboard and 1.0 forward. A leg (5.5 × 6.5 to z 21,
  5.5 × 4.5 to z 27) rises from the new boss to a knee at z 21–27 that joins the column; the column and the board bosses
  are unchanged from z 21 up. A 45° gusset under the knee at the leg. The knee's flat underside (≈ 105 mm²)
  needs support when the half prints upright (B6o: +z).
- Front floor: the old foot hole and c-bore filled; Ø3.4 + Ø6.5 × 1.0 c-bore at the new axis (its rim touches the joint's
  underside relief by 0.26 mm³, below the head's seat); the tie bridge's 0.05 base layer gone.
- Service: door off (4 × M3 from below); a finger straight in along the floor at x_rel ≈ −52, under the knee (z 21; the
  finger model's top is z 16.9), into the channel to the card's grip end (17 mm past the box's rear face); nail the card
  15.4 toward −x into the slot and draw it back. Refit: lay it in the slot, push it home with a fingertip.
- Checks: d17c finger solid 0 (control before d17b: 445 mm³ on the bracket); the right half's insertion path 0; the door's
  path 0 at the right-back corner; matrix 111 pairs, 3 as before. The right box's lower screw can now be driven with the
  bracket in place (driver line 0).
- Strength: the leg's bending section about x is twice the old column's; the knee offsets the column's load 15.25. Bench:
  push the board's top at the right column; it should move no more than at the left.
- Volumes (cm³): front 235.2269, MAIN_BRACKET 6.2403 (2 lumps), SPKBOX_R 26.3874; the rest as in d12.
- Exports: `~/Documents/HA_v5f_{front,main_bracket}.step` (world frame), `~/Documents/HA Panel v5 - tapered revF-d17.f3d`.
- Hidden copies: `MAIN_BRACKET_d17`, `MAIN_BRACKET_d17e`, `HOUSING_F_front_d17`.
- Bench: card out and back by finger, 5 / 5, door off; the right box's lower screw driven through the channel; the foot
  screw from below; support under the knee.

## Printability – d19 (2026-11-06)
Daniel 21:49: assess the prints for printability and change what helps without touching function or looks. 23:17: the cap
prints top face down (the top takes the plate's texture; the edge round's first 0.9 mm comes out slightly soft). Version
"rev F WIP 2026-11-06 d19 …".
- Support area per print in its B6o orientation (faces more than 45° down, the bed excluded), mm²: front floor down 11 506;
  cap top face down 295 (3 060 as fitted); slab on its side 2 392 (glass side down 4 761); carrier 0; door 285; grommet
  flange down 241; 5807 cradle 170; bracket L 152 → 122, R 278 → 245; BME680 hood 34; boxes L 1 975, R 2 592 (1 735 of each
  is the chamber's ceiling inside); clips 8.
- Done: MAIN_BRACKET, both halves – a 46° gusset under each lower board-boss arm, the column's width, from the column to
  x ±38.0 and up to z 35.7 under the boss; the Ø4.0 insert hole as it was. The arms print upright without support (they
  stood 31 mm over the bed); the 0.8–0.9 strips of arm beside the gusset print as short overhangs.
- Not changed:
  - LD2410C cradle floor (329 mm², support from z 2.5 floor down): the BME680 hood slides in under its back half; ribs
    behind y −20 block it (d19d A), ribs in front of it leave the back half and the tall support.
  - Upper board-boss arms (z 76.5): MAIN_front_env fills the space under them; their support can stand on the lower arm.
  - The right half's knee (z 21, 106 mm², d17): the finger's way to the microSD runs under it.
  - The right box's raised top (steps at y −24 outside, −11.5 inside): a chamfer behind y −24 would rise into the 1.0 the
    BME680 tray keeps over the box's top on the B5j-3 path (d12a); inside, the box needs supports for its chamber ceiling
    anyway.
  - Cloth recess, bottom edge, under-slab groove, slab ledges, rear rim: outer or interface faces set by earlier decisions.
- Print notes: tree supports from the second nozzle; "don't support bridges" on, so the vent bars and the cap seat's spans
  between the vent ribs (9–17 mm) print as bridges and do not stand on 160 mm towers. Supports that remain inside: the
  front's cradle floor; on the bracket the right half's knee and the upper arms (those can stand on the lower arms).
- Checks: d19d's added material ∩ every part 0, on the half's own path (65 steps each), the main board's (81) and the Pi
  adapter's (31) 0, the door never reaches it; full-body sweeps runs 17 / 18 0 (65 steps each); d17c finger solid and both
  drivers 0; matrix for the bracket 27 pairs, 1 as before (MAIN_front_env 724.91).
- Volumes (cm³): MAIN_BRACKET 6.5563 (2 lumps); the rest as in d17.
- Exports: `~/Documents/HA_v5f_main_bracket.step` (world frame), `~/Documents/HA Panel v5 - tapered revF-d19.f3d` (93.3 MB).
- Hidden copies: `MAIN_BRACKET_d19`.
