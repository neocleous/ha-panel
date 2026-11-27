# Model scripts: version 88 → 91 (the screws' room)

These scripts changed the Fusion model "HA Panel v5 - tapered" from version 88 to version 91 in the enclosure pass
"the screws' room" (register 4f-10, 2026-11-27; D520 to D531). The pass put the speaker boxes' driver opening and stops back
as version 85 had them, and gave five screw joints outside the boxes more room under their tips: the screen plate's two lower
screws and the BME hood's screw (shell), the grommet's two screws and the four screws from the base plate (door), and the two
microphone clamps' screws (clamps).

**The model is at version 91 (g46). It is work in progress, not for print, and waits for the print re-check's third look.**
No print file was made. Nothing here is on `main`.

Lengths are in mm, volumes in mm³. World: x + = the viewer's left, y + toward the screen, z up from the base plate's
underside. Print heights: a box y + 52; the shell 6.80 − y (chin down); the door z − 2.8 (standing); a clamp z − 172.7.

The brief, the reports of each block, the closing report and the hand-over documents are in the claude.ai Project
"HA Touch Panel" (`claude/brief-enclosure-screw-margins-2026-11-27.md`, `claude/report-enclosure-screw-margins-*.md`).

## Which script made which version
| Version | Block | What changed | Scripts |
|---|---|---|---|
| 89 (g44) | 1 | both speaker boxes: the driver's opening back to 40.6 across and the stops' flares whole (D529) | `s20_boxes.py`, `s21_put.py` |
| 90 (g45) | 2 | the shell: the screen plate's two lower insert holes 0.6 deeper (D524), the hood's pilot 1.1 deeper (D526) | `s31_deepen.py`, `s21_put.py` |
| 91 (g46) | 3 | the door: the grommet's two pilots 0.9 deeper (D527), four bosses 0.6 taller with holes 0.6 deeper (D528); both clamps: the head's seat 0.7 shallower (D525); the two clamp screws drawn 0.7 lower | `s40_door.py`, `s41_clamps.py`, `s31_deepen.py`, `s21_put.py` |

Each save is logged in `s21_save.txt` beside the outputs on the Mac. Blocks 0 and 4 were read-only.

## The files
- `s00_lib.py`: loads the last pass's `../model-v85/m00_lib.py` (and through it the earlier libraries, each by its sha256);
  version 88's guard volumes; the six bodies this pass may change; `get()` fetches a script from this branch at a commit and
  refuses it unless its sha256 and END line match; `old()` loads a script of an earlier pass from its folder on the Mac,
  refused unless its sha256 is the repository's.
- `s01_preflight.py`: the document's state, the counts and the 17 guard volumes by both readings against a table.
- `s10_look.py`: faces of a body in a world box (planes, cylinders, cones), needles, what one body has that another lacks.
- `s20_boxes.py`: block 1. The last pass's build of the boxes, step for step, with its aim-2 envelope cut off at the front
  wall's inner face (y −7.0); the checks on the temporary bodies.
- `s21_put.py`: hidden `_v88` copies, put, save, read back. **The only script that changes the document.**
- `s22_old.py`: runs a read-only check of an earlier pass with its output caught into this pass's folder.
- `s30_holes.py`: the holes this pass deepens, read before and after: the plastic behind each floor on the axis and round
  the rim, the wall round it, what lies beyond, the outer skin by the cloth reference `REF_F_outer`, the print.
- `s31_deepen.py`: a hole made deeper in a part, found on the part's own faces so that the cut continues its wall.
- `s40_door.py`: the door's four bosses (their tops, what stands near, the taller columns, the door's way) and the build.
- `s41_clamps.py`: the clamps' seats and the two drawn screws.
- `s50_close.py`: the close: the interference table against version 88's, each changed body against its `_v88` copy, the
  table of every M3 and M2.5 screw, the shell's way down, the door, the hood, the cap with its clamps, the screen plate.

## How they run
Every script is written here, pushed to this branch, fetched in Fusion from the branch at a named commit, checked by its
sha256 and its closing `# END` line, saved beside the outputs on the Mac (`~/Documents/HA_panel_renders/screw_margins_v88/`)
and run from there. The outputs are not in the repository; the reports quote them and name the files.

## What the next pass should know
1. **`s20_boxes.py` builds from the hidden `_v85` copies,** as the last pass's `m15_build.py` did; with `cut=False` it is that
   build and gives version 88's boxes exactly.
2. **The shell is slow.** A copy of it into the document, a put, or a difference of two shells takes 25 to 85 s each. Two
   calls that did two of these ran past the connector's 140 s wait; the connector dropped for a minute and both scripts
   finished. Keep one such step to a call.
3. **Results cached in the library (`k.c`) outlive a version.** Use a tag of the version for the library's `slide` and
   `matrix`, or they hand back the last pass's readings.
4. **`SCREWS_M2x6_env` follows its seats:** the two clamp screws are drawn 0.7 lower, proud of the clamps by 0.7.
5. **The needles of `s30_holes.py` start 0.05 outside a hole's wall,** so a wall reads 0.05 thinner than it is.
6. The connector's reply comes back empty; every script writes its output to a file, and the file is read.
