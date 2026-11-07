# Print audit — runs (2026-11-06 / 07)

Audit of the 14 prints of **HA Panel v5 - tapered**, version 35, "rev F WIP 2026-11-06 d19: printability - 46 deg gussets under
both main-board bracket halves' lower board-boss arms (no support under them printed upright), insert holes kept (Claude)".
Report: Project doc `claude/report-print-audit-2026-11-07.md`. Data and images: `~/Documents/HA_panel_renders/print_audit/`.

## Layout
| Folder | What |
|---|---|
| `fusion/` | Fusion 360 scripts (run on the Mac through the MCP loader below). Mac copies in `~/Documents/HA_panel_renders/print_audit/scripts/`. |
| `offline/` | Python 3 scripts run in the cloud container on the exported meshes (trimesh 5.2, numpy 2.5, scipy 1.18, matplotlib 3.11). |
| `slicer/` | The ASSUMED PrusaSlicer profile and the slice batches. |

The offline scripts carry the container paths they ran with: working folder `/home/claude/pa` (`data/`, `work/`, `slice/`,
`img/`) and the exports staged from the Mac at `/mnt/user-data/uploads/print_audit/exports/`. Edit those two roots to rerun
elsewhere.

Fusion loader (lessons 63, 75): `exec(open(path, encoding='utf-8').read(), G); G['run'](None)`, every script `readOnly: true`.
`pa_common.py` is exec'd after `~/Documents/v5f_common.py` and `~/Documents/v5f_b5_common.py` (sha256 9ca15203… / 0a7ca558…,
equal to the repo copies on `docs` at d75f2755). Log: `~/Documents/HA_panel_renders/print_audit/pa_log.json`.

## Fusion runs
| When | Script | Settings | Wrote | Result |
|---|---|---|---|---|
| 2026-11-06 23:50:09 | `fusion/pa0_preflight.py` | readOnly; activates the design model (the exploded-prints copy was active) | `data/pa0_preflight.json` | version 35 = latest, description equal; 13 guard volumes within ±0.00005 cm³, MAIN_BRACKET 2 lumps; 286 bodies, 25 visible; 8 `name (n)` bodies, none zero-volume; helper sha256 equal to the repo |
| 2026-11-06 23:50:44 | `fusion/pa1_export.py` | readOnly; mesh calculator, surface tolerance 0.01 mm, max normal deviation 10°; world mm (x_rel = x + 2.55, z up, floor z 0); bracket halves split by lump side | `exports/<tag>.stl` (14) | 18.1 s; mesh volumes within 0.031 % of the bodies (`offline/load_check.py` → `data/mesh_check.json`) |
| 2026-11-06 23:51:35 | `fusion/pa2_holes.py` | readOnly; cylindrical and conical faces r ≤ 5 mm | `data/pa2_holes.json` | 1117 faces |
| 2026-11-07 01:37:10 | `fusion/pa9_final.py` | readOnly; compares with pa0, then re-activates the exploded-prints copy | `data/pa9_final.json` | guard volumes unchanged (max deviation 0.00004 cm³), version 35, no document modified, visible list and both views as found, exploded copy unchanged and active again |
| 2026-11-07 02:14:27 | `fusion/pa3_bodies.py` | readOnly; activates the design model to list it, then re-activates the document that was active (took ≈ 8 min; Fusion answered no MCP call meanwhile) | `data/pa3_bodies.json` | 273 non-printed bodies with visibility, volume and box gap to each print; active document before = after (exploded-prints copy) |
| 2026-11-07 02:28:28 | `fusion/pa3_compfits.py` | readOnly; reads the design model **without activating it**; guard as pa_common; 47 current component bodies (model audit brief's list + LCD module bodies); measure-manager minimum distance for every print–component pair whose boxes come within 1 mm; meshes (0.01 mm) of the 35 components within 0.6 | `data/pa3_compfits.json`, `exports/comp/*.stl` (35) | 39.4 s; 130 pairs; guard OK; active document unchanged |
| 2026-11-07 02:43:52 | `fusion/pa9_final.py` (re-run after the component pass) | as above | `data/pa9_final.json` (replaces the 01:37 record) | guard volumes unchanged (max deviation 0.00004 cm³), version 35 = latest, no document modified, 286 bodies, visible list and both views as at the preflight, exploded copy unchanged and active |

## Offline runs (cloud container, Python 3.13, trimesh 5.2.0, numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2)
Build frame: the world mesh rotated so the build direction U (world vector, `pa_geom.ORIENT`) points to +z, z_min moved to 0.
Layers: first 0.20, then 0.20; each sampled at its mid-plane + 2e-4 mm (PrusaSlicer 2.7.2 convention, checked on test cubes
`slice/cube_2.3–2.6`). Rasters: even-odd scanline fill of plane-section segments at pixel size px.

| Script | Arguments / settings | Output |
|---|---|---|
| `offline/pa_layers.py <tag> <orient> <px>` | px 0.025 (clips, grommet, hood), 0.03 (cradle, brackets), 0.05 (carrier, cap, boxes), 0.06 (door, slab), 0.08 (front); orientations: plan for all; slab side+x / side−x / back_down; grommet side+x / side+z / side−z / flange_up; brackets flat+y / flat−y | `data/L_<tag>_<orient>.json`, `work/M_*.npz` |
| `offline/pa_summ.py` | unsupported = beyond 0.346 mm (60°) of the previous layer; bridge vs cantilever by anchor components; clusters ≥ 0.5 mm² | `data/S_*.json` |
| `offline/pa_thin.py` | opening at w = 0.84 (two 0.42 lines), widths refined on a 0.01 mm raster; gaps = closing 0.2 | `data/T_*.json`, `data/thin_*.txt` |
| `offline/pa_p7.py` | first layer z 0.1, convex hull, CoG, height / short side, long straight bed edges, 5 mm brim fit in 256 × 256 × 260 and 235.5 × 256 × 256 | `data/p1p7.json` |
| `offline/pa_zq.py` | horizontal faces → printed z under the mid-plane rule | `data/zq.json` |
| `offline/pa_fits.py A B` | points on A within 0.6 mm of B, 3 mm clusters | `data/fits.jsonl` |
| `offline/pa_fits_verify.py A B` | re-tests every point `pa_fits.py` signs as inside (closest-triangle normal) with the generalised winding number of B (B not watertight: the front) or `B.contains`; the reverse pair with `A.contains` (door / front forward only: the reverse ran out of memory) | `data/fits_verify.jsonl` (all negative spots: winding 0, i.e. sign errors next to edges) |
| `offline/pa_fits2.py A B` | facing-face clearances: sample A (4 / mm²), keep points within 1.6 mm of B's vertices or a dense surface sample of B, nearest point on B, keep pairs with n_A · n_B < −0.8 and gap < 0.6; inside points confirmed by winding number / contains; regions on a 2 mm grid, contact (< 0.05) and gap regions separate; area bands 0 / 0.05 / 0.15 / 0.25 / 0.35 / 0.45 / 0.5 / 0.6. Run on the 24 printed pairs whose boxes come within 1 mm, and on 45 print–component pairs from `pa3_compfits.json` (component meshes from `exports/comp/`) | `data/fits2.jsonl`, `work/F2_*.npz` |
| `offline/pa_p8.py` | bracket halves upright: section modulus per layer; horizontal force at the upper board screws (world z 80.5); Bambu ASA TDS V3.0 bending strength Z 40 MPa / XY 65 MPa | `data/p8_bracket.json` |
| `offline/pa_img.py`, `pa_montage.py`, `pa_vsec.py` | layer images (red = beyond 0.346 mm of the layer below), vertical sections (red ≥ 60° down) | `images/*.png` |
| `offline/pa_export_oriented.py` | oriented STLs for the slicer | `slice/orient/*.stl` |
| `offline/pa_gcode.py <gcode…>` | extrusion volume by `;TYPE` (only moves with X/Y and positive E), print time and mass from the footer | `data/gcode_summary*.jsonl` |
| `offline/pa_gview.py`, `pa_p11_views.py` | G-code layer views; offset = centre of the part's extrusion box minus the mesh box centre | `images/p11_*.png`, `data/p11_*.json` |
| `offline/pa_contacts.py`, `pa_contact_faces.py`, `pa_contact_regions.py <gcode tag> <tag> <orient>` | support top cells (0.25 mm grid) with part extrusion in either of the next two layers; nearest mesh face (16 nearest centroids, exact distance) gives the touched face and its world normal; regions = 1 mm z bands, 8-connected | `data/contact_regions.json`, `data/layer_summaries.zip` (C_*, CF_*, cells) |
| `offline/pa_wallcheck.py <gcode tag> <tag> <orient> x0 x1 y0 y1 z0 z1` | the part's extrusion moved to world coordinates; extrusion length per layer inside a world box (does the slicer print a thin wall) | console (cap front wall, cradle bezel, clip wall, cap lip end) |

## Slicer runs (PrusaSlicer 2.7.2, Ubuntu package; the GitHub release download was refused by the proxy)
Profile `slicer/x2d_asa_assumed.ini` — **ASSUMED X2D / ASA settings, not Bambu Studio's**: bed 256 × 256, height 260;
nozzle 0.4; layers 0.20 (first 0.20); 2 perimeters, Arachne, thin walls on; top 5 / bottom 3; 15 % gyroid; widths 0.42 external /
0.45 / 0.50 first layer / 0.42 support; 260 / 100 °C; organic supports, threshold 30°, don't support bridges on, contact
distance 0.2 top / 0 bottom, 3 interface layers, XY spacing 50 %, support on build plate only **off**; no skirt, no brim;
elephant-foot compensation 0; speeds 300 perimeter / 200 external / 270 infill / 150 support; max volumetric 18 mm³/s;
density 1.05 g/cm³.

| Batch | Command | Prints |
|---|---|---|
| `slicer/run_slices.sh` | `prusa-slicer --load x2d_asa_assumed.ini --export-gcode --output gc_<tag>_plan.gcode orient/<tag>_plan.stl` | 14 prints in the planned orientation |
| slab on its side | same profile, `orient/slab_side+x.stl` | slab side+x |
| `slicer/run_alt.sh` | same profile | grommet side+x / side+z / flange_up; brackets flat+y / flat−y; brackets flat+y with `--no-dont-support-bridges` |
| front, build plate only | `--support-material-buildplate-only` | front plan (990 s) |

G-code, logs and profile: `~/Documents/HA_panel_renders/print_audit/data/print_audit_slices_2026-11-07.zip`. The CLI printed no warnings for any
print (it has no floating-region or empty-layer alerts; those are GUI-only).
