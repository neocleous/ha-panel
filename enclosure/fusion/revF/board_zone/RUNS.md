# Main-board outline study — runs (2026-11-07)

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
