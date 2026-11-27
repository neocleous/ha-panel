# Model scripts: version 79 → 85 (the drivers' seat)

These scripts changed the Fusion model "HA Panel v5 - tapered" from version 79 to version 85 in the enclosure pass
"the drivers' seat" (register 4f-8, 2026-11-26). The pass gave each speaker driver a seat that takes the driver as it
was measured, put the level faces named by the print re-check on their layer grids, deepened the carrier's two pilots
for the ReSpeaker's screws, and filled the gap behind the boss of the sensor hood's screw.

**The model is at version 85 (g40). It is work in progress, not for print, and waits for its print re-check.**
No print file was made. Nothing here is on `main`.

Lengths are in mm, volumes in mm³. World coordinates: x + = the viewer's left, y + toward the screen, z up from the
base plate's underside.

The brief, the reports of each block, the closing report and the hand-over documents are in the claude.ai Project
"HA Touch Panel" (`claude/brief-enclosure-drivers-seat-2026-11-26.md`, `claude/report-enclosure-drivers-seat-*.md`).

## Which script made which version
| Version | Block | What changed | Scripts that build and put in |
|---|---|---|---|
| 80 (g35) | 2 | the drivers' seat: the shell's two bays, the boxes' fronts with stops and insert columns, the left box's pocket corner, both touch clips, the drivers as measured, their foam, their screw heads, the two speaker leads | `d20`, `d26`, `d21` |
| 81 (g36) | 2 | the clips' screws 3.0 off mid-height, so that the key clears the door opening's arch | `d20`, `d21` |
| 82 (g37) | 2 | the shell's four side bars cut back to the recess; the floor of the relief behind the left magnet on the grid | `d20`, `d21` |
| 83 (g38) | 3 | the level faces on the layer grid: base plate (top, six box seats, foot recesses, noses, the Pi's shoulders, the cradle's web), the boxes' bottoms and tab tops, the left box's pocket end wall, two faces of the shell; the four feet follow | `d31`, `d21` |
| 84 (g39) | 4 | the carrier's two pilots 5.6 deep with an entry chamfer; the ReSpeaker's two M2 × 6 in `SCREWS_M2x6_env` | `d41`, `d21` |
| 85 (g40) | 5 | the gap between the hood's boss and the shell's rear wall filled along the boss | `d51`, `d21` |

Each save is logged in `d21_save.txt` beside the outputs on the Mac. Blocks 0 and 1 were read-only.

**Archive of version 85:** `~/Documents/HA Panel v5 - tapered revF-g40.f3d`, 224,103,003 bytes,
sha256 `a3e9ff82accfa6e218429ee8c41658d45cde2debaf5546c76cc0e38921b2d8c9` (`d63_export.txt`).

## The files
- **`v80_lib.py`** loads the helper libraries of the earlier passes (commit 45a38e4, each checked by its sha256) once
  per Fusion session, and catches a script's printed output into a file.
- **Block 0 and the table:** `d01_preflight.py` (counts, guard volumes), `d02_matrix.py` (every body against every
  other; `compare` lists pairs new, gone and changed between two tables).
- **Block 1 (read-only):** `d10`, `d11`, `d13`, `d14` (the place as it stood, the clips' screws and keys),
  `d22_plancheck.py` (the plan's bodies against the model), `d23_section.py` and `d24_draw.py` (section outlines and
  the drawing in `pictures/`).
- **Block 2:** `d20_build.py`, `d26_leads.py`, `d21_put.py` (hidden `_v79` copies, put, save, read back),
  `d25_checks.py` (differences, walls, small faces), `d27_fits.py` (distances, the shell's way down, the clips' keys,
  the grid, the guards, the chambers, the pocket).
- **Block 3:** `d30_inspect3.py`, `d31_build3.py`, `d32_checks3.py`.
- **Block 4:** `d40_inspect4.py`, `d41_build4.py`, `d42_checks4.py`.
- **Block 5:** `d50_inspect5.py` (with sections drawn in letters), `d51_build5.py`, `d52_checks5.py`.
- **The close:** `d60_close.py` (the last pass's checks run again by their own functions), `d61_run.py` (several
  jobs in one Fusion call; the checked fetch), `d62_close2.py` (all that changed against version 79, the outer skin,
  the leads), `d63_export.py` (the archive).

## How they run
Every script is written here, pushed to this branch, fetched in Fusion from the branch at a named commit, checked by
its sha256 and its closing `# END` line, saved beside the outputs on the Mac
(`~/Documents/HA_panel_renders/drivers_seat_v80/`) and run from there. The outputs are not in the repository; the
reports quote them and name the files.

Only `d21_put.py` changes the document. Every check is read-only and works on temporary bodies.

## What the next pass should know
1. **The connector's reply can come back empty.** Each script writes its output to a file; the file is read.
2. **This Fusion measures distances to temporary bodies.** No `TMP_` body is needed for a distance, so the checks can
   run read-only and leave the document unmodified.
3. **The last pass's checks keep results in the library's cache under fixed names** (`close_gridfit`,
   `close_main01`, `close_rideholder`, and the tags `close79` and `v79s15`). The cache lives as long as Fusion runs.
   Run again on a later version they hand back the old results by face number or body name. `d60_close.py`'s `clear`
   drops them first. It was found when a face of version 79 appeared in version 85's grid list.
4. **`runpy.run_path` hands back a copy of a script's globals.** To replace a helper of a last-pass script, set it in
   the function's own `__globals__`.
5. **`SCREWS_M2x6_env` now holds two screws that belong to the display module.** A walk that leaves the module out
   must leave them out too (`d27_fits.py`, `RESP_SCREWS`); the last pass's walks count the body whole.
6. **`BRepBody.volume` of the shell scatters by a few mm³ after each change.** What a change added or removed is
   read from the difference's lumps.
7. **`d20_build.py` builds block 2 from the `_v79` copies.** Blocks 3 to 5 build from the model as the block before
   left it, so the scripts reproduce the model only in their order.
8. **Fusion on the Mac slows several-fold at times.** Each call stays small; `d61_run.py` does not begin a job once
   its limit is used.
