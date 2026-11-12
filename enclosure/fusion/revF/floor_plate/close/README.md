# rev F — close of the enclosure work (2026-11-12)

Part 2 of `claude/brief-enclosure-step3-repeat-2026-11-11.md` (blocks 5 to 7). Part 1 is in `../step3r/README.md`.
Reports in the claude.ai project: `claude/report-enclosure-close-blocks5-6-2026-11-12.md` (all tables),
`claude/handover-enclosure-2026-11-12.md` (draft build order, service order, audit findings), `claude/main-board-site-2026-11-12.md`
(issue 3), `claude/report-enclosure-close-2026-11-12.md`.

## Model
| Version | Name | What |
|---|---|---|
| 54 | rev F WIP 2026-11-12 g9 | coarse Pi envelope dropped; touch board envelope replaced by its seven real back parts |
| 55 | rev F WIP 2026-11-12 g10 | right speaker box: leftover 0.4 sheet under the raised roof taken out (109.6 mm3) |

Archives `~/Documents/HA Panel v5 - tapered revF-g9.f3d`, `…revF-g10.f3d`. Backups hidden in the model:
`PI5_components_env_v53`, `TOUCH_components_env_v53`, `SPKBOX_R_v54`.

## Scripts (`../fusion/`), run through the loader of the main README; data folder on the Mac `fp/close`
| Script | What |
|---|---|
| `v5f_j_lib.py` | library on top of `v5f_i_lib.py`: `run_j`, `crop`, `ivals`, `wext`, `solid`, `PRINTED` |
| `v5f_j_wrap.py` | earlier scripts run again unchanged: hole list (`j6c`), chamber volumes (`j6v`), save and archive (`j_save`) |
| `v5f_j5a_air.py` | open area of intake, back-wall rows (`VAR='low'`), door slots; free section of the cavity (`path2`) |
| `v5f_j5b_envelopes.py` | the two coarse envelopes: dry / `APPLY` |
| `v5f_j5c_rim.py` | pictures of the rim with the cloth turned under the edge (temporary bodies, deleted) |
| `v5f_j5d_tip.py` | masses, centre of gravity, tip-over backward and forward |
| `v5f_j6a_matrix.py` | interference matrix, first form (slow for big bodies; kept because j6a2 continues its table) |
| `v5f_j6a2_matrix.py` | interference matrix: distance first, big bodies in eight cached slabs |
| `v5f_j6b_probe.py` | probes: `needles`, `dist`, `boxes`, `inserts`, `walls`, `vdist`, `iron`, `axis`, `shift` |
| `v5f_j6f_sheet.py` | the leftover sheet in the right box: extrude cut of its top face on a copy, checks, swap |

## Results in short
- Air: intake 1 482.8 mm2; exhaust back wall 238.6 + 238.8, door slots 1 503.8, total 1 981.2 mm2; free section of the cavity never
  under 3 337 mm2; the main board closes nothing off.
- Tip-over backward 3.07 N at the top edge of the glass (was 3.00); 1 081.3 g; centre of gravity (-0.84, -17.56, 80.35); the rear
  feet carry 10.5 %.
- Interference: 98 bodies, 4 753 pairs, 0 failed, 78 not zero, none a new clash.
- Fasteners as built: 46 screws (30 standard M3 x 8), 32 inserts (28 M3, 4 M2.5).
- Chambers: left 118.70 / 87.11, right 121.09 / 89.20 cm3, closed.
- Open: the soldering iron cannot stand on the axis of the two inserts in the front shell (free only 8-10 deg toward the middle);
  front shell's first layer 997 mm2.

## Not in the repo
The status files (`fp/close/*.json`), the hole list, the six rim pictures (`fp/close/rim_*.png`) and the merge of these lessons into
the main `README.md`: this session had no git push; text went through the GitHub connector.

## Lessons (continue `../step3r/README.md`, 125-131)
- **132** The world box read from a body's vertices is wrong for round bodies: a cylinder has vertices on its seam only (the feet
  came out with zero width). Take centre and radius from the cylinder face.
- **133** A boolean with the whole front shell or door as its tool costs 5-35 s whatever the size of the other body (the tool is
  copied inside). Cut a big body once into eight slabs along its longest axis, cache them, and intersect only with the slabs the
  small body's box reaches. Check the slabs' volumes against the body's (within 0.1 %).
- **134** Before intersecting with a big body, measure the distance of the two model bodies: a pair that does not touch is done.
- **135** The volume of a big model body, or of a detailed temporary body, costs up to a second per read. Read each once per call;
  never inside a loop over pairs, needles or faces. One run of 23 needles took 175 s for this reason, and a matrix call spent 30 s
  after its loop on 32 volume reads.
- **136** A horizontal slice cut first to the outer form's reference body (`REF_F_outer`) gives the interior's free section even
  though the door's joint opens the cavity to the outside.
- **137** A wall survey - one needle per flat face of at least 3 mm2, along its inward normal - finds leftovers of earlier cuts
  that volume and lump checks pass (the 0.4 sheet in the right box).
- **138** A leftover sheet comes out cleanly by an extrude cut of its own top face (`extrudeFeatures`, face as profile, negative
  distance, `participantBodies`) on a model copy of the body; check the copy (what went, nothing added, one lump), then swap.
  Stacked temporary prisms would leave steps at a leaning wall.
- **139** Check the time budget before every expensive step, also before a crop made per item, not only inside the inner loop.
