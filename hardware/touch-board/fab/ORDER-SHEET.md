# Touch board rev E — JLC order sheet (fab issue 2026-11-21)

**Upload:** `touch-board-revE-jlc-2026-11-21.zip`
sha256 `12641c710499f8dab67cd457623986f8389a1c9a527aa9ff06c9db64083fa4ec`

- Bare board; no assembly files go to JLC.
- **What changed from rev D (set of 2026-11-09):** every silk line 0.15 wide; the back reads `HA panel touch board rev E 2026-11-21`; the board file carries a title block with rev E. Copper, mask, paste, outline and options are unchanged.
- **The cart line of the 2026-11-09 zip must be replaced by this one.** That zip is kept in `superseded/` and must not be ordered.
- **In the cart since 2026-11-21:** line `touch-board-revE-jlc-2026-11-21_Y23`, **€19.12**, build 3 days, the same as the 2026-11-09 line, which was deleted. (€19.03 on 2026-11-16: 3.62 + ENIG 15.40.) "Confirm Production file" is No on this line.
- JLC's capability figures were read on jlcpcb.com on **2026-11-16**; the soldermask figure for black on **2026-11-17**.
- The option names are the order page's own, read on 2026-11-16.

## What is in the zip (12 files)
`touch-board-revE-F_Cu.gtl`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Silkscreen.gto`, `-B_Silkscreen.gbo`, `-F_Paste.gtp` (empty), `-B_Paste.gbp`, `-Edge_Cuts.gm1`, `-PTH.drl`, `-NPTH.drl` (no holes), `-job.gbrjob`.

The paste files are in the zip, as in the set of 2026-11-09. JLC uses them only if a stencil is ordered on this line, which it is not: this board's paste pattern is on the stencil it shares with the mic strip, its own line (`../../stencil/fab/ORDER-SHEET.md`).

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
| Silkscreen | back only: text 1.0 high, 0.15 stroke; every line 0.15 wide | text 1.0, line 0.15 |

## Checks (2026-11-21)
`fab-check-2026-11-21.txt`, all passed: 4 via flashes of Ø0.6 on both copper layers and no soldermask opening at any; 26 paste apertures on the back for 26 pasted pads; outline 90.00 × 44.00 with 4 arcs; holes 4 × 0.30 plated, none unplated; job file 2 layers, 1.6 mm, rev E. A fresh export gives the same 12 files as the zip, line for line apart from the export's time. Render: `touch-board-revE-gerbers.png`.

KiCad's checks on the board: electrical rules 0; design rules at all severities 0 violations, 0 unconnected, parity clean.

How the set is made: `sh ../../main-board/tools/fab_export.sh ../touch-board.kicad_pcb touch-board-revE . 2026-11-21 F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts`.

## Earlier sets
- **Rev D, set of 2026-11-09:** `superseded/touch-board-jlc-2026-11-09.zip` (sha256 `2d62d7ec…6a34`), with its check of 2026-11-16. Electrically the same board; replaced for the silk widths and the revision text. Not to be ordered once rev E is uploaded.
