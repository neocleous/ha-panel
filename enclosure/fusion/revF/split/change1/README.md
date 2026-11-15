# rev F split, change pass after the assembly audit (2026-11-15)

Brief: `claude/brief-enclosure-change-pass-2026-11-15.md`. Report: `claude/report-enclosure-change-pass-2026-11-15.md`.
Hand-over for the print re-check: `claude/handover-enclosure-change-pass-2026-11-15.md`. Architect update: `claude/brief-architect-update-2026-11-15-change-pass.md`.

**Model:** "HA Panel v5 - tapered" version 64 (g19) -> **version 65**, "rev F WIP 2026-11-15 g20: change pass after the split's audit (F44, F45, F46, F50, rear feet) — not for print".
Archive `~/Documents/HA Panel v5 - tapered revF-g20.f3d` (187,535,895 bytes). Not for print. Nothing on `main`, nothing under `hardware/`.

## What changed in the model
| Body | Change | Volume mm³ (v64 -> g20) |
|---|---|---|
| `SPKBOX_L` / `SPKBOX_R` | **F44** the lug pocket filled to the split's own pocket floor (s -0.6985 / -1.04375 on the box-top lines; 0.3015 / 0.306 shallower, floor 0.69 below the lug's front face). **F45** a 0.4 x 45° lead-in: a countersink square to the lug's front face (world y), 0.4 wider than the mouth on the face, cut no deeper than the pocket's floor plane | 26,086.63 -> 26,088.32 / 26,807.97 -> 26,809.82 |
| `HOUSING_F_front` | **F46** the two bottom posts' pegs Ø7.0 -> Ø7.2 (d 11.6 to 12.8); the insert holes Ø4.0 x 6.35 cut again | 104,428.62 -> 104,433.98 |
| `HOUSING_F_plate` | **F46** pocket Ø7.25 -> Ø7.45, slot 7.25 x 8.75 -> 7.45 x 8.95 (8.95 along x), both 1.4 deep as before | 68,255.48 -> 68,247.71 |
| `FLOOR_PLATE` | **D153** the rear feet's recesses Ø13 x 0.5 from (±30, -69) to (±30, -70.6) | 32,450.57 -> 32,450.31 (the move is volume-neutral on a crop: 10.3736 out, 10.3737 in per side; lesson 198) |
| `FOOT_RL` / `FOOT_RR` | moved 1.6 back with their recesses | 443.37 |
| `KO_K5_UL/LL/UR/LR` | **F50** 1.0 forward along the screen's normal: start at d 15.8 | 2,309.07 / 3,848.45 |
| `*_v64` (hidden) | the eleven bodies above as at version 64 | — |

## Files
| File | What |
|---|---|
| `c0_calls.py` | Loader (libraries by git blob hash under fresh names `cp1k`, `cp1m`, `cp1a`, `cp1x`; cache `cp1_cache`), block 0: state, guard volumes, the audit's F44 numbers and the step-20 window reproduced |
| `lib_entry.py` | `cp1e`: the inserts' entry into the lugs' pockets: the F44 fill, the two lead-in variants, the fixed-offset table and the guided path with the contact's direction |
| `c1_calls.py` | Block 1: the lead-in variants compared on copies, the five changes, save, archive |
| `c2_calls.py` | Block 2: checks 1 to 8 |
| `tip.py` | The tipping figures: the split's D9 base rebuilt, this pass's change on top of it, and the k2a model run on today's bodies as a cross-check |

Libraries used unchanged (docs `8377478`): `revF/floor_plate/fusion/v5f_k_lib.py` (blob `ba85884`), `v5f_m_lib.py` (`62790f5`), `v5f_k2a_tip.py` (`388dfb5`),
`v5f_k4a_unit_checks.py` (`f5583bf`), `audit-asm/followup/aud4_lib.py` (`181243c`), `audit-asm/split/aud5x_lib.py` (`cdec604`).

## Lessons (on from the audit's 193)
- **194** The audit's F44 figures 0.42 (insert's end to floor) and 0.32 (pull until the lug's top edge meets the plate) are the first 0.02 steps in contact. Measured continuously they are 0.405 and 0.305. Reproduce a stepped number with its own step before reading a difference as a change in the model.
- **195** A pocket whose axis is 10° off its face has its rim 0.46 deeper on one side (at r 2.6). A chamfer round the pocket's own axis gives no bevel there, and that is the side an off-centre insert lands on. A lead-in for a part arriving square to the face is a countersink about the face's normal, capped at the pocket's floor plane so that it cannot eat the floor.
- **196** Classify a first contact by the direction between the two nearest points just before it (back off until the distance is above 0: `measureMinimumDistance` gives 0 and the origin for touching bodies, lesson 172). Within 25° of the motion it is a face that stops the part; a 45° bevel or the 80° wall steers it. Volume overlaps alone cannot tell a stop from a graze.
- **197** `v5f_k_lib`'s caches key a copy by name and volume. A body moved without a change of volume (feet, keep-outs, a recess moved inside solid material) keeps returning its old copy: purge by name (`k.purge`) after such a change, and keep a pass's cache apart (`'v5f_h_cache'` -> `'cp1_cache'` in the loader).
- **198** The base plate's whole-body volume moved by 0.26 mm³ (`BRepBody.volume`) and 0.19 mm³ (VeryHigh accuracy) under a change that a crop shows to be volume-neutral to 0.0001 mm³. Check a change's volume on a crop round it; keep the guard volumes on one method.
- **199** The base plate's underside is flat only to about 4.2 in from its rear edge; behind that it blends up into the rim (radius about 5, 1.4 high at the edge). A recess must stay inside: at x ±30 the rear feet stop at y -70.68.
- **200** `physicalProperties` of the fourteen printed parts and about forty component bodies, for two versions in one call, ran past the connector's 80 s. The result arrived in `k.c` when the call finished (lesson 187): keep results in a cache and read them in a light call.
- **201** The split's tipping figures (D9) were built from version 63's total (1,080.5 g at (-0.83, -17.57, 80.34)) by swapping the shell's pieces in, with the 3.6 g of new screws and inserts at the screen plate's centroid. The k2a model run on today's bodies gives 0.9 g less and the balance point 0.2 to 0.3 off: 0.01 N, 0.16°. Compare two versions on the same base.
