# The 22 µF substitute and the hardware records: reply to the Architect (2026-11-17)

From the electronics session (`claude/brief-electronics-22uF-2026-11-17.md`). Repo `neocleous/ha-panel`, branch `docs`, folder `hardware/`.

**Nothing was ordered. No basket was changed. Nothing on `main`. Nothing was uploaded to JLC.**

## 1. Answer
1. **C101, C102, C122 and C123 are now TDK C2012X7R1H475K125AC: 4.7 µF 50 V X7R, 0805.** DigiKey `445-C2012X7R1H475K125ACCT-ND`, 112'666 in stock on 2026-11-17.
2. **The board's copper did not change. The JLC uploads of 2026-11-16 stand, the main board's and the stencil's.** A fresh export of each equals its zip; the sha256 of both zips are unchanged.
3. **Why 4.7 µF does the job of 22 µF:** at 20 V a 22 µF 35 V 0805 keeps about 1.9 µF, and this part keeps about 1.9 µF too (TDK's DC-bias data, read 2026-11-17). TI's datasheet gives a voltage rule and no minimum capacitance; 50 V meets the rule with more room than 35 V.
4. **Daniel's choice:** he left it to the session on 2026-11-17 at 09:26 ("Make the best selection for the project"). The session took option 1a and told him before any file changed.
5. **The records of the log's §6 are corrected.**
6. **Still to do: the DigiKey basket change** (section 5). Daniel's Chrome could not be reached when the session came to it.

## 2. Paths and commits (branch `docs`, on top of `1b7c87d`)
| Commit | Content |
|---|---|
| `622f286eef33cd12a21dd48aa1aa06dd7b3f3cc2` | the part change: schematic, value texts, checks, assembly drawing, `NOTES.md`, `README.md`, `digikey-bom`, `bom-2026-11-17` |
| `9f5bb2a49317d23941614e3108fa91708599d288` | the records: `harness.md`, `gpio-leads.md`, the four order sheets, `jlc-fab.md` |
| `b5a793d1956a35cb171c0add8fec38a1a65ecafd` | the basket's state in `digikey-bom.md`; this reply |

| What | Path under `hardware/` |
|---|---|
| **Record of the change:** old → new, sources, checks | `main-board/rev3.2/parts-2026-11-17/README.md` |
| the export comparison, the two check reports | `main-board/rev3.2/parts-2026-11-17/export-compare-2026-11-17.txt`, `erc.txt`, `drc.txt` |
| **Main board upload, unchanged** | `main-board/fab/main-board-rev3.2-jlc-2026-11-16.zip`, sha256 `fc4588531ea277c1fc3e9009db38fae190042080e065443b0a663f34fa7449bd` |
| **Stencil upload, unchanged** | `stencil/fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip`, sha256 `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2` |
| Schematic | `main-board/amplifier.kicad_sch`, `io.kicad_sch` (and the title blocks of all five sheets); `main-board-schematic.pdf` |
| Board and stencil source: four value texts only | `main-board/main-board.kicad_pcb`, `stencil/stencil-main-touch.kicad_pcb` |
| Assembly drawing | `main-board/main-board-rev3.2-assembly.pdf` (4 pages), `…-assembly-names.png`, `…-assembly-values.png` |
| The part and its reason; the warning at the bench | `main-board/NOTES.md` §1, §3, §4; `main-board/README.md` |
| **Parts list** | `notes/bom-2026-11-17.md`, `.csv` (it supersedes `bom-2026-11-16`) |
| **DigiKey lines** | `notes/digikey-bom.md`, `.csv`: 56 lines, CHF 165.25 excl. VAT |
| Records of §6 | `notes/harness.md`, `main-board/gpio-leads.md`, the four `fab/ORDER-SHEET.md`, `notes/jlc-fab.md` |
| New tool | `main-board/gen/fab_same.sh`: exports a set afresh and compares it with an uploaded zip |

## 3. What changed, old → new
| | Until 2026-11-17 | Since 2026-11-17 |
|---|---|---|
| Part at C101, C102, C122, C123 | Cal-Chip GMC21X5R226M35NT, 22 µF 35 V X5R ±20 % | **TDK C2012X7R1H475K125AC, 4.7 µF 50 V X7R ±10 %** |
| DigiKey line | `4713-GMC21X5R226M35NTCT-ND`, 6 pieces, CHF 17.52; 0 in stock, 30-week lead time | `445-C2012X7R1H475K125ACCT-ND`, 10 pieces, CHF 3.01; 112'666 in stock |
| Land, pads, places | 0805, pads 1.0 × 1.45 | the same |
| Height at most | 1.45 | 1.50 (`MAIN_env.md` allows 3.0 for parts it does not list) |
| Schematic value | `22u 35V` | `4.7u 50V` |
| The 56 DigiKey lines | CHF 179.76 excl. VAT | CHF 165.25, CHF 14.51 less |
| Copper, holes, outline, silkscreen, soldermask, paste | | unchanged |
| The board's title block and its back-face text | rev 3.2, 2026-11-16 | unchanged |
| J10, J11 in the schematic | no part named | Sullins PRPC004SAAN-RC, `35-PRPC004SAAN-RC-ND` (D183, D187) |

**One thing new at the bench.** Two 0805 parts now read 4.7 µF: this one (50 V) and C12 (Samsung, 16 V, on the 3.3 V output). The 16 V part must not go on the amplifier's supply. The drawing and the placing list give the voltage at each of the five places. Section 7, decision 2, would remove the second part.

## 4. Why the part is sound
**TI** (TAS5756M datasheet SLAS988B, revised August 2015, read on ti.com 2026-11-17):
- §9.1.1, p. 60: a capacitor is rated at least 1.45 times the voltage across it: 29 V at 20 V, 34.9 V at the board's 24.06 V over-voltage trip.
- Table 22, p. 64: 22 µF, 0805, X5R, ±20 %, rated above 1.45 × the supply, at these four places.
- No minimum capacitance and no figure under bias anywhere. TI's own evaluation board (SLAU583, p. 13–14) fits TDK C2012X5R1V226M125AC, 22 µF 35 V X5R 0805.

**TDK** (product pages, "DC Bias Characteristic", read 2026-11-17; TDK calls the data reference only):

| TDK part | At 16 V | At 25 V | At 20 V, between the two points |
|---|---|---|---|
| C2012X5R1V226M125AC, 22 µF 35 V X5R, the part on TI's board | 2.32 µF | 1.46 µF | about 1.9 µF |
| **C2012X7R1H475K125AC, 4.7 µF 50 V X7R, chosen** | 2.37 µF | 1.41 µF | about 1.9 µF |
| C2012X5R1H106K125AC, 10 µF 50 V X5R | 2.86 µF | 1.58 µF | about 2.2 µF |
| C2012X5R1V156M125AC, 15 µF 35 V X5R | 1.71 µF | 1.07 µF | about 1.4 µF |

- **Cal-Chip publishes no DC-bias data** (GMC series datasheet, revision May '25). The figure for "the part in the design" is therefore TDK's, for the part of the same rating that TI fitted.
- TDK gives no point at 20 V; the last column lies between its 16 V and 25 V points.

**The options not taken** (DigiKey, read 2026-11-17 in Daniel's Chrome; all on the brief's list):
| Option | Why not | What it would reopen |
|---|---|---|
| Cal-Chip GMC21X5R106K50NT, 10 µF 50 V X5R 0805; 58'548 in stock; 10 for CHF 9.65 | its maker gives no curve; TDK's part of that rating keeps about 2.2 µF, 0.3 µF more | nothing |
| Cal-Chip GMC21X5R156M35NT, 15 µF 35 V X5R 0805; 7'592 in stock | no curve; TDK's part of that rating keeps less than the 22 µF part | nothing |
| A larger land: 1206 (TDK C3216X5R1V156M160AC, 15 µF 35 V, about 2.3 µF at 20 V) or 1210 (Taiyo Yuden GMK325BJ226MM-P, 22 µF 35 V, 2.70 high) | a 1206 at the same centres puts its supply pad on a ground via at C102 and C123 | the main board's fab set, the stencil, both lines in JLC's cart, the assembly drawing, the site rules |
| TI's own TDK part from Farnell Schweiz (order code 2528773; 4'926 in stock; sold in fives, CHF 0.526) | a sixth supplier, against DigiKey first | nothing on the board; one more order |
| Waiting for the TDK part at DigiKey | 24-week lead time | nothing; the build waits |

## 5. The DigiKey basket: one line to change, not yet changed
- **Out:** `4713-GMC21X5R226M35NTCT-ND`, 6 pieces.
- **In:** `445-C2012X7R1H475K125ACCT-ND`, 10 pieces, customer reference "HA-PANEL". 10 is the price break: CHF 0.07 more than 6.
- **State:** not made. Daniel's Chrome answered for reading earlier in the session and was no longer connected when the session came to the basket. The session changed nothing in the basket. Section 7, decision 1.

## 6. The records of the log's §6
| Record | What was corrected |
|---|---|
| `notes/harness.md` | Per Daniel's answer 2a: the Pi signal wires, the BME680 lead and the VEML6030 lead from Adafruit 3141 (D188); J10 and J11 as two 1 × 4 headers; a head that points to `claude/harness-list-2026-11-14.md` and names what is not corrected (every cut length, the Pi-end housings, the display lead's extension, the ribbon, the ReSpeaker's USB lead, the lead numbers) |
| `main-board/gpio-leads.md` | YBM becomes Adafruit 3141. Red = 3V3, black = GND, any other colour = signal |
| `notes/digikey-bom.md`, `.csv` | Rebuilt to the parts list §2: SC1132 and 266 out; the headers and 3141 in; "HA-PANEL"; the three shared lines; every price, quantity and stock figure as read on 2026-11-16; the capacitor line of 2026-11-17 |
| The four `ORDER-SHEET.md` | Black (D191); the stencil remark as entered (196 characters); "Flying Probe Fully Test" in place of the 4-wire row; "Specify Stackup", "Via Plating Method", "Tented" greyed out, OSP → ENIG 1U", "Select by Customer", the "Multiple PCBs" dialog, "No Fiducial"; each sheet's state is now "uploaded, in JLC's cart" with its line name and price |
| `notes/jlc-fab.md` | The state of 2026-11-17; the soldermask figure for black |

**Read today for these records:**
- **JLC, soldermask bridge** (jlcpcb.com/capabilities/pcb-capabilities, 2026-11-17): at 1 oz copper the smallest pad spacing is 0.10 for green, red, yellow, blue and purple, and **0.13 for black and white**. The sheets quoted the 0.10 of green.
  - All three boards pass in black. Smallest web between two pads: main board 0.15 (J2), mic strip 0.17, touch board 0.65.
  - Between a via's hole and a pasted pad the main board has 0.20 or more.
- **Adafruit 3141** (adafruit.com/product/3141 and DigiKey, 2026-11-17): a strip of 40, four wires of each of ten colours, 28 AWG, 152.4 long, **a bare socket contact on each end and no housing**.

## 7. Open points
**Decisions for Daniel:**
1. **Who changes the DigiKey basket line?**
   - a) The electronics session, in his Chrome, once it is reachable again. It then reads the whole basket back against `digikey-bom.md`. (Recommended; it is what the session chose under his answer of 09:26.)
   - b) Daniel himself: delete the 22 µF line, add 10 × `445-C2012X7R1H475K125ACCT-ND` with the reference "HA-PANEL".
2. **C12 on the same TDK part?** Optional.
   - a) Yes: C12 becomes the TDK 4.7 µF 50 V part too. Only one 0805 part then reads 4.7 µF, so the two cannot be mixed up. The 10 pieces cover it (5 needed). The Samsung line `1276-2873-1-ND` (3 pieces, CHF 0.63) leaves the basket. The schematic, the parts list and the drawing are issued again; the zips do not change. At 3.3 V the TDK part keeps about 4.6 µF (TDK), against the 2.0 µF the regulator needs (`NOTES.md` §3).
   - b) No: leave C12 as it is. The drawing and the bags carry the voltage.

**For the harness list's next issue and the instructions (5c):**
3. **Ground wires from the 3141 strip:** it has four wires of each colour. The leads cut from it need six ground wires (three Pi signal grounds, BME680, VEML6030, the display lead's extension) and four supply wires. `gpio-leads.md` takes three black for the Pi; the next issue should name the colours for the rest.
4. **The 3141's bare contacts in Daniel's Dupont housings:** assumed to fit; check on arrival.
5. **The J10/J11 header's height:** `MAIN_env.md` still has the KiCad model's 8.54 for a "generic part". DigiKey's page for the Sullins part gives a contact 11.39 long over all with a 3.05 tail and 2.50 of insulation, so about 8.34 above the board. `MAIN_env.md` was not changed.

**Not done, and why:**
6. **The 41 site rules were not run again.** No part, pad, hole, outline or height band changed; the part is 0.05 higher at most.
7. **The inrush figure in `NOTES.md` §1** (385 µF, 0.39 A) was not recalculated. It is not itemised there. The nominal capacitance behind the protection chip is 69 µF lower, which lowers the inrush.
8. **Not updated:** `notes/bom/lines.py`, `choice.py` and `R.json` (the inputs of the list of 2026-11-08); `notes/pi-config.md` (it names the SC1132 cable once); the order lists (superseded, D196).
9. **Not read:** Murata GRM21BZ71H475KE15L (4.7 µF 50 V, 0805, 87'866 in stock at DigiKey) would be a second source; its curve was not read.

## 8. Checks (KiCad 9.0.9, 2026-11-17)
- **Schematic check:** 0 errors, 0 warnings.
- **Board check with the schematic comparison:** 0 errors, 0 open connections, 0 differences to the schematic; the 2 known warnings (J2, J6).
- **Uploads:** a fresh export of the main board gives the zip's 12 files, a fresh export of the stencil its 3 files; apart from the lines with the export's time, 0 lines differ. sha256 of both zips as in section 2.
- **Parts list:** 46 DigiKey numbers on the boards, all in the list with the stated need; 116 parts fitted, as before; 56 lines, CHF 165.25.
- **Soldermask webs in black:** computed from the three board files; none under 0.13.

## 9. Sources (all read 2026-11-17 unless noted)
- TI, TAS5756M datasheet SLAS988B (rev. B, August 2015), ti.com; TAS5756M evaluation board guide SLAU583.
- TDK product pages for the parts in section 4, product.tdk.com (in Daniel's Chrome).
- Cal-Chip GMC series datasheet, revision May '25, calchip.com.
- DigiKey CH: product pages and the ceramic-capacitor filter (in Daniel's Chrome, signed in); the pages for Adafruit 3141 and Sullins PRPC004SAAN-RC.
- Farnell Schweiz, order code 2528773.
- JLC: capabilities page (soldermask). The order page's names are the parts-list session's of 2026-11-16 (`claude/parts-list-2026-11-16.md` §1; `claude/report-parts-list-2026-11-16.md` §4).
- Adafruit, product 3141.
