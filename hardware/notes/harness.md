# HA panel — harness list (block 3, part 3, 2026-11-09)

Every lead in the panel, with its cut length, both terminations and the wire it is made from. Cut lengths are the
enclosure's routed length + ≥ 50 slack (K20, architect log 2026-11-07), with the sensor leads from the enclosure chat's
V23b routing (model version 41; architect log 2026-11-09). Pin maps come from the KiCad boards on `docs`.

**No crimping** (H1 = a): every lead is made from pre-crimped parts. Contacts are moved between housings or cut off and
soldered.

## Leads

| # | Lead | Cond. | Main-board end | Other end | Cut (mm) | Made from | Notes |
|---|---|---|---|---|---|---|---|
| 1 | 20 V pigtail | 2 | **J1** XHP-2: 1 = +20 V (VIN_PIGTAIL), 2 = GND | 5807 output pads, soldered: X4-1 VOUT, X4-2 GND | ≈ 70 | 2 halves of ASXHSXH22K305 (22 AWG), 1 × XHP-2 | Mark the + conductor (all wires are black). |
| 2 | Speaker L | 2 | **J8** XHP-2: 1 = SPK_L_P (+), 2 = SPK_L_N (−) | Left DMA45-4 tabs, soldered (+ to the red tab) | ≈ 105 | 2 halves of ASXHSXH22K305, 1 × XHP-2 | Solder at the tabs before the box goes in. Mark +. |
| 3 | Speaker R | 2 | **J9** XHP-2: 1 = SPK_R_P (+), 2 = SPK_R_N (−) | Right DMA45-4 tabs, soldered | ≈ 105 | as #2 | as #2 |
| 4 | Radar | 4 | **J5** XHP-4: 1 = 5 V, 2 = GND, 3 = LD_TX (from the radar's TX), 4 = PI_TXD (to the radar's RX) | LD2410C pads, soldered: VCC, GND, TX, RX (OUT unused) | ≥ 125 | 4 halves of ASXHSXH22K305, 1 × XHP-4 | TX and RX cross here: J5.3 ← radar TX, J5.4 → radar RX. |
| 5 | Touch | 4 | **J6** XHP-4: 1 = 3V3_SENS, 2 = GND, 3 = SDA, 4 = SCL | Touch board rev D **J1** HOST pads, soldered (VCC, GND, SDA, SCL, labelled on the silk) | ≈ 105 | 4 halves of ASXHSXH22K305, 1 × XHP-4 | |
| 6 | BME680 | 4 | **J10 odd column** (pins 1-3-5-7 = 3V3, GND, SDA, SCL from the top), 1 × 4 Dupont housing on the 2 × 4 header | CJMCU-680 header, Dupont 1-pos housings as supplied: VCC, GND, SDA, SCL | **≥ 145** | 4 × Adafruit 266 F-F (152) | Contacts moved from their 1-pos housings into the 1 × 4 housing. Dress clear of the LCD-screw lane KO_K5_LR (2.53 in the model). |
| 7 | VEML6030 | 4 | **J10 even column** (pins 2-4-6-8, same order), 1 × 4 Dupont housing | VEML6030 board header, Dupont 1-pos housings | **≥ 165** | 4 × Adafruit 1949 F-F (305) | Plug in at step 13 with the cap held above. Tie the excess near J10. |
| 8 | GPIO plug A | 9 | **J3** wire pads, soldered (contact cut off) | Pi header pins 1–16, Daniel's 2 × 8 Dupont housing | 150 nominal (routed 49; ≥ 99) | 9 × Adafruit 266 F-F (152): about 140 once the contact is cut off (estimate) | Map: `../main-board/gpio-leads.md`. Red for 3V3, black for GND. |
| 9 | GPIO plug B | 4 | **J4** wire pads, soldered | Pi header pins 35–40, 2 × 3 Dupont housing | 150 nominal (routed 50; ≥ 100) | 4 × Adafruit 266 F-F (152) | as #8 |
| 10 | LCD power | 4 (2 used) | — | LCD connector → Pi plug A pins 2 (5 V) and 6 (GND) | **Daniel-extended, ≥ 205** | The LCD's own lead, extended by Daniel (D58) | SDA and SCL insulated (V22). |
| 11 | Mic L | 5 | — | Left strip wire pads ↔ ReSpeaker vacated mic pads, both soldered | ≥ 175 | JST A05SR05SR30K305B (305), both housings cut off | Cable order 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA. At the ReSpeaker: VDD → pad 1, CLK → 2, DATA → 3, GND → 4 (and 6), SEL → 5 (`../mic-strip/README.md`). Hot-melt over the strip pads; zip tie per decision 15. |
| 12 | Mic R | 5 | — | as #11 | ≥ 175 | as #11 | The ReSpeaker's own strap on pad 5 sets L/R: GND = left, VDD = right. |
| 13 | DSI | FPC | — | Pi 5 DSI (22-pin) ↔ LCD (15-pin) | 300 | Raspberry Pi SC1132 300 mm (2648-SC1132-ND) | Second cable is a spare. |
| 14 | Pi power | USB-C | **J2** USB4085 (door side) | Pi USB-C | 200 | 5 A C-to-C 0.2 m straight + 90° adapter (V11 option 1; order list) | Adapter orientation: V25. |
| 15 | ReSpeaker USB | USB | — | Pi USB-A ↔ ReSpeaker USB-C | 250 | Angled A-to-C 0.25 m (order list) | Check enumeration on arrival (V21). |
| 16 | Inlet | USB-C | — | Wall PD source ↔ 5807 receptacle | — | Daniel's 5 A e-marked cable (owned) | 5807 jumpers: cut **5V** and **1A** (20 V, 3.25 A request; E0 envelopes). |

Bench only (not in the panel): ReSpeaker speaker out → DMA45-4 with Adafruit 261 (JST PH 2-pin); LD2410C → Pi UART
with Adafruit 1949 leads (bench 1.5).

## J10 — plugged (D59, Daniel 2026-11-09)
- **Main board:** a 2 × 4 male pin header, 2.54 mm, fitted in J10's through-holes (front side, soldered from the back
  with the other through-hole parts). The footprint was already a 2 × 4 header pattern, so the board doesn't change. The
  value is now "2x04 male header 2.54 (D59)".
- **Leads:** each sensor lead ends in its own 1 × 4 Dupont housing on one column. The two columns carry the same four
  nets row by row (3V3_SENS, GND, SDA, SCL from the top), so either lead fits either column. Only the orientation
  matters: mark pin 1 (3V3) on each housing.
- **Height:** header + housing about 16.5 above the board (E0 estimate). This is inside the 30 mm front envelope and
  sits between the NID (1.1) and J5's plug (1.8), from the KiCad courtyards. It isn't modelled.
- **Slack:** the housing replaces about 14 mm of wire, so the same cut lengths leave that much more slack (enclosure
  chat, 2026-11-09).
- **Parts not in the DigiKey basket,** which is frozen (D51, D56):
  - one 2 × 4 male header (or two 1 × 4 pieces from a strip);
  - two 1 × 4 Dupont female housings.

  They come from order prep (AliExpress) or Daniel's stock: order list rev 5.

## Wire budget against the BOM
| Part | DigiKey PN | Bought | Used | Spare |
|---|---|---|---|---|
| JST ASXHSXH22K305, XH both ends, 22 AWG, 305, black (cut in half → 2 conductors) | 455-3241-ND | 10 wires | 7 (14 conductors: J1 2, J5 4, J6 4, J8 2, J9 2) | 3 |
| JST XHP-2 | 455-2266-ND | 4 | 3 (J1, J8, J9) | 1 |
| JST XHP-4 | 455-2267-ND | 3 | 2 (J5, J6) | 1 |
| Adafruit 266, F-F 152, 40 wires | 1528-1379-ND | 40 | 17 (GPIO 13, BME680 4) | 23 |
| Adafruit 1949, F-F 305, 20 wires | 1528-1960-ND | 20 | 4 (VEML6030) + 4 (bench 1.5) | 12 |
| JST A05SR05SR30K305B, 5-way 305 | 455-3712-ND | 4 | 2 | 2 |
| Raspberry Pi SC1132 DSI 300 | 2648-SC1132-ND | 2 | 1 | 1 |

Each half of an XH wire is about 150 including its socket, which covers every XH cut length here (≤ 125).

## Sources
- Cut lengths: architect log 2026-11-07 K20; architect log 2026-11-09 §1 (V23b: BME680 routed 90.5 → ≥ 145, VEML6030
  routed 114.7 → ≥ 165); enclosure update `claude/brief-architect-update-2026-11-09.md` §3 and §6.1 (J10 plugged:
  height, slack, the column map).
- GPIO routed lengths 49 / 50: `claude/report-model-audit-2026-11-05.md` §8 leads table.
- Pin maps: `hardware/main-board/main-board.kicad_pcb` (J1, J5, J6, J8, J9, J10 pad nets), `gpio-leads.md`,
  `hardware/mic-strip/README.md`, `hardware/touch-board/README.md`.
- 5807 output pads and jumpers: `claude/E0-envelopes-2026-11-01.md` (PD_env, Eagle parse).
- Decisions: D52 (screws), D56 (AT42QT1070 from stock), D58 (LCD lead), D59 (J10 plugged), H1 = a (no crimping),
  decision 15 (mic strain relief), V21, V22, V25.
