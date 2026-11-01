# HA Panel enclosure rev E – Fusion build scripts (2026-11-01)

Fusion 360 document: **HA Panel v5 - tapered** (cloud project *HA Touch Panel*, direct-modelling / no timeline).
Scripts are run through the Fusion MCP (`fusion_mcp_execute`, `featureType=script`); each script defines `run(context)` and logs to `~/Documents/v5d_log.json`.
MCP call timeout is 60 s – keep scripts to a handful of features each.

Authoritative spec: project doc `claude/enclosure-v5-revE-handover-2026-11-01.md` (claude.ai project *HA Touch Panel*).

| file | what it does | state after run |
|---|---|---|
| `v5e_p17_fillets_inner_shell.py` | places slab (home pose, then −27.43 mm along design Z), lofts outer body `BODY_E`, chin/slot cuts, R12 corners, floor R6 / top-rear R10 / top-front R3, `INNER_E` loft (wall 2.5), inner cuts, `REF_E_outer` copy, `HOUSING_E = BODY_E − INNER_E` | HOUSING_E 200.1 cm³, INNER_E 1787.7, REF_E_outer 1972.9 |
| `v5e_p18_door_boss_opening_pads.py` | `DOOR_plate` (offset 2.8, t 2.5), slab boss d 9→12.8 on the slot wall, LCD opening −60..53 × ZS±30 (d 8–16), pin notch, 4×Ø2.7 holes at (±47.5, ZS±34), 3 pads 60×8 (d 9.2→6.4), interference check | HOUSING_E 246.5 cm³ |
| `v5e_p19_fpcnotch_save.py` | notch boss front face for `LCD_panelFPC_conn_d9.5` (bbox +1 mm, d 8→10), interference check, f3d export, save | HOUSING_E 246.4 cm³, all interferences 0 |
| `revE_geom.py` | analytic rev E *interior* clearance model (world frame, mm): `clearance(x,y,z)`, `box_clear(...)`, `half_width_interior(y,z)` – used for the electronics fit study | – |
| `boxcalc.py` | sealed / vented (Thiele–Small) F3, Qtc, ripple – used for the DMA45-4 chamber study | – |

## Frames
* **Design frame** = Fusion native: origin at the original glass-front centre, Z along the display (up the 12° ramp), +Y toward the viewer, d = −Y (depth behind the glass).
* **World frame** (floor horizontal): `y_w = Y·C − Z·S`, `z_w = H + Y·S + Z·C` with H = 143.3, C = cos 12°, S = sin 12°, T = tan 12°.
* Helpers: `Dw(x,y,z)` world→design point (cm), `yfront(d,z) = −d/C − (z−H)·T`, `wz(p)`, `wy(p)`; XC = −2.55 (body centre x).
* Move along the ramp = pure design-Z translation; vertical world move = `V3(0, dz·S, dz·C)/10`.

## Lessons (direct modelling + API)
1. `copyPasteBodies` is not supported in direct modelling → `TemporaryBRepManager.copy()` + `comp.bRepBodies.add()`.
2. An extrude **JOIN** with `participantBodies=[hb]` still merged an overlapping body (SLAB_frame) into HOUSING_E. Build a NEW body, run `analyzeInterference`, then `combineFeatures` JOIN. Recovery of the slab was done by `importManager.importToNewDocument(revD.f3d)` + TemporaryBRep copy + move.
3. `executeTextCommand('Commands.Start UndoCommand')` had no effect – there is no scripted undo; keep `REF_E_outer` / `INNER_E` so the shell can be rebuilt from them.
4. Sketch on an offset plane: use `sk.modelToSketchSpace(P3(...))` and determine extrude direction sign with `sk.xDirection × sk.yDirection · target`.
