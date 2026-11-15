# Runs — print re-check of the split, 2026-11-15 (Mac clock)

| Time | Call / job | Result |
|---|---|---|
| 22:14:33 | r2_0_preflight | version 65 of 65, unmodified; 408 bodies (4 `_v63`, 11 `_v64` backups), 96 in the unit (16 leads, 13 keep-outs), 37 visible, no `AUD_*`; the nine guard volumes within 0.005 mm³ of the brief; scope B unchanged; Bambu Studio 02.09.01.70, presets equal to 2026-11-14's; one document open |
| 22:18:45–22:19:18 | r2_1_export | 14 STL; volumes, areas and centres of mass from the B-rep |
| ~22:18 | Z_cradle_repro | the 2026-11-14 cradle slice reproduced (1.48 g) |
| 22:26:12 | r2_2_faces | face dumps: screen 68, shell 1,492, left box 110, right box 437, base 815 |
| 22:32:43 | r2_3_orient | five scope-A parts in their bed frames |
| ~22:31 | Z_2m_* | two-material tests: Auto map without supports runs; Manual `1,2` prints objects twice |
| 22:34–22:37 | A_screen, A_shell_plain, A_spkbox_L/R, A_base, Y_screen_solid100 | 59.1/76.7 min 37.39 g; 543.0/560.6 129.57 g; 102.0/119.6 29.17 g; 115.9/133.5 31.02 g; 140.0/157.6 25.98 g; 78.8/96.4 67.32 g |
| ~22:36 | A_screen_solid, A_shell_if, X_slab_*, Y_slab_* | stop: cubic at 100 %; two-material support or interface |
| 22:45–22:49 | B_carrier, B_cradle, B_clip_L/R, B_hood, B_door, B_cap, B_grommet, A_shell_ifgeo | 30.5 min 10.39 g; 16.1 1.48; 5.8 0.49; 5.7 0.49; 4.4 0.78; 193.6/211.2 38.59 g ("floating cantilever", as 2026-11-14); 39.5 7.49; 23.9 1.15; ifgeo 598.2/615.8 174.39 g |
| 22:53 | B_slab; W_switch, W_switch_man | 197.2/214.8 29.51 g; both W stop |
| 22:57 | A_shell_v2 (blockers, 5 mm brim, elephant foot 0) | 528.1/545.7 127.64 g |
| 23:00 | A_shell_v2_solid, B_slab_solid, B_door_solid | 586.0/603.6 145.39 g; 365.4/383.0 63.82 g; 208.4/226.0 47.60 g |
| 23:31 | A_shell_v3 (recommended), A_shell_v3_L03 | 528.4/546.0 127.66 g; 517.2/534.9 127.66 g |
| ~23:44 | P1_base_boxes, P2_small, P5_cap_grommet | 326.2/343.8 85.96 g (right box: one unsupported region, as 2026-11-14); 41.6/59.2 13.63 g; 58.6/76.3 8.63 g |
| ~23:45 | T_chin8 | not run: its mesh was not on the Mac |
| 23:45:10 | r2_9_final_guard | version 65 of 65, unmodified; the nine guard volumes unchanged; 408 bodies, 96 unit, 37 visible, no `AUD_*`; camera as found; one document open, unmodified |

Times are Bambu Studio's estimates: print / with the printer's preparation (min); masses are the slicer's, Bambu ABS 1.04 g/cm³.
