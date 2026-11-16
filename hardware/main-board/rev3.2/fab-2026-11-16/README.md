# Main board rev 3.2 — fab issue 2026-11-16: what changed with the fab files, and the checks

Electronics session, brief `claude/brief-electronics-fab-files-rev3-2-2026-11-16.md`. Positions in the site's board
frame, seen from the door: **u** to the right (toward the left speaker), **v** up, mm.

## 1. Answer
- **`../../main-board.kicad_pcb` is rev 3.2 as it goes to the fab.** It was made from rev 3.2 of 2026-11-14
  (`../main-board-rev3.2-2026-11-14.kicad_pcb`, commit `08954e4`) by `gen/fab32.sh`.
- **No part, pad, hole, height or outline changed.** The enclosure's files stand: `main-board-rev3.2.step`,
  `main-board-rev3.1-plug-envelopes.step`, `MAIN_env.md`.
- **Changed: copper, one text and the stack-up.**
  1. 39 vias moved out of pasted pads, 1 taken out (section 2).
  2. The pours kept 0.50 back from the relief on all four layers (section 3).
  3. The stack-up JLC04161H-7628 set in the board file (section 4).
  4. The back-face text `REV 3.2 2026-11-14` → `REV 3.2 2026-11-16`; title block date and a third comment line.
- **Checks:** schematic check 0 errors, 0 warnings; board check 0 errors, 0 open connections, 0 differences to the
  schematic, the same 2 warnings as before (section 5).

## 2. Vias out of the pasted pads
**Found:** rev 3's router set vias on the ends of pads. On rev 3.2 of 2026-11-14, 47 of the 245 vias had their hole in
or within 0.10 of a pad's bare area: 39 at pads that get solder paste, 7 in test pads, 1 in the amplifier's thermal
pad. One more hole stood 0.14 from a pasted pad. KiCad's board check does not report a via in a pad of its own net.
Rev 2.1 had 4 such vias, rev 3 had 50, rev 3.1 and 3.2 had 47 (`plug-check-result.txt`, `gen/fab32_vias.py check`).

**Why it matters:** JLC plugs a via with ink only if it has no mask opening on either side, is 0.35 or more from other
mask openings and is "no wider than 0.5 mm diameter" (capabilities page, "Plugged vias", read 2026-11-16; JLC's
via-covering article of 2026-11-10 puts the 0.5 on the hole, the table does not say hole or copper). A hole in a pad stays
open, and on the hotplate the pad's paste can run down it. The boards are soldered on a hotplate, and Daniel does not
solder surface-mount parts by iron.

**Done:** every via with less than 0.20 of mask between its hole and a pasted pad was changed: 40 vias.
- **39 moved,** each to the nearest place that leaves 0.20 or more of mask (0.25 where that costs nothing), keeps every
  clearance of the board with 0.02 to spare, stays in the pours of its own net and does not cut into the 20 V inlet
  pour or the Pi's 5 V pour.
- Each is joined to its pad by a short door-side track as wide as the via or the pad allows (0.40 to 0.80 wide, 0.40 to
  1.35 long). The router's old stub from the pad to the via was taken out. A back-face track that ended on the via was
  carried to its new place.
- **5 of them were also made 0.2/0.45** (from 0.3/0.6), because the larger via found no place nearby: at F4.1 (+3V3),
  R3.2, C3.2, R8.2 and C10.2 (ground). JLC charges nothing extra for that size.
- **1 taken out:** the via in pin 14 of U1 (current monitor). A second via of the same net stands 0.53 away on the
  same track; the back-face track was carried to it.
- **35 of the 39 moved 0.65 or less.** The other four: 1.65 and 1.20 (two of the three output vias of U1, which sat
  among its pins and now stand above the pin row), 1.53 (R4's ground via, now on the pad's other side) and 1.29 (C2's
  ground via, kept out of the 20 V inlet pour).
- **Left as they are:** the vias in seven test pads (TP2, TP7, TP9, TP15, TP17, TP19, TP20) and the one ground via in
  the amplifier's thermal pad. No paste goes there.

Every move, old → new: [`via-moves.md`](via-moves.md). Before and after, drawn: `via-moves.png`. The plan the script
applied: `via-plan.json`; its log: `via-plan-run.txt`.

**After:** 244 vias (132 of 0.3/0.6, 87 of 0.2/0.45, 25 of 0.4/0.8). The smallest mask width between a hole and a
pasted pad is 0.20 (`via-check.txt`). Against JLC's plug conditions: the widest hole is 0.40 (if the 0.5 means the via's copper, only the 87 vias of 0.45
pass it); 61 of the 244 vias have their hole within 0.35 of a mask opening and so will not be plugged with ink. They keep their mask cover in the files
(`plug-check-result.txt`).

## 3. Copper at the relief
| | Rev 3.2 of 2026-11-14 | Fab issue 2026-11-16 |
|---|---|---|
| Pours to the relief's edge (ground on the door side, layer 2 and the back; the amplifier's supply on layer 3) | 0.30 | **0.50** |
| The same with JLC's cut 0.2 deeper (floor at u +41.8) | 0.10 | **0.30** |
| Pours to every other edge | 0.30 | 0.30 |
| Nearest track: I²C clock, back face | 0.38 | 0.38 (0.18 with the cut 0.2 deeper) |
| Nearest pads: R105 | 0.66 | 0.66 |

- **JLC's rule, read 2026-11-16:** copper 0.2 or more from a routed edge, as drawn; regular routing ± 0.2. The board
  met it before (0.30) and meets it now.
- **Why the pours were pulled back all the same** (architect log 2026-11-15 evening, D151 item 6): the relief is where
  the pliers and the USB-C plug's metal sleeve work, and the amplifier's 20 V supply plane on layer 3 runs along it.
  With the cut at its deep limit only 0.10 of board would have been left over that plane.
- **How:** one rule area, "relief: pours 0.50 from the edge", on the four copper layers. It keeps poured copper out and
  nothing else: no track, via or pad was touched.
- **The I²C clock track stays** at 0.38. It is a 3.3 V signal under solder mask. Moving it means moving the data line
  and the amplifier's strap via beside it again.
- Figures: `relief-edge-result.txt` (before: `relief-edge-2026-11-14-result.txt`); picture: `relief-copper.png`.

## 4. Stack-up
JLC04161H-7628, read on jlcpcb.com/impedance on 2026-11-16: copper 0.035 / 0.0152 / 0.0152 / 0.035; prepreg 7628
0.2104 (εr 4.4) between the outer and inner layers; core 1.065 (εr 4.6). It is the stack the supply-copper figures
have assumed since rev 3.1 (architect log 2026-11-11, B5), so nothing in them changes for it. It is now in the board
file (`(setup (stackup …))`) and in the Gerber job file.

## 5. Checks, with the numbers
| Check | Result | Where |
|---|---|---|
| Schematic check | 0 errors, 0 warnings | `../../erc-report.txt` |
| Board check with schematic comparison | 0 errors, 0 open connections, 0 differences; 2 warnings, the same as rev 3.2 (J6 and J2 footprints differ from the library copies) | `../../drc-report.txt` |
| Parts against rev 3.2 of 2026-11-14 | 120 and 120; moved: none. Outline: 5017.48 mm² before and after | `compare-2026-11-14-result.txt` |
| Vias and pasted pads | 0 vias with less than 0.20 of mask; smallest 0.20 | `via-check.txt` |
| Moved vias and the pours of their own net | 46 kept; 2 no longer at the via's centre: R10's via in the Pi's 5 V pour on the back (joined to it by a 0.6 track from its old place) and C3's via in the door-side ground pour (still in ground on layer 2 and the back) | `via-planes-result.txt` |
| Supply copper (rev 3.1's method) | see below | `supply-copper-result.txt` |
| Repeatable | a second run of the planner gives the same plan, byte for byte | `gen/fab32.sh` |

**Supply copper, calculated, mΩ at 20 °C:**

| Path | 2026-11-14 | 2026-11-16 | Why it moved |
|---|---|---|---|
| Pi 5 V: module → fuse / fuse → link / link → socket / return | 1.02 / 0.53 / 2.24 / 1.03 | 1.02 / 0.53 / **2.27** / 1.03 | R10's and R11's vias left the 5 V copper on the back |
| Pi 5 V, board copper in all | 4.82 | **4.84** | |
| 20 V: socket → fuse | 1.06 | 1.06 | |
| 20 V: fuse → protection chip | 0.99 | **0.92** | C2's ground via no longer cuts into the inlet pour |
| 20 V: chip → filter coil (layer 3) | 3.68 | 3.68 | |
| 20 V: coil → module | 5.27 | 5.27 | |
| Amplifier supply: fuse F5 → chip pins | 7.564 | 7.564 | |
| Amplifier supply: fuse F5 → C100–C102 | 8.875 | **8.886** | the supply plane 0.2 further from the relief |

**Not run again:** the 41 site rules of rev 3.2. They test parts, outline, holes, heights and through-hole joints, and
none of those changed (first row of the table above).

## 6. How to make it again
```
cd hardware/main-board
gen/fab32.sh rev3.2/main-board-rev3.2-2026-11-14.kicad_pcb /tmp/fab32 F4.1 R3.2 C3.2 R8.2 C10.2
```
The script copies the board beside the project file first: KiCad's Python reads the board's rules (net classes,
clearances) only from a `.kicad_pro` that lies beside the board, and a board read without it would be planned with
KiCad's own 0.2 clearance for every net.

## 7. Files in this folder
| File | What |
|---|---|
| `via-plan.json`, `via-plan-run.txt`, `fab32-run.txt` | the plan, the planner's log, the change script's log |
| `via-moves.md`, `via-moves.png` | every move in a table and drawn; `via_sheet.py` draws the sheet |
| `via-check.txt`, `via-planes-result.txt`, `via_planes.py` | the checks after the change |
| `plug-check-result.txt`, `plug_check.py` | both boards against JLC's three conditions for plugged vias |
| `relief-edge-result.txt`, `relief-edge-2026-11-14-result.txt`, `relief_edge.py`, `relief-copper.png`, `relief_picture.py` | the copper at the relief |
| `compare-2026-11-14-result.txt` | item-by-item comparison with rev 3.2 of 2026-11-14 (`../check/compare_boards.py`) |
| `supply-copper-result.txt` | the supply copper before and after (`../../rev3.1/check/pi5v_board.py`, `../check/pvdd_path.py`) |

Scripts in `../../gen/`: `fab32.sh` (driver), `fab32_vias.py` (planner, apply, check), `fab32.py` (relief, text,
stack-up), `assembly_rev32.py` (assembly drawing).

## Repeat check (2026-11-16, after the fab files were made)
`gen/fab32.sh rev3.2/main-board-rev3.2-2026-11-14.kicad_pcb <scratch dir> F4.1 R3.2 C3.2 R8.2 C10.2` was run once more from the 2026-11-14 board:
- the via plan is identical to `via-plan.json`, byte for byte;
- the board has the same 1458 tracks and vias, 21 pour layers and rule areas, 120 parts and 27 board graphics as `../../main-board.kicad_pcb`. KiCad gives new items new identifiers on every run and saves in identifier order, so the files differ in the order of some tracks, not in content;
- its fab files are identical to `../../fab/gerbers/` for 10 of the 12 files (creation date aside); the two outer copper files hold the same flashes, tracks and filled areas in another order;
- ERC 0 / 0; DRC 0 errors, 0 unconnected, 2 library warnings (J6, J2); via check as `via-check.txt`.
