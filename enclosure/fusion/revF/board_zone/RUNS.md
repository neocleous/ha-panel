# Main-board outline study and rev 2 body update — runs (2026-11-07 / 08)

Question (electronics brief 2026-11-07 22:52, Project doc `claude/brief-main-board-outline-2026-11-07.md`): with every SMD
part on the front, how big can the main board be at the current plane (front face y −63.4, 1.6 thick)?
Answer: Project doc `claude/report-main-board-outline-2026-11-07.md`. Data and images: `~/Documents/HA_panel_renders/board_zone/`.

Model: **HA Panel v5 - tapered**, version 37 = latest, "rev F WIP 2026-11-07 d22", read without activating it (lesson from
the print audit: activating it froze Fusion for ≈ 8 min), document unmodified before and after.

## Layout
| Folder | What |
|---|---|
| `fusion/` | Fusion scripts, run on the Mac. Mac copies in `~/Documents/HA_panel_renders/scripts_e/` (sha256 e39936d0… / 2d1e2357…, equal). |
| `offline/` | Python 3 in the cloud container (numpy 2.5.3, scipy 1.18.1, shapely 2.2.0, matplotlib 3.11.2) on the meshes staged from the Mac to `/mnt/user-data/uploads/HA_panel_renders/`. |

Fusion loader: `exec(open(path, encoding='utf-8').read(), {'__name__': 'e1x'})` with `readOnly: true`; each script calls
`run(None)` itself and writes its own status file.

## Fusion runs
| When | Script | Settings | Wrote | Result |
|---|---|---|---|---|
| 2026-11-07 22:56:40 | `fusion/v5f_e1a_list_bodies.py` | readOnly; design read without activation | `board_zone/bodies.json`, `e1a_status.json` | 290 bodies; version 37 = latest, unmodified. The MCP call timed out at 60 s and Fusion answered no call for a few minutes; the run finished |
| 2026-11-07 23:07:23 | `fusion/v5f_e1b_meshes.py` | readOnly; guard volumes (front 235.9107, door 47.2633, bracket 6.5563, boxes 25.6082 / 26.3874, cradle 2.1775, grommet 0.5062, carrier 10.0716, hood 0.8029 cm³); mesh calculator 0.02 mm (prints) / 0.05 mm (the rest), ≤ 10° normal deviation; world mm, x_rel | `board_zone/mesh/*.stl` (58) | 38.0 s; guard OK; none missing |

The front is the print audit's d22 export (`print_audit/exports/front_d22.stl`, 2026-11-07 14:15, sha256 45e62576…): mesh
volume 235.9236 cm³ against the body's 235.9107.

## Offline
| Script | What | Check |
|---|---|---|
| `offline/bz.py` | +y rays at the centres of a 0.5 mm x_rel / z grid (centres offset 0.0123 / 0.0371 so no ray runs along an edge); per cell the occupied y-intervals from the winding count; cached per mesh | MAIN_pcb 7,200 mm³ and 4,500 mm², MAIN_back_env 15,750 mm³ exact; every mesh 0 unbalanced cells; mesh volumes within 0.04 % of the bodies |
| `offline/maps.py` | body groups: fixed when the board goes in or after it (front, boxes, speakers, Pi, cooler, GPIO plugs, USB-A plug, Pi-power adapter/cable/plug, cradle, PD board, pigtail keep-out, ReSpeaker, LCD, BME680, LD2410C, touch board); keep-outs (K5 lanes, cap-key lanes, K7 fan, touch back); bracket; door; leads | — |
| `offline/plane.py` | `analyze(YF, tilt)`: cells where a fixed body or keep-out crosses the slab; the door's sweep (any door material in front of the back face); both grown by 1.0 mm in x–z; the free region connected to the board; front gap to the first fixed body or keep-out; back gap to the door or a fixed body; lead and bracket gaps | — |
| `offline/evalpoly.py`, `offline/outlines.py` | an outline's area, front-gap and back-gap areas, leads and bracket in front; outlines T, TS, PMAX and today's | today's board: 4,304 mm² usable, door sweep 6.27 mm, the J2 plug at the mouth line (designed contact) |
| `offline/exact.py` | surface samples every 0.25 mm on the meshes; least x–z distance from an outline to the samples in the slab (door: every sample in front of y −65) | — |
| `offline/bz_report.py` | one run: free region, the three outlines (areas, zones, clearances, leads, bracket, KiCad frame) and the plane-move table | output in the report |
| `offline/fig_report.py` | the outline figure | `main_board_outline_2026-11-07.png` (sent with the report) |

## Results (bz_report.py)
- Free region at the plane (1.0 mm to fixed parts, keep-outs and the door's sweep): 11,200 mm².
- Outlines (gross / usable without the four Ø8 bosses, mm²): today 4,500 / 4,304; T 6,139 / 5,940; TS 6,416 / 6,217;
  PMAX 6,876 / 6,674.
- Least clearances, PMAX (T): door sweep 2.39 (3.19), front shell 5.48 (6.90), K5 lanes 1.25 (1.37), cap-key lanes 1.14
  (1.33), cradle / PD board 2.64 (11.90); back gap to the door ≥ 1.08 (tab top corners; 2.12 on the centre line); J2 plug unchanged (mouth line).
- Plane moves (free area within |x| ≤ 45 above z 34, front ≥ 6, back ≥ 1; current 6,832 mm²): 4 mm back 5,618, 2 mm back
  6,224, 2 mm forward 7,421, 4 mm forward 7,662; tilt 3° top back 5,810, 3° top forward 7,844, 6° top forward 8,728.

## e2 — main board rev 2 in the model (2026-11-08)
Electronics: `claude/report-main-board-rev2-2026-11-08.md`, `hardware/main-board/MAIN_env.md` rev 2 (docs @ 733cb5a): the
board is T's base, 90 × 55 (z 34–89, −x top corner cut); holes, connectors and K20 lengths unchanged. Answer: Project doc
`claude/report-main-board-rev2-checks-2026-11-08.md`.

| When | Script | Settings | Result |
|---|---|---|---|
| 2026-11-08 00:43:42 | `fusion/v5f_e2a_activate.py` | readOnly; activates the design (the exploded-prints copy was active) | 0.6 s; version 37 = latest, unmodified |
| 2026-11-08 00:44:38 | `fusion/v5f_e2b_main_board_rev2.py`, first run | modifying | built the bodies at design x ±45 instead of x_rel ±45 (no XC offset), i.e. 2.55 mm toward +x_rel; seen in the bodies' boxes, not saved |
| 2026-11-08 00:45:20 | `fusion/v5f_e2b0_undo_shift.py` | modifying; checks the three misplaced bodies by volume and design x-range, deletes them, gives the originals back their names | originals 7.2 / 130.14 / 15.75 cm³ again |
| 2026-11-08 00:45:46 | `fusion/v5f_e2b_main_board_rev2.py`, corrected (x = XC + x_rel, placement check added) | modifying; guard volumes and names | MAIN_pcb 7.9192 (x_rel ±45), MAIN_front_env 146.9829, MAIN_back_env 14.2437 cm³, 1 lump each, as computed by hand; old bodies hidden as `MAIN_*_e2` |
| 2026-11-08 00:46:50 | `fusion/v5f_e2c_checks.py` | readOnly; the six bodies (new, old) against 90 current bodies; TemporaryBRep intersection volume, else measure-manager minimum distance, for boxes within 1 mm | 12.5 s; table in the answer |
| 2026-11-08 00:54:48 | `fusion/v5f_e2d_save.py` | saves, exports the f3d, re-activates the exploded-prints copy | version 38 "rev F WIP 2026-11-08 e2: main board rev 2 …"; `~/Documents/HA Panel v5 - tapered revF-e2.f3d` 98.6 MB |
| 2026-11-08 00:55:31 | `fusion/v5f_e2e_verify.py` | readOnly, without activation | version 38 = latest, description as saved, unmodified; MAIN bodies as above |

Bodies (world, x_rel): MAIN_pcb y −65.0…−63.4 on the outline. MAIN_front_env y −63.4…−33.4 for z 35.8–89 and y −63.4…−39.2
for z 34–35.8, without x < −41.5 ∧ z > 83.5. MAIN_back_env y −65.0…−67.9 without the bare corners (x < −38 or > 43.5,
z > 82), plus J2's courtyard x 19.72–30.28, z 34–43.67 to y −68.5.

Offline (same container; `access*.py` read the `bz.py` column cache in `../bz/cache` and the board file on `docs` @ 733cb5a):

| Script | What | Result |
|---|---|---|
| `offline/kpcb.py` | reads footprints (reference, layer, position, courtyard, pads) and Edge.Cuts from a `.kicad_pcb` | rev 2 and 50da2b8: every tall part and connector at the same place |
| `offline/door_sweep.py` | door taken off straight back: door samples (0.25 mm) ahead of each body's rear face over its footprint; gap behind | board 4.18 mm from that door material (old 6.27); door ≥ 1.95 mm behind the board (old 2.90), at the +x top corner; the 2.9 back envelope touches at the bare zone's edge (x 43.5, z 89) |
| `offline/access.py`, `access2.py`, `access4.py`, `access6.py`, `access7.py` | plugging the front-face leads after the board is on: 1 mm voxels; obstacles = step-10 parts (cap on or off, cradle in or out) + board slab + parts (courtyard × MAIN_env heights); a fingertip ball travels from behind the open back to the plug top (y −53.6); hand ball for the finger length | top edge 84 and 89 give the same result. J1, J5, J8, J9: Ø20 fingertip touches. J6: Ø14 gets within 1.1 mm, Ø16–20 within 2.1 (C7 beside it); without C7, Ø20 touches. All five over the top edge: sealing it stops Ø20, sealing below or the sides changes nothing |

## e3 — main board rev 2.1: C7 moved (2026-11-08)
Electronics: `claude/report-main-board-rev2-1-c7-2026-11-08.md`, MAIN_env rev 2.1 (docs @ 236be84): C7 (Würth 860160572003,
Ø5.0 ± 0.5 × 12.5) from (x_rel 0.5, z 66.6) to the top strip above the NID, centre (−5.67, 86.05); nothing else moved
(`kpcb.py`: every other footprint, the outline and the via / segment counts equal to 733cb5a). Answer: Project doc
`claude/report-main-board-rev2-1-checks-2026-11-08.md`.

| When | Script | Settings | Result |
|---|---|---|---|
| 2026-11-08 11:11:24 | `fusion/v5f_e3a_c7.py` | modifying; activates the design; guard volumes, document unmodified | MAIN_C7_env 0.29698 cm³ (Ø5.5 × 12.5, y −63.4…−50.9, x_rel −8.42…−2.92) and KO_C7_vent 0.07127 cm³ (Ø5.5 × 3, y −50.9…−47.9), hidden |
| 2026-11-08 11:11:49 | `fusion/v5f_e3b_c7_checks.py` | readOnly; both bodies against 93 bodies within 20 mm: intersection volume and minimum distance | 0.6 s; only the main-board envelopes touch (inside MAIN_front_env, on MAIN_pcb); nearest others: LCD 5 V lead 20.9 mm from the vent space, bracket 29.5, DSI ribbon 42.4, VEML lead 44.3 |
| 2026-11-08 11:13:59 | `fusion/v5f_e3c_save.py` | saves, f3d, re-activates the exploded-prints copy | version 39 "rev F WIP 2026-11-08 e3: main board rev 2.1 …"; `~/Documents/HA Panel v5 - tapered revF-e3.f3d` 98.7 MB |

Offline: `access8.py` (rev 2 against rev 2.1, Ø14 / 16 / 20, cradle out and in, openings sealed one at a time) and
`access9.py` (Ø24 / 28; finger length beyond a Ø40 hand). Their `rev2.kicad_pcb` / `rev21.kicad_pcb` are `git show 733cb5a:` /
`236be84:hardware/main-board/main-board.kicad_pcb`. Rev 2.1: a Ø24 fingertip touches all five plug tops, J6
included (rev 2: Ø14 within 1.1 mm, Ø16–24 within 2.1); J1, J5, J8, J9 as in rev 2; all over the top edge. At Ø28 J6
stops 12.1 mm short in both. Finger beyond a Ø40 hand (Ø16): J1 42 (43 cradle in), J5 13, J6 46 (rev 2: none), J8 44,
J9 41 mm. C7's joints: 9.3 mm back gap to the door, nothing else behind.

## e5 — J10 sensor leads, touch board rev D, mic strip (2026-11-09)
Architect 2026-11-09 (log 2026-11-08 §8, D55): V23b route the BME680 and VEML6030 leads to J10 (clear of the C7 vent
keep-out) with routed and cut lengths; V26 touch board rev D's back parts against KO_touch_back; V27 the strip's Ø0.8 port
against the cap's Ø1.5 ports. Board files on `docs` @ 6cfb845. Fusion scripts in `../` (`v5f_e5*.py`); the design was
closed at the start and opened from the hub (version 40, unmodified). Answer: Project doc
`claude/brief-architect-update-2026-11-09.md`.

| When | Script | Settings | Result |
|---|---|---|---|
| 2026-11-09 09:05:30 | `../v5f_e5a_probe.py` | readOnly | boxes, cap ports and pins; V26 part void (loose design box, README lesson 85) |
| 09:07:17 | `../v5f_e5a2_v26.py` | readOnly; vertex extents | V26 pass (see the README e5 checkpoint) |
| 09:08:25 | `../v5f_e5b_meshes.py` | readOnly; 94 bodies, tolerance 0.1 | 222 MB in `~/Documents/HA_panel_renders/e5/mesh`, 71 s |
| 09:20:39 | `../v5f_e5c_lead_checks.py` | readOnly; temporary tubes | new leads ∩ every body 0 except the designed contacts; nothing within 2.0 but the sensor ends' bodies; parts near J10: BME680 within 1.0 of the NID, VEML within 2.0 of the NID and J5's plug |
| ≈ 09:22 | `../v5f_e5d_leads.py` | modifying | ran and wrote its status, then rolled back by the MCP (the wrapper's own `run()` call failed; README lesson 86) |
| 09:24:25 | `../v5f_e5d_leads.py` | modifying; loader with a no-op `run()` | LEAD_BME680 0.6381, LEAD_VEML 0.8101 cm³ added; old → `*_e5`; exact distances as in the checkpoint |
| 09:24:40 | `../v5f_e5e_save.py` | saves | version 41, `revF-e5.f3d` 93.4 MB |
| 09:25:17 | `../v5f_e5f_verify.py` | readOnly | version 41 latest, not modified, bodies and file as saved |

Offline (same container; work folder with the e5b meshes in `mesh/`):

| Script | What | Result |
|---|---|---|
| `offline/lead_vox.py` | z-column winding voxels, 0.5 mm, x_rel −95…25, y −80…10, z 60…190, of every mesh but MAIN_front_env and the two old sensor leads; main board rev 2.1's front parts as courtyard × height boxes (NID 27.5, C5 / C6 16, C7 12.5, XH mated 9.8, L1 6.5, L100–L103 5.4, NANO2 2.94, SMB 2.7, 2920 1.8, wire-pad headers 2.0, the rest 1.8; J10 left out); distance field | 240 × 180 × 260, 2,160,562 voxels occupied, 3.9 s |
| `offline/lead_route.py bme -66.557 -36.212 84.387 -18.42 -50 77.5 '{"need": 4.0, "pref": 6.0, "relax": [[[[-23, -63.4, 74], [-16.5, -44, 81]], 2.3]]}'` | BME680 from bo (d12a) to 13.4 in front of its J10 column | (−66.56, −36.21, 84.39) → (−43.25, −35.75, 96.75) → (−18.42, −50.0, 77.5), 60.9 |
| `offline/lead_route.py veml 0 -39.7 165 -20.97 -50 77.5 '{"need": 4.0, "pref": 6.0}'` | VEML6030 from below the cap exit (c2c) to 13.4 in front of its column | (0, −39.7, 165) → (−21.75, −48.75, 77.75) → (−20.97, −50.0, 77.5), 91.9; built as the straight line (0, −39.7, 165) → (−20.97, −50, 77.5), 90.6, which e5c / e5d check exactly |
