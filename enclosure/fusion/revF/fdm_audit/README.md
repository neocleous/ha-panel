# Design-for-FDM audit of version 66 (2026-11-18)

Independent audit to `claude/brief-fdm-design-audit-v66-2026-11-18.md`. Model "HA Panel v5 - tapered", version 66 (g21),
**read-only**: every Fusion call ran with `readOnly: true`, no version saved. Report and hand-over:
`claude/report-fdm-design-audit-v66-2026-11-18.md`, `claude/handover-fdm-design-audit-v66-2026-11-18.md` (project docs).

## What is here
| Folder | Content |
|---|---|
| `fusion/` | the three scripts run inside Fusion: preflight and guard volumes, the audit's measurement meshes, the slicer runner |
| `scripts/` | the offline analysis (Python 3, numpy, scipy, trimesh, shapely, embreex, matplotlib) |
| `data/` | results as JSON: `ray_*` true thickness features, `plane_*` thickness in the layers, `gaps_*` / `slits_*` narrow gaps, `slice_place.json`; `block6_slices.txt` (the checks on the last seven slices), `lip_fit.txt` (what stands in front of the lip) |
| `img/` | sections, thickness renders, as-sliced layers, the pictures put to Daniel |

## Method
1. `fusion/f1_export_mesh.py` writes each printed body as a mesh (0.005 mm surface tolerance) into
   `~/Documents/HA_panel_renders/fdm_audit/mesh/` as raw number files. They are measurement meshes, not print files.
2. `scripts/a0_check_mesh.py` checks them against the guard volumes; `a1_slice.py` cuts every part into its print layers
   in its print orientation (`fdm_lib.PARTS`).
3. `a4_ray.py`: true thickness. About ten rays per mm² go from the surface into the material along the inward normal;
   thin samples of one class that lie together are one feature, tagged wall (counted in lines), skin (counted in layers) or sloped.
4. `a2_plane.py`: thickness inside each layer (opening with discs of the class widths), joined over the layers.
5. `a5_gaps.py`: air gaps under 0.45 inside one body (slits between features that should be one piece).
6. `s1_make_jobs.py`, `fusion/f2_slicer.py`, `s2_gcode.py`, `s4_section.py`: audit slices in Bambu Studio 02.09.01.70 with the
   print plan's process (0.20 Standard: 2 walls, 15 % grid, classic walls, thin-wall detection off), no supports, no brim;
   the G-code is read back and each loaded section is compared as sliced with the model.
7. `c1_loads.py`: the load cases. `sec.py`, `secm.py`, `render.py`, `p_exceptions.py`: pictures.
8. Block 6: `a7_holes.py` finds the upright round holes in a part's layers; `s5_block6.py` reads the last seven slices
   (volume by line type, posts and bosses in torsion as sliced, the boxes' touch-clip block and floor boss layer by layer,
   the grommet's walls, regions that start in mid-air); `s6_lip_fit.py` measures what printed parts stand in front of the
   lip's inner faces, after Daniel chose the 2.0 lip.

## Frames
Model mm (Fusion cm x 10): y = minus the depth behind the glass, z = up along the screen.
World: x_w = x_m + 2.55; y_w = c y_m - s z_m; z_w = s y_m + c z_m + 143.3 (c, s of 12 degrees).
Print: (u, v, h) per part, h = height above the bed (`fdm_lib.Part`).

## Lessons
213. Asking all 419 bodies for their volume in one call runs past the connector's 80 s; names and visibility are instant. Read volumes for the bodies you need.
214. `meshManager.createMeshCalculator()` and writing files from Fusion's Python are allowed in a read-only script.
215. Never `time.sleep()` in a connector script: it runs on Fusion's main thread, the call is dropped and the desktop bridge can disconnect.
216. The mesh of a body is not always watertight (shell, base plate) and can carry internal faces; slice sums still agree with the volume to 0.5 %.
217. Colouring a face by its thinnest sample misleads on large faces; cut the mesh to faces under 1 mm first (`render.thickness_mesh`).
218. The print plan's process uses classic walls with thin-wall detection off and fills solid any inner region under 15 mm²: thin bosses come out solid, large cones and posts come out as two lines and a 15 % grid.

219. An as-sliced area counted as line width times layer height reads 100 to 113 % on solid plastic (the lines' rounded sides overlap). Compare against that, not against 100 %.
220. A block that is 2.0 thick round a hole lying in the layers is not 2.0 of plastic: with 2 walls, 5 top and 3 bottom layers the slicer leaves 2 lines beside the hole, 1.0 under it, 0.6 over it and grid behind (the boxes' touch-clip block). A round boss under 15 mm² of inner region is filled solid (the boxes' floor bosses).
221. After a conversation is cut and resumed, `project_write` to an existing doc is refused until the doc has been read with `project_read` in the resumed conversation.
222. Before proposing to thicken a wall inward, list what stands in front of it. The door frame's front faces at y -53.5 stop the box backs in step 19; the 2.0 lip has to stay behind them.

## Status: closed (2026-11-18 19:25)
Blocks 0 to 6 done. Daniel's answers to the four exceptions (18:59): 1a (lip 2.0, grown inward 0.8), 2a (groove web 1.0), 3a (magnet seats stay 0.45,
first-print check), 4a (listed items accepted). All thirteen audit slices read. Guard volumes identical at 16:23 and 18:59:56; the document was
version 66 of 66 and unmodified at 19:02:38. Findings: Blocker 0, Major 2, Minor 7, Note 6. Nothing here is a print file; nothing was written to `main` or `hardware/`.
