# Touch board rev D — JLC order sheet (set of 2026-11-09, confirmed current 2026-11-16; sheet corrected 2026-11-17)

**Upload:** `touch-board-jlc-2026-11-09.zip`
sha256 `2d62d7eca9126be672a78bb0a46d35bbd1463b2dc3d9a8c736272d2777056a34`

- Bare board; no assembly files go to JLC.
- **The set was not re-issued.** The board file has not changed since this zip was made. An export on 2026-11-16 gives the same files, line for line apart from the creation date. "Rev D" is the name in the project's records; the board's title block carries no revision.
- **Price on 2026-11-16:** 5 boards, black, €19.03 (3.62 + ENIG 15.40), build 3 days.
- JLC's capability figures were read on jlcpcb.com on **2026-11-16**; the soldermask figure for black on **2026-11-17**.
- The option names are the order page's own, read on 2026-11-16.

## What is in the zip (12 files)
`touch-board-F_Cu.gtl`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Silkscreen.gto`, `-B_Silkscreen.gbo`, `-F_Paste.gtp` (empty), `-B_Paste.gbp`, `-Edge_Cuts.gm1`, `-PTH.drl`, `-NPTH.drl` (no holes), `-job.gbrjob`.

The paste files are in the zip from 2026-11-09. JLC uses them only if a stencil is ordered on this line, which it is not: this board's paste pattern is on the combined stencil (`../../stencil/fab/ORDER-SHEET.md`).

## Order options
| Option | Choice | Note |
|---|---|---|
| Base material | FR-4 | |
| Layers | **2** | |
| Dimensions | **90 × 44 mm** | |
| Quantity | 5 | JLC's minimum on 2026-11-09; 1 needed |
| Delivery format | single PCB | |
| Thickness | **1.6 mm** | |
| PCB colour / silkscreen | **black** / white | chosen 2026-11-16 (green before). Black costs nothing more on a 2-layer board |
| Surface finish | **ENIG**, thickness "1U\"" | chosen 2026-11-09. The page's default for a 2-layer board is OSP: change it |
| Outer copper | 1 oz | |
| Via covering | tented | |
| Min via hole size/diameter | "0.3mm/(0.4/0.45mm)" | the vias are 0.3/0.6 |
| Electrical test | **"Flying Probe Fully Test"** | the only test the page of 2026-11-16 offers; it has no "4-Wire Kelvin Test" row |
| Board outline tolerance | regular, ±0.2 mm | |
| Mark on PCB | **"Remove Mark"** | |
| Gold fingers, castellated holes, edge plating | no | |
| "Stencil: order together with PCB" | **off** | the stencil is its own line |
| PCB remark | none | |

## The files against JLC's limits
JLC figures: https://jlcpcb.com/capabilities/pcb-capabilities, read 2026-11-16. The soldermask bridge was read again on 2026-11-17 for black: 1 oz copper, pad spacing 0.10 at least for green, red, yellow, blue and purple, **0.13 for black and white**.

| Item | This board | JLC |
|---|---|---|
| Track / space | 0.25 / 0.15 | 0.10 / 0.10 (1–2 layers) |
| Vias | 4 × 0.3/0.6 (the electrode feeds) | minimum 0.15/0.25 |
| Component holes, unplated holes | none | — |
| Copper to the routed edge | 0.3 | 0.2 |
| Outline | routed, 90.00 × 44.00, four rounded outer corners | regular ±0.2 |
| Soldermask | front: no openings (the four electrodes are under the mask); back: 30 openings, the smallest web between two of them 0.65 (C1, C2) | bridge 0.13 (black) |
| Silkscreen | back only: text 1.0 high, 0.15 stroke; library outlines 0.12 wide | text 1.0, line 0.15: the outlines may print thin |

## Checks (2026-11-16)
`fab-check-2026-11-16.txt`, all passed: 4 via flashes of Ø0.6 on both copper layers and no soldermask opening at any; 26 paste apertures on the back for 26 pasted pads; outline 90.00 × 44.00 with 4 arcs; holes 4 × 0.30 plated, none unplated; job file 2 layers, 1.6 mm.
