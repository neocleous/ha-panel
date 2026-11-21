# Mic strip rev 3 — JLC order sheet (fab issue 2026-11-21)

**Upload:** `mic-strip-rev3-jlc-2026-11-21.zip`
sha256 `0e378603bf06f547f44f3cb741d6ad13222e0321c87d36a35d0614bcfe94b095`

- One design, used twice in the panel (left and right strip). Bare board; no assembly files go to JLC.
- **What changed from the set of 2026-11-09 (rev 1):** 13 vias moved out of the pads that take solder and one taken out (24 vias, was 25); every silk line 0.15 wide; the board file carries a title block with rev 3. Outline, holes, port, parts, pads and options are unchanged. Rev 2 (31.4 long) was never built; the name is not reused.
- **The 2026-11-09 zip's cart line was replaced by this one before the order.** That zip is kept in `superseded/` and must not be ordered.
- **Ordered 2026-11-21:** line `mic-strip-rev3-jlc-2026-11-21_Y22`, **€19.90**, build 3 days: the €18.94 of the 2026-11-09 line plus €0.96 for "Confirm Production file". The 2026-11-09 line was deleted. (€18.85 on 2026-11-16: 3.62 + ENIG 15.04 + deburring 0.18.)
- JLC's capability figures were read on jlcpcb.com on **2026-11-16**; the soldermask figure for black on **2026-11-17**.
- The option names are the order page's own, read on 2026-11-16.

## What is in the zip (12 files)
`mic-strip-rev3-F_Cu.gtl`, `-B_Cu.gbl`, `-F_Mask.gts`, `-B_Mask.gbs`, `-F_Silkscreen.gto`, `-B_Silkscreen.gbo`, `-F_Paste.gtp` (empty), `-B_Paste.gbp`, `-Edge_Cuts.gm1`, `-PTH.drl`, `-NPTH.drl`, `-job.gbrjob`.

The two paste files are in the zip, as in the set of 2026-11-09. JLC uses them only if a stencil is ordered on this line, which it is not: since 2026-11-21 the strip's back paste is cut on the touch board's stencil, its own line (`../../stencil/fab/ORDER-SHEET.md`).

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
| Confirm Production file | **Yes** | Daniel, 2026-11-21. JLC sends its production file for confirmation; if it is not confirmed within 48 hours, the order goes into production by itself (the dialog's "Do not confirm automatically" box is left unticked). €0.96 |
| Gold fingers, castellated holes, edge plating | no | |
| "Stencil: order together with PCB" | **off** | the strip's pattern is on the touch board's stencil, its own line |
| PCB remark | none | |

## The files against JLC's limits
JLC figures: https://jlcpcb.com/capabilities/pcb-capabilities, read 2026-11-16. The soldermask bridge was read again on 2026-11-17 for black: 1 oz copper, pad spacing 0.10 at least for green, red, yellow, blue and purple, **0.13 for black and white**.

| Item | This board | JLC |
|---|---|---|
| Track / space | 0.20 / 0.15 | 0.10 / 0.10 (1–2 layers) |
| Vias | 24 × 0.3/0.5; every hole 0.217 or more from the opening of each pad that takes paste (J1.2's, in its wire pad, aside) | minimum 0.15/0.25 |
| Unplated holes | 1 × Ø0.8 (mic port), 2 × Ø2.0 (locating holes for the cap's pins) | Ø0.50 minimum |
| Copper to the routed edge | 0.3 | 0.2 |
| Outline | routed rectangle 28.00 × 6.00 | regular ±0.2 |
| Soldermask web between two pads | 0.17 smallest (at the microphone) | 0.13 (black) |
| Silkscreen | back only: outlines 0.15 wide, no text | line 0.15 |
| Thickness | 0.8 | ±0.1 for boards under 1.0 mm |

## Checks (2026-11-21)
`fab-check-2026-11-21.txt`, all passed: 24 via flashes of Ø0.5 on both copper layers and no soldermask opening at any; 35 paste apertures on the back for 35 pasted pads; outline 28.00 × 6.00; holes 24 × 0.30 plated, 1 × 0.80 and 2 × 2.00 unplated; job file 2 layers, 0.8 mm, rev 3; pours current. A fresh export gives the same 12 files as the zip, line for line apart from the export's time. Render: `mic-strip-rev3-gerbers.png`.

KiCad's checks on the board: electrical rules 0; design rules at all severities 0 violations, 0 unconnected, parity clean.

How the set is made: `sh ../../main-board/tools/fab_export.sh ../mic-strip.kicad_pcb mic-strip-rev3 . 2026-11-21 F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts`.

## Earlier sets
- **Rev 1, set of 2026-11-09:** `superseded/mic-strip-jlc-2026-11-09.zip` (sha256 `f405cc56…4564`), with its check of 2026-11-16. Must not be ordered: 13 via holes lie in pads that take solder.
