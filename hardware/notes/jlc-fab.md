# JLC order sheet: main board, mic strip, touch board, stencil (block 3; rev 2026-11-09)

Three boards and one stencil go into Daniel's JLC order (the one with the Spooky Manor boards; D54). **Bare boards only:** no SMT assembly, so no BOM or CPL files go to JLC. Daniel assembles the boards himself.

Rev 2026-11-09: touch board rev D added (D57: 2 layers, 1.6, ENIG); the stencil now covers the main board's front **and** the touch board's back, from its own zip (D57).

| Upload | Board | KiCad source |
|---|---|---|
| `hardware/main-board/fab/main-board-jlc-2026-11-08.zip` | main board, layout rev 2.1 | `hardware/main-board/main-board.kicad_pcb` |
| `hardware/mic-strip/fab/mic-strip-jlc-2026-11-08.zip` | mic strip; one design, used twice | `hardware/mic-strip/mic-strip.kicad_pcb` |
| `hardware/touch-board/fab/touch-board-jlc-2026-11-09.zip` | touch board rev D | `hardware/touch-board/touch-board.kicad_pcb` |
| `hardware/stencil/fab/stencil-main-touch-jlc-2026-11-09.zip` | **stencil line only:** main-board front + touch-board back paste | `hardware/stencil/stencil-main-touch.kicad_pcb` (generated; `hardware/stencil/README.md`) |

The unzipped files sit next to each zip in `fab/gerbers/`; hole counts are in `fab/drill-report.txt`.

## Order options
| Option | Main board | Mic strip | Touch board rev D |
|---|---|---|---|
| Base material | FR-4 | FR-4 | FR-4 |
| Layers | 4 | 2 | 2 |
| Size | 90 × 55 mm | 28 × 6 mm | 90 × 44 mm |
| Quantity | 5 (JLC minimum; 1 needed) | 5 (JLC minimum; 2 needed) | 5 (JLC minimum; 1 needed) |
| Delivery format | single PCB | single PCB (see "Panelisation") | single PCB |
| Thickness | 1.6 mm | **0.8 mm** (strip stack in the cap, K21) | 1.6 mm (rev F chin seat, as rev C) |
| Impedance control | no | — | — |
| Layer stack-up | JLC04161H-7628: 7628 prepreg 0.2104, core 1.065; the same build as "No requirement" | — | — |
| Outer copper | 1 oz | 1 oz | 1 oz |
| Inner copper | 0.5 oz (JLC default) | — | — |
| Via hole / diameter | 0.2 / 0.45 mm, which carries no surcharge | 0.2 / 0.45 mm | 0.3 / 0.6 mm |
| Via covering | tented | tented | tented |
| Surface finish | **ENIG** (Daniel, 2026-11-08) | **ENIG** (Daniel, 2026-11-08) | **ENIG** (Daniel, 2026-11-09, D57) |
| Mask / silkscreen | green / white | green / white | green / white |
| Order number on the board | JLC default placement | JLC default placement | JLC default placement (the front has no silk and sits behind the wall) |
| Gold fingers, castellations, edge plating | no | no | no |
| SMT stencil tick box on this line | **no** (see "Stencil") | no | **no** (see "Stencil") |

## What the files use against JLC's limits
| Item | Main board | Mic strip | Touch board rev D | JLC limit |
|---|---|---|---|---|
| Track / space | 0.10 / 0.15 | 0.20 / 0.15 | 0.25 / 0.15 (rule; supply 0.40) | 0.09 / 0.09 multilayer; 0.10 / 0.10 for 1–2 layers |
| Vias | 0.2/0.45 ×18, 0.3/0.6 ×131, 0.4/0.8 ×4 | 0.2/0.45 ×28 | 0.3/0.6 ×4 (electrode feeds) | 0.15/0.25 minimum; 0.2 preferred; extra cost below 0.45 diameter at 0.2–0.25 hole |
| Component hole annular ring | 0.35 min, except J2 | — | — (no component holes) | multilayer 1 oz: 0.20 recommended, 0.15 absolute |
| J2 (USB4085) ring | 0.15: 16 contacts Ø0.4 in Ø0.7 pads (GCT's recommended layout) | — | — | at the multilayer absolute minimum, so JLC's review may mention it |
| Plated slots | J2's 4 shell stakes, 0.6 × 1.4 and 0.6 × 2.1 | — | — | 0.35 multilayer (0.5 in the description) |
| NPTH | 4 × Ø2.7 (mounting) | Ø0.8 (mic port), 2 × Ø2.0 (heat-stake pins) | none | Ø0.50 minimum |
| Copper to edge | 0.3 | 0.3 | 0.3 | 0.2 |
| Silkscreen | text 1.0 high, 0.15 stroke; KiCad library outlines 0.12 | outlines and polarity marks only (no room for references) | back only: text 1.0 / 0.15, KiCad library outlines 0.12 | text 1.0 / 0.15, lines ≥ 0.15 |

- **Thin silk outlines.** The 0.12 mm outlines come from the KiCad standard footprints and may print thin. The block 3 assembly drawing carries every reference, polarity mark and pin-1 mark.
- **Paste layers are included.** Main board: F.Paste only, since B.Paste is empty. Strip and touch board: B.Paste only, because their parts are on the back. JLC uses them only if the stencil box on that board's line is ticked, which it is not ("Stencil").

## Stencil (main board front + touch board back; D57, Daniel 2026-11-09)
**One JLC SMT stencil, ordered as its own stencil line from `hardware/stencil/fab/stencil-main-touch-jlc-2026-11-09.zip`.**
- That file's top paste layer holds both patterns: the main board's front as drawn, and the touch board's back mirrored, 10 mm below it. The pattern extent is 90.1 × 109.2 mm.
- Do not tick the stencil box on the main-board or touch-board PCB lines; that would cut a stencil from one board's zip alone.
- The strip's 12 SMD parts are pasted by syringe.
- How the file is built and checked: `hardware/stencil/README.md`.

| Option | Choice | Why |
|---|---|---|
| Stencil type | Non-framework | hand use on the hotplate; framework stencils are for printers |
| Stencil side | **Top** | both patterns are on the file's top paste layer; the touch board's back pattern is already mirrored |
| Thickness | 0.12 mm | standard thickness at no extra cost; JLC suggests 0.10–0.12 for fine pitch |
| Polishing | Electropolishing | JLC lists it as ideal for ICs at or below 0.5 mm pitch (the TAS5756M) |
| Fiducials | No fiducial | aligned by hand to the pads |
| Size | the smallest size the order page offers that holds 90.1 × 109.2 mm | both outlines; size and price in the order list rev 5 |
| **Remark** | "One stencil, two boards: main board top paste and touch board bottom paste, already mirrored in this file. No copper layer on purpose. Please cut every aperture 1:1 as drawn and keep both patterns where they are." | By default JLC resizes apertures for IC packages and 0805+ parts. The TAS5756M thermal-pad windows (70–80 % of the pad, SLAS988B 11.1.3.2) are designed and must stay as drawn. |

## Export settings
JLC's KiCad 9 guide, applied with kicad-cli 9.0.9:
- **Gerbers:**
  - Protel extensions, X2 attributes and netlist attributes on;
  - coordinate format 4.6 mm;
  - values excluded;
  - soldermask subtracted from silkscreen (not in the guide; it keeps silk off pads).
- **Drill:**
  - Excellon, PTH and NPTH in separate files;
  - absolute origin, millimetres, decimal zeros;
  - oval holes in alternate drill mode (G85 slots).

- **Stencil:** `kicad-cli pcb export gerbers --layers F.Paste,Edge.Cuts --exclude-value` on the generated stencil file.

**Check:** rendered from the exported files with pygerber 2.4.3, and matching the KiCad boards:
- the main-board front stack (copper, mask, silk, edge);
- both sides of the strip;
- both sides of the touch board (2026-11-09): the front has the four electrodes under the mask with no openings, and the back has the parts, the HOST pads and their labels;
- the stencil, which is also checked flash by flash against both boards' paste files (`hardware/stencil/README.md`).

## Panelisation
- **Not required.** JLC's minimum board size is 3 × 3 mm, and the strip is 28 × 6.
- JLC says panelisation is "recommended" for small boards. Five single strips are the simplest order.
- If the order page asks for a panel anyway, use "Panel by JLCPCB" without edge rails.
- At 0.8 mm the strip is above JLC's 0.6 mm manual-review threshold.

## Sources
Read 2026-11-08 (the touch-board column and the stencil options use the same pages):
- JLC PCB capabilities — https://jlcpcb.com/capabilities/pcb-capabilities
- JLC "How to generate Gerber and Drill files in KiCAD 9" — https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9
- JLC stack-ups — https://jlcpcb.com/impedance
- JLC stencil capabilities — https://jlcpcb.com/capabilities/pcb-stencil-manufacturing
- GCT USB4085 drawing rev B (2023-02-28), recommended PCB layout — https://gct.co/files/drawings/usb4085.pdf (read 2026-11-07)
