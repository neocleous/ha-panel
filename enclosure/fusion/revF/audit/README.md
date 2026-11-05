# HA Panel v5 rev F (c2) — model audit scripts (2026-11-05/06)

Independent read-only audit of **"HA Panel v5 - tapered"**, version 23 ("rev F WIP 2026-11-05 c2: …", 214 bodies), under
`claude/brief-model-audit-2026-11-05.md`. Report: Project doc `claude/report-model-audit-2026-11-05.md`.

- **Read-only.** Every Fusion script runs with `readOnly: true` and works on TemporaryBRep copies; it starts with the
  guard in `v5f_audit_common.py` (printed-part volumes, 214 bodies, document unmodified, no `AUDIT_tmp_` bodies). Nothing
  was created, edited, saved or versioned. End state (a6b, 2026-11-06 00:38): guards unchanged, 214 bodies, version 23 =
  latest, unmodified, visible list = start, no `AUDIT_tmp_` bodies, the exploded-view document unmodified and active again
  as found.
- **Log:** `~/Documents/v5f_audit_log.json` (the design log `~/Documents/v5f_log.json` is not written).
- **Files on the Mac:** scripts are copied to `~/Documents/audit/scripts/` (by commit, `curl` from this branch); meshes
  `~/Documents/audit/mesh/` (10 printed parts, 0.01 mm tolerance, binary STL in world mm with x_rel),
  `~/Documents/audit/mesh_ref/REF_F_outer.stl`; data `~/Documents/audit/data/` (`holes.json`, `bbox_*.json`,
  `sweep_*.json`, `tools_*.json`, `thick_*`, `ovh_*`, `a2a_*`, `a2b_near_0.json`, `log_summary.json`).
- **How a run looks:** a one-line loader sets the parameters, then `exec(open(os.path.expanduser('~/Documents/audit/scripts/<script>')).read())`.
  Every loader used is in `RUNS.md` (73 distinct runs).
- **Frames:** world mm, x as x_rel = x − XC (XC −2.55), +x = viewer's left (`v5f_common.py`, `v5f_b5_common.py` helpers).

## Scripts
| Script | Block | Purpose | Result (report §) | Runs / runtime |
|---|---|---|---|---|
| `v5f_audit_common.py` | all | guard, end-state facts, world mesh + STL writer, `mindist` | – | – |
| `v5f_a0a_preflight.py` | 0 | switch to the design document, record version, bodies, guards, lumps, visible set, camera / style, helper sha256 | v23 = latest, 214 bodies, guards OK, 23 visible | 1 |
| `v5f_a1a_validity.py` | 1 | lumps / shells (void shells), micro faces and edges, sharp concave edges (time-boxed, edge ranges) | findings 1, 13, 18 | 11 (chunked) |
| `v5f_a1b_meshes.py` | 1 | MeshCalculator meshes → binary STL in world mm | 10 parts + REF_F_outer | 3 / 0.5–4.3 s |
| `v5f_a1c_holes.py` | 1 | every cylindrical face ≤ Ø9: Ø, hole / boss, axis, centre, length, area | `holes.json` (700 faces); findings 8, 12, 14, 27–31 | 1 / 1.8 s |
| `v5f_a1d_sections.py` | 1–5 | ASCII containment maps / lines (`SECS`) | sections for findings 9, 14, 19, 22, 24, 27, 32–34, 37–40 | 19 / 0–243 s |
| `v5f_a2a_matrix.py` | 2 | full interference matrix, B6w3 part filter + cap and lanes, chunked | 83 parts, 76 non-zero, 0 failures | 2 / 0.5–17.8 s |
| `v5f_a2b_nearmiss.py` | 2 | `measureMinimumDistance` for every box pair within 1.0 | 105 pairs < 1.0; finding 20 | 1 / 22.3 s |
| `v5f_a2c_bbox.py` | 2–5 | tight world boxes for name patterns | `bbox_all.json`, `bbox_every.json` (214) | 2 |
| `v5f_a3a_sweep.py` | 3–5 | insertion sweeps, ≤ 0.5 mm steps, fixed bodies cropped to the swept box; swings about world x; one lump of a body | 24 paths; findings 21, 24, 25 | 28 / 0.1–58.6 s |
| `v5f_a3b_tools.py` | 3 | tool lines: cylinder (shank + 0.5) from the head, bisected to the first obstruction, optional region crop | findings 21, 22, 27 | 8 / 1.0–62.1 s |
| `v5f_a5a_box_air.py` | 5 | speaker-chamber void test (gasket plate, wire-hole plug) and air bounds | sealed except the wire hole; +x 86.22–117.81, −x 89.16–121.05 cm³ | 2 / 0.6–0.8 s |
| `v5f_a5b_mass_tip.py` | 5 | B6n method with the cap, ASA / PETG (1.27 and 1.25) | 3.01 N (ASA) / 3.25 N (PETG) at the glass top edge | 1 / 36.0 s |
| `v5f_a6a_doc_checks.py` | 6 | lane axes (K5 and cap) from their cylinder faces; document facts | K5 25.00°; cap 24.64° / 27.56° | 1 / 0.1 s |
| `v5f_a6b_end_state.py` | 6 | end-state check; re-activates the exploded-view document | all checks pass | 1 |
| `v5f_a6c_log_summary.py` | 6 | run counts and runtimes from the audit log | `log_summary.json` | 1 |
| `offline/a_mesh.py` | 1 | in the Mac's VM on the STLs: validity, ray thickness (r-tree segment rays, area-weighted clusters), knife edges, overhangs | findings 2–7, 10, 11, 15–17 | – |
| `offline/a_g4_corners.py` | 1 | G.4 feature boxes for the concave-edge list | finding 13 | – |

## New lessons (Fusion API and method)
1. `BRepShell.volume` raises "InternalValidationError: ASMInterface::getEntityVolume" on tiny void shells; `isVoid` and
   `area` still work, so list shells per lump to find voids.
2. `pointContainment` on HOUSING_F_front costs ≈ 50 ms per point (4 360 points took 243 s and blocked Fusion). Keep a
   call ≤ 800 points; small bodies are much faster.
3. MeshCalculator meshes repeat nodes per face, but the edge tessellation matches, so an STL merged by position is closed;
   a non-watertight result points at real topology (here a tangent line contact).
4. Without embree, trimesh's ray tracer runs out of memory (4 GB VM) at ≈ 50 k triangles × 15 k rays. Cast finite
   segments against an r-tree of triangle boxes with a vectorised Möller–Trumbore test instead (2–17 s for 0.1–0.4 M rays).
5. Ray thickness on stepped faces (the c2h skirt) reads the tooth depth; confirm a thin reading with a section.
6. Sweeps: crop the fixed bodies to the swept box once. Near a seat a door-sized boolean costs 3.5–45 s per step, so run
   the last millimetres as separate short calls.
7. Tool access is a separate check from part insertion: tool lines found three blocked screw sets that every part sweep
   and the matrix had passed.
8. A later cut (B4i's USB slot) can sever an earlier feature (a screw bore) with no interference anywhere. Compare each
   hole's face area with its full cylinder (439 vs 902 mm²) to find partly removed bores.
9. `TemporaryBRepManager.copy(lump)` + `pointContainment` picks one lump of a boolean result. A chamber whose lump reaches
   the test box's faces is open; the same test with the known opening unplugged proves the method.
10. The MCP call times out at 60 s, but the script finishes; read its result from the audit log tail with the filesystem
    tools, and don't re-send it.
11. Lane and bore angles: read them from the cylinder faces' `geometry.axis` (exact), not from bounding boxes.
