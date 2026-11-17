# C12 on the TDK 4.7 µF 50 V part: reply to the Architect (2026-11-17, 20:10)

From the electronics session (`claude/brief-electronics-c12-2026-11-17.md`, D202). Repo `neocleous/ha-panel`, branch `docs`, folder `hardware/`.

**Nothing was ordered. Nothing on `main`. Nothing was uploaded to JLC. One line was removed from the DigiKey basket, on Daniel's "a" (section 4).**

## 1. Answer
1. **C12 is TDK C2012X7R1H475K125AC, 4.7 µF 50 V X7R 0805,** the part of C101, C102, C122 and C123. One 4.7 µF part is on the boards.
2. **Both JLC zips are unchanged.** A fresh export of each equals its zip; both sha256 are as before (section 2).
3. **The Samsung line is out of the DigiKey basket.** Chrome was connected and DigiKey was not ordered. Nothing else was touched; the basket was read back three times (section 4).
4. **`pi-config.md`** names Daniel's Waveshare 200 mm ribbon (D133).
5. **Checks clean** (section 5).

## 2. Commits and sha256
| Commit on `docs` (on top of `9cffbcf`) | Content |
|---|---|
| `5dd2f22727c5f1504e6ba8c0e0edc36b29f12453` | the whole change: schematic, value texts, checks, drawing, `NOTES.md`, `README.md`, parts list, `digikey-bom`, `pi-config.md` |
| the commit after it | this reply |

`main` is at `62ea4d8`, as before.

| Upload | sha256, unchanged |
|---|---|
| `main-board/fab/main-board-rev3.2-jlc-2026-11-16.zip` | `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd` |
| `stencil/fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` | `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2` |

## 3. What changed
| What | Path under `hardware/` | Change |
|---|---|---|
| Schematic | `main-board/io.kicad_sch` | C12: value `4.7u 50V`, TDK, C2012X7R1H475K125AC, `445-C2012X7R1H475K125ACCT-ND`; a four-line note under U2 |
| Title blocks | all five `.kicad_sch` | the parts line begins with C12; date 2026-11-17 and rev 3.2 as they were |
| Board file | `main-board/main-board.kicad_pcb` | C12's value text on the fabrication layer; one line of the file |
| Stencil's source | `stencil/stencil-main-touch.kicad_pcb` | the same value text, so the source stays in step |
| Schematic PDF | `main-board/main-board-schematic.pdf` | exported again |
| Assembly drawing, same file names | `main-board/main-board-rev3.2-assembly.pdf`, `-values.png` | the five places read `4.7u`; the placing list has one line of 5; the two-part warning is gone. `-names.png` came out identical |
| Notes | `main-board/NOTES.md` §3 | C12's part and its capacitance at 3.3 V |
| README | `main-board/README.md` | the bench warning dropped; C12 named with the morning's change |
| Order sheets | `main-board/fab/ORDER-SHEET.md`, `stencil/fab/ORDER-SHEET.md` | one sentence each: the part changes do not touch the zip |
| Record | `main-board/rev3.2/parts-2026-11-17/README.md` §6, `erc-c12.txt`, `drc-c12.txt`, `export-compare-c12-2026-11-17.txt` | the change and its checks |
| **Parts list** | `notes/bom-2026-11-17.md`, `.csv` | reissued under the same name: the TDK line with need 5, quantity 10; the Samsung line gone |
| **DigiKey lines** | `notes/digikey-bom.md`, `.csv` | 55 lines, CHF 164.62 excl. VAT; the basket change recorded |
| Pi configuration | `notes/pi-config.md`, setting 5 | the ribbon is Daniel's Waveshare 200 mm, 22-way to 15-way (D133), not the SC1132 cable |
| Generator | `main-board/gen/main_board.py`, `bom_fields_main.json`, `assembly_rev32.py` | in step with the files |

**C12 at 3.3 V.** TDK's DC-bias curve for the part gives 4.62 µF at 3.15 V and 4.50 µF at 4 V, so about 4.6 µF at 3.3 V (product.tdk.com, nominal capacitance, read 2026-11-17 at about 19:58 in Daniel's Chrome; TDK calls the data reference only). The regulator needs 2.0 µF (SBVS186H 8.1.1). Taking off the part's 10 % tolerance and X7R's 15 % over temperature leaves about 3.5 µF by arithmetic; ageing is not counted. The whole curve is in the record, §6.

## 4. The DigiKey basket
- **Before, read 2026-11-17 at about 19:55:** 76 lines, 56 "HA-PANEL", CHF 253.94 excl. VAT, 274.51 incl., no line ticked. This is the state of 11:30.
- **Removed at 19:56:** line 29, `1276-2873-1-ND`, Samsung CL21B475KOFNNNE, 3 pieces, CHF 0.63, "HA-PANEL". Only that line's box was ticked, then "Delete" and "OK".
- **Read back at 19:56 and, after a reload, at 19:57,** each time line by line against the reading before:
  - **75 lines; 55 of them "HA-PANEL"** (52 with that reference alone, and the three merged lines);
  - the 74 other lines are as before in part, quantity, reference, unit price, amount and availability, and in the same order;
  - every line "Immediate"; no line ticked;
  - HM-V2's 18 lines and the two lines without a reference are as before;
  - the TDK line is line 75: 10 pieces, CHF 3.01, "HA-PANEL".
- **The panel's 55 lines:** CHF 164.62 excl. VAT (the basket's own amounts added up); CHF 177.95 incl. 8.1 % VAT by arithmetic.
- **The whole basket, as it shows:** CHF 253.31 excl. VAT, VAT 20.52, **CHF 273.83**; shipping free.
- **Read a third time at 20:06,** with the list set against the basket: 75 lines, 55 "HA-PANEL", no line ticked, the same totals. The 55 numbers of `digikey-bom.csv` are the basket's 55 "HA-PANEL" lines, with the same quantities except on the three merged lines (35, 25 and 2 in the basket for 25, 10 and 1 in the list).
- The two price rises of 2026-11-16 are still not in the basket's prices (`F3141CT-ND` 2.82, `455-3241-ND` 0.598).
- The session's tabs are closed.

These are the figures the parts list (§2, §11) and the evening log (§4) give "by arithmetic". They are now the basket's own.

## 5. Checks (KiCad 9.0.9, 2026-11-17)
- **Before any change,** on `9cffbcf`, in a fresh install of KiCad 9.0.9: schematic check 0 and 0; board check 0 errors, 0 open, 0 differences, the 2 known warnings; both exports equal to their zips. The same as the morning's.
- **After the change, at 20:00, and again on a fresh clone of `5dd2f22`:**
  - schematic check: 0 errors, 0 warnings;
  - board check with the schematic comparison: 0 errors, 0 open connections, 0 differences, the 2 known warnings (J6, J2);
  - main board: the zip's 12 files, 0 lines differ apart from the export's time;
  - stencil: its 3 files, 0 lines differ.
- **Parts list:** 45 DigiKey numbers on the boards, all in the list with the stated need; 116 parts fitted, as before; 55 lines, 55 rows in the `.csv`, total CHF 164.62.
- **Drawing:** the placing list reads "5 × 4.7u 50V, 0805, TDK C2012X7R1H475K125AC: C12, C101, C102, C122, C123"; no "16V" is left in it.

## 6. Choices made under D150, and deviations
1. **A note under U2 on the 3.3 V sheet** says why a 50 V part sits on 3.3 V. C12's note field carries the 4.6 µF.
2. **The stencil's source file** got the same value text as the board file, as in the morning.
3. **`bom-2026-11-17` is reissued under its own name,** as its second issue. The morning's first issue is in the history at `622f286`.
4. **`NOTES.md` had no bench warning.** The warning stood in `README.md`, on the drawing and in the parts list's head; it is gone from all three. `README.md` now has one line in its place: one part, five places.
5. **The record** is a new §6 in `rev3.2/parts-2026-11-17/README.md`; its §1 to §5 stand as the morning's.
6. **The two order sheets** name C12 in their sentence on the part change.

## 7. Open points
**No decision is needed from Daniel.**

**For the Architect:**
1. **The parts list** (`claude/parts-list-2026-11-16.md` §2): the "to change" line is done, and the rows "once the C12 line leaves, by arithmetic" are the basket's own figures of 19:57. Not edited by this session.
2. **For 5c:** the bench note on two 4.7 µF parts is gone from the drawing and the README (log §5, item 1).

**Left as they were:**
3. `notes/bom/lines.py`, `choice.py` and `R.json` still name the Samsung part (inputs of the list of 2026-11-08; log §7, item 6).
4. `notes/harness.md`, row 13, still names the SC1132 cable in its table; its head says so (D197).
5. **The 41 site rules were not run again.** No part, pad, hole or outline changed. The TDK part is 1.50 high at most and `MAIN_env.md` allows 3.0; the Samsung part's own height was not read.

**Not verified:**
6. DigiKey's repricing at checkout (+0.67).
7. The TDK line's stock was not read again on its product page; the basket shows all 10 pieces "Immediate".
8. TDK calls its DC-bias data reference only.

## 8. Sources (read 2026-11-17)
- DigiKey CH, the basket, digikey.ch/ordering/shoppingcart, in Daniel's Chrome: about 19:55 to 19:57, and 20:06.
- TDK, product page of C2012X7R1H475K125AC, "DC Bias Characteristic": https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7R1H475K125AC, at about 19:58.
- TI TPS709 datasheet SBVS186H §8.1.1, as `NOTES.md` §3 cites it (read 2026-11-07).
