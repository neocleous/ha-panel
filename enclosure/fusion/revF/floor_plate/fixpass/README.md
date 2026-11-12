# rev F - the fix pass after the second assembly audit (2026-11-12)

Brief `claude/brief-enclosure-fix-pass-2026-11-12.md`. Reports in the claude.ai project: `claude/report-enclosure-fix-pass-2026-11-12.md`
(all numbers), `claude/handover-enclosure-fix-pass-2026-11-12.md` (build order in the audit's step numbers, print checks, facts for the
instructions), `claude/brief-architect-update-2026-11-12-fix-pass.md`. Earlier: `../close/README.md`, `../../../audit-asm/README.md`.

## Model "HA Panel v5 - tapered"
| Version | Name | What |
|---|---|---|
| 56 | rev F WIP 2026-11-12 g11 | shell: the two boss holes for the box-top screws on a 10 deg line, 0.5 higher; tabs with wedge seat and relief; carrier plate trimmed; three notches in the LCD opening's edge |
| 57 | g12 | plate: lowered band widened under the rear of the side walls; front feet to (+-80, -5.5) |
| 58 | g13 | leads: USB 240 with its loop, display power lead through the first notch, bay widened to u +37, first notch to u -9.5, slack placed (microphone leads, Pi power, DSI), BME680 lead lifted |
| 59 | g14 | notch for the ReSpeaker's USB plug lengthened to u 84; USB lead's end turns on a radius of 4 |
| 60 | g15 | the two old sensor strips marked `REF_SENSOR_strip_*_retired` |

Archives `~/Documents/HA Panel v5 - tapered revF-g11.f3d` ... `revF-g15.f3d`. Backups hidden in the model with the suffix `_v55`:
front shell, both boxes, carrier, plate, both front feet, seven leads.

## Scripts (`../fusion/`)
This session had no folder access to the Mac and no git push. Scripts went to `docs` through the GitHub connector and were loaded
into Fusion by commit from raw.githubusercontent.com, with their sha256 checked. The library lives in `sys.modules['v5f_k']`
(its dict `c` keeps namespaces, caches and results between connector calls); a step script is run with `k.step(sha, name, sha256, ...)`.
Every connector call stays under 80 s: checks keep their results and are called again until nothing is left.

| Script | What |
|---|---|
| `v5f_k_lib.py` | frames, temporary solids, slabs of the big bodies, crops, needles, hole list, tool lines, camera, `fetch`, `step` |
| `v5f_k_pic.py` | template bodies `AUD_*`, visibility, camera for the connector's screenshot query |
| `v5f_k1a_block1.py`, `v5f_k1b_tab_relief.py` | block 1 |
| `v5f_k2a_tip.py`, `v5f_k2b_plate.py`, `v5f_k2c_band.py` | block 2 (k2c's band tool replaces k2b's) |
| `v5f_k3a_leads.py`, `v5f_k3b_lead_checks.py`, `k3_routes.json` | block 3: a lead is a route (nodes in the board, slab or world frame); the file is the record of all 16 |
| `v5f_k4a_unit_checks.py`, `v5f_k4b_addenda.py` | block 4: way in, ride-in, slide, reach, matrix, chambers; k4b corrects k4a's lead parts and adds the way out |

Not in a script (typed into the connector, parameters in the report): the route generators of block 3 (their result is
`k3_routes.json`), the lengthening of the side notch (one box, board frame u 76.4..84.0, v -1.85..16.25, through the wall),
the marking of the sensor strips, the measurements for the facts of block 5.

## Results in short
- Iron +2.42 and 2.0 key +2.80 on the built 10 deg line; 1.70 of wall under and above each hole.
- Gap at the cloth with the unit 1.5 behind: 1.21 or more. Way in clear at 1.2 to 1.5 behind (graze at 1.05, also in version 55).
- Front feet: tips forward at 8.2 deg about their centres (was 4.2).
- All 16 leads in the record; four spare lengths placed; every lead in a notch with 1.0 or more beside it.
- Ride-in at 23 positions: 0 mm3 for 30 module bodies and 8 lead parts. Interference: 96 bodies, 4 560 pairs, 76 not zero, none new.
- 46 screws, 32 inserts; chambers closed and unchanged.

## Lessons (continue `../close/README.md`, 132-139, and the audit's 140-145)
- **146** A union of some 70 moved copies of a prism with a spline wall did not finish in minutes (the connector gave up at 80 s,
  Fusion stayed busy). Sample the wall's edge with needles and build the tool from plain boxes along the chords.
- **147** `measureMinimumDistance` returns meaningless positions when the distance is 0. Take the place of an overlap from the
  lumps of the intersection.
- **148** A script that raises is rolled back whole by the connector. Guards can be strict, but one guard set too tight costs the
  whole call: compute first, guard, then change the model in the last lines.
- **149** Camera: `viewExtents` is about the visible height in cm. After a perspective camera the orthographic extents come out
  wrong: use orthographic views only. The connector's screenshot query returns the picture as a file.
- **150** A lead that overlaps "its own plug" can hide a real clash with it. Compare the overlap in mm3 with the old lead's, not
  by name (the Pi power lap ran through its plug: 187.8 against 1.25).
- **151** Routes are data. Round the nodes, push the file, rebuild the bodies from the pushed file, and compare by value: a text
  hash differs for 0 and 0.0.
- **152** A rigid ride-in of a lead is meaningful only for the part the module holds, up to the notch floor. Free tails and
  stowed coils give false contacts.
- **153** A lift check needs fine steps where two parts pass each other: the graze of the driver screw heads exists only 6.5 to 8
  below the seat and at less than 1.2 behind.
- **154** A needle through the whole shell costs about 4 s (eight slabs). Crop a local region once and run the needles in that.
- **155** Adding and deleting template bodies leaves the document "modified" though nothing differs from the saved version.
- **156** Before lengthening an existing cut, read its plane faces from the body (normal and extents) and build the tool on them.
  Check the removed volume against the block's arithmetic (7.5 x 18.1 x 5.8 = 787.35) and the lump count before the swap.
- **157** A trial cut on a cached crop shows only what lies inside the crop's box: two trial lengths of the side notch removed
  the same volume because the crop ended before both.
