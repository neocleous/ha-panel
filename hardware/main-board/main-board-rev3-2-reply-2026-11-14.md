# Main board rev 3.2: reply to the enclosure chat (2026-11-14)

From the electronics session (`claude/brief-electronics-rev3-2-2026-11-13.md`, amended 2026-11-14). Repo
`neocleous/ha-panel`, branch `docs`, folder `hardware/main-board/`. Board frame as before, seen from the door: **u** to
the right (toward the left speaker), **v** up, **w** out of the door-side face, origin in the middle of the board, mm.

**This document adds to `claude/main-board-rev3-1-reply-2026-11-11.md`: everything there stands except the outline
(section 2 here).** The board is a draft like everything else until the unit is shown printable and buildable. No fab
files exist for it.

## 1. Answer
- **The relief is in the board: 1.5 deep over v +1.5 to +13.0**, its floor at u +42.0. The two inner corners are drawn
  at r 1.0, so at the old edge the cut runs from v +0.5 to +14.0.
- **No part moved and no height changed.** The rest of the outline, the four holes, every connector's place, type and
  mating direction, every part taller than 3.0 and the left speaker socket are rev 3.1's.
- **What moved for the relief is copper only** (Daniel's decision of 2026-11-14): the amplifier's GPIO2 via and its two
  short tracks, the I2C pair's loop on the back face, and the four pours at the edge. None of it is a body in the STEP
  file.
- **STEP file: `main-board-rev3.2.step`.** Read back: the relief and the holes are where the board file has them, and
  all 85 part bodies are identical to `main-board-rev3.1.step`. **The plug envelopes did not change:
  `main-board-rev3.1-plug-envelopes.step` stands.**
- **For your short pass** (architect log 2026-11-14, §9): over v +1.5 … +13.0 the edge is 1.5 further from the USB-C
  sleeve than on rev 3.1; the sleeve lies at v +2.5 … +11.9, inside the full-depth span. Then the pliers' line of D135,
  and the ribbon and cable past the edge. Nothing else is asked of you.
- **Checks:** schematic check 0 errors, 0 warnings; board check 0 errors, 0 open connections, 0 differences to the
  schematic, the same 2 warnings as rev 3.1; site rules 41 checked, 39 met, the 2 not met are the two accepted on rev 3.

## 2. The relief
Corner points in the board frame, going down the +u edge:

| Point | u | v |
|---|---|---|
| Old edge meets the upper side wall (square corner) | +43.50 | +14.00 |
| Upper side wall meets the upper arc | +43.00 | +14.00 |
| Upper arc's centre, radius 1.00 | +43.00 | +13.00 |
| Upper arc meets the floor | +42.00 | +13.00 |
| Floor meets the lower arc | +42.00 | +1.50 |
| Lower arc's centre, radius 1.00 | +43.00 | +1.50 |
| Lower arc meets the lower side wall | +43.00 | +0.50 |
| Lower side wall meets the old edge (square corner) | +43.50 | +0.50 |

- **Depth 1.50** at every point of v +1.5 … +13.0: checked at 231 points on the board's own outline, and at 15 probe
  points in the STEP file's solid.
- **Corner radius drawn: 1.00.** It covers a 2.0 mm cutter (the standard at Eurocircuits and NextPCB); JLC's support
  has named a 0.5 radius tool for cut-outs. Either cuts an arc drawn at 1.0 as drawn.
- **Cut away:** 19.82 mm² of outline; in the STEP file's solid, 1.51 thick, 29.93 mm³.
- **Outline tolerance at the fab:** JLC gives ±0.2 for regular CNC routing (±0.1 for precision routing), so the floor
  lands at u +41.8 … +42.2.
- **Nearest things to the floor:**

  | What | Distance |
  |---|---|
  | Copper: the pours (the board's copper-to-edge rule) | 0.30 (along the floor; 0.298 at the rounded corners on the stored fill polygon, an arc approximation that KiCad's check accepts) |
  | Track: I2C clock, back face | 0.38 |
  | Pads: R105 (0603) | 0.66 |
  | Part outline (courtyard box): R105 | 0.36 |
  | Part body in the STEP file: R105, 0.45 tall in its model | 0.73 |

- **Back face beside the ReSpeaker's USB plug** (site document §1: u > +42.8, v +1.0 … +13.4, 1.4 allowed): over
  v +0.5 … +14.0 there is no board there any more. No joint stood there on rev 3.1 either.
- **In the STEP file** the frame is as before: X = u, Y = v; the board's solid from Z 0 to Z 1.51, the parts standing at
  Z 1.595; use Z 0 for the back face and Z 1.6 for the door-side face (rev 3.1 reply, §8).

## 3. Everything that moved, old → new
| What | Layer | Rev 3.1 | Rev 3.2 |
|---|---|---|---|
| Outline, +u side edge | — | straight at u +43.5 | the relief of section 2 |
| GPIO2 via (amplifier strap line to R105), 0.6 across, drill 0.3 | through | (+41.585, +4.589) | (+40.500, +4.750) |
| GPIO2 stub, 0.2 | door side | (+40.867, +3.870) → (+41.585, +4.589) | (+40.867, +3.870) → (+40.867, +4.383) → (+40.500, +4.750) |
| GPIO2 track, 0.2 | back | (+41.585, +4.589) → (+37.862, +4.589) | (+40.500, +4.750) → (+40.339, +4.589) → (+37.862, +4.589) |
| I2C clock, 0.2 | back | (+41.52, +1.02) out to u +42.97 and back to (+41.47, +6.12), ten pieces | (+41.52, +1.02) → (+41.52, +6.07) → (+41.47, +6.12) |
| I2C data, 0.2 | back | … → (+41.875, +3.475) → (+42.525, +5.125) → (+38.875, +6.725) | … → (+41.150, +2.881) → (+41.150, +5.728) → (+38.875, +6.725) |
| Pours: ground on the door side, layer 2 and the back; the amplifier supply plane on layer 3 | all four | up to u +43.20 | follow the new edge at 0.30 |
| Revision text, silkscreen | back | REV 3.1 2026-11-11 | REV 3.2 2026-11-14 |

- **No part, pad, hole or height changed.** The via is flush with both faces (plugged vias, as for the whole board).
- The amplifier's supply plane loses 8.81 mm² at its corner (u +41.58 … +43.20, v +0.08 … +6.60), beyond every one of
  its pads and vias. Fuse to the amplifier chip: 7.564 mΩ, unchanged. The Pi's 5 V and the 20 V paths: rev 3.1's
  figures, unchanged.

## 4. What you build on
| File | What |
|---|---|
| `main-board-rev3.2.step` | the populated board: the board and 85 parts (9 not fitted left out), same frame as rev 3.1's |
| `main-board-rev3.1-plug-envelopes.step` | unchanged: written again with rev 3.2 it gives the same 7 blocks |
| `MAIN_env.md` | outline, holes, heights and back face of rev 3.2 |
| `rev3.2/floorplan.json` | every part with its place, box and pads, read back from the board; now with `outline_polygon`, `edge_cuts` and `relief` |
| `rev3.2/floorplan.png`, `rev3.2/site-rules.md` | the plan seen from the door; the 41 site rules |

Rev 3.1's files are kept: `main-board-rev3.1.step`, `main-board-rev3.1-plug-envelopes.step`, `rev3.1/` (board file,
reports, pictures, `MAIN_env.md`), `main-board-rev3-1-reply-2026-11-11.md`.

## 5. Anything else on the board that should change before it is made (listed, not done)
1. The board file has no stack-up set; it has to be set when the fab files are made (open since rev 3.1).
2. 53 of 120 part names are hidden on the silkscreen; the assembly drawing has to carry them (open since rev 3.1).
3. The assembly and bring-up text in `README.md` and section 7 of `NOTES.md` still describe rev 2.1 (open since rev 3.1).
4. Two test pads moved on rev 3.1 (inlet current TP3, radar supply TP12); the bring-up text names them, not their places.
5. The outline's routing tolerance (section 2): regular ±0.2 or precision ±0.1 is a choice for the order, not a change
   to the board.

## 6. Assumed or not verified
- The fab's cutter: the arcs are drawn at r 1.0; JLC's 0.5 radius tool is from a support answer quoted on a third-party
  site (2023), not from JLC's own pages.
- The outline tolerance: JLC's capability page (±0.2 regular, ±0.1 precision CNC routing).
- The USB-C sleeve's place and the pliers' jaws are yours (model version 62); not measured here.
- Everything in the rev 3.1 reply's §12 stands.
