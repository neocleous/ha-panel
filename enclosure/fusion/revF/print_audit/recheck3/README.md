# Print audit re-check of version 67 (2026-11-18 / 19) — HA Panel v5 rev F, version 67 (g22)

Scripts of the print re-check of version 67. Brief: Project doc `claude/brief-print-audit-recheck-v67-2026-11-18.md`.
Report: `claude/report-print-audit-recheck-v67-2026-11-19.md`; hand-over: `claude/handover-print-audit-recheck-v67-2026-11-19.md`.
Everything here is READ-ONLY on the design: every Fusion call ran with `readOnly: true` and saved no version. Nothing here is a
print file; nothing was ordered. Findings PR25 to PR36. Runs: `RUNS.md`.

## Frames
World mm: x centred (+x = the viewer's left), y + toward the viewer, z up from the base plate's underside. Model mm → world:
x_w = x_m + 2.55; y_w = cos12°·y_m − sin12°·z_m; z_w = sin12°·y_m + cos12°·z_m + 143.3. Slab frame (d behind the glass, up along
the screen): y = −d·cos12° − up·sin12°; z = 143.3 − d·sin12° + up·cos12°. Bed frames are the print files' matrices
(`print_files/_work/data/pf_2_orient.json` on the Mac) plus each job's offset: shell bed z = 6.799167 − y_w (chin down);
boxes bed z = y_w + 52 (rear face down); door bed z = z_w − 2.8 (standing); cap bed z = 180 − z_w; screen plate back down.

## What is here
- `fusion/r3_9_final_guard.py` — the closing read (document, version, counts, the 14 guard volumes, camera). The preflight read
  the same items. `fusion/r3_bs_lib.py` (sha256 336a261a…, checked by every call) + `r3_bs.py` + `mkbs.py` — Bambu Studio
  02.09.01.70 headless from Fusion's Python (D139): a queue of three jobs started with `subprocess.Popen` and polled by separate
  calls; no `time.sleep()`.
- **Not here: four Fusion calls that were sent inline and whose text was not kept** — the preflight, the mesh export, the
  print-file-grade export (two calls) and the 8 mm cut. `RUNS.md` names the repo script each was built on and its result; their
  outputs are on the Mac (`data/`, `mesh/`, `orient_hr/`). A later run should save each call as a file before sending it.
- `scan/` — the design-for-FDM scan on version 67. The method's scripts are `fdm_audit/scripts/` unchanged (a1 layers, a2
  in-layer bands, a4 ray thickness, a5 gaps); here only `fdm_lib.py` (the guard volumes of version 67) and the new ones:
  `r3_cmp_gaps.py`, `r3_cmp_ray.py`, `r3_cmp_plane.py` (version 67 against version 66), `r3_feat.py` (named features),
  `r3_sec.py` (sections).
- `slicer/` — `r3_orient.py` (meshes → bed STL with the print files' matrices), `r3_specs.py` + `mkjob.py` (the jobs; run with
  `PF_ORIENT_SUB=orient_hr R3_PREFIX=H` for the print-file-grade meshes), `variants.json` (the seven jobs derived by hand),
  `r3_blockers.py` (the shell's blockers v3 = the settled 14 boxes + one cylinder r 2.35 along each post insert hole, and the
  adhesion test's set), `r3_plate_blockers.py` (two boxes over the screen plate's peg pocket and slot).
- `calib/r3_mkcal.py` — the calibration block with a lug carrying a sideways Ø2.7 × 5.5 pilot (axis 3.35 above the bed, the
  same place in the layers as the boxes' pilot).
- `offline/` — the G-code read back against the model: `r3_gparse.py` (segments with feature, tool, object), `r3_gq.py`
  (library: part layers, printed footprint as the union of lines, sections and cuts), `r3_cover.py` (prints as modelled),
  `r3_midair.py`, `r3_overhang.py`, `r3_under.py` (what lies under a face), `r3_posts*.py`, `r3_bosses.py`, `r3_lip.py`
  (sections as sliced for the stresses), `r3_fits.py` (point 12), `r3_final.py` (the final slices: holes free of support, the
  plate's support by place), `r3_tip.py` (masses and tipping on the D9 base, with recheck2's `r2_tip.py`), `r3_plan.py` (plan
  totals and the two-material estimate), `r3_view.py` (pictures).
- `data/` — results: `export_v67.json` (volumes and centres of mass), `cover_*.json`, `midair_*.json`, `overhang_*.json`,
  `tip_v67.json`, `plan_v67.json`, the scan's logs.

## On the Mac
`~/Documents/HA_panel_renders/print_audit_recheck3/`: `mesh/` (14 bodies at 0.005), `orient/` and `orient_hr/` (bed STL,
blockers, calibration meshes), `slicer/` (flat presets, jobs, `out/<job>/` with G-code, 3MF, `result.json`, `seg.npz`,
`gsum.json`), `lib/`, `offline/`, `data/`. Audit slices, not print files.

## Lessons of this run
1. **Mesh fineness changes the slice.** The 0.005 audit meshes made P1 30 min longer (gap infill and travel) than the same
   bodies at the print files' 0.01 mm and 10°. Plan figures come from print-file-grade meshes.
2. **Tree supports add layers of their own** at other heights: index the part's layers separately (`G.PL`).
3. **The classic wall generator with thin-wall detection off drops short features under two lines** (the door's seat skins,
   the cap's 0.60 end walls). `detect_thin_wall` cures both; per object it goes into the assemble list's `print_params`.
4. **Auto tree support fills a blind hole that faces the bed** (the four post insert holes): block it with a cylinder.
5. **Normal (auto) support leaves the screen plate's raised border as a bridge** (10–17 % covered); trees with a dense
   interface cover it.
6. **Length × width overstates a section where lines overlap.** Sections as sliced use the union of the lines.
7. **A void in the printed footprint is only infill if it lies wholly inside the model's material**; otherwise it is a missing
   feature (`r3_cover.py`).
8. **Save every inline connector script as a file when it is sent.** Four of this run's were not, and the conversation's
   earlier turns could not be read back.
9. The cloud git proxy pushes only to a repository attached to the session with push access.
