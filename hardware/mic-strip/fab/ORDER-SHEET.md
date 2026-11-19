# Mic strip — JLC order sheet (set of 2026-11-09, confirmed current 2026-11-16 and 2026-11-19; sheet corrected 2026-11-17)

**Upload:** `mic-strip-jlc-2026-11-09.zip`
sha256 `f405cc567fab336cf9e0fb4b0da1def971ca79bae3d6d8b02ea9bce7e5584564`

- One design, used twice in the panel (left and right strip). Bare board; no assembly files go to JLC.
- **The set was not re-issued.** The board file has not changed since this zip was made. Exports on 2026-11-16 and 2026-11-19 give the same files, line for line apart from the creation date. The board has no revision in its title block; this issue, of 2026-11-09, is the one with 0.3 mm via holes.
- **Price on 2026-11-16:** 5 boards, black, €18.85 (3.62 + ENIG 15.04 + deburring 0.18), build 3 days.
- JLC's capability figures were read on jlcpcb.com on **2026-11-16**; the soldermask figure for black on **2026-11-17**.
- The option names are the order page's own, read on 2026-11-16.

## What is in the zip (12 files)
`mic-strip-F_Cu.gtl`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Silkscreen.gto`, `-B_Silkscreen.gbo`, `-F_Paste.gtp` (empty), `-B_Paste.gbp`, `-Edge_Cuts.gm1`, `-PTH.drl`, `-NPTH.drl`, `-job.gbrjob`.

The two paste files are in the zip from 2026-11-09. JLC uses them only if a stencil is ordered on this line, which it is not: the strip's parts are pasted by syringe.

## Order options
| Option | Choice | Note |
|---|---|---|
| Base material | FR-4 | |
| Layers | **2** | |
| Dimensions | **28 × 6 mm** | |
| Quantity | 5 | JLC's minimum on 2026-11-09; 2 needed |
| Delivery format | single PCB | if the page asks for a panel: "Panel by JLCPCB" without edge rails |
| Thickness | **0.8 mm** | the strip stack in the top cap |
| PCB colour / silkscreen | **black** / white | chosen 2026-11-16 (green before). Black costs nothing more on a 2-layer board |
| Surface finish | **ENIG**, thickness "1U\"" | chosen 2026-11-08. The page's default for a 2-layer board is OSP: change it |
| Outer copper | 1 oz | |
| Via covering | tented | |
| Deburring | on | the page's default for a board this small; €0.18 |
| Min via hole size/diameter | "0.3mm/(0.4/0.45mm)" | the vias are 0.3/0.5 |
| Electrical test | **"Flying Probe Fully Test"** | the only test the page of 2026-11-16 offers; it has no "4-Wire Kelvin Test" row |
| Board outline tolerance | regular, ±0.2 mm | |
| Mark on PCB | **"Remove Mark"** | |
| Gold fingers, castellated holes, edge plating | no | |
| "Stencil: order together with PCB" | **off** | |
| PCB remark | none | |

## The files against JLC's limits
JLC figures: https://jlcpcb.com/capabilities/pcb-capabilities, read 2026-11-16. The soldermask bridge was read again on 2026-11-17 for black: 1 oz copper, pad spacing 0.10 at least for green, red, yellow, blue and purple, **0.13 for black and white**.

| Item | This board | JLC |
|---|---|---|
| Track / space | 0.20 / 0.15 | 0.10 / 0.10 (1–2 layers) |
| Vias | 25 × 0.3/0.5 | minimum 0.15/0.25 |
| Unplated holes | 1 × Ø0.8 (mic port), 2 × Ø2.0 (locating holes for the cap's pins) | Ø0.50 minimum |
| Copper to the routed edge | 0.3 | 0.2 |
| Outline | routed rectangle 28.00 × 6.00 | regular ±0.2 |
| Soldermask web between two pads | 0.17 smallest (at the microphone) | 0.13 (black) |
| Silkscreen | back only: outlines 0.12 wide, no text | line 0.15: may print thin |
| Thickness | 0.8 | ±0.1 for boards under 1.0 mm |

## Checks (2026-11-16)
`fab-check-2026-11-16.txt`, all passed: 25 via flashes of Ø0.5 on both copper layers and no soldermask opening at any; 35 paste apertures on the back for 35 pasted pads; outline 28.00 × 6.00; holes 25 × 0.30 plated, 1 × 0.80 and 2 × 2.00 unplated; job file 2 layers, 0.8 mm; pours current.
