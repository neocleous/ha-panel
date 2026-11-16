# Runs: print files, 2026-11-16 (Mac clock, CET)

| Time | Call / job | Result |
|---|---|---|
| 15:07:05 | pf_0_preflight | **Model:** version 65 of 65, unmodified; 408 bodies (4 `_v63`, 11 `_v64`); 96 in the unit (16 leads, 13 keep-outs); 37 visible; no `AUD_*`; the nine guard volumes within 0.005 mm³ of the brief; scope B unchanged. **Slicer:** Bambu Studio 02.09.01.70, system presets equal to the 11-14 copies; "Bambu PLA Basic @BBL X2D 0.4 nozzle" present. (A first attempt at 14:44 got no answer from Fusion.) |
| 15:09:37–15:10:30 | pf_1_export | 14 STL. B-rep volumes equal the guard and scope-B figures |
| ~15:11 | pf_1b_cmp | Against recheck2's exports: same triangle counts, mesh volumes and bounds (0.0); triangle order differs |
| 15:16:21 | pf_2_orient | Matrices: scope A fit within 0.000016 mm, scope B from the 11-14 records. Bounds equal to the re-checks' oriented meshes within 0.0001 |
| ~15:18 | pf_4_flatten | ABS and Support for ABS re-flattened, identical to recheck2's flat files. PLA Basic flattened (chain of 4); coloured variants written |
| 15:21:01 | pf_3_cut8 | The shell's first 8.0 mm: 28,319.93 mm³, one lump, 718,420 triangles, bed z 0 to 8.003. Guard checked before and after |
| 15:24:56 | A0_cal, A4_P3a (test) | A0_cal stopped: "no object fully inside" (pos is an offset; the calibration meshes sat round 0, 0). A4_P3a exported for the window, return code 0 |
| ~15:26–15:43 | the 20 jobs and two controls | See below |
| ~15:28 | pf_5_publish (ABS) | 9 projects to `2_…` and `3_…`, plate name and grouping set |
| 15:31 | pf_open | `open -g -a BambuStudio` started a second Bambu Studio (pid 89405). Its windows were out of the tools' reach |
| 15:33 | pf_ps | SIGTERM to pid 89405, started 15:31:40 by pf_open. Daniel's own instance (pid 53911) untouched |
| ~15:39 | pf_5_publish (PLA) | 8 projects to `1_PLA_trial/` |
| 15:46:01 | pf_9_final_guard | Version 65 of 65, unmodified; 408 bodies, 96 in the unit, 37 visible, no `AUD_*`; the nine guard volumes as at the start; scope B unchanged; camera as found; one document open, unmodified |
| ~15:55 | pf_ps (list only) | One Bambu Studio running: pid 53911, Daniel's, started 2026-11-15 22:35:19. Its window "Untitled", an empty plate: none of the three window projects open |
| 15:55:44 | pf_9_final_guard (again, after pf_ps) | As at 15:46:01 and as at the start: version 65 of 65, unmodified; 408 bodies, 96 in the unit, 37 visible, no `AUD_*`; the nine guard volumes and scope B unchanged; camera as found |

## Slices (Bambu Studio's estimates: print / with the printer's preparation, min; the slicer's masses)
| Job | Print / prep | Filament | Note |
|---|---|---|---|
| A0_cal | 46.2 / 63.8 | 14.79 g ABS | |
| A1_P1 | 325.1 / 342.8 | 85.86 g ABS | 1 unsupported region on the left box (PR9) |
| A2_P2 | 41.6 / 59.3 | 13.63 g | as the re-check |
| A3_P3b | 78.8 / 96.4 | 67.32 g | as the re-check |
| A4_P3a | — | — | window project (exported, rc 0) |
| A5_P5 | — | — | window project (exported, rc 0) |
| A0_adh | — | — | window project (exported, rc 0) |
| A6_P4 | 58.6 / 76.3 | 8.63 g | as the re-check |
| A7_P6 | 193.4 / 211.0 | 38.59 g | "floating cantilever" (PR9) |
| A4s_P3a_1m | 590.2 / 607.8 | 164.71 g | stand-in: the shell with blockers, interface geometry in black ABS |
| A5s_P5_1m | 192.4 / 210.0 | 31.15 g | stand-in: the slab, top Z 0, dense interface, in black ABS |
| A0bs_adh_1m | 104.1 / 121.7 | 23.18 g | stand-in: the 8 mm cut, interface geometry in black ABS |
| T0_cal | 29.4 / 35.0 | 18.49 g PLA | |
| T1_P1 | 314.4 / 320.0 | 106.38 g | 1 unsupported region on the right box (PR9) |
| T2_P2 | 36.2 / 41.8 | 17.04 g | |
| T3_P3b | 70.4 / 76.1 | 84.14 g | |
| T4_P3a | 492.8 / 498.5 | 150.01 g | |
| T5_P5 | 197.0 / 202.7 | 36.88 g | |
| T6_P4 | 56.3 / 62.0 | 10.79 g | |
| T7_P6 | 113.1 / 118.7 | 48.23 g | "floating cantilever" |
| Z1_P1_rc2mesh | 326.2 / 343.9 | 85.96 g | recheck2's meshes, this session's settings: the re-check's slice reproduced |
| Z2_P1_rc2mesh_plainABS | 326.2 / 343.8 | 85.96 g | the same with the colourless ABS preset |

## Commits (`docs`)
- `4048255`: README, RUNS, mkcall, `lib/`.
- `44ed3a9`: `fusion/`, the twelve steps.
- `58d2446`: `slicer/`, `calib/`, `offline/`.
- Each file checked against the session's copy by its git blob hash after the push.
