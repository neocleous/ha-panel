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
