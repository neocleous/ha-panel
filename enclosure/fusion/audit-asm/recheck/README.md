# Assembly audit, re-check after the fix pass (2026-11-12)

Brief `claude/brief-assembly-audit-recheck-2026-11-12.md`. Report `claude/report-assembly-audit-recheck-2026-11-12.md` (all numbers, findings F30 to F37).
Instructions `claude/assembly-instructions-2026-11-12.md`. Model "HA Panel v5 - tapered" version 60; nothing was changed or saved.

## How it ran
- Every probe ran through the Fusion connector's script call with `readOnly: true`, except the eight picture calls (visibility, camera, template bodies `AUD_*`; all deleted, visibility and camera put back; the document then shows as modified).
- The fix pass's library `../../revF/floor_plate/fusion/v5f_k_lib.py` was loaded unchanged from commit `9531973` as `sys.modules['aud3']` (sha256 `adc99aca...6d56bb`), `../aud2_lib.py` as `aud2c` for its reach tables, `v5f_k_pic.py` for the picture helpers.
- `aud3x_lib.py` (commit `752b796`) was loaded from that commit as `sys.modules['aud3x']` and ran as pushed.
- `aud3x_checks.py` is a **typed copy** of the functions that were typed into the connector calls and attached to `aud3x` at run time. It has not been run in this form. The one-off calls (parameters and results) are listed below and in the report.
- The big bodies were probed through the enclosure chat's cached slabs (`v5f_h_cache`), whose keys carry the body's volume.

## Checks and where their numbers are (report sections)
| Check | How | Report |
|---|---|---|
| Iron and 2.0 key on the 10 deg line | `aud3x.line`, stations 0.5, shell crops x 0..99.5 / -99.5..0, y -64..10, z 44..116 | 5.1, 5.2 |
| Tab relief, boss, seat | `k.faces` in boxes round (58, -4, 80) | 5.1 |
| Plate unit's way in | `lift` (boxes, drivers, screw-head envelope), `plate` (eight slabs), smallest distances to shell crops z 2..100; behind 0.5 .. 3.0; screw heads also as cylinders r 2.70 and as domes | 5.3 |
| Cloth | needles every 0.5 along both walls: shell underside at z 2.83, plate's raised field at z 2.3; gap square to the edge | 5.3 |
| Shell on its front | viewer-facing plane faces of the shell by depth; needles along the slab normal for the cloth; `physicalProperties` | 5.3 |
| Feet | `k.holes_of` on the plate | 5.4 |
| Display's power lead | distances to the module's bodies; pin ends = lumps of the board's bodies below w -1.65; the lead's under-board part shifted in u | 5.5 |
| Ride-in | `ride_setup`, `ride`: 45 pieces x 23 positions, lead parts by the fix pass's boxes; a second run with the lead parts ending 1.5 above the notch floors for the sideways clearance | 5.6 |
| USB plug's room | rays (`k.needle_t`) from the plug's faces, crop of the shell in the board frame (40..95, -20..35, -30..75) | 5.6 |
| DSI ribbon | strips 0.4 thick as boxes in the board and world frames against every current body | 5.7 |
| Reach | `reach2` with the lead bodies of the spare lengths as extra obstacles | 5.9 |
| Places of the spare lengths | `aud3x.finger` on the place, six directions; tweezers as a finger 6 across, 120 long | 5.8 |
| Service | plate unit's way out and the left box's slide as distances to the parts that stay; main board screws with `aud3x.line` | 5.10 |

## Lessons (continue the fix pass's 146-157)
- **158** Give every connector call a time limit inside its loops. A box grown step by step with a boolean per step against shell crops ran for about 25 minutes and blocked Fusion; the connector gives up at 80 s but the script goes on.
- **159** `measureMinimumDistance` takes temporary bodies on both sides and costs a few ms on a crop: a moved copy against a crop gives the clearance, not only a yes or no. 0 mm3 between two bodies can be a touching fit (the boxes' rear faces at 1.5 behind).
- **160** Crop once without reading a big body's volume in a loop (the volume read costs seconds); keep the crop's pieces in a dict of your own.
- **161** The connector's screenshot query leaves the picture as a file in the session's workspace; `saveAsImageFile` leaves one on the Mac.
- **162** A flat ribbon is not a line: check it as a strip whose width is set by its sockets. It can bend about its width only; every other change of direction is a crease.
