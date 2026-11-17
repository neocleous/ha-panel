# rev F: the posts, the shadow gap, FDM strength and the door's vents (2026-11-17)

Brief: `claude/brief-enclosure-posts-shadow-gap-2026-11-17.md` (D204 to D211). Reports: `claude/report-enclosure-posts-shadow-gap-block1-2026-11-17.md` (study, questions, the strength rule and its list), `claude/report-enclosure-posts-shadow-gap-2026-11-17.md` (closing).
Hand-over for the print re-check: `claude/handover-enclosure-posts-shadow-gap-2026-11-17.md`. Architect update: `claude/brief-architect-update-2026-11-17-posts-shadow-gap.md`.

**Model:** "HA Panel v5 - tapered" version 65 (g20) -> **version 66**, "rev F WIP 2026-11-17 g21: posts, shadow gap, FDM strength, door vents (D204–D211) — not for print".
Archive `~/Documents/HA Panel v5 - tapered revF-g21.f3d` (193,745,925 bytes). Not for print. Nothing on `main`, nothing under `hardware/`.
419 bodies (408 + 11 hidden `_v65`), 96 in the unit, 37 visible, no `AUD_*`.

## What changed in the model
| Body | Change | Volume mm³ (v65 -> g21) |
|---|---|---|
| `HOUSING_F_front` | **Top posts** (x ±70, up 27): 15° cone from the Ø9 land into the wall, two gussets 2.6 (free edges on a 27° cone), the corner wall behind restored from `_v63`. **Bottom posts** (x ±85, up −82): land Ø11, peg Ø8.0 × 1.2, 15° cone, rear face on world y −2.6, buttress 11 high into the side wall, strut 5.2 wide onto the chin block. Insert holes Ø4.0 × 6.35 cut again. **Fins** beside the top posts (x ±38.2…39.8) removed, 215.22 each. **Six gussets** under the cap's seat 2.0 -> 2.6, away from the cap key's lanes | 104,433.98 -> 107,864.32 |
| `HOUSING_F_plate` | **D205, option a:** back at d 12.0 outside an island whose edge is `REF_F_outer`'s outline at d 12.6 (0.73 beyond the side walls' front tips); border 3.0, island 3.8. Pocket Ø8.25, slot 8.25 × 9.75, 1.4 deep | 68,247.71 -> 66,463.68 |
| `HOUSING_F_door` | **D210, option a:** nine slots 3.0 wide at x 0, ±6…±24, z 59.5 to 116.0 (1,508.1 mm²; the old twelve filled from `HOUSING_F_door_d5b`). Four bosses: a buttress as wide as the boss (8.0) into the wall, z 2.8 to 10.5 | 47,019.77 -> 47,573.05 |
| `HOUSING_F_cap` | 45° root flare 1.0 on the four bosses (z 176.5 to 177.5) | 9,944.06 -> 9,980.25 |
| `FLOOR_PLATE` | Pi posts: 45° root flare 1.0 (r 4.8 at z 2.5). The two posts under the cradle: joined behind their axes, cone r 5.5 -> 4.0 over z 2.5 to 8.5, growing to the rear only | 32,450.31 -> 32,621.88 |
| `SPKBOX_L` / `SPKBOX_R` | Touch clip's screw hole 0.85 back (y −6.95), its block 1.7 longer to the rear (y −10.2). The old pilot's tip behind the lower inner driver insert filled (floor insert's wall 1.62 -> 2.3). Outer driver columns Ø7.5 -> Ø8.0; the four bosses under the driver's frame Ø8.0 | 26,088.32 -> 26,321.75 / 26,809.82 -> 27,043.25 |
| `TOUCH_CLIP_L` / `_R` | Hole 0.85 back, lug 1.7 longer to the rear | 489.56 -> 571.16 |
| `RESP_CARRIER` | Four posts: cone r 6.0 at the slab -> r 4.0 at the top, kept inside the slab's outline; no growth toward the ReSpeaker (lower pair) or the right microphone's lead (upper left). Lower pair whole again where the slab's bottom edge cut them (wall 1.70 -> 2.0). ReSpeaker bosses: 45° root flare 1.0 | 12,404.26 -> 13,651.99 |
| `CRADLE_5807` | 0.05 on the side beside the right screw hole (wall 1.95 -> 2.0) | 1,770.95 -> 1,771.22 |
| `*_v65` (hidden) | the eleven bodies above as at version 65 | — |

## Checks on version 66 (closing report §5)
Outer skin: only the two pegs outside (26.389 mm³ each). Interference: 76 pairs = version 65's; changed only door × `KO_capkey_SL` 97.399 -> 211.189.
Step 19: peg wall 2.0, play 0.125, drop-in overlap 0.0, slit 0.2. Door: 1,508.1 mm², nearest slot wall 48.62 from the BME680's slits (48.64 before).

## Files
| File | What |
|---|---|
| `cp2_lib.py` | Loader (`v5f_k_lib.py` as `cp2k`, cache `cp2_cache`, `KX` binding the main document by name), the scratch document for pictures, the data channel. **Written again after the session; not run as it stands** (lesson 205) |
| `cp2_posts.py` | The four posts and the plate's border and pocket, as run |
| `cp2_vents.py` | The door's layouts. Rebuilt from the bytecode of what ran; re-run check in lesson 205 |
| `cp2_fix.py` | Block 2: every new body on temporary copies, `delta()` and `outside()`, as run (fetched by Fusion from this branch by commit hash) |
| `cp2_calls.py` | Blocks 2 and 3 call by call: reference matrix, builds, commit, checks, save, archive |
| `offline/` | Workspace side: `chan.py` (data channel), `geo.py`, `model.py` (meshes, sections), `survey.py` (every cylinder and thin slab of the printed parts: the strength list), `vents.py`, `door_behind.py`, `compose.py`, `make_pics.py`, `gap_sections.py` (the question pictures) |
| `data/` | `boss_table.txt`, `slab_table.txt` (the survey's raw tables, version 65), `vent_layouts.json` |
| `img/` | The four question pictures and four renders of the fixes as built |

Not in the repo: block 1's check helper `part_checks` (bytecode only) and the meshes (7 MB).
Libraries used unchanged (docs `d223ad3`): `revF/floor_plate/fusion/v5f_k_lib.py` (blob `ba85884`), `v5f_k4a_unit_checks.py` (`f5583bf`).

## Lessons (on from the change pass's 201)
- **202** `REF_F_outer` is the shell offset 0.7 everywhere, also in front of the side walls' front edges (front plane d 12.3). The cloth ends on the rounded edge, so the plate's back (d 12.8) lies inside the reference there. It is the right body for "does plastic break the skin" (part minus reference), not for the cloth's true extent at the front.
- **203** Study in an unsaved scratch document (root attribute to find it again, `AUD_*` copies) and bind the library to the main document by name (`KX`): read-only work and temporary booleans run while the scratch document is active, and the main document stays unmodified until the commit. Activate the main document for the commit only. Close the scratch document by its attribute, never by its name.
- **204** Data from the Mac to the workspace: Fusion's Python packs bytes into a grey PNG; the Filesystem connector's `read_media_file` leaves that exact file in the workspace. Renders come the same way and can then be labelled there. The Mac's home is `/Users/danielneocleous`.
- **205** Five helper files of block 1 were typed into Fusion and kept nowhere else; only their bytecode could be listed afterwards (`dis`). Write every source to a file first, push it, and let Fusion fetch it by commit hash (`k.RAW % (sha, path)`): the sha256 of what ran then equals the file's. `cp2_vents.py` was rebuilt from the listing and run again on version 65's door: blank 50,930.19, layout `b` 47,034.26 (the same as in block 1).
- **206** An axis read from the centroid of a cut circle was 0.37 off (carrier's lower posts: up −52.33 instead of −52.70), and with it the side of their thin wall: it faces the slab's bottom edge, which cuts the posts, not the ReSpeaker. Take axes from the cylinder faces (`axes_d`).
- **207** An offline distance that used one wall depth for every height was 3 off on a leaning wall (slot to the BME680's slits 51.8; measured on the faces 48.6). Give Daniel only what was measured on the model, or say that it is an estimate.
- **208** `delta()`: the new body minus the old as one temporary body, then its distance to every neighbour whose box it meets. It showed, before the commit: a flare 0.05 from the Pi's power lead's space, cones 0.11 from it beside the cradle posts (it hugs them at 0.2), a cone inside the right microphone's lead (0.89 beside the post), a cone 0.51 from the door. An envelope 0.2 from a post leaves no room to grow on that side.
- **209** One heavy item per call: `BRepBody.volume` of fourteen bodies 43 s; a boolean with the whole shell 8 to 18 s; `k.region` on a changed shell 25 s per new box; distances from many bodies to the big ones past 80 s. Keep results in `k.c` and read them in a light call (lesson 200).
- **210** Thickening a gusset without touching the wall's outside: crop it from the cached pieces, move the crop by the added thickness, keep only the slab beside the old face (an oriented box), and cut it with the reference moved 1.7 inward along the gusset. Then the outer-skin test.
- **211** The fins beside the top posts were a leftover of the split: they tied the cap's side pads to the wall that became the screen plate, and hung on by a neck 3.5 × 1.6. After a split, look for features that lost one of their two roots.
- **212** "Confirm the counts" meant nothing to Daniel. Say what the check is for (the right, untouched file is open; the figures equal the brief's) and ask for the go-ahead in plain words.
