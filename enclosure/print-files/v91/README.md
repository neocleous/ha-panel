# Print files of version 91 (register 5d-3, 2026-11-27)

The scripts that made the print files of "HA Panel v5 - tapered" **version 91**: the PLA trial, the ABS calibration plate and
the adhesion test, and the black ABS set (brief `claude/brief-print-files-v91-2026-11-27.md` in the Project). The print files
themselves stay on the Mac, in `~/Documents/HA_panel_renders/print_files_v91/`. Nothing here is a print file.

## How it ran
- **Fusion steps** run in Autodesk Fusion's Python through its MCP connector, read-only (`readOnly: true`), no version saved.
  A call loads `pf91_lib.py` from the Mac's work folder and runs `go(script, function, outfile, ...)`: the script must end with
  its own `# END <name>` line, and its printed text goes to `_work/out/<outfile>`.
- **Bambu Studio 02.09.02.62** runs headless from Fusion's Python through the version-67 chain's queue
  (`print_files_v67/_work/lib/pfbs.py`, read where it is), three jobs at a time. No slice was made in the window.
- **Offline tools** (`pf91_tools.py`, and the re-check's `recheck/r91_lin.py`, `recheck/r91_tools.py`) run as background
  processes under `/opt/homebrew/bin/python3`, beside part C's `cgq.py` (`adversarial_audit_v69/c/`, read where it is).

## Folders
| Path | What |
|---|---|
| `pf91_*.py` | this step's scripts, in the order they ran (below) |
| `recheck/r91_26_blk.py` | the re-check's blocker rules (D477, D545), as `pf91_26_blk.py` ran them on version 91's holes |
| `recheck/r91_lin.py`, `recheck/r91_tools.py` | the re-check's arc-straightener (index for the hole reading) and its `blk` and `cmpset` tools |
| `data/r91_orient.json`, `data/pf91_orient.json` | the world-to-bed matrices: the re-check's and this step's (the 18 matrices equal) |
| `data/r91_21_holes.json` | the round holes read on version 91's model (the re-check's), which the blockers and the hole reading use |
| `stl/door_enf.stl`, `stl/holder_enf.stl` | the two support enforcers: the door's baffle bottom (D418), the holder's window top (D468) |
| `stl/cal_add_v91.stl` | the calibration plate's second block with D473's four additions |
| `specs/<job>/` | every job's spec and slicer arguments as run: `T*` the PLA trial, `A*` the ABS projects; `T02b`, `T04b`, `A06b` are variants for the Architect, not print files |
| `data/pf91_40_publish.json`, `data/pf91_41_totals.json` | the files as published (sha256, plate fields) and the times and grams |

## The steps, in order
1. `pf91_00_preflight` (`main`, `env`), `pf91_01_older` — model, guard volumes, slicer, the re-check's slices; the older print files recorded.
2. `pf91_10_geom` (`export`, `cut8`, `orient`, `cmp`), `pf91_11_cmpset` — the 17 meshes and the adhesion piece; compared with the re-check's.
3. `pf91_26_blk` — the blockers (r91_26_blk's rules), the door's enforcer, the two copied pieces; compared with the re-check's.
4. `pf91_12_cal` — the calibration plate's second block, built on temporary bodies.
5. `pf91_20_jobs` (`jobs`, `start`), `pf91_21_argcmp`, `pf91_22_wait` — the 23 jobs, each the re-check's job for its plate replayed.
6. `pf91_30_stop` (`gsum`, `gcmp`, `lin`, `holes`), `pf91_33_hsum`, `pf91_32_p7`, `pf91_34_hprof`, `pf91_36_prof2`, `pf91_38_lip`,
   `pf91_37_var`, `pf91_35_rerun` — the stop rule (D507, D542): each plate's slice against the re-check's, every hole on its plate.
7. `pf91_31_pic` — the plates seen from above (P1b's clips, D509).
8. `pf91_40_publish`, `pf91_41_totals` — the plates that passed, to their folders; times and grams.
