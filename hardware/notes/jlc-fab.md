# JLC order sheet: main board, mic strip, touch board, stencil (block 3; rev 2026-11-09)

Three boards and one stencil go into Daniel's JLC order (the one with the Spooky Manor boards; D54). **Bare boards only:** no SMT assembly, so no BOM or CPL files go to JLC. Daniel assembles the boards himself.

Rev 2026-11-09: touch board rev D added (D57: 2 layers, 1.6, ENIG); the stencil now covers the main board's front **and** the touch board's back, from its own zip (D57). Later the same day: strip vias 0.3/0.5 and a new strip zip (D63 = b, "Strip vias").

| Upload | Board | KiCad source |
|---|---|---|
| `hardware/main-board/fab/main-board-jlc-2026-11-08.zip` | main board, layout rev 2.1 | `hardware/main-board/main-board.kicad_pcb` |
| `hardware/mic-strip/fab/mic-strip-jlc-2026-11-09.zip` | mic strip; one design, used twice. Vias 0.3/0.5 (D63 = b); it replaces the 2026-11-08 zip, which was removed from the tree. | `hardware/mic-strip/mic-strip.kicad_pcb` |
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
| Via hole / diameter | 0.2 / 0.45 mm, which carries no surcharge | **0.3 / 0.5 mm** (D63 = b, 2026-11-09) | 0.3 / 0.6 mm |
| Via covering | **plugged** (JLC's default; "Tented" is greyed out for 4 layers on the order page, 2026-11-09) | tented | tented |
| Surface finish | **ENIG** (Daniel, 2026-11-08) | **ENIG** (Daniel, 2026-11-08) | **ENIG** (Daniel, 2026-11-09, D57) |
| Mask / silkscreen | green / white | green / white | green / white |
| Mark on PCB | "Remove Mark" (the order page's default, no charge, 2026-11-09) | same | same |
| Gold fingers, castellations, edge plating | no | no | no |
| Min via hole size/diameter (order page) | "0.3mm/(0.4/0.45mm)": the page's note says that on multilayer boards a 0.2 mm hole with ≥ 0.45 mm diameter costs nothing extra | "0.3mm/(0.4/0.45mm)": the vias are 0.3/0.5, inside the free class (D63 = b) | "0.3mm/(0.4/0.45mm)" (vias 0.3/0.6) |
| 4-Wire Kelvin Test (Advanced Options) | **No**: the page switches it on by itself when a smaller via class is picked; switch it back | No | No |
| "Stencil: Order together with PCB" on this line | **off** (see "Stencil") | off | **off** (see "Stencil") |

## What the files use against JLC's limits
| Item | Main board | Mic strip | Touch board rev D | JLC limit |
|---|---|---|---|---|
| Track / space | 0.10 / 0.15 | 0.20 / 0.15 | 0.25 / 0.15 (rule; supply 0.40) | 0.09 / 0.09 multilayer; 0.10 / 0.10 for 1–2 layers |
| Vias | 0.2/0.45 ×18, 0.3/0.6 ×131, 0.4/0.8 ×4 | **0.3/0.5 ×25** (D63 = b): ring 0.10, hole to hole ≥ 0.45, hole to other-net copper ≥ 0.29 | 0.3/0.6 ×4 (electrode feeds) | 0.15/0.25 minimum; 0.2 preferred; extra cost below 0.45 diameter at 0.2–0.25 hole |
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
- Leave the stencil toggle on the main-board and touch-board PCB lines off; it would cut a stencil from one board's zip alone.
- The strip's 12 SMD parts are pasted by syringe.
- How the file is built and checked: `hardware/stencil/README.md`.

| Option | Choice | Why |
|---|---|---|
| Product | "SMT Stencil" (its own quote page, not the PCB line's stencil toggle) | the upload is the combined stencil zip |
| Framework | No | hand use on the hotplate; framework stencils are for printers |
| Stencil side | **Top only** | both patterns are on the file's top paste layer; the touch board's back pattern is already mirrored |
| Dimensions | **Custom 190 × 190 mm** | same price as the smallest standard size (380 × 280), 0.33 kg instead of 0.96 kg; holds the 90.1 × 109.2 pattern; rev C used 190 × 190 |
| Thickness | "Select by Customer", **0.12 mm** | no extra charge; JLC suggests 0.10–0.12 for fine pitch |
| Stencil process type | Solder paste stencil | |
| Multiple PCBs on one stencil | **Yes** | The page's note: "If you have multiple different PCBs on one stencil, please click Yes." The pop-up then asks whether JLC may re-arrange the patterns' typesetting or distance. The option only stays on with **Yes**, at no extra charge. |
| Polishing | Electropolishing (+€4.45) | JLC lists it as ideal for ICs at or below 0.5 mm pitch (the TAS5756M) |
| Fiducials | No fiducial | aligned by hand to the pads |
| Stencil aperture openings | **"1:1 as per Paste Layer"** | The default "Follow JLCPCB's Standard" resizes apertures. The TAS5756M thermal-pad windows (70–80 % of the pad, SLAS988B 11.1.3.2) are designed and must stay as drawn. |
| **Stencil remark** | "Two PCBs on one stencil: main board top paste, and touch board bottom paste already mirrored in this file. No copper layer on purpose. Keep each pattern's orientation; spacing may change." | the pattern orientation is the one thing a re-arrangement must not change |

## Strip vias: resolved by D63 = (b) (Daniel, 2026-11-09)
**The strip is re-routed with 0.3 mm via holes:** 28 vias at 0.2/0.45 became **25 vias at 0.3/0.5**.
- Upload: `hardware/mic-strip/fab/mic-strip-jlc-2026-11-09.zip`.
- Details: `hardware/mic-strip/README.md` and `claude/report-electronics-strip-vias-2026-11-09.md`.

**Why it was needed:**
- JLC's order-page note states its 0.2 mm exemption ("free at ≥ 0.45 mm diameter") only "for multi-layer boards", and the strip has 2 layers.
- The worst case at review was +€44.45:
  - via class €14.82;
  - a 4-wire Kelvin test the page adds by itself, €14.82;
  - plugged instead of tented vias, €14.81.
- A plain re-drill in the 0.45 pads would have broken the board's 0.10 via ring and 0.25 hole clearance, and left two GND vias 0.24 apart.

**JLC capabilities, 2-layer, re-read 2026-11-09** (https://jlcpcb.com/capabilities/pcb-capabilities):

| Item | JLC figure |
|---|---|
| Minimum via hole / diameter | 0.15 / 0.25 mm |
| Via diameter vs hole | 0.10 mm larger, 0.15 preferred |
| Via hole to hole | 0.2 mm; the page does not split same net and different nets |
| Pad hole to hole | 0.45 mm |
| Via hole to track | 0.2 mm |
| NPTH to track | 0.2 mm |
| PTH annular ring, 1 oz | 0.25 recommended / 0.18 minimum. There is no separate via-ring row; the via rule is the 0.10 difference above. |
| Small vias | 0.1 or 0.15 mm holes, and 0.2 or 0.25 mm holes under 0.45 mm diameter, "will cost more". |

**The strip against those figures:**
- vias 0.3/0.5: diameter 0.20 over the hole, ring 0.10;
- via hole to hole ≥ 0.45;
- via hole to NPTH ≥ 0.56;
- via hole to other-net track ≥ 0.29;
- every figure is within the board's own stricter rules (hole clearance 0.25, hole to hole 0.25).

**Order:** select "0.3mm/(0.4/0.45mm)" and leave the 4-wire Kelvin test off. Re-quoted 2026-11-09 at €18.62, unchanged.

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
- both sides of the strip, re-checked 2026-11-09 after D63: 25 via flashes Ø0.5 on each copper layer and none on either mask (tented); drill report 25 × Ø0.300 PTH, NPTH unchanged;
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

## Quotes (jlcpcb.com quote page, 2026-11-09, not signed in, no coupons)
JLC offers only EUR and USD for Switzerland. CHF is indicative at the ECB reference rate of 2026-11-05: 0.9180 CHF/EUR.

| Line | Options as above | Build time | Price |
|---|---|---|---|
| Main board | 4 L, 90 × 55, 5 pcs, 1.6, ENIG 1U", FR4 TG135, 1/0.5 oz, plugged | 3–4 days | €22.56 = €7.16 + ENIG €15.40 (≈ CHF 20.71) |
| Mic strip | 2 L, 28 × 6, 5 pcs, 0.8, ENIG 1U", tented, deburring (page default for small boards), via class 0.3mm/(0.4/0.45mm), 4-wire test off | 3 days | €18.62 = €3.58 + ENIG €14.86 + deburring €0.18 (≈ CHF 17.09). Re-quoted 2026-11-09 ≈ 17:05 after D63, unchanged; the vias are now in the free class. |
| Touch board rev D | 2 L, 90 × 44, 5 pcs, 1.6, ENIG 1U", tented | 3 days | €18.80 = €3.58 + ENIG €15.22 (≈ CHF 17.26) |
| Stencil | non-framework, top, custom 190 × 190, 0.12, two PCBs, electropolished, 1:1 | 1–2 days | €10.91 = €6.46 + electropolishing €4.45 (≈ CHF 10.02) |
| **Total, our part of the order** | | | **€70.89 (≈ CHF 65.08)**, shipping excluded |

- **Shipping:**
  - The page shows DHL Express at €21.06 (2–4 business days) for each line on its own; the stencil at 190 × 190 also shows €21.06, at 0.33 kg.
  - The parcel is shared with the Spooky Manor boards, so the real figure appears at checkout.
  - Weights: main 0.21 kg, strip 0.14 kg, touch 0.19 kg, stencil 0.33 kg.
- **Desktop prices:** the page shows lower "Desktop Price" figures (from €20.77 / €16.83 / €17.01 / €9.12) for orders placed through JLC's desktop app.
