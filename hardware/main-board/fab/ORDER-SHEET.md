# Main board rev 3.3 — JLC order sheet (fab issue 2026-11-21)

**Upload:** `main-board-rev3.3-jlc-2026-11-21.zip`
sha256 `26ff743470ad6834af4412218b2413478ce8ec22a962c775d0f4b1875617acdd`

- Bare board. No SMT assembly, so no BOM or placement file goes to JLC.
- **Price:** €30.08 on 2026-11-16 (7.25 + ENIG 15.58 + colour 7.25), build 3–4 days; the cart line of the rev 3.2 zip read €30.24 on 2026-11-21. Rev 3.3 has the same size, layers and options, so the price should not move; the cart shows it once the zip is uploaded.
- **What changed from rev 3.2 (2026-11-16):** PS1's row of 13 pins moved 3.0 toward the top edge to match Mean Well's side view (its body and box did not move); J6 pin 1 takes +3V3 ahead of F4 through one inner-layer track; the via in one of U100's paste windows is taken out; every silk line is 0.15 wide; the back reads `REV 3.3 2026-11-21`. Outline, holes other than PS1's, parts and options are unchanged.
- **The rev 3.2 zip in the cart must be replaced by this one.** It is kept in `superseded/` and must not be ordered.
- JLC's capability figures below were read on jlcpcb.com on **2026-11-16**; the soldermask figure for black on **2026-11-17**.
- The option names are the order page's own, read on 2026-11-16.

## What is in the zip (12 files)
| File | Layer |
|---|---|
| `main-board-rev3.3-F_Cu.gtl` | door-side copper: parts and signals |
| `main-board-rev3.3-In1_Cu.g1` | inner 1: ground |
| `main-board-rev3.3-In2_Cu.g2` | inner 2: +5 V, +20 V, amplifier supply |
| `main-board-rev3.3-B_Cu.gbl` | back copper: signals and ground |
| `main-board-rev3.3-F_Mask.gts`, `-B_Mask.gbs` | soldermask |
| `main-board-rev3.3-F_Silkscreen.gto`, `-B_Silkscreen.gbo` | silkscreen; the back reads `REV 3.3 2026-11-21` |
| `main-board-rev3.3-Edge_Cuts.gm1` | outline with the relief |
| `main-board-rev3.3-PTH.drl`, `-NPTH.drl` | plated and unplated holes (Excellon, mm) |
| `main-board-rev3.3-job.gbrjob` | job file with the stack-up |

No paste layer is in this zip. JLC's KiCad 9 guide asks for paste layers only on stencil or assembly orders; the paste goes to JLC in the stencil's own zip (`../../stencil/fab/ORDER-SHEET.md`).

## Order options
| Option | Choice | Note |
|---|---|---|
| Base material | FR-4 | the page of 2026-11-16 reads "FR-4 TG135" |
| Layers | **4** | |
| Dimensions | **87.0 × 57.9 mm** | the page reads it from the outline |
| Quantity | 5 | JLC's minimum on 2026-11-09; 1 needed |
| Delivery format | single PCB | |
| Thickness | **1.6 mm** | |
| PCB colour / silkscreen | **black** / white | chosen 2026-11-16 (green before). Black adds €7.25 on this board. The page's note on the colour: "Two more days than green solder mask" |
| Surface finish | **ENIG**, thickness "1U\"" | chosen 2026-11-08 |
| Outer copper | 1 oz | |
| Inner copper | 0.5 oz | JLC's default |
| Impedance control | no | the page of 2026-11-16 reads "No requirement" |
| Layer stack-up | "Specify Stackup": **Yes**, then **JLC04161H-7628** | the stack-up can be chosen only once "Specify Stackup" is set to "Yes". JLC's "No requirement" stack-up shows the same layer values; it is written into the board file and the job file |
| Via covering | **Plugged** | "Tented" is greyed out on 4-layer boards. See "What JLC's review may raise", item 2 |
| Via plating method | "Not Specified" | a row on the page of 2026-11-16; left as the page sets it |
| Min via hole size/diameter | "0.3mm/(0.4/0.45mm)" | the board has 0.2 mm holes in 0.45 mm vias; the page's note of 2026-11-09 says that costs nothing extra on multilayer boards. On 2026-11-09 a smaller class also switched a 4-wire test on; the page of 2026-11-16 has no such row. |
| Electrical test | **"Flying Probe Fully Test"** | the only test the page of 2026-11-16 offers; it has no "4-Wire Kelvin Test" row |
| Board outline tolerance | **regular, ±0.2 mm** | High precision (±0.1) is not wanted. |
| Mark on PCB | **"Remove Mark"** | standing choice |
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
JLC figures: https://jlcpcb.com/capabilities/pcb-capabilities, read 2026-11-16 (the page shows no revision date). The soldermask bridge was read again on 2026-11-17 for black: 1 oz copper, pad spacing 0.10 at least for green, red, yellow, blue and purple, **0.13 for black and white**.

| Item | This board | JLC |
|---|---|---|
| Track / space | 0.15 / 0.15 | 0.09 / 0.09 (multilayer) |
| Vias (243), hole/diameter | 131 × 0.3/0.6, 87 × 0.2/0.45, 25 × 0.4/0.8 | minimum 0.15/0.25; 0.2 or 0.25 holes cost more below 0.45 diameter |
| Thermal holes in the two chips' centre pads | U100: 39 × 0.2 in 0.45; U1: 15 × 0.3 in 0.6. They are part of the footprints: inside the centre pad on the door side, under soldermask on the back. | as vias |
| Soldermask between a via's hole and a pad that takes paste | 0.20 or more at all 243 vias | soldermask bridge 0.13 (black) |
| Component hole ring | 0.35 or more, except J2 | multilayer 1 oz: 0.20 recommended, 0.15 minimum |
| J2 (USB4085) ring | 0.15: 16 contacts of Ø0.4 in Ø0.7 pads, GCT's own land pattern | at JLC's minimum |
| Plated slots | 4 at J2, 0.6 wide (0.6 × 1.4 and 0.6 × 2.1) | 0.35 minimum (multilayer) |
| Unplated holes | 4 × Ø3.2 (M3 mounting) | Ø0.50 minimum |
| Copper to the routed edge | 0.30; **0.50 at the relief** | 0.2 |
| Outline | routed; two inner corners of radius 1.0 at the relief | regular ±0.2. Inner corners come out near R 0.5 with a 1 mm cutter (JLC blog, 2026-07-28). |
| Soldermask web between two pads | 0.15 smallest (J2: 0.153 between its contacts' pads) | 0.13 (black): 0.02 to spare |
| Silkscreen | text 1.0 high, 0.15 stroke; every line 0.15 wide | text 1.0, line 0.15 |

Holes in all (`drill-report.txt`): plated 382 = 126 × 0.20, 146 × 0.30, 41 × 0.40, 4 slots 0.60 wide, 2 × 0.80, 8 × 0.95, 40 × 1.00, 13 × 1.15, 2 × 1.30; unplated 4 × 3.20.

## What JLC's review may raise
1. **J2's ring of 0.15.** It is the maker's land pattern and sits exactly at JLC's stated minimum. Answer: keep as drawn.
2. **Vias that cannot be ink-plugged.** JLC's table gives three conditions for a plugged via: no soldermask opening on either side, 0.35 or more from other openings, and "no wider than 0.5 mm diameter".
   - **The 0.35:** on this board 60 of the 243 vias have their hole closer than that to a pad's opening.
   - **The 0.5:** the table does not say whether it means the hole or the via's copper. JLC's via-covering article (dated 2026-11-10) says plugged holes of 0.5 or less. By the hole, every via passes (0.2, 0.3, 0.4). By the copper, only the 87 vias of 0.45 would; the 131 of 0.6 and the 25 of 0.8 would not. Rev 2.1 had the same via sizes.
   - **What it means:** in the files every via is covered by soldermask on both faces. For a via it cannot ink-plug, JLC's article names epoxy or copper filling as the alternative; it does not say what happens on a plain order. Nothing on the board depends on a via being filled: each has at least 0.20 of soldermask between its hole and the nearest pad that takes paste. Answer to a query: leave them covered by soldermask, no filling.
3. **Seven vias left in bare copper on purpose,** at test pads (TP2, TP7, TP9, TP15, TP17, TP19, TP20; the hole is 0.08 inside the pad's opening). Test pads take no paste. The one that lay in U100's centre pad was taken out on 2026-11-21. Two more vias sit closer than 0.20 to an opening without paste: 0.13 from TP3 and 0.18 from J3 pad 9.
4. **No paste files.** Expected for a bare board.

## Checks on this zip (2026-11-21)
`fab-check-2026-11-21.txt` (made by `../tools/fab_check.py`), all passed:
- every expected file is there, with the right layer function in its header;
- a round flash of the right diameter at each of the 243 vias on all four copper layers;
- no soldermask opening at any via, either face; 339 openings on the door side and 89 on the back, one per pad that needs one;
- outline 87.00 × 57.90 with 2 arcs;
- hole counts per diameter equal to the board's;
- job file: 4 layers, 1.6 mm, ENIG, the stack-up above;
- the copper pours stored in the board file are current (a refill changes none);
- a fresh export of the board gives the same 12 files as the zip, line for line apart from the export's time (`../tools/fab_same.sh`).

KiCad's own checks on the board: electrical rules 0 errors, 0 warnings; design rules 0 errors, 0 unconnected, 0 schematic mismatches, 3 warnings: J2 and J6 differ from their library footprints, as since rev 2.1, and C6, whose + mark is 0.1 smaller to stay clear of L1's outline with the wider silk. Render of the nine layers: `main-board-rev3.3-gerbers.png`.

How the set is made: `../tools/fab_export.sh ../main-board.kicad_pcb main-board-rev3.3 . 2026-11-21 F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts` (kicad-cli 9.0.9; settings in `../../notes/jlc-fab.md`).

## Earlier sets
- **Rev 3.2, fab issue 2026-11-16:** `superseded/main-board-rev3.2-jlc-2026-11-16.zip` (sha256 `fc458853…49bd`), with its check and render. Must not be ordered: its PS1 pin row does not match Mean Well's side view.
- The rev 2.1 set of 2026-11-08 (the 90 × 55 board) is superseded and must not be ordered. It is no longer in this folder; the history keeps it ([`rev2.1/fab/` at commit 45a38e4](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee/hardware/main-board/rev2.1/fab)).
