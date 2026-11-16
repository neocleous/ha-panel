# Main board rev 3.2, fab files, stencil and parts list: reply to the Architect (2026-11-16)

From the electronics session (`claude/brief-electronics-fab-files-rev3-2-2026-11-16.md`). Repo `neocleous/ha-panel`, branch `docs`, folder `hardware/`. Board frame as before, seen from the door: **u** to the right, **v** up, mm.

**Nothing was uploaded to JLC. No quote, no basket, no order. Nothing on `main`.**

## 1. Answer
1. **The fab sets exist for all three boards, and the stencil.** Two are new (main board rev 3.2, stencil), two are the sets of 2026-11-09, confirmed current (mic strip, touch board rev D). Each has an order sheet beside its zip.
2. **The main board changed in copper only.** No part, pad, hole, height or outline moved: the enclosure's files stand (`main-board-rev3.2.step`, `main-board-rev3.1-plug-envelopes.step`, `MAIN_env.md`).
3. **One finding went beyond the brief:** 40 vias stood in or against pads that take solder paste. They were moved (39) or taken out (1). Four of the moves are longer than a millimetre. Daniel was told at the preflight and has not objected; it is decision 1 of the closing report.
4. **The parts list: no DigiKey line changes.** One part changed that never was a DigiKey line: the sensor connector is two 1 × 4 pin headers since rev 3.

## 2. Paths and commits (branch `docs`)
| Commit | Content |
|---|---|
| `525343b0cbd99caf90037206ab8b1ce563af6c6a` | main board rev 3.2, fab issue: the board file, its record, assembly drawing, README and NOTES |
| `2da9dbcab83cb49ce7baaf2b16273d7f152b918e` | the fab sets, the stencil, the four order sheets, `hardware/notes/jlc-fab.md` |
| `a1fc8e5eaf8cb01883bbeae5845eb93e0ced6acb` | the parts list and its difference to the DigiKey lines |
| the commit after it | this reply; JLC's plugged-via wording corrected in three files (section 6, item 2) |

| What | Path under `hardware/` |
|---|---|
| **Main board upload** | `main-board/fab/main-board-rev3.2-jlc-2026-11-16.zip` — sha256 `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd` |
| its order sheet, check, render | `main-board/fab/ORDER-SHEET.md`, `fab-check-2026-11-16.txt`, `main-board-rev3.2-gerbers.png`, `drill-report.txt`, `gerbers/` |
| **Stencil upload** | `stencil/fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` — sha256 `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2` |
| its order sheet, check, picture | `stencil/fab/ORDER-SHEET.md`, `stencil-check-2026-11-16.txt`, `../stencil-preview.png`, `stencil/README.md` |
| **Mic strip upload** (unchanged) | `mic-strip/fab/mic-strip-jlc-2026-11-09.zip` — sha256 `f405cc567fab336cf9e0fb4b0da1def971ca79bae3d6d8b02ea9bce7e5584564`; `mic-strip/fab/ORDER-SHEET.md`, `fab-check-2026-11-16.txt` |
| **Touch board upload** (unchanged) | `touch-board/fab/touch-board-jlc-2026-11-09.zip` — sha256 `2d62d7eca9126be672a78bb0a46d35bbd1463b2dc3d9a8c736272d2777056a34`; `touch-board/fab/ORDER-SHEET.md`, `fab-check-2026-11-16.txt` |
| Index of the four uploads, JLC's figures of 2026-11-16, export settings | `notes/jlc-fab.md` |
| **Parts list and its difference** | `notes/bom-2026-11-16.md`, `notes/bom-2026-11-16.csv`; script `notes/bom/boards_bom.py` |
| The board as it goes to the fab | `main-board/main-board.kicad_pcb` (title block: rev 3.2, 2026-11-16; back-face text `REV 3.2 2026-11-16`) |
| The board as left on 2026-11-14 | `main-board/rev3.2/main-board-rev3.2-2026-11-14.kicad_pcb` |
| Record of the fab issue: every change, every check | `main-board/rev3.2/fab-2026-11-16/README.md` (via moves: `via-moves.md`, `via-moves.png`) |
| Assembly drawing, all 120 names and values | `main-board/main-board-rev3.2-assembly.pdf` (4 pages, A3), `…-assembly-names.png`, `…-assembly-values.png` |
| Assembly and bring-up text, test pads with their places | `main-board/README.md`; `main-board/NOTES.md` §5 and §7 |
| Superseded, kept, **not to be ordered** | `main-board/rev2.1/fab/main-board-jlc-2026-11-08.zip`; `stencil/fab/superseded/stencil-main-touch-jlc-2026-11-09.zip` |

## 3. What changed on the main board, old → new
| Item | Rev 3.2 of 2026-11-14 | Fab issue 2026-11-16 |
|---|---|---|
| Parts, pads, holes, outline, heights | — | **unchanged** (120 parts, none moved; outline 5017.48 mm²) |
| Vias | 245: 137 × 0.3/0.6, 83 × 0.2/0.45, 25 × 0.4/0.8 | **244: 132 × 0.3/0.6, 87 × 0.2/0.45, 25 × 0.4/0.8** |
| Vias with less than 0.20 of soldermask between hole and a pasted pad | 40 | **0** (smallest 0.20) |
| of the 40 | — | 39 moved, 5 of those also made 0.2/0.45 (at F4.1, R3.2, C3.2, R8.2, C10.2); 1 taken out (U1 pin 14) |
| the moves | — | 35 of 39 are 0.65 or less; the other four are 1.65 and 1.20 (U1's output), 1.53 (R4's ground), 1.29 (C2's ground) |
| new door-side tracks from pad to via | — | 0.40 to 1.35 long, 0.40 to 0.80 wide |
| Pours to the relief's edge, all four layers | 0.30 | **0.50** (0.30 left with JLC's cut 0.2 deeper) |
| Pours to every other edge | 0.30 | 0.30 |
| I²C clock track to the relief's edge | 0.38 | 0.38 (not moved) |
| Stack-up in the board file | none | **JLC04161H-7628** |
| Back-face text | `REV 3.2 2026-11-14` | `REV 3.2 2026-11-16` |
| Pi 5 V, board copper, calculated | 4.82 mΩ | 4.84 mΩ |
| 20 V, fuse → protection chip, calculated | 0.99 mΩ | 0.92 mΩ |
| Amplifier supply, F5 → C100–C102, calculated | 8.875 mΩ | 8.886 mΩ |

Left as they were: the vias at seven test pads (TP2, TP7, TP9, TP15, TP17, TP19, TP20) and one in the amplifier's centre pad. No paste goes on test pads; the centre pad has 39 thermal holes of its own.

## 4. The JLC order sheets
Every option with its reason is in the four `ORDER-SHEET.md` files. The orders at a glance:

| | Main board rev 3.2 | Mic strip | Touch board rev D | Stencil |
|---|---|---|---|---|
| Upload | `main-board-rev3.2-jlc-2026-11-16.zip` | `mic-strip-jlc-2026-11-09.zip` | `touch-board-jlc-2026-11-09.zip` | `stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` |
| Layers | 4 | 2 | 2 | — |
| Size, mm | 87.0 × 57.9 | 28 × 6 | 90 × 44 | custom 190 × 190; pattern 90.1 × 112.1 |
| Thickness, mm | 1.6 | 0.8 | 1.6 | 0.12 |
| Finish | ENIG | ENIG | ENIG | electropolished |
| Vias | plugged | tented | tented | — |
| Copper | 1 oz outer, 0.5 oz inner | 1 oz | 1 oz | — |
| Stack-up | JLC04161H-7628 | — | — | — |
| Outline tolerance | regular, ±0.2 | regular, ±0.2 | regular, ±0.2 | — |
| Mark | "Remove Mark" | "Remove Mark" | "Remove Mark" | — |
| Quantity | 5 (1 needed) | 5 (2 needed) | 5 (1 needed) | 1 |
| Other | 4-wire test off; stencil switch off | 4-wire test off; stencil switch off | stencil switch off | top only; two PCBs on one stencil; apertures 1:1; remark in the sheet |

- **The main board's zip has no paste layer.** JLC's KiCad 9 guide asks for paste layers only on stencil or assembly orders. The paste is in the stencil's own zip.
- **Option names** are those read on JLC's order page on 2026-11-09. The order page was not opened on 2026-11-16, because that is the quote step.
- **Quantities of 5** are JLC's minimum as read on 2026-11-09.

**JLC's figures, read on jlcpcb.com on 2026-11-16** (full table with pages: `notes/jlc-fab.md`):

| Figure | JLC | The boards |
|---|---|---|
| Copper to a routed edge | 0.2 or more | 0.30; 0.50 at the relief |
| Outline tolerance | ±0.2 regular; ±0.1 high precision, which needs a board of 50 × 50 or more and three tooling holes | regular |
| Plugged vias | no soldermask opening on either side; 0.35 or more from other openings; "no wider than 0.5 mm diameter" | section 6, item 2 |
| Smallest via | 0.15 hole, 0.25 diameter; 0.2 holes cost more below 0.45 diameter | 0.2/0.45 smallest |
| Component hole ring, multilayer 1 oz | 0.20 recommended, 0.15 minimum | 0.15 at J2 (the maker's land pattern), 0.35 or more elsewhere |
| Track / space | 0.09 / 0.09 multilayer; 0.10 / 0.10 on 1–2 layers | 0.15 / 0.15; strip 0.20 / 0.15; touch 0.25 / 0.15 |
| Soldermask bridge, green | 0.10 | 0.15 smallest (J2) |
| Silkscreen | line 0.15, text 1.0 | text 1.0 / 0.15; library outlines 0.12 (may print thin) |
| Stack-up JLC04161H-7628 | copper 0.035 / 0.0152 / 0.0152 / 0.035; prepreg 7628 0.2104; core 1.065 | as in the board file |
| Stencil | 0.12 is a standard thickness; electropolishing named for 0.5 pitch and below; several designs on one stencil allowed; apertures 1:1 by remark; custom size up to 650 × 580 | as ordered |

## 5. The parts list and its difference to the DigiKey lines
`notes/bom-2026-11-16.md` holds the three boards part by part (references, value, package, maker, maker's part number, per board, per set) and the set against each DigiKey line.

- **Set:** 1 main board, 2 mic strips, 1 touch board; 116 fitted parts (85 + 2 × 12 + 7). Nine places on the main board stay empty (R8, R9, R20–R25, R27).
- **DigiKey, order list rev 5: 55 lines, 45 of them board parts.**
  - **Changed quantities: none.** Every one of the 45 has the same need as on 2026-11-08.
  - **Added: none. Removed: none.**
  - **Spares rule (D50): met on all 45.**
- **Not DigiKey lines:**

| Part | Per set | State |
|---|---|---|
| Male pin header 1 × 4, 2.54, straight (J10, J11) | 2 | **changed at rev 3** (one 2 × 4 before). J10 and J11 are about 26 apart, so a 2 × 4 piece cannot serve both. Order list rev 5 line N2 and log 2026-11-16 morning §2 ("the 2 × 4 header … Daniel has") name the old part. |
| Tinned copper wire 1.0 (LK1) | 1 short piece | stock, as assumed on 2026-11-08 |
| AT42QT1070-SSUR (touch board U1) | 1 | Daniel's stock (D56) |

- **Why rev 3, 3.1 and 3.2 moved no line:** they changed the outline, the places of the parts, the copper and the mounting holes. Values and part numbers are those of rev 2.1, as the rev 3 reply said (§9).
- **No price or stock was looked up.** The DigiKey figures are those of 2026-11-08.

## 6. For the register
1. **Decision 1 for Daniel** (closing report §7): the vias moved out of the pasted pads stay (taken as agreed unless he says otherwise), or JLC's epoxy-filled vias instead, or back to the 2026-11-14 copper.
2. **JLC's wording on plugged vias** leaves two things open; neither changes the files:
   - 61 of the 244 vias have their hole closer than 0.35 to a pad's opening, so by JLC's table they are not ink-plugged;
   - the table says a plugged via must be "no wider than 0.5 mm diameter" without saying hole or copper. JLC's via-covering article (2026-11-10) puts the 0.5 on the hole. By the copper, only the 87 vias of 0.45 would qualify. Rev 2.1 had the same sizes.
   - Every via is covered by soldermask in the files, and none stands in a pasted pad any more. If JLC's review asks: leave them covered, no filling.
3. **The harness list is out of date on the sensor leads:** `hardware/notes/harness.md` (2026-11-09) still has both leads on one 2 × 4 header at J10. Since rev 3: BME680 on J10, VEML6030 on J11, pin 1 to 4 = 3V3_SENS, GND, SDA, SCL on both. For the harness list's next issue (log 2026-11-16 morning §6, item 9).
4. **Order list rev 5 §1 names three superseded uploads:** `main-board-jlc-2026-11-08.zip`, `mic-strip-jlc-2026-11-08.zip`, `stencil-main-touch-jlc-2026-11-09.zip`. The current four are in section 2.
5. **The quote of 2026-11-09 (€70.89)** was for the 90 × 55 board and the first stencil. The parts list takes a new one.
6. **Not regenerated:** the two 3D pictures (`main-board-3d-door-side.png`, `main-board-3d-back.png`) show rev 3.2 of 2026-11-14; the session had no 3D model library. Parts and silkscreen are the same; only vias and one text line differ. The schematic and its PDF did not change.
7. **Not run again:** the 41 site rules. They test parts, outline, holes, heights and through-hole joints; none changed.
