# Main board rev 3.2 — JLC order sheet (fab issue 2026-11-16)

**Upload:** `main-board-rev3.2-jlc-2026-11-16.zip`
sha256 `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd`

- Bare board. No SMT assembly, so no BOM or placement file goes to JLC.
- **Not uploaded, not quoted** (Daniel, 2026-11-16). The parts-list session takes the quote from this sheet.
- JLC's capability figures below were read on jlcpcb.com on **2026-11-16**. The order page itself was not opened today: the option names are the ones read on 2026-11-09 (`../../notes/jlc-fab.md`).

## What is in the zip (12 files)
| File | Layer |
|---|---|
| `main-board-rev3.2-F_Cu.gtl` | door-side copper: parts and signals |
| `main-board-rev3.2-In1_Cu.g1` | inner 1: ground |
| `main-board-rev3.2-In2_Cu.g2` | inner 2: +5 V, +20 V, amplifier supply |
| `main-board-rev3.2-B_Cu.gbl` | back copper: signals and ground |
| `main-board-rev3.2-F_Mask.gts`, `-B_Mask.gbs` | soldermask |
| `main-board-rev3.2-F_Silkscreen.gto`, `-B_Silkscreen.gbo` | silkscreen; the back reads `REV 3.2 2026-11-16` |
| `main-board-rev3.2-Edge_Cuts.gm1` | outline with the relief |
| `main-board-rev3.2-PTH.drl`, `-NPTH.drl` | plated and unplated holes (Excellon, mm) |
| `main-board-rev3.2-job.gbrjob` | job file with the stack-up |

No paste layer is in this zip. JLC's KiCad 9 guide asks for paste layers only on stencil or assembly orders; the paste goes to JLC in the stencil's own zip (`../../stencil/fab/ORDER-SHEET.md`).

## Order options
| Option | Choice | Note |
|---|---|---|
| Base material | FR-4 | |
| Layers | **4** | |
| Dimensions | **87.0 × 57.9 mm** | the page reads it from the outline |
| Quantity | 5 | JLC's minimum on 2026-11-09; 1 needed |
| Delivery format | single PCB | |
| Thickness | **1.6 mm** | |
| Mask / silkscreen | green / white | |
| Surface finish | **ENIG** | Daniel, 2026-11-08 |
| Outer copper | 1 oz | |
| Inner copper | 0.5 oz | JLC's default |
| Impedance control | no | |
| Layer stack-up | **JLC04161H-7628** | the same build as "No requirement"; it is written into the board file and the job file |
| Via covering | **Plugged** | see "What JLC's review may raise", item 2 |
| Min via hole size/diameter | "0.3mm/(0.4/0.45mm)" | the board has 0.2 mm holes in 0.45 mm vias; the page's note of 2026-11-09 says that costs nothing extra on multilayer boards. If the page picks a smaller class by itself, it also switches the 4-wire test on. |
| 4-Wire Kelvin Test | **No** | |
| Board outline tolerance | **regular, ±0.2 mm** | D151 item 6. High precision (±0.1) is not wanted. |
| Mark on PCB | **"Remove Mark"** | Daniel's standing decision |
| Gold fingers, castellated holes, edge plating | no | |
| "Stencil: order together with PCB" on this line | **off** | the stencil is its own line |
| PCB remark | none | |

## Stack-up (JLC04161H-7628, JLC's impedance page, read 2026-11-16)
| Layer | Material | Thickness, mm |
|---|---|---|
| door-side copper | 1 oz | 0.035 |
| prepreg | 7628, εr 4.4 | 0.2104 |
| inner 1 copper (ground) | 0.5 oz | 0.0152 |
| core | εr 4.6 | 1.065 |
| inner 2 copper (supplies) | 0.5 oz | 0.0152 |
| prepreg | 7628, εr 4.4 | 0.2104 |
| back copper | 1 oz | 0.035 |

Sum 1.586 mm with copper; JLC states ±10 % on the finished thickness for boards of 1.0 mm and more.

## The files against JLC's limits
JLC figures: https://jlcpcb.com/capabilities/pcb-capabilities, read 2026-11-16 (the page shows no revision date).

| Item | This board | JLC |
|---|---|---|
| Track / space | 0.15 / 0.15 | 0.09 / 0.09 (multilayer) |
| Vias (244) | 132 × 0.3/0.6, 87 × 0.2/0.45, 25 × 0.4/0.8 | minimum 0.15/0.25; 0.2 or 0.25 holes cost more below 0.45 diameter |
| Thermal holes in the two chips' centre pads | U100: 39 × 0.2 in 0.45; U1: 15 × 0.3 in 0.6. They are part of the footprints: inside the centre pad on the door side, under soldermask on the back. | as vias |
| Soldermask between a via's hole and a pad that takes paste | 0.20 or more at all 244 vias (`../rev3.2/fab-2026-11-16/via-check.txt`) | soldermask bridge 0.10 (green) |
| Component hole ring | 0.35 or more, except J2 | multilayer 1 oz: 0.20 recommended, 0.15 minimum |
| J2 (USB4085) ring | 0.15: 16 contacts of Ø0.4 in Ø0.7 pads, GCT's own land pattern | at JLC's minimum |
| Plated slots | 4 at J2, 0.6 wide (0.6 × 1.4 and 0.6 × 2.1) | 0.35 minimum (multilayer) |
| Unplated holes | 4 × Ø3.2 (M3 mounting) | Ø0.50 minimum |
| Copper to the routed edge | 0.30; **0.50 at the relief** | 0.2 |
| Outline | routed; two inner corners of radius 1.0 at the relief | regular ±0.2. Inner corners come out near R 0.5 with a 1 mm cutter (JLC blog, 2026-07-28). |
| Soldermask web between two pads | 0.15 smallest (J2) | 0.10 (green) |
| Silkscreen | text 1.0 high, 0.15 stroke; library outlines 0.12 wide | text 1.0, line 0.15: the 0.12 outlines may print thin |

Holes in all (`drill-report.txt`): plated 383 = 126 × 0.20, 147 × 0.30, 41 × 0.40, 4 slots 0.60 wide, 2 × 0.80, 8 × 0.95, 40 × 1.00, 13 × 1.15, 2 × 1.30; unplated 4 × 3.20.

## What JLC's review may raise
1. **J2's ring of 0.15.** It is the maker's land pattern and sits exactly at JLC's stated minimum. Answer: keep as drawn.
2. **Vias that cannot be ink-plugged.** JLC plugs a via only if its hole is 0.35 or more from any soldermask opening. On this board 61 of the 244 vias are closer than that (`../rev3.2/fab-2026-11-16/plug-check-result.txt`). In the files they are covered by soldermask on both faces; what JLC does with a via it cannot plug is not stated on its pages. Nothing on the board depends on these 61 being filled: each has at least 0.20 of soldermask between its hole and the nearest pad that takes paste.
3. **Eight vias left in bare copper on purpose:** seven at test pads (TP2, TP7, TP9, TP15, TP17, TP19, TP20; the hole is 0.08 to 0.09 inside the pad's opening) and one in U100's centre pad. Test pads take no paste; U100's centre pad already has 39 thermal holes. Two more vias sit closer than 0.20 to an opening without paste: 0.13 from TP3 and 0.18 from J3 pad 9.
4. **No paste files.** Expected for a bare board.

## Checks on this zip (2026-11-16)
`fab-check-2026-11-16.txt` (made by `../gen/fab_check.py`), all passed:
- every expected file is there, with the right layer function in its header;
- a round flash of the right diameter at each of the 244 vias on all four copper layers;
- no soldermask opening at any via, either face; 339 openings on the door side and 89 on the back, one per pad that needs one;
- outline 87.00 × 57.90 with 2 arcs;
- hole counts per diameter equal to the board's;
- job file: 4 layers, 1.6 mm, ENIG, the stack-up above;
- the copper pours stored in the board file are current (a refill changes none).

KiCad's own checks on the board: electrical rules 0 errors, 0 warnings; design rules 0 errors, 0 unconnected, 0 schematic mismatches, 2 warnings (J2 and J6 differ from their library footprints, as since rev 2.1). Render of the nine layers: `main-board-rev3.2-gerbers.png`.

How the set is made: `../gen/fab_export.sh ../main-board.kicad_pcb main-board-rev3.2 . 2026-11-16 F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts` (kicad-cli 9.0.9; settings in `../../notes/jlc-fab.md`).

## Earlier sets
The rev 2.1 upload of 2026-11-08 (the 90 × 55 board) is kept in `../rev2.1/fab/main-board-jlc-2026-11-08.zip`. It is superseded by this set and must not be ordered.
