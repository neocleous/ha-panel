# Print audit re-check (2026-11-14) — HA Panel v5 rev F, version 63

Scripts of the independent print audit re-check. Report: Project doc `claude/report-print-audit-recheck-2026-11-14.md`;
hand-over: `claude/handover-print-audit-recheck-2026-11-14.md`. The first audit's scripts in `../fusion`, `../offline`, `../slicer`
were reused (read from `docs` at 2170c7a). Everything here is READ-ONLY on the design: every Fusion call ran with `readOnly: true`
and saved no version.

## Frames
World mm as `v5f_common` / `pa_common`: x = x_rel (centred, +x = the viewer's left), y + toward the viewer, z up from the base
plate's underside; design cm. Exports are binary STL in world mm (mesh calculator, 0.01 mm chordal, 10° normal deviation).

## fusion/ — calls through the Fusion connector
Each call is `rc_common.py` + one `rcN_*.py`, joined by `build.py` into `calls/<name>.call.py` and sent as the script text.
- `rc_common.py` — document/version/guard check (`rc_guard`: version 63 of 63, unmodified, the 8 guard volumes within 0.01 mm³,
  one lump each), world transforms, mesh export, logging. All module-level names start `RC_` / `rc_`.
- `rc0_preflight.py` — version, counts (392 / 95 unit / 36 visible), guard, scope-B volumes, camera, slicers on the Mac.
- `rc0b_slicer_probe.py`, `rc3_slicer_setup.py`, `rc4_bs_probe.py` — find Bambu Studio, copy its system presets, CLI help.
- `rc1_export.py` — the 13 printed parts as STL; `rc2_holes.py` — every cylinder (r ≤ 6) and cone of the 13 parts (1,175 rows).
- `rc5_bs_run.py`, `rc6_bs_batch.py` — Bambu Studio headless from Fusion's Python (`subprocess.Popen`, own session), a queue of
  at most 3 jobs; `rc6` reaps finished children with `waitpid(WNOHANG)` (they stay zombies otherwise and look alive).
- `rc7_comp_export.py` — body list with visibility and volume; one component mesh. Slow: reading 392 volumes takes > 5 min.
- `rc8_leads_export.py` — the four ride-in lead bodies and the main board; `rc9_final_guard.py` — the closing check.

## slicer/ — Bambu Studio jobs (built in the cloud, run on the Mac)
- `flatten.py` — resolves Bambu's system presets (inherits chain + `include` templates; own keys win) into flat JSON.
- `orient.py` — world STL → build orientation (first audit's `pa_geom.ORIENT`), with the world→bed matrix.
- `blockers.py` — support-blocker boxes given in world mm, written in a print's bed frame; `front_plan_blk.cmd` — the front
  shell's boxes as run.
- `mkjob.py <spec.json>` — assemble list + argument list for one job (every option as `--key=value`). Set `RC_MAC_DIR` to the Mac
  folder; `{RC}` in a spec stands for it. `mkbatch.py start|poll jobs…` — the Fusion call text for `rc6`.
- `spec_*.json` — every job of this run (A_* = scope A singles, P* = plan plates, T_ring12 = the foot ring).

## offline/ — analysis in the cloud
- `gparse.py` — G-code → extrusion segments (npz); `gsupport.py` — support contacts in world coordinates; `gsup_proj.py`,
  `gview*.py` — pictures; `unsup.py` — overhang regions left without support.
- `win_check.py`, `win_lips.py`, `win_frame.py`, `win_bands.py` — the plate unit's window: the shell lowered at a forward offset
  s against the driver screw heads, the plate and the boxes; `win_bands.py` gives the limit each height band sets.
- `ride010.py` — the ride-in's 0.08 (lead parts as `aud4_lib.LEADPART` crops them, moved along the screen's normal).
- `insert_walls.py` — wall round each insert hole by rays from the hole's surface; `holes_summ*.py` — hole schedule by print axis.
- `pa_geom.py` — the first audit's, with this run's upload path and orientations (carrier, plate).
- `xsec.py`, `boss_probe.py`, `boss_sec.py` — sections and rays round the box-top bosses; `rc_query.py` — the layer analysis's
  regions inside a world box; `rc_render.py` — quick shaded views; `rc_load_check.py` — the mesh check of the 13 exports.

## Results
The results quoted in the report (`data/`, `img/`) and every export stay on the Mac in
`~/Documents/HA_panel_renders/print_audit_recheck/`, as in the first audit; none of them is a print file and none is in git.

## Lessons
- A Bambu Studio child of Fusion's process is a zombie until reaped: `os.waitpid(pid, os.WNOHANG)` before `os.kill(pid, 0)`.
- Bambu Studio CLI: pass every option as `--key=value` (a boolean takes the next token as its value otherwise).
- The two-material slab (ABS + Support for ABS, X2D) stops without a result in CLI mode (tree and normal supports): slice it in
  the window.
- `device_commit_files` refuses files of about 40 MB and more: slice big parts from the world export with a position in the
  assemble list.
- `brim_type = brim_ears` gives the front shell no ears at all; the painted brim is a window-only step.
