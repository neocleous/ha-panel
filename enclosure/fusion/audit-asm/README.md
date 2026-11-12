# Assembly audit, second pass (2026-11-12) - probe library

Brief `claude/brief-assembly-audit-pass2-2026-11-12.md`; report `claude/report-assembly-audit-pass2-2026-11-12.md`;
draft instructions `claude/assembly-instructions-draft-2026-11-12.md` (claude.ai project). Model "HA Panel v5 - tapered"
version 55. **The audit changed nothing in the model and created no `AUD_*` body.**

## How it ran
- Every call through the Fusion connector with `readOnly: true` (enforced). No file on the Mac was read or written:
  the session had no folder access, so the first pass's `~/Documents/ha_asm_audit/` scripts were not used.
- `aud2_lib.py` is the library as it was built up during the session. It was exec'd into a module kept in
  `sys.modules['aud2']` (results and temporary bodies in its dict `c`), and each probe was a short `run()` that called it.
  The module was removed from `sys.modules` at the end.
- Big bodies (front shell, door, plate, slab frame) are probed through the eight slabs per body that the enclosure chat
  left in `sys.modules['v5f_h_cache']` (`('tile', name, volume, i)`), after checking their volumes against the live bodies.
  Without that cache `parts()` raises: cut the slabs first (lesson 133 of `../revF/floor_plate/close/README.md`).

## Method
- Tool access: `line()` samples the tool's axis every 5 mm from 2 mm behind the working end; margin = point-to-body
  distance (`measureMinimumDistance(point, body)`, 0 inside a body) less the tool's radius at that station. 'head' = the
  first 7 mm, 'beyond' = the rest. States (bodies present at a step) are the `ST` lists.
- Reach: `reach()` = the rounded fingertip of 2026-11-11 (cylinder + ball, tip on the mated plug's top, 60 long), blocked
  above 1.0 mm3, neighbours' mated plugs as blocks (`PLUGB`), supply module at 28.5.
- Paths of parts: temporary copies moved (`mcopy`, `xmoved`) and intersected with crops of the fixed bodies (`region`).
- Sections: `needle()` = a 0.04 x 0.04 bar intersected with a body; returns the solid stretches along it.

## Probes run (parameters in the report's tables)
| What | Function | Note |
|---|---|---|
| hole list of the printed parts | `holes_of` | radii 0.7-7.0, holes and pins, per axis |
| every screw, insert, pin at its step | `probe`, `line` | tools IRON, KEY20, KEY25, MICRO, DRILL |
| radar ribs, tilt scan | `line` with `tilt` | down 5-25, sideways 0-30 |
| cap side screws | `capscan` | 20-25 deg off the axis, 0-30 deg toward the middle, 2.0 and 2.5 key |
| BME680 hood's way in | `mcopy` + `clash` on a grid | lift 3.5, inboard 0-60, back 0-66 |
| USB-A plug in the left box's pocket | `needle`, `mcopy` | travel in +x 0.55 |
| reach, build order and all in | `reach` | `ORDER`, `ALLP` |
| cloth hem against the plate | `needle` at z 2.9 (shell) and z 2.4 (plate) | plate 0, 1.05, 1.3, 1.5 behind |
| LCD opening | `needle_d` | board frame |
| cap's way up | `capbar` | bar 154 x 19.2 x 8 / 10 / 12 |
| lead ends and straight distances | vertices of the `LEAD_*` bodies | unit moved 30 / 95 down |
| tilted line for the shell holes | `line` | 0-14 deg, iron and 2.0 key |

## Lessons 140-145
In the report, section 12.
