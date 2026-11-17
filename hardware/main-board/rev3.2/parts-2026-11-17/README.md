# Main board rev 3.2 — C101, C102, C122, C123: 22 µF 35 V becomes 4.7 µF 50 V (2026-11-17)

Brief `claude/brief-electronics-22uF-2026-11-17.md` (D192). Daniel left the choice to the electronics session on
2026-11-17 ("make the best selection for the project").

**The same evening C12 took the same part (D202): section 6.** Sections 1 to 5 are the record of the morning and stand
as written, except the first point of section 5.

**The copper did not change. The uploads of 2026-11-16 stand:** main board
`fab/main-board-rev3.2-jlc-2026-11-16.zip` (sha256 `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd`)
and stencil `stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip`
(sha256 `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2`).

## 1. The change
| | Until 2026-11-17 | Since 2026-11-17 |
|---|---|---|
| Part | Cal-Chip GMC21X5R226M35NT | **TDK C2012X7R1H475K125AC** |
| Value | 22 µF 35 V X5R, ±20 % | **4.7 µF 50 V X7R, ±10 %** |
| DigiKey | `4713-GMC21X5R226M35NTCT-ND`, 6 pieces, CHF 17.52 | `445-C2012X7R1H475K125ACCT-ND`, 10 pieces, CHF 3.01 |
| DigiKey stock on 2026-11-17 | 0, on backorder, 30-week lead time | 112'666 |
| Land | 0805, pads 1.0 × 1.45 | the same |
| Size (maker) | 2.0 × 1.25, thickness 1.25 ± 0.20 | 2.0 × 1.25, thickness 1.25 +0.25/−0.15 |
| Height at most | 1.45 | 1.50 |
| Temperature range | −55 to 85 °C | −55 to 125 °C |
| Schematic value | `22u 35V` | `4.7u 50V` |

Places: C101 and C102 beside C100, C122 and C123 beside C121; each between the amplifier's supply (after fuse F5) and
ground. They are the only bulk on the amplifier's side of F5; C5 (120 µF) is on the 20 V side of it.

## 2. Why this part is sound
**What TI asks** (TAS5756M datasheet SLAS988B, revised August 2015; read on ti.com on 2026-11-17):
- §9.1.1, p. 60: a capacitor's voltage rating is at least 1.45 times the voltage across it. At 20 V that is 29 V; at
  the board's over-voltage trip of 24.06 V it is 34.9 V. A 50 V part meets both.
- Table 22, p. 64: C101, C102, C122, C123 = 22 µF, 0805, ceramic X5R, ±20 %, rated above 1.45 × PVDD.
- No minimum capacitance is given anywhere, and no figure under bias. §10.1.2 (p. 83) refers to the evaluation board;
  §11.1.2 (p. 84) wants the small bypass capacitors as close to the supply pins as possible (C100, C121: not changed).
- TI's own evaluation board (SLAU583, parts list on p. 13–14) fits TDK C2012X5R1V226M125AC, 22 µF 35 V X5R 0805.

**What is left at 20 V** (TDK's product pages, "DC Bias Characteristic", nominal capacitance; read on
product.tdk.com on 2026-11-17; TDK calls the data reference only, not guaranteed):

| TDK part | Land | At 16 V | At 25 V | At 20 V, between the two points |
|---|---|---|---|---|
| C2012X5R1V226M125AC, 22 µF 35 V X5R (on TI's board) | 0805 | 2.32 µF | 1.46 µF | about 1.9 µF |
| **C2012X7R1H475K125AC, 4.7 µF 50 V X7R (chosen)** | 0805 | 2.37 µF | 1.41 µF | about 1.9 µF |
| C2012X5R1H106K125AC, 10 µF 50 V X5R | 0805 | 2.86 µF | 1.58 µF | about 2.2 µF |
| C2012X5R1V156M125AC, 15 µF 35 V X5R | 0805 | 1.71 µF | 1.07 µF | about 1.4 µF |
| C2012X5R2A475K125AC, 4.7 µF 100 V X5R | 0805 | 2.22 µF | 1.34 µF | about 1.8 µF |
| C2012X6S1H475K125AC, 4.7 µF 50 V X6S | 0805 | 1.71 µF | 0.96 µF | about 1.3 µF |
| C2012X5R1V685K125AC, 6.8 µF 35 V X5R | 0805 | 0.86 µF | 0.51 µF | about 0.7 µF |
| C3216X5R1V156M160AC, 15 µF 35 V X5R | 1206 | 2.88 µF | 1.72 µF | about 2.3 µF |

- TDK gives no point at 20 V. The last column is read between the 16 V and 25 V points (a straight line and a
  power-law fit give 1.94 and 1.84 µF for the 22 µF part, 1.95 and 1.83 µF for the chosen part).
- So the four capacitors together hold about 7.7 µF at 20 V with either part, not the 88 µF of the nominal values.
- Cal-Chip publishes no DC-bias data (GMC series datasheet, revision May '25, read 2026-11-17). The figure for the
  22 µF part is therefore TDK's, for the part TI itself fitted.

**Not taken** (DigiKey's filter, read 2026-11-17 in Daniel's Chrome):
- 22 µF, 0805, 35 V or more: four parts listed, three at 0 (Cal-Chip, TDK ×2) and one obsolete; none at 50 V or more.
- Cal-Chip GMC21X5R106K50NT, 10 µF 50 V X5R 0805 (58'548 in stock, 10 for CHF 9.65): no curve from its maker.
- Cal-Chip GMC21X5R156M35NT, 15 µF 35 V X5R 0805 (7'592 in stock): no curve; TDK's part of that rating is below the 22 µF part at 20 V.
- TI's own TDK part from Farnell Schweiz (4'926 in stock, sold in fives at CHF 0.526): a sixth order, against DigiKey first.
- Waiting for the TDK part at DigiKey: 24-week lead time.
- A larger land (1206: TDK 15 µF 35 V; 1210: Taiyo Yuden GMK325BJ226MM-P, 22 µF 35 V, 2.70 high): a 1206 at the same
  centres puts its supply pad onto a ground via at C102 and C123 and leaves 0.37 and 0.42 between pads of opposite
  nets within the pairs. It would reopen the fab set, the stencil and both JLC lines.

## 3. What was changed
| File | Change |
|---|---|
| `amplifier.kicad_sch` | C101, C102, C122, C123: value, maker, maker's part number, DigiKey number, specification; a note under the six supply capacitors |
| `io.kicad_sch` | J10, J11: maker, part number and DigiKey number of the header the parts list chose (Sullins PRPC004SAAN-RC, D183) |
| all five `.kicad_sch` | title block: date 2026-11-17 and a fourth line naming the two part changes. Revision stays 3.2 |
| `main-board.kicad_pcb` | the value text of the four parts on the fabrication layer (`22u 35V` → `4.7u 50V`). Nothing else |
| `../stencil/stencil-main-touch.kicad_pcb` | the same four value texts, so that the stencil's source stays in step |
| `main-board-schematic.pdf` | exported again |
| `main-board-rev3.2-assembly.pdf`, `-names.png`, `-values.png` | made again: the four values; the header reads "parts as of 2026-11-17"; the voltage is shown on the five 0805 parts that read 4.7 µF; J10 and J11 name their part |
| `erc-report.txt`, `drc-report.txt` | the checks of 2026-11-17 |
| `NOTES.md` §1 and §4, `README.md` | the part and its reason; the warning about the two 4.7 µF parts |
| `gen/main_board.py`, `gen/bom_fields_main.json` | the generator's values, so that it gives the same schematic |
| `gen/assembly_rev32.py` | the three drawing changes above |
| `gen/fab_same.sh` | new: exports a set afresh and compares it with an uploaded zip |
| `../notes/digikey-bom.md`, `.csv`, `../notes/bom-2026-11-17.md`, `.csv` | the DigiKey line and the parts list |

**Not changed:** copper, pads, holes, outline, silkscreen, soldermask, paste; the board's title block and the text
`REV 3.2 2026-11-16` on the back; `MAIN_env.md` (it allows 3.0 for every part not listed), the STEP files and the
plug envelopes.

## 4. Checks (KiCad 9.0.9, 2026-11-17)
- **Schematic check:** 0 errors, 0 warnings (`erc.txt`).
- **Board check with the schematic comparison:** 0 errors, 0 open connections, 0 differences to the schematic, the 2
  known warnings (J6 and J2 differ from their library footprints) (`drc.txt`).
- **The uploads are still this board's** (`export-compare-2026-11-17.txt`, made by `gen/fab_same.sh`):
  - a fresh export of the main board gives the 12 files of the zip in JLC's cart; apart from the lines that carry
    the time of the export, 0 lines differ;
  - a fresh export of the stencil gives its 3 files; 0 lines differ.
- **Parts list:** `../notes/bom-2026-11-17.md`: 46 DigiKey numbers on the boards, all in the list with the stated
  need; 116 parts fitted, as before.
- **Not run again:** the 41 site rules. They test parts, pads, outline, holes and heights; none changed beyond the
  0.05 of height above.

## 5. Two things to know at the bench
1. **Two 0805 parts read 4.7 µF: only until the evening of 2026-11-17.** That morning they were this one (50 V) and
   C12 (Samsung CL21B475KOFNNNE, 16 V, on the 3.3 V regulator), and the 16 V part must not go on the amplifier's 20 V
   supply. Since D202, C12 is this part too (section 6). The warning is gone from the drawing, `README.md` and the
   parts list.
2. **The inrush figure in `NOTES.md` §1** (385 µF, 0.39 A) was worked out before this change. The nominal capacitance
   behind the protection chip is now 69 µF lower. The 385 µF is not itemised there, so the figure is not
   recalculated; less capacitance means a lower inrush.

## 6. C12 takes the same part (2026-11-17, evening; D202)
Brief `claude/brief-electronics-c12-2026-11-17.md`. Daniel took option a at 19:30: one 4.7 µF part on the boards, so
the 16 V part cannot be placed on the amplifier's supply by mistake.

| | Until the evening of 2026-11-17 | Since |
|---|---|---|
| Part at C12 | Samsung CL21B475KOFNNNE, 4.7 µF 16 V X7R 0805 | **TDK C2012X7R1H475K125AC, 4.7 µF 50 V X7R 0805** |
| DigiKey | `1276-2873-1-ND`, 3 pieces, CHF 0.63 | on the line `445-C2012X7R1H475K125ACCT-ND`: 10 pieces for 5 places |
| Schematic value | `4.7u 16V` | `4.7u 50V` |
| Land, pads, place | 0805, pads 1.0 × 1.45 | the same |

**Why it is sound.** C12 is the output capacitor of the 3.3 V regulator U2, which needs 2.0 µF of effective
capacitance (SBVS186H 8.1.1; `NOTES.md` §3). TDK's DC-bias curve for this part (product.tdk.com, "DC Bias
Characteristic", nominal capacitance, read 2026-11-17 at about 19:58; TDK calls the data reference only):

| DC voltage | 0 | 1.25 | 2 | 2.5 | 3.15 | 4 | 5 | 6.3 | 8 | 10 | 12.5 | 16 | 25 | 35 | 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| µF | 4.70 | 4.76 | 4.73 | 4.69 | 4.62 | 4.50 | 4.34 | 4.11 | 3.78 | 3.40 | 2.94 | 2.37 | 1.41 | 0.91 | 0.58 |

- At 3.3 V, between the points at 3.15 V and 4 V: **about 4.6 µF.**
- Taking off the part's 10 % tolerance and X7R's 15 % over temperature leaves about 3.5 µF (4.6 × 0.90 × 0.85;
  ageing not counted). That is above 2.0 µF.
- The points at 16 V and 25 V are those read in the morning (section 2).

**What was changed**
| File | Change |
|---|---|
| `io.kicad_sch` | C12: value, maker, maker's part number, DigiKey number, specification, note; a four-line note under U2 |
| all five `.kicad_sch` | the title blocks' parts line now begins with C12. Date and revision as they were |
| `main-board.kicad_pcb`, `../stencil/stencil-main-touch.kicad_pcb` | C12's value text on the fabrication layer (`4.7u 16V` → `4.7u 50V`). Nothing else |
| `main-board-schematic.pdf` | exported again |
| `main-board-rev3.2-assembly.pdf`, `-values.png` | made again: the five places read `4.7u` with no voltage, the placing list has one line of 5, and the footnote on two parts is replaced. `-names.png` came out identical |
| `erc-report.txt`, `drc-report.txt` | the checks of the evening |
| `NOTES.md` §3 and its head, `README.md` | the part and its capacitance at 3.3 V; the bench warning dropped |
| `gen/main_board.py`, `gen/bom_fields_main.json`, `gen/assembly_rev32.py` | in step with the files |
| `fab/ORDER-SHEET.md`, `../stencil/fab/ORDER-SHEET.md` | one sentence each: the part changes do not touch the zip |
| `../notes/digikey-bom.md`, `.csv`; `../notes/bom-2026-11-17.md`, `.csv` | 55 lines; the TDK line with need 5, quantity 10; the Samsung line gone |

**Checks (KiCad 9.0.9, 2026-11-17, 20:00)**
- **Schematic check:** 0 errors, 0 warnings (`erc-c12.txt`).
- **Board check with the schematic comparison:** 0 errors, 0 open connections, 0 differences to the schematic, the 2
  known warnings (J6, J2) (`drc-c12.txt`).
- **The uploads are still this board's** (`export-compare-c12-2026-11-17.txt`): the main board's 12 files and the
  stencil's 3 files, 0 lines differ apart from the export's time. sha256 as at the top of this file.
- **Before any change,** the same three checks were run on `9cffbcf` in a fresh KiCad 9.0.9 install, with the same
  results as in section 4.
- **Parts list:** 45 DigiKey numbers on the boards, all in the list with the stated need; 116 parts fitted, as before.

**The DigiKey basket:** the Samsung line was removed on 2026-11-17 at 19:56 in Daniel's Chrome (`../../notes/digikey-bom.md`,
"DigiKey basket").
