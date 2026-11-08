# JLC bare-board order sheet: main board and mic strip (block 3, 2026-11-08)

These two boards are added as two designs to Daniel's JLC order (the one with the Spooky Manor boards). **Bare boards only:** no SMT assembly, so no BOM or CPL files go to JLC. Daniel assembles the boards himself.

| Upload | Board | KiCad source |
|---|---|---|
| `hardware/main-board/fab/main-board-jlc-2026-11-08.zip` | main board, layout rev 2.1 | `hardware/main-board/main-board.kicad_pcb` |
| `hardware/mic-strip/fab/mic-strip-jlc-2026-11-08.zip` | mic strip; one design, used twice | `hardware/mic-strip/mic-strip.kicad_pcb` |

The unzipped files sit next to each zip in `fab/gerbers/`; hole counts are in `fab/drill-report.txt`.

## Order options
| Option | Main board | Mic strip |
|---|---|---|
| Base material | FR-4 | FR-4 |
| Layers | 4 | 2 |
| Size | 90 × 55 mm | 28 × 6 mm |
| Quantity | 5 (JLC minimum; 1 needed) | 5 (JLC minimum; 2 needed) |
| Delivery format | single PCB | single PCB (see "Panelisation") |
| Thickness | 1.6 mm | **0.8 mm** (strip stack in the cap, K21) |
| Impedance control | no | — |
| Layer stack-up | JLC04161H-7628: 7628 prepreg 0.2104, core 1.065; the same build as "No requirement" | — |
| Outer copper | 1 oz | 1 oz |
| Inner copper | 0.5 oz (JLC default) | — |
| Via hole / diameter | 0.2 / 0.45 mm, which carries no surcharge | 0.2 / 0.45 mm |
| Via covering | tented | tented |
| Surface finish | **ENIG** recommended (flat pads for the 0.5 mm HTSSOP-48 and its PowerPAD on the hotplate); LeadFree HASL is the cheaper fallback | **ENIG** recommended (small LGA pads of the IM69D120); LeadFree HASL as fallback |
| Mask / silkscreen | green / white | green / white |
| Order number on the board | JLC default placement | JLC default placement |
| Gold fingers, castellations, edge plating | no | no |

## What the files use against JLC's limits
| Item | Main board | Mic strip | JLC limit |
|---|---|---|---|
| Track / space | 0.10 / 0.15 | 0.20 / 0.15 | 0.09 / 0.09 multilayer; 0.10 / 0.10 for 1–2 layers |
| Vias | 0.2/0.45 ×18, 0.3/0.6 ×131, 0.4/0.8 ×4 | 0.2/0.45 ×28 | 0.15/0.25 minimum; 0.2 preferred; extra cost below 0.45 diameter at 0.2–0.25 hole |
| Component hole annular ring | 0.35 min, except J2 | — | multilayer 1 oz: 0.20 recommended, 0.15 absolute |
| J2 (USB4085) ring | 0.15: 16 contacts Ø0.4 in Ø0.7 pads (GCT's recommended layout) | — | at the multilayer absolute minimum, so JLC's review may mention it |
| Plated slots | J2's 4 shell stakes, 0.6 × 1.4 and 0.6 × 2.1 | — | 0.35 multilayer (0.5 in the description) |
| NPTH | 4 × Ø2.7 (mounting) | Ø0.8 (mic port), 2 × Ø2.0 (heat-stake pins) | Ø0.50 minimum |
| Copper to edge | 0.3 | 0.3 | 0.2 |
| Silkscreen | text 1.0 high, 0.15 stroke; KiCad library outlines 0.12 | outlines and polarity marks only (no room for references) | text 1.0 / 0.15, lines ≥ 0.15 |

- **Thin silk outlines.** The 0.12 mm outlines come from the KiCad standard footprints and may print thin. The block 3 assembly drawing carries every reference, polarity mark and pin-1 mark.
- **Paste layers are included,** for an optional JLC stencil. Main board: F.Paste only, since B.Paste is empty. Strip: B.Paste only, because its parts are on the back.

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

**Check:** the main-board front stack (copper, mask, silk, edge) and both sides of the strip were rendered from the exported files with pygerber 2.4.3, and they match the KiCad boards.

## Panelisation
- **Not required.** JLC's minimum board size is 3 × 3 mm, and the strip is 28 × 6.
- JLC says panelisation is "recommended" for small boards. Five single strips are the simplest order.
- If the order page asks for a panel anyway, use "Panel by JLCPCB" without edge rails.
- At 0.8 mm the strip is above JLC's 0.6 mm manual-review threshold.

## Sources
Read 2026-11-08:
- JLC PCB capabilities — https://jlcpcb.com/capabilities/pcb-capabilities
- JLC "How to generate Gerber and Drill files in KiCAD 9" — https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9
- JLC stack-ups — https://jlcpcb.com/impedance
- GCT USB4085 drawing rev B (2023-02-28), recommended PCB layout — https://gct.co/files/drawings/usb4085.pdf (read 2026-11-07)
