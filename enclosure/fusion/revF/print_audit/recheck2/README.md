# Print audit re-check of the split (2026-11-15) — HA Panel v5 rev F, version 65 (g20)

Scripts of the print re-check of the split front shell. Brief: Project doc `claude/brief-print-audit-recheck-split-2026-11-15.md`
(amended 22:15). Report: `claude/report-print-audit-recheck-split-2026-11-15.md`; hand-over:
`claude/handover-print-audit-recheck-split-2026-11-15.md`. Everything here is READ-ONLY on the design: every Fusion call ran
with `readOnly: true` and saved no version. Nothing here is a print file; nothing was ordered.

## Frames
World mm as the earlier audits: x = x_rel (centred, +x = the viewer's left), y + toward the viewer, z up from the base plate's
underside. Slab frame: d = −(y·cos12° + (z − 143.3)·sin12°) (depth behind the glass), up = −y·sin12° + (z − 143.3)·cos12°.
Exports are binary STL in world mm (0.01 mm chordal). Each print's bed frame is given by its 4 × 4 world→bed matrix
(`offline/orient2.py`; the matrices are in the results on the Mac, `data/orient_<tag>_plan.json`):

| Print | Build "up" in world | Bed z of a world point |
|---|---|---|
| Screen plate, back down | (0, cos12°, sin12°), the screen's normal | 0.9781·y + 0.2079·z − 16.99 (plate's back at 0) |
| Shell, chin down | (0, −1, 0) | 6.7992 − y |
| Boxes, rear face down | (0, 1, 0) | y + 52.0 |
| Base plate | (0, 0, 1) | z |

## Fusion calls (`fusion/`, `lib/`, the three `mk*.py`)
The library and the step scripts live on the Mac (`~/Documents/HA_panel_renders/print_audit_recheck2/lib/`); a call is a short
loader that checks each file's sha256 and execs it (`mkrun.py <step>`, `mk.py`, `mkbs2.py start|poll`). `fusion/build.py`
joins `r2_common.py` with one step for the first calls.
- `lib/r2lib.py` (= `fusion/r2_common.py`, sha256 7bbb5a1c…) — document, version and guard check (version 65 of 65,
  unmodified, the nine guard volumes of the brief within 0.01 mm³), the unit's count, world transforms, mesh export, logging.
- `fusion/r2_0_preflight.py` — counts (408 bodies, 96 in the unit, 37 visible, no `AUD_*`), guard and scope-B volumes, camera,
  Bambu Studio's version and presets (equal to the copies of 2026-11-14).
- `fusion/r2_1_export.py` — the 14 printed parts as world STL with volume, area and centre of mass.
- `fusion/r2_2_faces.py` — every B-rep face of the five scope-A parts (type, normal or axis, radius, vertex box).
- `fusion/r2_3_orient.py` — world STL → bed STL with a 4 × 4 matrix (pure Python on the Mac).
- `lib/r2bs.py` (sha256 909ef54e…) — Bambu Studio 02.09.01.70 headless from Fusion's Python: a queue of three jobs, children
  reaped with `waitpid(WNOHANG)`; `fusion/r2_bs.py` is its first form.
- `fusion/r2_9_final_guard.py` — the closing check.

## Slicer jobs (`slicer/`)
- `mkjob.py <spec.json>` — assemble list and argument list for one job (every option `--key=value`). `{R2}` / `{OLD}` in a spec
  stand for this run's and the 2026-11-14 run's Mac folders (`R2_MAC_DIR`, `R2_OLD_DIR`). Base options: High Flow nozzles,
  X-Y hole compensation 0.1, elephant foot 0.15, "don't support bridges", tree(auto) at 30°.
- `specs/` — every job: `A_*` scope A, `B_*` scope B, `P*` plan plates, `Y_screen_solid100` the solid screen plate,
  `A_shell_v2` / `A_shell_v3` the shell with blockers (v3 = the recommended settings), `A_shell_v3_L03` a 0.3 first layer,
  `A_shell_ifgeo` the interface's geometry in one material, `*_solid` 100 % infill; `W_*`, `X_*`, `Y_slab_*`, `Z_*` the
  two-material tests (they stop; see Lessons). `T_chin8` never ran (its 36 MB cut mesh could not be copied to the Mac).
- `shell_blockers_v2.txt` — the shell's 14 blocker boxes in world mm (chin's bed edges, ten lip pockets, exhaust rows);
  `offline/blockers2.py` writes them in the bed frame.

## Analysis (`offline/`)
- `r2_gparse.py` — G-code → extrusion segments (npz) with feature and tool; `r2_gsum.py` — time, filament, part-only mass.
- `r2_gq.py` — rasters of a layer's extrusions (lines with their width) and world↔bed transforms.
- `r2_faces.py` — helpers over the face dumps; `r2_vis.py` (by face) and `r2_visreg.py` (by world box) — where a face prints
  against the model along its normal, the share over support, the first layer's features.
- `r2_holes.py` — free radius round each insert hole's true axis, layer by layer.
- `r2_lug.py` — the lug pocket's floor and faces in the boxes as sliced; `r2_shellpos.py` — lands and pads in the shell.
- `r2_cmp_shell.py` — the shell at 0.2 and 0.3 first layer: window faces, lands, post-hole mouths.
- `gsupport.py` — support contacts in world coordinates (from 2026-11-14).
- `r2_tip.py` — the D9 tipping figures (formulas of the ballast pass) restated from the masses as sliced.
- `r2_geom.py`, `r2_survey.py`, `orient2.py`, `r2_sec.py` — orientations, mesh survey, sections (block 1).

## Results
On the Mac in `~/Documents/HA_panel_renders/print_audit_recheck2/`: `exports/` (14 STL), `slicer/` (flat presets, oriented
meshes, jobs, `out/<job>/` with G-code, 3MF, `result.json`, logs), `data/` (Fusion records and `r2_offline_results.tar.gz`,
the cloud analysis results quoted in the report), `r2_log.json`. Audit slices, not print files; none is in git.

## Lessons
- **Two materials in the command line:** with Support for ABS on the second nozzle as support or interface, Bambu Studio
  02.09.01.70 stops after "filament maps changed after pre-slicing" (Manual or Auto map, either nozzle type, with or without
  a tower). Manual map `1,2` without supports prints every object twice. Two objects on two filaments with a tower and no
  supports also stop (`W_switch*`). Slice two-material plates in the window.
- `support-type=tree(hybrid)` is not a valid value; 100 % sparse infill refuses the cubic pattern (use zig-zag).
- **Layer rule:** a layer is printed where its mid-plane is inside the solid. A face exactly on a mid-plane can go either way
  (the boxes' front face at bed z 48.3 printed; the base plate's recess ceiling at 0.5 did not). The shell's bed offset 6.7992
  puts every face square to world y at an odd tenth 0.0008 below a mid-plane, so all of them print 0.1 toward the viewer; a
  0.3 first layer reverses the parity (odd tenths exact, even tenths 0.1 forward).
- **X-Y hole compensation is not applied in layers printed straight onto support** (the shell's post-hole mouths, 4 layers).
- `device_commit_files` refused a 36 MB file (HTTP 400): keep commits well under that.
- The Fusion connector returns after 80 s while the script runs on; reads carry their own time checks.
