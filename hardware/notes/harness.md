# HA panel — harness list (block 3, part 3, 2026-11-09; two points corrected 2026-11-17)

> **The current harness list is `claude/harness-list-2026-11-14.md`, in the project** (fifth issue: model version 62, main
> board rev 3.1). This file was written for main board rev 2.1 and is kept as the record of 2026-11-09.
>
> **Corrected here on 2026-11-17** (architect log 2026-11-17 §6; Daniel's answer 2a):
> 1. the Pi signal wires, the BME680 lead and the VEML6030 lead are cut from Adafruit 3141 (D188);
> 2. J10 and J11 are two 1 × 4 headers.
>
> **Not corrected. For these the list of 2026-11-14 and the parts list (`claude/parts-list-2026-11-16.md` §8) apply:**
> - **every cut length.** The list of 2026-11-14 gives the free lengths: 20 V 90, speakers 98 and 90, radar 75, touch 87,
>   BME680 93, VEML6030 116, Pi signal wires 70, display's power lead 180, microphone leads 230;
> - **the Pi end of leads 8 and 9:** three housings (1 × 3, 2 × 5, 2 × 3), as in `../main-board/gpio-leads.md`, not a
>   2 × 8 and a 2 × 3;
> - **lead 10:** the extension is two Adafruit 3141 wires spliced onto the display's own lead (D194);
> - **lead 13:** the display's ribbon is Daniel's own Waveshare 200 ribbon (D133). The Raspberry Pi SC1132 left the
>   DigiKey basket on 2026-11-16 (D184);
> - **lead 15:** the ReSpeaker's USB lead is the ADT-Link flat cable, 25 cm (D129);
> - the lead numbers, which the list of 2026-11-14 counts differently.

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
| 6 | BME680 | 4 | **J10**, a 1 × 4 header (pins 1 to 4 = 3V3_SENS, GND, SDA, SCL), 1 × 4 Dupont housing | CJMCU-680: VCC, GND, SDA, SCL, soldered (the wire's other contact cut off) | **≥ 145** (superseded: 93 free) | 4 × Adafruit 3141 F-F (152, 28 AWG) (D188) | The contacts come bare, with no housing; they go straight into the 1 × 4 housing. Dress clear of the LCD-screw lane KO_K5_LR (2.53 in the model). |
| 7 | VEML6030 | 4 | **J11**, a 1 × 4 header (pins 1 to 4 = 3V3_SENS, GND, SDA, SCL), 1 × 4 Dupont housing | VEML6030 board: soldered (the wire's other contact cut off) | **≥ 165** (superseded: 116 free) | 4 × Adafruit 3141 F-F (152, 28 AWG) (D188) | A 152 wire covers the 116 and leaves 36 for the joint (D194). It does not cover the 165 of 2026-11-09. |
| 8 | GPIO plug A | 9 | **J3** wire pads, soldered (contact cut off) | Pi header pins 1–16, Daniel's 2 × 8 Dupont housing | 150 nominal (routed 49; ≥ 99) (superseded: 70 free) | 9 × Adafruit 3141 F-F (152, 28 AWG) (D188) | Map: `../main-board/gpio-leads.md`. Red for 3V3, black for GND. |
| 9 | GPIO plug B | 4 | **J4** wire pads, soldered | Pi header pins 35–40, 2 × 3 Dupont housing | 150 nominal (routed 50; ≥ 100) (superseded: 70 free) | 4 × Adafruit 3141 F-F (152, 28 AWG) (D188) | as #8 |
| 10 | LCD power | 4 (2 used) | — | LCD connector → Pi plug A pins 2 (5 V) and 6 (GND) | **Daniel-extended, ≥ 205** | The LCD's own lead, extended by Daniel (D58) | SDA and SCL insulated (V22). |
| 11 | Mic L | 5 | — | Left strip wire pads ↔ ReSpeaker vacated mic pads, both soldered | ≥ 175 | JST A05SR05SR30K305B (305), both housings cut off | Cable order 1 VDD, 2 GND, 3 CLK, 4 SEL, 5 DATA. At the ReSpeaker: VDD → pad 1, CLK → 2, DATA → 3, GND → 4 (and 6), SEL → 5 (`../mic-strip/README.md`). Hot-melt over the strip pads; zip tie per decision 15. |
| 12 | Mic R | 5 | — | as #11 | ≥ 175 | as #11 | The ReSpeaker's own strap on pad 5 sets L/R: GND = left, VDD = right. |
| 13 | DSI | FPC | — | Pi 5 DSI (22-pin) ↔ LCD (15-pin) | 300 | Raspberry Pi SC1132 300 mm (2648-SC1132-ND) | Second cable is a spare. |
| 14 | Pi power | USB-C | **J2** USB4085 (door side) | Pi USB-C | 200 | 5 A C-to-C 0.2 m straight + 90° adapter (V11 option 1; order list) | Adapter orientation: V25. |
| 15 | ReSpeaker USB | USB | — | Pi USB-A ↔ ReSpeaker USB-C | 250 | Angled A-to-C 0.25 m (order list) | Check enumeration on arrival (V21). |
| 16 | Inlet | USB-C | — | Wall PD source ↔ 5807 receptacle | — | Daniel's 5 A e-marked cable (owned) | 5807 jumpers: cut **5V** and **1A** (20 V, 3.25 A request; E0 envelopes). |

Bench only (not in the panel): ReSpeaker speaker out → DMA45-4 with Adafruit 261 (JST PH 2-pin); LD2410C → Pi UART
with Adafruit 1949 leads (bench 1.5).

## J10 and J11 — plugged (D59, Daniel 2026-11-09; two headers since main board rev 3)
- **Main board:** two 1 × 4 male pin headers, 2.54 mm, straight: **J10 for the BME680, J11 for the VEML6030.** They sit
  on the side with the parts (the door side) and are soldered from the back with the other through-hole parts.
  - Part: Sullins PRPC004SAAN-RC, DigiKey `35-PRPC004SAAN-RC-ND` (D183, D187); 2 needed, 10 in the basket.
  - Rev 2.1 had one 2 × 4 header, J10, with a column for each sensor.
- **Leads:** each sensor lead ends in its own 1 × 4 Dupont housing. Both headers carry the same four nets, pin 1 to 4:
  3V3_SENS, GND, SDA, SCL. A lead on the wrong header still works; a housing turned round does not. Mark pin 1 (3V3)
  on each housing.
- **Height:** `../main-board/MAIN_env.md` has the header at 8.54 above the board and about 16.5 with the housing (an
  estimate, made before the part was chosen).
- **Bought and not bought:**
  - the two headers are a DigiKey line since 2026-11-16;
  - the two 1 × 4 Dupont female housings come from Daniel's stock.

## Wire budget against the BOM
| Part | DigiKey PN | Bought | Used | Spare |
|---|---|---|---|---|
| JST ASXHSXH22K305, XH both ends, 22 AWG, 305, black (cut in half → 2 conductors) | 455-3241-ND | 10 wires | 7 (14 conductors: J1 2, J5 4, J6 4, J8 2, J9 2) | 3 |
| JST XHP-2 | 455-2266-ND | 4 | 3 (J1, J8, J9) | 1 |
| JST XHP-4 | 455-2267-ND | 3 | 2 (J5, J6) | 1 |
| Adafruit 3141, F-F 152, 28 AWG, 40 wires (D188; in place of Adafruit 266, `1528-1379-ND`, out of stock) | 1528-2176-ND | 40 | 23 (Pi signal wires 13, BME680 4, VEML6030 4, display lead's extension 2) | 17 |
| Adafruit 1949, F-F 305, 20 wires | 1528-1960-ND | 20 | 4 (bench 1.5, the LD2410C test). No longer used for the VEML6030 lead | 16 |
| JST A05SR05SR30K305B, 5-way 305 | 455-3712-ND | 4 | 2 | 2 |
| Raspberry Pi SC1132 DSI 300 | 2648-SC1132-ND | 0 | — | taken out of the basket on 2026-11-16 (D184) |

Each half of an XH wire is about 150 including its socket, which covers every XH cut length here (≤ 125).

**Adafruit 3141** (Adafruit's product page and DigiKey, read 2026-11-17): a strip of 40 wires, four of each of ten
colours, 28 AWG (7 strands), a little over 150 long (DigiKey: 152.4), a bare socket contact on each end and no housing.

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
- Corrections of 2026-11-17: architect log 2026-11-17 (D183, D184, D187, D188, D194; §6); `claude/parts-list-2026-11-16.md`
  §2 and §8; `claude/harness-list-2026-11-14.md`; `../main-board/NOTES.md` §3 (J10, J11).
