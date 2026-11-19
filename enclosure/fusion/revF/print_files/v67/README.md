# Print files of version 67 (2026-11-19): the PLA trial, the ABS calibration and adhesion test, the black ABS set (HA Panel v5 rev F, version 67, g22)

Scripts of the print-files session on version 67.
- **Brief:** Project doc `claude/brief-print-files-v67-2026-11-19.md`.
- **Sheet:** `claude/print-files-v67-2026-11-19.md`.
- **Report and hand-over:** `claude/report-print-files-v67-2026-11-19.md`, `claude/handover-print-files-v67-2026-11-19.md`.
- **Runs:** `RUNS.md`.

Everything here is **read-only on the design**: every Fusion call ran with `readOnly: true` and saved no version; the adhesion
test's cut is a temporary B-rep copy, never added to the design. No `time.sleep()` in any connector script (lesson 215). Nothing
was ordered. The print files of 2026-11-16 (`print_files/`) and the re-check's files (`print_audit_recheck3/`) were only read.

## Where the files are (the Mac)
`~/Documents/HA_panel_renders/print_files_v67/`:

| Folder | What |
|---|---|
| `1_PLA_trial/` | 8 projects `TRIAL_PLA_0` … `_7` (calibration + P1, P2, P3b, P3a, P5, P4, P6), sliced |
| `2_ABS_calibration_and_adhesion_test/` | `ABS_0a_calibration_v67` (sliced), `ABS_0b_adhesion_test_shell_8mm_WINDOW_v67` (for the window) |
| `3_ABS_black_set/` | `ABS_1` … `_7`; P3b, P3a and P5 `…_WINDOW_v67` |
| `_work/` | `lib/` (pflib67, pfbs and the steps, sha256-checked by every call), `exports/` (14 world STL + `shell_chin8`), `orient/` (bed meshes, blockers, calibration parts, one diagnostic box), `slicer/` (`flat/` presets, `jobs/`, `out/<job>/` with 3MF, G-code, `result.json`, logs), `data/` (records), `pf67_log.json` |

## Frames
As the re-checks and the print files of 2026-11-16: world mm, x = x_rel (centred, +x = the viewer's left), y + toward the viewer,
z up from the base plate's underside. Bed meshes use the world-to-bed matrices of 2026-11-16 (`print_files/_work/data/pf_2_orient.json`,
copied as `_work/data/pf_2_orient_v65.json`), as the re-check of version 67 did; the shell's bed frame is bed z = 6.7992 − world y.

## Fusion calls (`fusion/`, `lib/`, `mkcall.py`)
`python3 mkcall.py <step> '<json args>' [extra lib files] [--tag=x]` prints a short loader and keeps it in `fusion/calls/`
(recheck3 lesson 8: every call sent is kept as a file). The loader checks `pflib67.py`, any extra library and the step on the Mac by
sha256, then execs them (`R2_ARGS` set first).

- **`lib/pflib67.py`** — the 2026-11-16 `pflib.py` with version 67, the 14 guard volumes of D228 (the shell within 15 mm³, D228's
  note; the rest within 0.01) and this run's folders.
- **`lib/pfbs.py` + `fusion/pf_bs.py`** — Bambu Studio 02.09.01.70 headless from Fusion's Python (D139), the 2026-11-16 code
  unchanged: a queue of three jobs started with `subprocess.Popen`, polled by separate calls.
- **`pf67_0_preflight`** — version, counts, guard volumes, camera, Bambu Studio, presets, the re-check's files, the files of
  2026-11-16 (sha256 of every project, the `_work` tree counted); then makes `print_files_v67/` and copies the flat presets.
- **`pf67_1_export`** — the 14 printed parts at 0.01 mm chordal and 10°: world STL, then bed STL with the 2026-11-16 matrices (the
  same code as `pf_2_orient`), compared with the re-check's `orient_hr/` meshes.
- **`pf67_1b_cmp`** — fresh bed meshes against the re-check's: triangle counts, in-order vertex differences, bounds.
- **`pf67_3_cut8`** — the adhesion test: the shell's first 8.0 mm (29,467.842 mm³), as `pf_3_cut8`.
- **`pf67_4_copy`** — the re-check's blockers (v3, chin8 v3, the plate's two) and calibration meshes, sha256-checked.
- **`pf67_5_publish`** — each finished 3MF to its folder and name, with the plate name and Manual grouping set; read back.
- **`pf67_6_probe_lip`** — names the faces along the band the PLA shell's slice flags (measures only).
- **`pf67_9_final_guard`**, **`pf67_9b_camera`** — the closing check (model, files of 2026-11-16, new projects) and the camera.

## Slicer jobs (`slicer/`)
- **`specs67.py`** — every job of the three sets: the 2026-11-16 `specs.py` (D181) with the re-check's changes (D237 to D242,
  D247), each as the re-check sliced it. `PF_MAC_WORK=… PF_JOBS=… python3 specs67.py` builds `jobs/<job>/`.
- **`mkjob.py`** — the 2026-11-16 builder, unchanged (`"slice": false` exports a project for the window).
- **`diag67.py`** — the diagnostic jobs X1 to X7 for the PLA shell's warning (not print files).

## Other scripts
- **`offline/check67.py`** — G-code checks: support inside the post insert holes; the screen plate's support by place; totals.
- **`offline/under67.py`** — support under named faces of the shell (recheck3's `r3_under.py` method).
- **`offline/check3mf.py`** — reads a project back: settings, plate, objects and parts, placement.
- **`offline/plan67.py`** — totals per set and the two-material estimate of the window projects (PR17's method).
- The calibration parts come from `print_files/calib/mkcal.py` and `print_audit/recheck3/calib/r3_mkcal.py`, rebuilt here and
  byte-equal to the re-check's copies.

## Lessons of this run
1. **Fresh exports at the same settings reproduce the re-check's meshes:** the same triangles in the same order, vertices within
   0.000015 mm. The adhesion test's cut (a temporary B-rep copy) comes out with the same triangles in another order.
2. **Rounding below 0.0001 mm still moves a slice slightly** where a face lies on a layer's mid-plane (the cap's pocket floors
   print one 0.12 layer lower) and in tree supports (the shell's stand-in 5 min shorter).
3. **The slicer's "could not get support" warning depends on the filament preset.** With the same plain trees, the PLA shell is
   flagged and the ABS shell is not; the G-code under the flagged place is the same. `--debug=4` or higher logs
   `warn_uncovered_overhangs` with the area and the lowest height; filling the gap under the place in a test slice confirms it.
4. **`device_commit_files` creates the folders a path needs.**
5. **A plate thumbnail is written even for an unsliced project** (`Metadata/plate_1.png`, `top_1.png`): the model only, no supports
   or tower.
