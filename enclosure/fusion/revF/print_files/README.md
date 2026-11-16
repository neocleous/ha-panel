# Print files (2026-11-16): the PLA trial, the ABS adhesion test, the black ABS set (HA Panel v5 rev F, version 65, g20)

Scripts of the print-files session.
- **Brief:** Project doc `claude/brief-print-files-2026-11-16.md`.
- **Sheet:** `claude/print-files-2026-11-16.md`.
- **Report:** `claude/report-print-files-2026-11-16.md`.

Everything here is **read-only on the design**. Every Fusion call ran with `readOnly: true` and saved no version. The adhesion test's cut is a temporary B-rep copy that is never added to the design. Nothing was ordered.

## Where the files are (the Mac)
`~/Documents/HA_panel_renders/print_files/`:

| Folder | What |
|---|---|
| `1_PLA_trial/` | 8 projects `TRIAL_PLA_0` … `_7` (calibration + P1, P2, P3b, P3a, P5, P4, P6), sliced |
| `2_ABS_calibration_and_adhesion_test/` | `ABS_0a_calibration` (sliced), `ABS_0b_adhesion_test_shell_8mm_WINDOW` (for the window) |
| `3_ABS_black_set/` | `ABS_1` … `_7`; P3a and P5 `…_WINDOW` |
| `_work/` | `lib/` (pflib, pfbs and the steps as run, sha256-checked by every call), `exports/` (14 STL + `shell_chin8`), `orient/` (bed meshes, blockers, calibration parts), `slicer/` (`flat/` presets, `jobs/`, `out/<job>/` with 3MF, G-code, `result.json`, logs), `data/` (records), `pf_log.json` |

## Frames
As the re-checks (`print_audit/recheck2/README.md`): world mm, x = x_rel (centred, +x = the viewer's left), y + toward the viewer, z up from the base plate's underside.

Bed meshes use the re-checks' own world-to-bed matrices:
- **scope A** (screen plate, shell, boxes, base plate): recovered from recheck2's export and oriented-mesh pairs, which keep the triangle order;
- **scope B:** recheck/slicer/orient/*.json, `M_world_to_bed`.

The shell's bed frame is bed z = 6.7992 − world y. Its first 8.0 mm are therefore world y ≥ −1.2008.

## Fusion calls (`fusion/`, `lib/`, `mkcall.py`)
`python3 mkcall.py <step> '<json args>' [extra lib files]` prints a short loader. The loader checks `pflib.py`, any extra library and the step on the Mac by sha256, then execs them (`R2_ARGS` set first).

- **`lib/pflib.py`** — recheck2's `r2lib.py` with this session's folders: document, version and guard check, the unit's count, world transforms, mesh export, logging.
- **`pf_0_preflight`** — version 65 of 65, unmodified; counts; the nine guard volumes; scope B; Bambu Studio's version; the system presets against the 11-14 copies; the X2D PLA and ABS presets present; copies recheck2's flat presets.
- **`pf_1_export`** — the 14 printed parts as world STL (0.01 chordal) with B-rep volume, area and centre of mass.
- **`pf_1b_cmp`** — fresh exports against recheck2's: same triangle count, mesh volume and bounds; the triangle order differs.
- **`pf_2_orient`** — the bed meshes (see Frames); copies the shell's blocker mesh.
- **`pf_3_cut8`** — the adhesion test: the shell intersected with a box in a TemporaryBRepManager copy, kept to bed z 0 to 8.0, meshed and put on the bed with the shell's matrix. Guard checked before and after.
- **`pf_4_flatten`** — the system presets flattened from the Mac's Bambu Studio, as recheck/slicer/flatten.py:
  - ABS and Support for ABS re-flattened, identical to recheck2's copies;
  - PLA Basic added;
  - coloured variants written (display colour only; preset names kept).
- **`lib/pfbs.py` + `pf_bs`** — Bambu Studio 02.09.01.70 headless from Fusion's Python (D139), recheck2's `r2bs.py` unchanged. Modes start and poll; three jobs at a time.
- **`pf_5_publish`** — copies each finished 3MF to its folder and name, and sets two plate fields the command line leaves unset:
  - the plate name;
  - the plate's filament grouping, as Manual with the project's nozzles: filament 1 on the main (left) nozzle, Support for ABS on the auxiliary (right).

  Every other zip entry is copied unchanged, G-code included.
- **`pf_open`, `pf_ps`** — open a project in the Mac's Bambu Studio (`open -g`), and list or stop a Bambu Studio instance that `pf_open` started (see Lessons).
- **`pf_copy`** — copies named files from `HA_panel_renders/` into `_work/cmp/` for reading.
- **`pf_9_final_guard`** — the closing check.

## Slicer jobs (`slicer/`)
- **`specs.py`** — every job of the three sets, built from the print plan (log 11-16 §5) and the re-check's job specs: P1_base_boxes, P2_small, Y_screen_solid100, A_shell_v3, B_slab, P5_cap_grommet, B_door.
  - The Support-for-ABS interface (D173) on the shell and the adhesion test; all support in Support for ABS on the slab.
  - Prime towers where both nozzles reach.
  - `python3 specs.py` writes `specs/<job>.json` and builds `jobs/<job>/`.
- **`mkjob.py`** — recheck2's builder with three changes:
  - `"slice": false` exports the project without slicing: the window projects;
  - Title and Description metadata;
  - `{RC2}` for the re-check's folder.

  `pos` is a plain offset added to the mesh's own bed coordinates.
- **`slicer/specs_as_run.json`** — every job's spec as run: the 20 jobs and the two P1 controls (`Z1`: the re-check's meshes; `Z2`: the same with the colourless ABS preset). `specs.py` writes the 20 to `specs/<job>.json`.

## Other scripts
- **`calib/mkcal.py`** — the calibration parts:
  - frame 120/108 × 5;
  - tower 20 × 20 × 30;
  - hole block 40 × 16 × 8 with two Ø4.0 holes 6 deep and two Ø3.4 holes through.

  Watertight; sent to the Mac as binary STL.
- **`offline/blk_clip.py`** — the shell's blockers clipped to its first 8 mm: the band along the chin's edges.
- **`offline/totals.py`** — time and filament per project and per set from the `result.json` files.

## Lessons
- **The command line exports a two-material project without slicing:** `--export-3mf` without `--slice`, return code 0. That is how the window projects are made. Slicing them still stops (PR10, PR17).
- **`pos` in the assemble list is an offset added to the mesh's coordinates, not a place on the bed.** Meshes made round 0, 0 land off the plate ("no object fully inside").
- **The command line drops a plate name that contains `|`**, and writes the plate's grouping as "Auto For Flush" even with `filament-map-mode=Manual`. `pf_5_publish` sets both.
- **A fresh export has the same geometry as recheck2's but another triangle order.** Tree supports then differ slightly: P1 1.1 min shorter and 0.10 g lighter, and PR9's unsupported region is flagged on the other box. With recheck2's meshes the slice is reproduced exactly.
- **`open -a BambuStudio <file>` starts a second Bambu Studio.** The computer-use tools cannot reach that instance's windows. The Open dialog belongs to a macOS service process, so a session cannot open a file in the window itself; Daniel opens it.
- **Bambu Studio names the X2D's nozzles "Main" (left, direct drive, whole bed) and "Auxiliary"** (right, Bowden, x ≥ 20.5; the plate shows "Left nozzle only area").
- **`device_commit_files`** once kept the old content when a new version was committed from the same staged path. Stage each version under a new path.
- **macOS `ps` has no `etimes`.** Use `lstart`.
