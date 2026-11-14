# rev F - main board rev 3.2 placed (2026-11-14)

Brief `claude/brief-enclosure-rev3-2-placed-2026-11-14.md`; governing input `claude/main-board-rev3-2-reply-2026-11-14.md`. Closing report
`claude/report-enclosure-rev3-2-placed-2026-11-14.md`; update for the Architect `claude/brief-architect-update-2026-11-14-rev3-2-placed.md`
(both in the claude.ai project). Lengths mm, volumes mm3. Board frame (u, v, w) of the site document.

## Model "HA Panel v5 - tapered"
| Version | Name | What |
|---|---|---|
| 62 | rev F WIP 2026-11-13 g17 | ribbon pass, block 2 (start of this pass; closed without saving and reopened, unmodified) |
| 63 | rev F WIP 2026-11-14 g18 | main board rev 3.2 placed: only the board's solid replaced; rev 3.1's board hidden as `MAIN_pcb_v62` |

Archive `~/Documents/HA Panel v5 - tapered revF-g18.f3d` (173 086 500 bytes). 392 bodies, 95 in the unit, 36 visible. No printed part changed:
the front shell, both boxes, the carrier, the base plate, the cradle, the door and the cap have version 62's volumes.

## Script
`v5f_n_rev32_calls.py`: the connector calls as run, in order, with their results as comments. It loads the fix pass's library
(`../fusion/v5f_k_lib.py`), the ribbon pass's strip library (`../fusion/v5f_m_lib.py`), the unit checks (`v5f_k4a`, `v5f_k4b`, `v5f_m3b`) from
`fafa8fd` and the assembly audit's `enclosure/fusion/audit-asm/followup/aud4_lib.py` from `2c8c9a0` (jaws, pliers' envelope, service obstacles,
ride-in), each by its git blob hash. The STEP file is `hardware/main-board/main-board-rev3.2.step` at `07aa692` (blob `d2663e8`).

## Results in short
- **The relief in the model is at the reply's corner points:** floor u +42.000 over v +1.5 to +13.0, arcs r 1.000 on (+43.0, +1.5) and
  (+43.0, +13.0), side walls at v +0.5 and +14.0. 29.929 mm3 cut, nothing added. The STEP's 139 part solids equal the model's part bodies
  (0.0000 mm3 both ways), so only the board's solid was replaced.
- **USB-C sleeve to the board:** 1.70 (sleeve 0.92 off the socket's face), 0.78 on the socket's face (rev 3.1: 0.20 and 8.05 mm3 inside);
  with the relief 0.2 smaller all round 1.50 and 0.58.
- **Pliers' line of D135** (the audit's jaws, 30 to 35 deg below, handle 10 to 15 deg toward the middle, tips at the board's face): the board
  is 0.19 to 0.31 away, 0.07 to 0.14 with the jaws 0.5 nearer; nearest is the board's square corner at the relief's lower end (u +43.5,
  v +0.5), the floor is 1.63 or more away. R105's body 1.98 or more. With the outline 0.2 larger all round the jaws touch that corner if
  their tips go down to the board's face (0.0047 mm3 at most, 0.5 nearer); 0.25 above the face they clear by 0.05 or more.
- **Flat leads:** ribbon 2.90 (its nearest point is at v -16, below the relief), USB cable 11.87.
- **Ride-in** at 23 positions out to 60: 0 mm3; the board passes the LCD opening with 1.03.
- **Outline 0.2 larger all round:** ride-in 0.83, key paths 0.25 (right-speaker side) and 0.35 (left), sleeve 1.50, ribbon 2.70; nothing
  overlaps. Regular routing (+-0.2) is enough.
- **Interference:** 76 pairs not zero, the same 76 as version 62 (none new, gone or changed).

## Lessons (numbered on from the audit follow-up's 174)
- **175** Reproduce a borrowed check's published number before using it on a changed model. The audit's jaws gave its 0.25 mm3 only with the
  tips at the board's face and the direction built as elevation and azimuth; the template's own default (tips 1.0 up) gives 0.
- **176** A routing tolerance moves every edge of a cut, not only its floor. Model "+0.2" as the cut 0.2 smaller all round (floor 0.2 out,
  arcs 0.2 smaller on the same centres, side walls 0.2 inward) and the outer edges 0.2 out. Build it as the old board minus the shrunk cut,
  and check the construction by rebuilding the nominal board the same way (0.0000 mm3 both ways).
- **177** When a relief removes the nearest feature, look at the relief's own ends next. Here the square corner where the side wall meets
  the old edge took over from the floor and came 1.4 nearer the jaws than the floor.
- **178** Check a changed STEP part by part before importing it whole: group its solids as before and take both differences against the
  model's bodies. 0.0000 both ways justifies replacing only the solid that changed.
- **179** Run the interference matrix on the unchanged version before the change: a measured reference beats a list rebuilt from reports.
  With a new tag the first call rebuilds the big bodies' slabs (73 s): budget two calls.
- **180** Closing and reopening a document keeps Python's modules. Copies cached by name and volume stay valid when the same version is
  reopened, but load the libraries fresh under the pass's own names so that caches keyed by name alone start empty.
