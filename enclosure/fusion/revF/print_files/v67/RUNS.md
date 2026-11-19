# Runs: print files of version 67, 2026-11-19 (Mac clock, CET)

Every Fusion call ran with `readOnly: true` through `mkcall.py`'s sha256-checked loader; no version saved; no `time.sleep()`.
Each call's text is kept in `fusion/calls/`.

| Time | Call / job | Result |
|---|---|---|
| 08:58:21 | pf67_0_preflight | **Model:** version 67 of 67, unmodified, "rev F WIP 2026-11-18 g22: FDM fixes (FDM2-FDM13, D222-D228) - not for print"; 427 bodies (4 `_v63`, 11 `_v64`, 11 `_v65`, 8 `_v66`); 96 in the unit (16 leads, 13 keep-outs); 37 visible; no `AUD_*`; the 14 guard volumes of D228 equal to 0.001 mm³, one lump each; one document open. **Slicer:** Bambu Studio 02.09.01.70; its system presets equal to the copies of 2026-11-14; the 2026-11-16 flat presets equal to the re-check's. **Re-check's files found:** `orient_hr/` meshes, blockers v3, chin8 v3, plate blockers, calibration meshes. **Print files of 2026-11-16:** 17 projects, each equal to its recorded size and sha256; `_work/` 284 files, last change 2026-11-16 15:55:49. No Bambu Studio running. **New folder made:** `print_files_v67/` with its three set folders and `_work/`; the flat presets copied (identical). 18.6 s |
| 09:01:00 | pf67_1_export | The 14 printed parts at 0.01 mm chordal and 10°, world STL in `exports/` and bed STL in `orient/` with the matrices of 2026-11-16 (`pf_2_orient.json`, as the re-check). B-rep volumes equal to the guard. Triangle counts equal to the re-check's print-file-grade meshes (shell 1,162,054; base plate 843,906; cradle 240,938; door 135,210 …). 34.4 s |
| 09:01:38 | pf67_3_cut8 | The shell's first 8.0 mm: **29,467.842 mm³**, one lump, 724,218 triangles, bed 29.54..226.46 × 39.41..122.74 × 0..8.0032; the shell 111,611.475 before and after. 6.8 s |
| 09:01:45 | pf67_4_copy | From `print_audit_recheck3/orient_hr/`, sha256-checked: `shell_plan_blk_v3.stl`, `shell_chin8_blk_v3.stl`, `screen_plan_blk.stl`, `cal_frame.stl`, `cal_tower.stl`, `cal_holes_v67.stl`; the matrices as `data/pf_2_orient_v65.json` |
| ~09:02 | pf67_1b_cmp | Fresh bed meshes against the re-check's: the 14 parts have the same triangles in the same order, vertices within 0.000015 mm (float rounding). The 8.0 cut has the same triangles (centroids within 0.000017 mm, checked in the cloud) in another order |
| (cloud) | `calib/r3_mkcal.py`, `print_files/calib/mkcal.py` | Rebuilt: `cal_holes_v67` (1,966 triangles, 5,650.28 mm³, x −20..28, y −8..8, z 0..8; pilot Ø2.7 along x 22.5..28, axis z 3.35), `cal_frame`, `cal_tower`: each byte-equal to the re-check's copy after the header |
| 09:06:50 | T4_P3a, T1_P1, T5_P5 → T7_P6, T3_P3b, T2_P2, T6_P4, T0_cal | **The PLA trial, sliced** (Bambu PLA Basic, Textured PEI, plain trees): see the table below |
| 09:09–09:26 | X1_T4_blkv2, X2_A4s_plain, X3_T4_pos30, X4_T4_w2, X5_T4_dbg, X6_T4_thin, X7_T4_lipfill (diagnostics, `slicer/diag67.py`; not print files) | The PLA shell's warning "2 overhang region(s) that could not get support" traced: it stays with the blockers v2 (X1), at the ABS position (X3), with 2 walls (X4) and with thin-wall detection (X6); not in ABS with the same plain trees (X2). The trace log (X5): "2 of 173 region(s) uncovered, 172.933 mm2, lowest_z=0.6". With the gap under the band along the chin's top edge (between the cloth groove and the screen) filled (X7, a box x 36..220, y 87.15..89.35, z 0..0.45 joined to the shell) the warning is gone: both regions are that band, which starts 0.4 above the bed. In the slice the band's lowest 0.2 (0.48 wide) is not printed; it prints from 0.6 up, on support interface at 0.2 and 0.4; the ABS slices leave out the same 0.2 |
| 09:26:32 | pf67_5_publish (PLA, 7) | `1_PLA_trial/`, plate names and Manual grouping set |
| 09:27:33 | pf67_5_publish (T4_P3a) | `1_PLA_trial/TRIAL_PLA_4_P3a_shell_v67.3mf` |
| ~09:28 | A1_P1, A7_P6, A2_P2 → A6_P4, A0_cal | **The ABS calibration and the one-material ABS plates, sliced** (table below) |
| 09:30:58 | pf67_5_publish (ABS, 5) | `2_ABS_calibration_and_adhesion_test/ABS_0a_calibration_v67.3mf`; `3_ABS_black_set/` P1, P2, P4, P6 |
| ~09:31 | A4_P3a, A0_adh, A3_P3b, A5_P5 (`--export-3mf` without `--slice`) | The four window projects exported, return code 0 each |
| 09:31:50 | pf67_5_publish (window, 4) | `ABS_0b_adhesion_test_shell_8mm_WINDOW_v67.3mf`, `ABS_3_P3b_screen_plate_WINDOW_v67.3mf`, `ABS_4_P3a_shell_WINDOW_v67.3mf`, `ABS_5_P5_slab_WINDOW_v67.3mf`: plate names and Manual grouping `1 2` set |
| 09:32–09:38 | A4s_P3a_1m, A0s_adh_1m, A3s_P3b_1m, A5s_P5_1m | The one-material stand-ins (interface geometry in black ABS), table below |
| (cloud) | `offline/check3mf.py` on the four window projects | Filaments 1 Bambu ABS (black) and 2 Bambu Support for ABS (white), Shrinkage 100 % each; filament map 1, 2 Manual (project and plate); both nozzles High Flow; trees; support filament 1 and interface filament 2 (slab: 2 and 2); top Z distance 0; 2 interface layers; interface spacing 0; prime tower on, 35 wide at x 110, y 205 (slab: 30 wide at x 30, y 110); walls 4 (test, shell) and 2; the plate 100 % zig-zag; brims 5 / none / 5 / 3; X-Y hole compensation 0.1; elephant foot 0.15; "don't support bridges"; the blockers are support-blocker parts of the part's own object; no G-code inside |
| ~09:42 | pf67_6_probe_lip | The faces of the shell along the band the PLA slice flags (world x ±93, y 4.2..6.4, z 49.0..52.6): the cloth groove's upper wall (251 mm², facing down the screen, 1.0 from the slab), the band's top (163 mm², x ±45, 0.2 from the screen plate: the slit) and the groove's web (144 mm², x ±48, facing the viewer). The flagged strip is the band's front between the groove and the screen's bottom edge, 0.4 behind the chin's face |
| 09:45:23 | pf67_9_final_guard | **Model:** version 67 of 67, unmodified, the same description; 427 bodies (4 `_v63`, 11 `_v64`, 11 `_v65`, 8 `_v66`), 96 in the unit (16 leads, 13 keep-outs), the same 37 visible, no `AUD_*`; the 14 guard volumes equal to D228 (difference 0.000 mm³), one lump each; one document open, unmodified. **The print files of 2026-11-16:** all 17 projects equal to the start (bytes, mtime, sha256); `_work/` unchanged (284 files, 966,543,465 bytes, last change 2026-11-16 15:55:49). **The 17 new projects** equal to their publish record. No Bambu Studio running. **The camera is not as found** (next line) |
| 09:46:00 | pf67_9b_camera | The view moved between 08:58 and 09:45: eye (−86.2, −14.8, −8.9) → (−245.4, −157.6, 77.1), target (−0.26, −8.86, −4.87) → (−20.30, −16.60, 0.27), same visual style. No call of this session sets the camera (every call read-only, none touches the viewport); the document is unmodified. Left as it is |

### The PLA trial (Bambu Studio's estimates: print / with the printer's preparation, min; grams)
| Job | Print / prep | PLA | 2026-11-16 | Warning |
|---|---|---|---|---|
| T0_cal | 34.5 / 40.2 | 22.43 g | 29.4 / 35.0, 18.49 g | |
| T1_P1 | 318.4 / 324.1 | 109.08 g | 314.4 / 320.0, 106.38 g | one overhang region on the right box (PR9) |
| T2_P2 | 37.9 / 43.5 | 17.62 g | 36.2 / 41.8, 17.04 g | |
| T3_P3b | 75.2 / 80.8 | 83.01 g | 70.4 / 76.1, 84.14 g | |
| T4_P3a | 494.4 / 500.1 | 170.84 g | 492.8 / 498.5, 150.01 g | 2 overhang regions without support: the band along the chin's top edge, between the cloth groove and the screen (diagnostics above) |
| T5_P5 | 197.0 / 202.6 | 36.87 g | 197.0 / 202.7, 36.88 g | |
| T6_P4 | 56.5 / 62.1 | 10.82 g | 56.3 / 62.0, 10.79 g | |
| T7_P6 | 119.7 / 125.3 | 51.45 g | 113.1 / 118.7, 48.23 g | "floating cantilever" (PR9) |
| **Set (7 plates)** | **21 h 39 / 22 h 19** | **479.68 g** | | |
| **With the calibration** | **22 h 14 / 22 h 59** | **502.11 g** | 21 h 50 / 22 h 35, 471.95 g | |

Checks (`offline/check67.py`): T4_P3a no support inside the four post insert holes (0 lines; X1 without the cylinders 20–21 mm³ in each); T3_P3b no support in the peg pocket or slot, 2,127 mm² of support under the border, the rest the trees' feet beyond the plate's two ends.

### The ABS calibration and one-material plates (against the re-check's slices of the same jobs)
| Job | Print / prep | Black ABS | Re-check | Warning |
|---|---|---|---|---|
| A0_cal | 50.7 / 68.4 | 17.95 g | H0_cal_solid 50.7 / 68.4, 17.95 g: identical | |
| A1_P1 | 328.3 / 345.9 | 87.96 g | H1s_P1_solid 329.9 / 347.6, 88.00 g | one overhang region on the right box (PR9) |
| A2_P2 | 42.9 / 60.5 | 14.10 g | H2_P2: identical | |
| A6_P4 | 58.8 / 76.4 | 8.66 g | H6_P4_capthin 60.2 / 77.8, 8.68 g | |
| A7_P6 | 196.5 / 214.1 | 41.16 g | H7_P6_thin 196.1 / 213.8, 41.17 g | "floating cantilever" (PR9) |

- The differences come from the fresh meshes (vertices within 0.000015 mm of the re-check's): A6_P4's pocket floors lie on a layer's mid-plane (re-check §4) and print one layer (0.12) lower here (top surface at bed z 1.64 instead of 1.76; −1.35 min, −0.03 g); A7_P6 differs in travel only (+0.38 min); A1_P1 −1.6 min, −0.04 g.
- **The cap's 0.60 end walls print as in the re-check's slice with thin-wall detection** (layers 14 to 21, the wall band along the outline: the same uncovered area as H6_P4_capthin in every layer, 1 mm² less than without the setting; cloud check with `offline/check67.py` parsing).
- Boxes and the calibration block solid: the masses equal the re-check's 100 % slices (88.0 g against 86.3 g at 15 %; 17.95 g against 15.27 g).

### The window projects' stand-ins and the two-material estimate (`offline/plan67.py`, method of PR17)
| Window project | Stand-in (one material) | Re-check's stand-in | Estimate with two materials |
|---|---|---|---|
| Adhesion test | 108.5 / 126.2 min, 25.69 g | F0_adh 108.1 / 125.7, 25.68 g | about 1 h 55 / 2 h 13; 27.2 g black ABS, 2.30 g Support for ABS (272 mm³ on 38 layers, 76 changes, tower 3.4 cm³) |
| P3b screen plate | 88.5 / 106.1 min, 67.87 g | F3_P3b: identical | about 1 h 29 / 1 h 46; 66.8 g, 1.37 g (1,093 mm³ on 2 layers, 4 changes, tower 0.2 cm³) |
| P3a shell | 589.8 / 607.5 min, 194.31 g | F4_P3a 594.9 / 612.6, 193.87 g | about 10 h 39 / 10 h 57; 203.7 g, 20.58 g (4,380 mm³ on 297 layers, 594 changes, tower 26.7 cm³) |
| P5 slab | 192.4 / 210.0 min, 31.15 g | H5_P5s 192.3 / 209.9, 31.15 g | about 3 h 14 / 3 h 31; 28.1 g, 4.29 g (all support, 3,295 mm³ on 9 layers, 18 changes, tower 0.8 cm³) |

Checks on the stand-ins (`offline/check67.py`, `offline/under67.py`):
- no support inside the shell's four post insert holes (A4s) or the adhesion test's two (A0s); none in the plate's peg pocket or slot (A3s);
- under-face support, A4s against the re-check's F4_P3a, identical: top lands 100 % (interface 100 %), bottom lands and pegs 100 % (100 %), lip at the arch 86 % (85 %), radar pocket and brace 99 % (99 %), the groove's roof bridged (0 %); the band along the chin's top edge 99 % on interface (the PLA shell, plain trees: 48 %);
- A4s is 5.1 min shorter than F4_P3a (support −3.0 min, travel −1.9 min): the trees move with the fresh meshes' rounding (lesson 4 of 2026-11-16).

Note on the calls kept in `fusion/calls/`: the `pf_bs` poll calls were sent with different `only` lists (the jobs named in each
poll above); each is `pf_bs_poll.call.py` with that list in `R2_ARGS`. The diagnostic box of X7 is `offline/diag_lipfill_box.py`'s
output (byte-equal after the header).
