# Model scripts: version 85 → 88 (the boxes' margins)

These scripts changed the Fusion model "HA Panel v5 - tapered" from version 85 to version 88 in the enclosure pass
"the boxes' margins" (register 4f-9, 2026-11-27; D515 to D519). The pass gave each speaker driver 1.0 to its box all
round and 2.0 behind it, gave the screws into the boxes more room below their tips, read the tip room of every screw
into a printed part and every driver clearance on an approximate figure, and drew the inlet board's two M2 × 6.

**The model is at version 88 (g43). It is work in progress, not for print, and waits for the print re-check's third
look.** No print file was made. Nothing here is on `main`.

Lengths are in mm, volumes in mm³. World: x + = the viewer's left, y + toward the screen, z up from the base plate's
underside. A box prints rear face down: bed = y + 52.

The brief, the reports of each block, the closing report and the hand-over documents are in the claude.ai Project
"HA Touch Panel" (`claude/brief-enclosure-box-margins-2026-11-27.md`, `claude/report-enclosure-box-margins-*.md`).

## Which script made which version
| Version | Block | What changed | Scripts |
|---|---|---|---|
| 86 (g41) | 2 | both speaker boxes: the aim-2 envelope round each driver taken out, the walls rebuilt where it would open a pocket, the holes deeper | `m15_build.py`, `m16_put.py` |
| 87 (g42) | 2 | the right clip's pilot block square, not round (a sliver of 0.15 mm² gone) | `m15_build.py`, `m16_put.py` |
| 88 (g43) | 3 | the inlet board's two M2 × 6 drawn in `SCREWS_M2x6_env` | `m18_inlet.py`, `m16_put.py` |

Each save is logged in `m16_save.txt` beside the outputs on the Mac. Blocks 0, 1 and 4 were read-only.

## The files
- `m00_lib.py`: loads the last pass's `../model-v80/v80_lib.py` (which loads the earlier libraries at commit 45a38e4, each
  by its sha256); version 85's guard volumes; catches a script's output into this pass's folder; `checked()` refuses a
  script whose sha256 or END line does not match.
- Block 0: `m01_preflight.py`.
- Block 1 (read-only): `m10_screws.py` (every round hole of every printed part; what stands under each screw's head; the
  plastic beyond each hole), `m11_holes.py` (the list of screw holes), `m12_driver.py` (the driver's zones to its box),
  `m13_plan.py` (the aim-2 envelope against the boxes), `m14_probe.py` (bodies in a box, faces, needles),
  `m15_build.py` (the plan's bodies, then the build; checks on the temporary bodies).
- Block 2: `m15_build.py`, `m16_put.py` (hidden `_v85` copies, put, save, read back), `m17_checks.py` (walls, small
  faces, the grid, the chambers, the plug).
- Block 3: `m18_inlet.py`.
- Block 4, the close: `m20_close.py` (the interference table and its comparison with version 85's, the guards, the
  shell's way down, the added material's way down, the boxes' slide onto the plate, the box-top screws' key).

## How they run
Every script is written here, pushed to this branch, fetched in Fusion from the branch at a named commit, checked by its
sha256 and its closing `# END` line, saved beside the outputs on the Mac (`~/Documents/HA_panel_renders/box_margins_v85/`)
and run from there. The outputs are not in the repository; the reports quote them and name the files.
Only `m16_put.py` changes the document. Every check is read-only and works on temporary bodies.

## What the next pass should know
1. **`m15_build.py` builds from the hidden `_v85` copies,** so a second run on a later version builds the same boxes.
2. **The aim-2 envelope is one body per driver** (`m15_build.E`): the driver as the model draws it grown 1.0 (the basket's
   cone 1.05, so that its slant keeps 1.0) and its rear end carried 2.0 back. A box keeps aim 2 when nothing of it lies in E.
3. **The shell's way down was walked for what this pass added only** (`m20_close.walkadd`): removed material cannot meet
   anything, so the whole walk now finds what version 85's found, or less. Three full walks of the boxes' backs were run as
   a check and read as version 85's.
4. **`SCREWS_M2x6_env` holds all 11 M2 × 6 now,** two of them the display module's (the ReSpeaker's) and two the cradle's.
5. **The connector's reply comes back empty;** every script writes its output to a file, and the file is read.
6. **Fusion slows on the shell:** needles and walks through it take 1 to 2.4 s a step.
