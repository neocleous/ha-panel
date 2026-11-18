# Runs — print re-check of version 67 (recheck3), 2026-11-18 / 2026-11-19 (Mac clock, CET)

Times are Bambu Studio's estimates: print / with the printer's preparation (min); masses are the slicer's, Bambu ABS 1.04 g/cm³.
Every Fusion call ran with `readOnly: true`; no version saved. 40 audit slices in all (12 R, 24 H, 4 F); none is a print file.

| Time | Call / job | Result |
|---|---|---|
| 11-18, before 23:37 | preflight (sent inline, text not kept) | version 67 of 67, unmodified; 427 bodies, 96 in the unit, 37 visible, no `AUD_*`; the 14 guard volumes equal to the brief; Bambu Studio 02.09.01.70 |
| 23:37:28–23:38:07 | mesh export (inline, built on `fdm_audit/fusion/f1_export_mesh.py`) | 14 printed bodies as `.v.f32` / `.t.i32` at 0.005 mm, with volume, area, centre of mass and lumps (`data/export_v67.json`) |
| 23:51:54–23:56:24 | `R*` (12 jobs, audit-grade 0.005 meshes) | superseded: the fine meshes lengthen the slice (R1_P1 359.6 min 86.77 g against H1_P1 329.3 min 86.31 g; R4_P3a_w2 597.6 min 182.86 g; R4_P3a_w4 601.2 min 195.42 g) |
| 23:55:01, 23:56:11 | print-file-grade export, two calls (inline, built on `print_files/fusion/pf_1_export.py` and `pf_2_orient.py`) | 14 bodies as bed STL at 0.01 mm chordal and 10° normal deviation into `orient_hr/` (shell 1,162,054 triangles, base plate 843,906, cradle 240,938, door 135,210) |
| 23:52:54 | the 8 mm cut (inline, built on `print_files/fusion/pf_3_cut8.py`) | the shell's first 8.0 as a temporary body: 29,467.842 mm³, one lump, bed 29.54..226.46 × 39.41..122.74 × 0..8.0032; the shell's volume 111,611.475 before and after; document unmodified. Cut again at print-file grade in the second export call (724,218 triangles, the same volume) |
| 23:56:44 | H1_P1, H4_P3a_w2, H4_P3a_w4 | 329.3/346.9 86.31 g; 592.2/609.8 181.20 g; 595.2/612.9 193.76 g |
| 23:57:47 | H1s_P1_solid, H3_P3b_nosup, H3_P3b_tree_if | 329.9/347.6 88.00 g; 80.0/97.6 65.56 g; 89.3/106.9 67.98 g |
| 23:58:41 | H3_P3b_norm_if, H7_P6, H2_P2 | 84.2/101.8 66.62 g; 196.5/214.2 41.31 g ("floating cantilever", PR9); 42.9/60.5 14.10 g |
| 23:59:53 | H6_P4, H5_P5s, H0_cal | 60.1/77.8 8.69 g; 192.3/209.9 31.15 g; 47.1/64.7 15.27 g |
| 00:00:45 | H0_cal_solid, H0_adh_w2, H0_adh_w4 | 50.7/68.4 17.95 g; 104.8/122.4 23.73 g; 108.5/126.2 25.74 g |
| 00:01:01 | H4_P3a_w3, H3_P3b_tree, H3_P3b_norm | 590.5/608.2 191.50 g; 83.0/100.6 66.17 g; 81.5/99.1 65.90 g |
| 00:01:16 | H1w_P1_w4, H4_P3a_w2_nosup | 333.0/350.7 87.14 g; 290.9/308.5 89.67 g |
| 00:01:30 | H7_P6_trees | 198.5/216.1 41.65 g |
| 00:14:44 | H7_P6_thin, H7_P6_arachne | 196.1/213.8 41.17 g; 196.1/213.8 41.11 g |
| 00:23:07 | H6_P4_capthin | 60.2/77.8 8.68 g |
| 00:31:43 | F4_P3a, F0_adh, F3_P3b (the recommended window plates as one-material stand-ins) | 594.9/612.6 193.87 g; 108.1/125.7 25.68 g; 88.5/106.1 67.87 g |
| 00:38:03 | F4_P3a_w2 | 592.2/609.9 181.31 g |
| 00:54:44 | `fusion/r3_9_final_guard.py` | version 67 of 67, unmodified; 427 bodies (4 `_v63`, 11 `_v64`, 11 `_v65`, 8 `_v66` backups), 96 in the unit (16 leads, 13 keep-outs), 37 visible, no `AUD_*`; the 14 guard volumes equal to the brief to 0.001 mm³, one lump each; camera as found; one document open, unmodified |

The recommended set: P1 = `H1s_P1_solid`, P2 = `H2_P2`, P3b = `F3_P3b`, P3a = `F4_P3a`, P5 = `H5_P5s`, P4 = `H6_P4_capthin`, P6 = `H7_P6_thin`,
calibration = `H0_cal_solid`, adhesion test = `F0_adh`.
