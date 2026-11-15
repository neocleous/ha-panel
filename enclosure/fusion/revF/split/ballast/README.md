# rev F split, ballast pass: weight low in the base plate (2026-11-15)

Brief: `claude/brief-enclosure-ballast-2026-11-15.md`. Report: `claude/report-enclosure-ballast-2026-11-15.md`.
Hand-over for the print re-check: `claude/handover-enclosure-ballast-2026-11-15.md`. Architect update: `claude/brief-architect-update-2026-11-15-ballast.md`.

**Outcome: no weight.** The study found room for about 80 g of steel low in the plate unit, almost all of it where it does not help
the backward case. Daniel chose option A (no weight) on 2026-11-15 at about 21:44. **The model is unchanged:** "HA Panel v5 - tapered"
version 65 (g20) stays the model of record; no version was saved and no archive exported. Not for print. Nothing on `main`, nothing
under `hardware/`.

## What the study found (version 65, D9 base: 1,055.1 g at (-0.81, -17.84, 79.67))
- Every 100 g under the balance point (y -17.8) would raise every tipping force by 9.5 %. That is where the Pi and its air intake sit.
- The low free room is (1) the 1.2 gap under the speaker boxes (2.5 sheets in floor pockets) and (2) narrow strips behind the Pi
  and the boxes, 4 or less in front of the rear feet line (y -70.6): 100 g there adds +47 % to the forward pull and +0.8 % to the backward push.
- Gross free floor area 1,100 mm² at 8 high; after 0.5 clearance and a 4 minimum width one solid piece fits behind the Pi (555 mm²).

| Option | Added | Unit | Backward, glass top edge | Backward, screen centre | Forward pull | Forward tips at |
|---|---|---|---|---|---|---|
| A none (chosen) | 0 | 1,055 g | 3.07 N | 5.41 N | 0.72 N | 8.5° |
| B 2.5 sheets under the boxes (29 + 11 g) | 40 g | 1,095 g | 3.17 N | 5.58 N | 0.76 N | 9.0° |
| C 10 plate behind the Pi | 44 g | 1,099 g | 3.08 N | 5.43 N | 0.87 N | 10.1° |
| D both | 83 g | 1,138 g | 3.18 N | 5.60 N | 0.91 N | 10.6° |

Dropped in the study: stock flat bar (19 g behind the Pi, 9 + 4 g under the boxes), steel BBs in printed pockets (24 g), tungsten putty or
cubes in printed pockets (about 50 g: the walls take the narrow room), washers on the M3 x 8 (grams), lead.

## Files
| File | What |
|---|---|
| `b0_load.py` | Loader (libraries by git blob hash under `cp2k`, `cp2m`, `cp2a`, `cp2x`; cache `cp2_cache`), state, counts, guard volumes |
| `b0_tip.py` | Version 65's tipping table reproduced on the D9 base (k2a model at v65 and on the `_v64` bodies, the difference on D9) |
| `b1_survey.py` | The base plate's flat faces and floor loops (intake field 475 x Ø2.0 on a 3.0 grid), the unit's bodies below z 40, the magnet pockets |
| `b1_sections.py` | Sections at 37 heights and the plate's outlines, written to `~/Documents/HA_panel_renders/ballast/` |
| `b1_render.py` | The options drawn in a scratch document for `ballast_3_rear34.png` (open, shot, close) |
| `analysis/geo.py` | Section loader, free-column map (`free_col`), keep-clears, the D9 tipping formulas (`figs`, checked to 0.001 against Fusion) |
| `analysis/pockets.py`, `plates.py`, `rects.py` | Sizing: printed pockets, laser-cut plates, stock bar pieces |
| `analysis/shapes.py`, `opts2.py` | The option outlines (`results/cand_pts.json`) and their tipping table (`results/opt_figs.json`) |
| `analysis/pics.py`, `annot3.py` | Pictures 1 to 3 (`~/Documents/HA_panel_renders/ballast/ballast_1_plan.png`, `_2_lever.png`, `_3_rear34.png`) |

Workspace scripts read the staged JSON from `/mnt/user-data/uploads/ballast` and write to `/home/claude/bal`; change the paths to rerun.

## Assumptions
Steel 7.85 g/cm³. Clearance 0.5 round and above every part; printed pocket walls 1.2; no part narrower than 4. The door goes on from
behind, so the space behind each of its four bosses is kept free. Keep-clears: the intake field (x -43.25..41.75, y -59.7..-4.7), the
microSD finger channel (x -64..-44, from y -24 back), the anchor and its tie (x 53..64, y -61..-52). The Pi's Wi-Fi antenna sits at its
corner by the GPIO header's far end (Raspberry Pi: "top left, next to the 40-pin header"); 20 kept from it is this pass's margin, no
published figure (Raspberry Pi says only "away from metal").

## Lessons (on from 201)
- **202** A scratch design document (`documents.add`, direct design) is a safe canvas for pictures of what-ifs: temporary copies go in with `bRepBodies.add`; planes by `setByPlane`, sketches, extrudes and combine-cuts work there; `close(False)` and `activate()` the model again. The model of record stays unmodified (checked: version 65, not modified). Take every copy before the scratch document opens: `v5f_k_lib` reads `app.activeProduct`.
- **203** `TemporaryBRepManager.planeIntersection` gives a body's section in milliseconds: 37 heights x 30 bodies in 3 s. It throws InternalValidationError on some bodies at some heights (`DRV_screw_heads_env` at z 15 to 28); retry at ±0.03 / 0.07 or skip with a note.
- **204** `findBRepUsingRay` on the root component of a 408-body design costs about 0.5 s a ray (111 rays in 55 s): no good for maps. Use sections.
- **205** Measure free room as columns (free over the whole height, the next level above included) and then take off clearances and walls. Here 1,100 mm² of gross free floor at 8 high gave 555 mm² for one solid piece and 234 to 457 mm² of cavity for a walled pocket.
- **206** Building a section's region by polygonizing all its edges and joining the faces fills its holes: conservative for obstacles, wrong for true regions (build rings with `linemerge` and XOR them). Hollow parts such as the speaker boxes must be filled anyway: their chambers are no room.
- **207** `SaveImageFileOptions.isBackgroundTransparent = True` left the environment's background in the picture in this version. Label pictures outside Fusion.
- **208** Files between Fusion and the workspace: Fusion writes to `~/Documents/HA_panel_renders/<pass>/`, that one folder is connected to the session (one approval), `device_stage_files` brings it in, `device_commit_files` takes pictures back.
- **209** Before sizing a weight, place the free room against the feet lines: weight helps the backward case by its distance in front of the rear feet line and the forward case by its distance behind the front feet line. Room near the rear feet only helps the forward case.
