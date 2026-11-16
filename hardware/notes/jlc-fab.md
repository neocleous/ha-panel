# JLC orders: the four uploads, JLC's figures and the export settings (rev 2026-11-16)

Three boards and one stencil go to JLC. **Bare boards only:** no SMT assembly, so no BOM or placement files go to JLC. Daniel assembles the boards himself.

**Rev 2026-11-16 (fab issue of main board rev 3.2):** new main-board set and new stencil; the strip and touch-board sets of 2026-11-09 are confirmed current. Each upload now has its own order sheet next to its zip. **Nothing was uploaded and no quote was taken on 2026-11-16** (Daniel). JLC's capability pages were read on 2026-11-16; the order page was not opened, so the option names in the order sheets are those read on 2026-11-09.

| Upload | Board | Order sheet | sha256 of the zip |
|---|---|---|---|
| `hardware/main-board/fab/main-board-rev3.2-jlc-2026-11-16.zip` | main board rev 3.2, 87.0 × 57.9, 4 layers | `hardware/main-board/fab/ORDER-SHEET.md` | `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd` |
| `hardware/mic-strip/fab/mic-strip-jlc-2026-11-09.zip` | mic strip, 28 × 6, 2 layers; one design, used twice | `hardware/mic-strip/fab/ORDER-SHEET.md` | `f405cc567fab336cf9e0fb4b0da1def971ca79bae3d6d8b02ea9bce7e5584564` |
| `hardware/touch-board/fab/touch-board-jlc-2026-11-09.zip` | touch board rev D, 90 × 44, 2 layers | `hardware/touch-board/fab/ORDER-SHEET.md` | `2d62d7eca9126be672a78bb0a46d35bbd1463b2dc3d9a8c736272d2777056a34` |
| `hardware/stencil/fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` | **stencil line only:** main board door side + touch board back | `hardware/stencil/fab/ORDER-SHEET.md` | `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2` |

Superseded, kept for the record, **not to be ordered:** `hardware/main-board/rev2.1/fab/main-board-jlc-2026-11-08.zip` (rev 2.1, 90 × 55) and `hardware/stencil/fab/superseded/stencil-main-touch-jlc-2026-11-09.zip` (its paste pattern).

The unzipped files sit next to each zip in `fab/gerbers/`; hole counts are in `fab/drill-report.txt`; the check of each set is `fab/fab-check-2026-11-16.txt` (stencil: `fab/stencil-check-2026-11-16.txt`).

## The orders at a glance
| | Main board rev 3.2 | Mic strip | Touch board rev D | Stencil |
|---|---|---|---|---|
| Layers | 4 | 2 | 2 | — |
| Size, mm | 87.0 × 57.9 | 28 × 6 | 90 × 44 | custom 190 × 190 |
| Thickness, mm | 1.6 | 0.8 | 1.6 | 0.12 |
| Finish | ENIG | ENIG | ENIG | electropolished |
| Vias | plugged | tented | tented | — |
| Quantity | 5 (1 needed) | 5 (2 needed) | 5 (1 needed) | 1 |
| Other | stack-up JLC04161H-7628; outline regular ±0.2; "Remove Mark" | "Remove Mark" | "Remove Mark" | top only; two PCBs on one stencil; apertures 1:1 |

Every option, with its reason, is in the order sheets.

## JLC's figures, read 2026-11-16
| Figure | Value | Page |
|---|---|---|
| Copper to a routed edge | 0.2 mm or more | capabilities |
| Outline tolerance | ±0.2 regular; ±0.1 "high precision", which needs a board of at least 50 × 50 and three tooling holes of 1.5 or more | capabilities |
| Plugged vias | three conditions: no soldermask opening on either side; 0.35 or more from other soldermask openings such as pads; "no wider than 0.5 mm diameter". The table does not say hole or copper; the via-covering article says plugged holes of 0.5 or less | capabilities; via-covering article |
| Vias that cannot be plugged | the alternative JLC names is epoxy or copper filling (free on boards of 6 layers and more) | via-covering article |
| Smallest via | hole 0.15, diameter 0.25; a 0.2 or 0.25 hole in less than 0.45 diameter costs more | capabilities |
| Ring of a component hole, multilayer, 1 oz | 0.20 recommended, 0.15 minimum | capabilities |
| Plated slot | 0.35 wide minimum (multilayer); 0.5 on 2 layers | capabilities |
| Unplated hole | Ø0.50 minimum | capabilities |
| Track / space | 0.09 / 0.09 multilayer; 0.10 / 0.10 on 1–2 layers | capabilities |
| Silkscreen | line 0.15, text height 1.0 | capabilities |
| Soldermask bridge | 0.10 (green) | capabilities |
| Inner copper | 0.5 oz by default | capabilities |
| Finished thickness | ±10 % at 1.0 mm and more; ±0.1 below 1.0 | capabilities |
| Inner corner of a routed outline | not in the capabilities table; JLC's blog gives about R 0.5 with a 1 mm cutter | blog, 2026-07-28 |
| 4-layer stack-up JLC04161H-7628 | copper 0.035 / 0.0152 / 0.0152 / 0.035; prepreg 7628, 0.2104, εr 4.4; core 1.065, εr 4.6. The page's "No requirement" stack-up shows the same layer values; the page does not call it the default in words. | impedance |
| Stencil thickness | 0.10, 0.12, 0.15, 0.18, 0.20 | stencil |
| Stencil electropolishing | named for ICs of 0.5 pitch and below, and BGA | stencil |
| Several designs on one stencil | supported; JLC may adjust the layout; leave a remark | stencil |
| Stencil apertures | optimised by JLC's engineers by default; a remark makes them follow the paste layer 1:1 | stencil |
| Stencil custom size | within 650 × 580 (without frame) | stencil |
| Stencil aperture | larger than 0.08 mm | stencil |
| Files from KiCad 9 | Protel extensions, X2, netlist attributes, 4.6 mm; drill Excellon, alternate oval mode, absolute, mm, decimal, plated and unplated separate; **paste layers only for stencil or assembly orders** | KiCad 9 article |

Pages are listed under "Sources".

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
JLC's KiCad 9 guide, applied with kicad-cli 9.0.9 by `hardware/main-board/gen/fab_export.sh` (boards) and `hardware/main-board/gen/stencil_export.sh` (stencil):
- **Gerbers:**
  - Protel extensions, X2 attributes and netlist attributes on;
  - coordinate format 4.6 mm;
  - values excluded;
  - soldermask subtracted from silkscreen (not in the guide; it keeps silk off pads).
- **Drill:**
  - Excellon, PTH and NPTH in separate files;
  - absolute origin, millimetres, decimal zeros;
  - oval holes in alternate drill mode (G85 slots).
- **Paste layers:** not in the main board's set of 2026-11-16, following the guide. The strip and touch-board sets of 2026-11-09 contain theirs; JLC ignores them on a bare-board order without the stencil switch.
- **File names** carry board and revision (`main-board-rev3.2-…`, `stencil-main-rev3.2-touch-revD-…`), so two sets cannot be mixed.

**Check of every set (2026-11-16):** `hardware/main-board/gen/fab_check.py` reads the exported files and compares them with the KiCad board: files and layer functions, a flash at every via on every copper layer, no soldermask opening at a via, paste counts, outline extent and arcs, hole counts per diameter, the job file's stack-up, and that the stored pours are current. The stencil is checked aperture by aperture against both boards' paste files by `hardware/main-board/gen/stencil_check.py`.

## Panelisation
- **Not required.** JLC's minimum board size is 3 × 3 mm, and the strip is 28 × 6.
- JLC says panelisation is "recommended" for small boards. Five single strips are the simplest order.
- If the order page asks for a panel anyway, use "Panel by JLCPCB" without edge rails.
- At 0.8 mm the strip is above JLC's 0.6 mm manual-review threshold.

## Sources
Read 2026-11-16:
- JLC PCB capabilities — https://jlcpcb.com/capabilities/pcb-capabilities (the page shows no revision date)
- JLC stack-ups — https://jlcpcb.com/impedance
- JLC stencil capabilities — https://jlcpcb.com/capabilities/pcb-stencil-manufacturing
- JLC "How to generate Gerber and Drill files in KiCad 9" — https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9 (page dated 2026-11-10)
- JLC "PCB via covering" — https://jlcpcb.com/help/article/pcb-via-covering (page dated 2026-11-10)
- JLC blog on rounded corners — https://jlcpcb.com/blog/rounded-corners-pcb-design (2026-07-28)

Read earlier:
- JLC order and quote pages, 2026-11-09 (option names, prices below)
- GCT USB4085 drawing rev B (2023-02-28), recommended PCB layout — https://gct.co/files/drawings/usb4085.pdf (read 2026-11-07)

## Quotes of 2026-11-09 (jlcpcb.com quote page, not signed in, no coupons)
**These are the figures for the rev 2.1 main board (90 × 55) and the first stencil. No quote was taken for the 2026-11-16 sets;** the parts-list session takes it from the order sheets. The strip and touch-board lines are for the same files as today.

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
