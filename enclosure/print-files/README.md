# Print-file scripts

These scripts make the enclosure's print files from the Fusion model "HA Panel v5 - tapered" (version 67). They export
each printed part, set it on the bed in its chosen orientation, and build the Bambu Studio projects for three sets:

- the PLA fit trial;
- the ABS calibration and the adhesion test;
- the black ABS set.

That makes 17 projects in all. 13 are sliced by the scripts; 4 are set up for Bambu Studio's window, because they print
with two filaments. The projects themselves are kept on the Mac, not in this repo (see [`../README.md`](../README.md)).

## How they run
- **The Fusion steps** run inside Autodesk Fusion's Python, sent through Fusion's MCP connector, with the design open.
  Each one is read-only on the design and saves no version.
- **Calls:** `python3 v67/mkcall.py <step> '<json args>' [extra lib files] [--tag=x]` prints a short loader. The loader
  reads `pflib67.py`, any extra library and the step from the Mac's work folder, checks each by sha256, then runs it.
  The repo's files and the Mac's copies must therefore be the same. `mkcall.py` also writes each call to
  `v67/fusion/calls/`; those records are not kept in the repo.
- **Bambu Studio 02.09.01.70** runs headless from Fusion's Python: a queue of three jobs, started by one call and
  polled by the next.
- **The offline checks** run with Python 3, numpy, trimesh and shapely.

## Folders
| Path | What |
|---|---|
| `v67/` | **the version-67 chain, which made the print files of record** (2026-11-19) |
| `mkcall.py`, `calib/`, `fusion/`, `lib/`, `offline/`, `slicer/` | the first version of the chain (2026-11-16, version 65). Its orientation step, `fusion/pf_2_orient.py`, made the world-to-bed matrices that version 67 still uses; `v67/` carries updated copies of its library and slicer code |
| `recheck3/` | four scripts from the print re-check of version 67 that the chain needs (see below) |
| `data/pf_2_orient.json` | **the world-to-bed matrices:** each printed part's orientation on the bed. A byte-for-byte copy of the Mac's file (sha256 `1d37da540a429178f2a9b8ec5e0747dcf0f08c8a8273a09f0694a2d5443c8cf2`). **The scripts still read the Mac's copy** |
| `v67/slicer/specs/` | the job spec of every project, as run: `T*` the PLA trial, `A*` the ABS projects, `A*s_*_1m` the one-material stand-ins of the window projects |

## The steps of version 67, in order
1. `pf67_0_preflight` — the model's version, counts and guard volumes; Bambu Studio and its presets; the re-check's
   files and the files of 2026-11-16. Then it makes `print_files_v67/` and copies the flat presets.
2. `pf67_1_export`, then `pf67_1b_cmp` — the 14 printed parts at 0.01 mm chordal and 10°: world STL, then bed STL with
   the matrices; compared with the re-check's meshes.
3. `pf67_3_cut8` — the adhesion test: the shell's first 8.0 mm.
4. `pf67_4_copy` — the re-check's blockers and calibration meshes, each checked by sha256.
5. `slicer/specs67.py` — builds every job of the three sets with `mkjob.py`, into the Mac's `_work/slicer/jobs/`:
   `PF_MAC_WORK=… PF_JOBS=… python3 specs67.py`.
6. `pf_bs` — runs Bambu Studio: start, then poll; three jobs at a time.
7. `pf67_5_publish` — each finished project to its folder and name, with the plate name and the grouping set; read back.
8. `offline/check67.py`, `check3mf.py`, `under67.py`, `plan67.py` — the G-code checks (support inside the insert holes,
   the screen plate's support by place), a project read back, support under named faces, and the totals per set.
   Run `under67.py` from `v67/offline/`.
9. `pf67_9_final_guard` — the closing check: the model unchanged, the files of 2026-11-16 untouched, the new projects.

The calibration parts come from `calib/mkcal.py` (frame and tower) and `recheck3/calib/r3_mkcal.py` (the hole block
with the pilot lug).

## What the chain reads from the Mac
Under `~/Documents/HA_panel_renders/`:
- `print_files_v67/_work/` — the chain's own work folder: `lib/` (the copies of `pflib67.py`, `pfbs.py` and the steps
  that every call checks), the exports, bed meshes, jobs, slicer output and logs.
- `print_files/_work/` — from the first run: `data/pf_2_orient.json` (the matrices, copied into this repo as
  `data/pf_2_orient.json`), the flat presets in `slicer/flat/` and the v2 blockers in `orient/`. Copies of the matrices
  and presets are also in `print_files_v67/_work/`.
- `print_audit_recheck3/orient_hr/` — the re-check's meshes, v3 blockers and calibration parts.
- `print_audit_recheck2/` and `print_audit_recheck/` — files of the earlier re-checks, preset copies among them.
- Bambu Studio's own system presets.

## The re-check scripts (`recheck3/`)
| Script | What it makes | Run |
|---|---|---|
| `calib/r3_mkcal.py` | `cal_holes_v67.stl`: the calibration's hole block with the sideways Ø2.7 pilot | `python3 r3_mkcal.py <out dir>` |
| `slicer/r3_blockers.py` | the shell's support blockers (version 3) and the adhesion test's set | `python3 r3_blockers.py <out dir>` |
| `offline/r3_gq.py` | bed-frame geometry; imported by `r3_blockers.py` | — |
| `scan/fdm_lib.py` | the analysis library, with version 67's guard volumes; imported by `r3_gq.py` | — |

They run in a Linux workspace, not in Fusion, and look for each other at fixed paths:
- `r3_blockers.py` imports `r3_gq` from `/home/claude/r3/offline/`, so copy `recheck3/offline/` there.
- `r3_gq.py` imports `fdm_lib` from `/home/claude/r3/scan/scripts/`, so copy `recheck3/scan/fdm_lib.py` there.
- `fdm_lib` reads meshes from `/home/claude/r3/scan/mesh/`.
- They read the Mac's files staged under `/mnt/user-data/uploads/HA_panel_renders/`: the matrices, the v2 blockers and
  the re-check's slicer output.

## If the model changes
These are bound to version 67:
- `v67/lib/pflib67.py`: the version, the 14 guard volumes and the printed parts' body names;
- the world-to-bed matrices, valid only while each part keeps its orientation and its face on the bed;
- the re-check's blockers, fitted to version 67;
- `v67/fusion/pf67_3_cut8.py`: the shell's bed frame, bed z = 6.7992 − world y;
- `v67/slicer/specs67.py`: the positions, towers and offsets.

## Notes for running it
- No `time.sleep()` in a Fusion step.
- Don't drive the macOS Open dialog.
- `open -a` starts a second Bambu Studio.

The run logs and session notes of both runs are in the history
([`enclosure/fusion/revF/print_files/` at commit 45a38e4](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee/enclosure/fusion/revF/print_files)).
