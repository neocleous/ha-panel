# E0 order lists — rev 4 (2026-11-03): bench-test order + full order

Block 5 of `claude/brief-sourcing-followup-2026-11-02.md`. It replaces the single basket of rev 3.x with the two lists of architect log D18. Nothing is ordered (Claude never places orders).

**Sequence (D18):** the enclosure design (A1) and the electronics design (B1) are completed first. Then the **bench-test order** (§1), bench stage 1, gates A and B. Then the **full order** (§2), and stage 2 (gate C) on main-board spin 1.

**Price basis:**
- AliExpress: CHF incl. VAT, ship to CH, seen in the browser 2026-11-01 to 2026-11-03 (date per line). Most are 11.11 sale prices ending 2026-11-18; re-check at order time.
- DigiKey CH: CHF excl. VAT; 8.1 % VAT added at checkout; free delivery from CHF 70.
- SoundImports: EUR excl. VAT at EUR/CHF 0.9249 (2026-10-27 close).
- LCSC: USD at USD/CHF 0.8238 (2026-10-26 close).
- digitec.ch: CHF incl. VAT.
- **Choice** lines ship free once the order's Choice subtotal reaches CHF 9.

**"Fixed by enclosure design"** marks lines whose length, size, colour or variant A1's finished design sets. The current assumption is given.

## Totals
| List | Supplier | Amount (CHF) |
|---|---|---|
| **Bench-test order** | AliExpress | 36.07 incl. shipping (+ a Choice fee for the PH2.0 lead, not verified) |
| | SoundImports NL | 34.30 excl. VAT (+ shipping to CH, not published; CH import VAT + carrier fee on delivery) |
| | **Subtotal** | **≈ 70.37** + the unverified fees |
| **Full order** | AliExpress | 65.92 incl. shipping (V11 alternates not included) |
| | DigiKey CH | 121.06 excl. VAT = **130.87** incl. 8.1 % VAT |
| | LCSC | 2.27 + shipping (not verified) |
| | digitec.ch | 31.00 (+ shipping below CHF 50, not verified) |
| | PCB fab | placeholder — B1 sets it (main board + 2 mic strips) |
| | **Subtotal** | **≈ 230.06** + PCB fab + the unverified fees |
| **Overall** | | **≈ CHF 300.43** + PCB fab + the unverified fees |

## 1. Bench-test order — only what bench stage 1 needs
Per the bench plan's purchase sequence (`claude/E0-bench-plan-2026-11-02.md` rev 3.4). Stage 1 also uses owned items: the Pi 5 + Active Cooler, the LCD, the owned USB-A-to-C cable, a multimeter, hot-air rework tools, and a ~115 cm³ test box printed in ASA or PETG (owned).

| # | Supplier | Item | Listing | Variant | Qty | CHF | Shipping | Delivery (as seen) | Seen | Test |
|---|---|---|---|---|---|---|---|---|---|---|
| B1 | AliExpress — Seeedstudio AI Hardware Store | Seeed ReSpeaker Lite, board only (no XIAO) | https://www.aliexpress.com/item/1005007467885378.html | "ReSpeaker Lite" | 1 | 19.08 (sale; reg. 25.21; max 3 per shopper) | 4.52 | 11–17 Nov | 2026-11-02 | 0, 1.1–1.8, rework |
| B2 | AliExpress — Shenzhen Hi-Link Module Store | Hi-Link HLK-LD2410C | https://www.aliexpress.com/item/1005005637495945.html | HLK-LD2410C / 2PCS | 1 | 5.77 | free | 7–12 Nov | 2026-11-01 | 1.5 |
| B3 | AliExpress — Greenmark Store (Choice) | PH2.0 2P plug with 200 mm 26 AWG leads, 10 sets (ReSpeaker J2 → DMA45-4) | https://www.aliexpress.com/item/4000091077742.html | 10 Sets 2P | 1 | 1.11 (sale) | Choice fee below CHF 9 (not verified) | 8–12 Nov | 2026-11-02 | 1.3 |
| B4 | AliExpress — Jinger Electronic Connector | Dupont F-F jumpers, 30 cm, 40 wires (LD2410C pads → Pi UART for 1.5; later BME680/VEML6030 and the GPIO-lead fallback) | https://www.aliexpress.com/item/1005009372155336.html | Female to Female, 30 cm | 1 | 1.50 (sale; reg. 1.69) | 4.09 | 17–21 Nov | 2026-11-02 | 1.5 |
| B5 | SoundImports NL | Dayton Audio DMA45-4 (all three: one for stage 1, two for the build) | https://soundimports.eu/en/dayton-audio-dma45-4.html | — | 3 | 34.30 (€37.08 excl. VAT; €12.36 each) | not published | "10+ In stock" | 2026-11-01 | 1.3 |

AliExpress bench subtotal: 27.46 + 8.61 shipping = **36.07** (+ the Choice fee).

## 2. Full order — after gates A and B pass

### 2.1 AliExpress
Parked cart lines (less the ribbon, removed by option 1, and less B1–B4), plus block 4, plus the V11 alternates in §2.1b.

| # | Item | Listing | Store | Variant | Qty | CHF | Shipping | Delivery (as seen) | Seen | Flag |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | DSI FPC cable (B), Pi 5 22-pin → 15-pin | https://www.aliexpress.com/item/1005013185742687.html | Shenzhen Seeven Electronics | 300 mm | 2 | 3.32 (1.66 each, sale; reg. 2.21) | 5.39 | 11–18 Nov | 2026-11-01 | — |
| A2 | Socket screws DIN912 A2, M2.5 × 6, 55 pcs (LCD) | https://www.aliexpress.com/item/1005006999030038.html | EN XIXIAN Store | M2.5 × 6 DIN912 | 1 | 2.17 | store: free over CHF 9 (A2–A5 = 9.05) | 9–15 Nov | 2026-11-02 | V8: × 6 or × 8, fixed by enclosure design |
| A3 | Socket screws DIN912 A2, M2.5 × 8, 55 pcs (LCD) | same | same | M2.5 × 8 DIN912 | 1 | 2.31 | same | same | 2026-11-02 | V8 |
| A4 | Button screws ISO7380 A2, M3 × 8, 55 pcs (door) | same | same | M3 × 8 ISO7380 | 1 | 2.46 | same | same | 2026-11-02 | — |
| A5 | Socket screws DIN912 A2, M2 × 6, 55 pcs (ReSpeaker, 5807) | same | same | M2 × 6 DIN912 | 1 | 2.11 (sale; reg. 2.80) | same | 8–12 Nov | 2026-11-02 | M2 × 5 if A1's boss needs it; 1.5 mm hex key |
| A6 | Hex button self-tapping screws M2.5 × 8, 100 pcs (speakers, Pi) | https://www.aliexpress.com/item/1005005730916402.html | NINDEJIN Official Store | M2.5 × 8 | 1 | 1.73 | free | 7–12 Nov | 2026-11-01 | — |
| A7 | DAREX ball-end hex screwdriver 2.0 × 200 mm (K5 lanes) | https://www.aliexpress.com/item/1005009097586025.html | AIPUSI's Tools Store | Ball Head 2.0 × 200 mm | 1 | 4.37 | 4.51 | 13 Nov – 8 Dec | 2026-11-02 | — |
| A8 | XH2.54 2P single-head lead, 300 mm, 22 AWG UL1007, lot of 20 (speakers ×2, 20 V pigtail ×1) | https://www.aliexpress.com/item/1005008234144700.html | Shop1104384424 Store | B-R, 300 mm, 22 AWG | 1 | 1.55 | 3.69 | 11–18 Nov | 2026-11-02 | cut to A1's routed length |
| A9 | XH2.54 4P single-head lead, 300 mm, 26 AWG, 10 sets (LD2410C, touch board) | https://www.aliexpress.com/item/1005003433248478.html | HGD Store | 10 Sets 4P | 1 | 1.99 | 4.03 | 4–27 Nov | 2026-11-02 | cut to length |
| A10 | USB-C to USB-C, 5 A / 48 V / 240 W, USB 3.2 Gen2, straight plugs (Pi power) | https://www.aliexpress.com/item/1005008666410388.html | Ali Digital Global Store (Choice) | 0.2 m | 1 | 2.88 (sale) | Choice | 9–13 Nov | 2026-11-03 | V11: length and angle fixed by enclosure design (§2.1b) |
| A11 | Fabric F1: 100 % polyester knit mesh, 160 cm wide | https://www.aliexpress.com/item/1005004787719702.html | NO.3 Knit Store (Choice) | 160 × 45 cm; colour fixed by enclosure design (13 dark grey 5.26 / 6 white 5.98 / 1 light gray 6.26) | 1 | 5.26 | Choice | 9–15 Nov | 2026-11-02 | colour; G measured in A2 |
| A12 | Closed-cell CR (neoprene) foam tape, self-adhesive, black, 1 mm × 10 mm × 10 m | https://www.aliexpress.com/item/1005009332031483.html | Spring King Store | Thickness 1mm(10m L), Black, Width 10mm | 1 | 3.01 | 3.94 (A12 + A13) | 12–19 Nov | 2026-11-02 | width fixed by enclosure design |
| A13 | same, 2 mm × 10 mm × 5 m | same | same | Thickness 2mm(5m L), Black, Width 10mm | 1 | 2.54 | with A12 | same | 2026-11-02 | width |
| A14 | Brass heat-set inserts M2 × L4 × OD3.2, 50 pcs | https://www.aliexpress.com/item/1005011938823673.html | XIXIAN ASTA Store (Choice) | M2xL4xOD3.2, 50pcs | 1 | 1.81 | Choice | 9–15 Nov | 2026-11-02 | — |
| A15 | Bare pre-crimped Dupont leads, double head, UL1007 26 AWG, 10 per colour (GPIO plugs A/B) | https://www.aliexpress.com/item/1005006121593354.html | YBM Connectors Store | Double Head 10pcs, 20 cm: black, red, yellow | 3 | 2.76 (0.92 each) | 4.09 | 4–27 Nov | 2026-11-02 | length fixed by enclosure design (20 cm assumed; 30 cm 1.04 each) |

Choice lines A10 + A11 + A14 = 9.95 ≥ CHF 9 → free Choice shipping. **AliExpress full subtotal: 40.27 + 25.65 shipping = 65.92.**

#### 2.1b V11 alternates — **choose after the enclosure design** (not in the totals; seen 2026-11-03)
| Use | Listing | Store | Variants | CHF | Shipping, delivery | Note |
|---|---|---|---|---|---|---|
| Pi power, right-angle 5 A C-to-C cable | https://www.aliexpress.com/item/1005006184315674.html | Shop1103071211 Store (Choice), 95.8 %, 301 sold | Straight / Middle-bending / Side-bending / Up-bending; 0.5–3 m | 4.50 (shown for 0.5 m Straight) | Choice; 11–16 Nov | 5 A / 240 W; shortest 0.5 m → ≈ 0.3 m to stow |
| Pi power, 90° USB-C adapter (male → female) on the straight A10 | https://www.aliexpress.com/item/1005010347053934.html | cablecreation Official Store, 98.1 % | Right Angle / Middle Angle / Up Angle | 3.10 (sale; 4 left) | 3.00; 10–13 Nov | 240 W PD; adds a mated contact pair to the Pi path (bench 2.7) |
| ReSpeaker → Pi USB-A, angled USB-A-to-C | https://www.aliexpress.com/item/1005010017337576.html | Shop1105137815 Store (Choice), 95.5 %, 600+ sold | A-C: UD, LR, DLR, Straight; Black/Purple; 0.15/0.25/0.5/1 m | 2.42 | Choice; 10–16 Nov | USB data mentioned, not verified |
| same | https://www.aliexpress.com/item/1005012768935723.html | "High-Quality Approved FFP2 Mask Store" (Choice), 95.0 %, 1,000+ sold | Dual Elbow / Elbow to Straight / Straight to Elbow / Dual Straight A-C; 0.15/0.25/0.5 m | 2.41 | Choice; 9–13 Nov | 66 W; USB data mentioned, not verified |

Seen, not proposed: 0.25 m elbow C-to-C at 100 W / 4 A (https://www.aliexpress.com/item/1005012360847827.html), because it is rated below 5 A. No listing states overmould dimensions.

### 2.2 DigiKey (digikey.ch) — CHF excl. VAT, free delivery from CHF 70
All protection and capacitor lines are decided (decisions 27–31). The TAS5756M network lines are provisional until B1's schematic (decision 32). Stock is as seen on the date given; "lead time" is the factory lead time where DigiKey showed one, otherwise the line is in stock.

| Brief item | Part | DigiKey PN | Qty | Unit CHF | Line CHF | Stock | Link |
|---|---|---|---|---|---|---|---|
| 4 | Adafruit 5807 HUSB238 PD sink | 1528-5807-ND | 2 | 4.93 | 9.86 | 2'032 | https://www.digikey.ch/en/products/detail/adafruit-industries-llc/5807/21839778 |
| 5 | Mean Well NID100-5 (5 V 11 A SIP-13); 2nd unit = fallback | 1866-NID100-5-ND | 2 | 9.21 | 18.42 | 1'675 | https://www.digikey.ch/en/products/detail/mean-well-usa-inc/NID100-5/10659917 |
| 9 | Littelfuse SMBJ22A TVS (20 V input) | SMBJ22ALFCT-ND | 2 | 0.41 | 0.82 | 3'436 | https://www.digikey.ch/en/products/detail/littelfuse-inc/SMBJ22A/285992 |
| 9 | Littelfuse 0453005.MR NANO2 5 A fast, 12.5 mΩ (20 V main) | F3139CT-ND | 2 | 1.85 | 3.70 | 9'533 | https://www.digikey.ch/en/products/detail/littelfuse-inc/0453005-MR/552261 |
| 9 / V14 | Littelfuse 0453010.MR NANO2 10 A fast, 5.6 mΩ (Pi 5 V branch; decision 28). Factory lead time 23 wk. | F3141CT-ND | 2 | 2.82 | 5.64 | 8'261 | https://www.digikey.ch/en/products/detail/littelfuse-inc/0453010-MR/552264 |
| 9 | Littelfuse 2920L260/33DR PTC 2.6 A / 33 V (amp 20 V branch) | 18-2920L260/33DRCT-ND | 2 | 1.23 | 2.46 | 28'439 | https://www.digikey.ch/en/products/detail/littelfuse-inc/2920L260-33DR/21801850 |
| 9 | Bel 0ZCJ0020FF2E PTC 0.2 A / 30 V (3.3 V sensor/touch branch; decision 30) | 5923-0ZCJ0020FF2ECT-ND | 2 | 0.19 | 0.38 | 320'978 | https://www.digikey.ch/en/products/detail/bel-fuse-inc/0ZCJ0020FF2E/4156326 |
| **new** dec. 30 | Littelfuse 0453001.MR NANO2 1 A fast, 153 mΩ (LD2410C branch) | F3137CT-ND | 2 | 1.85 | 3.70 | 4'789 | https://www.digikey.ch/en/products/detail/littelfuse-inc/0453001-MR/552257 |
| **new** dec. 31 | TI TPS16630PWPT eFuse, 4.5–60 V, 31 mΩ, 0.6–6 A, dV/dt and OVP (20 V input; 0453005.MR stays upstream). Factory lead time 26 wk. | 296-TPS16630PWPTCT-ND | 2 | 4.38 | 8.76 | 524 | https://www.digikey.ch/en/products/detail/texas-instruments/TPS16630PWPT/10715348 |
| 9 | Panasonic EEU-FR1J121B 120 µF 63 V (NID input, per EMC circuit) | P15289CT-ND | 2 | 0.96 | 1.92 | 146 | https://www.digikey.ch/en/products/detail/panasonic-industry/EEU-FR1J121B/3072306 |
| 9 / V15 | Würth 860160572003 22 µF 35 V electrolytic, Ø5 × 12.5 max, 2.0 mm pitch (NID output C3 per the EMC circuit; decision 29) | 732-9541-1-ND | 2 | 0.12 | 0.24 | 19'381 | https://www.digikey.ch/en/products/detail/w%C3%BCrth-elektronik/860160572003/5727771 |
| **new** dec. 29 | Bourns SRR1260-150M 15 µH, I_sat 4.6 A, 27 mΩ, 12.5 × 12.5 × 6.5 (NID EMC input L1; Mean Well asks for NiZn, Bourns says ferrite — B1 confirms) | SRR1260-150MCT-ND | 2 | 0.92 | 1.84 | 1'449 | https://www.digikey.ch/en/products/detail/bourns-inc/SRR1260-150M/1969956 |
| 9 | Samsung CL21B104KBCNNNC 100 nF 50 V X7R 0805 | 1276-1003-1-ND | 10 | 0.037 | 0.37 | 3'965'655 | https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL21B104KBCNNNC/3886661 |
| 9 | Samsung CL32B106KBJNNNE 10 µF 50 V X7R 1210 | 1276-3387-1-ND | 4 | 0.57 | 2.28 | 750'307 | https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL32B106KBJNNNE/3889045 |
| 9 | JST B2B-XH-A header 2-pos | 455-B2B-XH-A-ND | 6 | 0.08 | 0.48 | 222'606 | https://www.digikey.ch/en/products/detail/jst-sales-america-inc/B2B-XH-A/1651045 |
| 9 | JST B4B-XH-A header 4-pos | 455-B4B-XH-A-ND | 2 | 0.14 | 0.28 | 68'126 | https://www.digikey.ch/en/products/detail/jst-sales-america-inc/B4B-XH-A/1651047 |
| 9 | JST BM05B-SRSS-TB 5-pos 1.0 mm SMD header (mic strips) | 455-BM05B-SRSS-TBCT-ND | 4 | 0.52 | 2.08 | 158'476 | https://www.digikey.ch/en/products/detail/jst-sales-america-inc/BM05B-SRSS-TB/926697 |
| 9 | JST A05SR05SR30K305B 5-pos cable 305 mm, pin 1–1 (strip → ReSpeaker mic pads; cut one end) | 455-3712-ND | 4 | 1.62 | 6.48 | 1'358 | https://www.digikey.ch/en/products/detail/jst-sales-america-inc/A05SR05SR30K305B/6708516 |
| **new** H2 = a | GCT USB4105-GF-A USB-C receptacle, 16P, rated 5 A (main-board 5 V out to the Pi's USB-C; CC Rp = the 10 kΩ below). Lead time 7 wk. | 2073-USB4105-GF-ACT-ND | 2 | 0.66 | 1.32 | 84'133 | https://www.digikey.ch/en/products/detail/gct/USB4105-GF-A/11198441 |
| 11 | 3M SJ-5012 (BLACK) Ø12.7 × 3.5, sheet of 56 (min. unit) | SJ5012-0-ND | 56 | 0.1134 | 6.35 | 494'074 | https://www.digikey.ch/en/products/detail/3m/SJ-5012-BLACK/30809 |
| **new** D1 = a, R4 | **TI TAS5756MDCAR** stereo class-D amp, HTSSOP-48, MSL 3; lead time 20 wk; tube TAS5756MDCA CHF 6.71 | 296-40565-1-ND (cut tape) | 2 | 5.37 | 10.74 | 5'508 | https://www.digikey.ch/en/products/detail/texas-instruments/TAS5756MDCAR/4914148 |
| **new** R6 | TI SN74LVC1G17DCKR Schmitt buffer, SC-70-5 (strip CLK input, with 0 Ω bypass) | 296-11934-1-ND | 4 | 0.22 | 0.88 | 213'136 | https://www.digikey.ch/en/products/detail/texas-instruments/SN74LVC1G17DCKR/389053 |
| **new** R5 | TI TPD1E05U06DPYR ESD, 0402, VRWM 5.5 V, 0.42–0.5 pF typ (strip CLK/DATA/VDD; the Voice PE's ESDPSA0402V05 is not at DigiKey; the 12 pF TPD1E10B06 is rejected to keep CLK load low, R6) | 296-39341-1-ND | 10 | 0.222 | 2.22 | 579'922 | https://www.digikey.ch/en/products/detail/texas-instruments/TPD1E05U06DPYR/3844805 |
| **new** R5 | YAGEO CC0402MPX5R5BB106 10 µF 6.3 V X5R 0402, max 0.70 mm thick (strip decoupling with the owned 100 nF; CL05A106MQ5NUNC is discontinued at DigiKey) | 13-CC0402MPX5R5BB106CT-ND | 10 | 0.135 | 1.35 | 186'080 | https://www.digikey.ch/en/products/detail/yageo/CC0402MPX5R5BB106/11611330 |
| **new** R6 | YAGEO RC0402FR-0733RL 33 Ω 1 % 0402 (DATA source termination) | 311-33.0LRCT-ND | 10 | 0.017 | 0.17 | 1'286'428 | https://www.digikey.ch/en/products/detail/yageo/RC0402FR-0733RL/726593 |
| **new** R6 | YAGEO RC0402FR-07100RL 100 Ω 1 % 0402 (DATA alternative, VDD RC filter) | 311-100LRCT-ND | 10 | 0.017 | 0.17 | 3'348'744 | https://www.digikey.ch/en/products/detail/yageo/RC0402FR-07100RL/726527 |
| **new** R6, D4a | YAGEO RC0402JR-070RP 0 Ω 0402 (strip buffer bypass + ~8 D4a links; RC0402JR-070RL is out of stock) | YAG1279CT-ND | 30 | 0.013 | 0.39 | 1'438'628 | https://www.digikey.ch/en/products/detail/yageo/RC0402JR-070RP/4935294 |
| **new** R11 / V13 | Littelfuse SMBJ6.0A-E TVS: standoff 6.0 V, breakdown 6.67–7.37 V, clamp 10.3 V at 58.3 A (5 V rail; decision 27) | 18-SMBJ6.0A-ECT-ND | 2 | 0.44 | 0.88 | 2'985 | https://www.digikey.ch/en/products/detail/littelfuse-inc/SMBJ6-0A-E/27575275 |
| **new** dec. 32 | CODACA CSBA0850-100M 10 µH, I_sat 8 A, 31.6 mΩ, 8.7 × 8.5 × 5.1 (TAS5756M LC filter L100–L103; provisional) | 4044-CSBA0850-100MCT-ND | 5 | 1.47 | 7.35 | 690 | https://www.digikey.ch/en/products/detail/codaca/CSBA0850-100M/29538896 |
| **new** dec. 32 | Samsung CL21B684KBFVPNE 0.68 µF 50 V X7R 0805 (LC filter C109/C110/C116/C117; provisional) | 1276-7009-1-ND | 10 | 0.132 | 1.32 | 60'531 | https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL21B684KBFVPNE/7320514 |
| **new** dec. 32 | Samsung CL10B224KB8NNNC 0.22 µF 50 V X7R 0603 (bootstrap C104/C108/C111/C115; provisional) | 1276-CL10B224KB8NNNCCT-ND | 10 | 0.065 | 0.65 | 182'863 | https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL10B224KB8NNNC/10479537 |
| **new** dec. 32 | Murata GRM155R71H104KE14D 0.1 µF 50 V X7R 0402 (C100/C121; provisional) | 490-10700-1-ND | 10 | 0.022 | 0.22 | 26'013 | https://www.digikey.ch/en/products/detail/murata-electronics/GRM155R71H104KE14D/4906220 |
| **new** dec. 32 | Taiyo Yuden UMK107AB7105KA-T 1 µF 50 V X7R 0603 (GVDD C103; provisional) | 587-3247-1-ND | 10 | 0.097 | 0.97 | 505'202 | https://www.digikey.ch/en/products/detail/taiyo-yuden/UMK107AB7105KA-T/3660085 |
| **new** dec. 32 | Taiyo Yuden LMK105BJ105KVHF 1 µF 10 V X5R 0402 (C105/C118/C119/C120; provisional) | 587-3712-1-ND | 10 | 0.035 | 0.35 | 542'037 | https://www.digikey.ch/en/products/detail/taiyo-yuden/LMK105BJ105KVHF/4811078 |
| **new** dec. 32 | Taiyo Yuden TMK105CBJ225MV-F 2.2 µF 25 V X5R 0402 (C106/C107/C113/C114; provisional) | 587-6022-1-ND | 10 | 0.074 | 0.74 | 1'437'062 | https://www.digikey.ch/en/products/detail/taiyo-yuden/TMK105CBJ225MV-F/7403800 |
| **new** dec. 32 | Cal-Chip GMC21X5R226M35NT 22 µF 35 V X5R 0805 (PVDD C101/C102/C122/C123; provisional; B1 may use the 4 × 10 µF 1210 instead) | 4713-GMC21X5R226M35NTCT-ND | 5 | 2.92 | 14.60 | 8'688 | https://www.digikey.ch/en/products/detail/cal-chip-electronics-inc/GMC21X5R226M35NT/18151151 |
| **new** dec. 32 | YAGEO RC0402FR-07100KL 100 kΩ 1 % 0402 (SPK_GAIN R100 to GND; provisional) | 311-100KLRCT-ND | 10 | 0.017 | 0.17 | 5'054'459 | https://www.digikey.ch/en/products/detail/yageo/RC0402FR-07100KL/726526 |
| **new** dec. 32 | YAGEO RC0402FR-07150KL 150 kΩ 1 % 0402 (SPK_GAIN R101 to GVDD_REG; provisional) | 311-150KLRCT-ND | 10 | 0.017 | 0.17 | 711'120 | https://www.digikey.ch/en/products/detail/yageo/RC0402FR-07150KL/726542 |
| **new** dec. 32 | YAGEO RC0402FR-071KL 1 kΩ 1 % 0402 (radar TX → Pi RX series; provisional) | 311-1.00KLRCT-ND | 10 | 0.017 | 0.17 | 3'133'009 | https://www.digikey.ch/en/products/detail/yageo/RC0402FR-071KL/726513 |
| | **DigiKey total** | | | | **120.89** | | |

#### DigiKey — USB-C CC pull-ups for the Pi power output (H2 = a)
| Use | Part | DigiKey PN | Qty | Unit CHF | Line CHF | Stock | Link |
|---|---|---|---|---|---|---|---|
| CC1/CC2 Rp | YAGEO RC0402FR-0710KL 10 kΩ 1 % 0402. Rp to 5 V advertises 3 A; `PSU_MAX_CURRENT=5000` lifts the Pi's limit. | 311-10.0KLRCT-ND | 10 | 0.017 | 0.17 | 8'331'881 | https://www.digikey.ch/en/products/detail/yageo/RC0402FR-0710KL/726523 |
| | **Subtotal** | | | | **0.17** | | |

**DigiKey basket total: CHF 121.06 excl. VAT (CHF 130.87 incl. 8.1 % VAT).** Block 3 lines seen 2026-11-02 22:00–22:20; the rest 2026-11-01/02.

**Removed by option 1 (rev 3.9):** Bel 0ZCJ0075AF2E × 2 (LCD branch, −0.54), Würth 61300411121 × 2 (1 × 4 LCD header, −0.30), Würth 61204021621 × 1 (2 × 20 ribbon header, −0.95). The GPIO landing's headers, if B1 uses headers, are sourced once B1 names the pattern.

**Removed by H2 = a:** CSD25404Q3 ×2, BCM856BSH ×2, 47 kΩ ×10 (−CHF 3.99). The Pi is no longer back-powered through its header, so the HAT guide's safety diode does not apply.


### 2.3 LCSC
| Item | Listing | Qty | Unit | Line | Stock (seen 2026-11-01) | Note |
|---|---|---|---|---|---|---|
| MEMSensing MSM261DHP006 (C22390138), strip mics | https://www.lcsc.com/product-detail/C22390138.html | 4 | USD 0.6882 = CHF 0.57 | CHF 2.27 | 1'449 | Bundle with the mic-strip PCB order; shipping not verified. Not stocked by DigiKey. |

### 2.4 digitec.ch (CH exception, decision 35)
| Item | Listing | Qty | CHF | Stock, delivery (seen 2026-11-02) |
|---|---|---|---|---|
| 3M Super 77, 500 ml (475 g) | https://www.digitec.ch/de/s1/product/3m-super-77-475-g-500-ml-klebstoff-32032712 | 1 | 19.90 | > 10 in stock; "übermorgen" |
| UHU Kontaktkleber flüssig, 120 g | https://www.digitec.ch/de/s1/product/uhu-kontaktkleber-fluessig-120-g-klebstoff-5852544 | 1 | 11.10 | > 10 at the supplier; Nov 04–05 |

Shipping below CHF 50 applies; the fee is not on the product pages (not verified).

### 2.5 PCB fab — placeholder (B1)
- Main board (MAIN_env U: ≈ 90 × 50, 4 × Ø2.7) and two mic strips (30 × 6 × 0.8). B1 sets the stack-up, fab and price.
- Daniel's usual fab for bare boards is JLCPCB.

### 2.6 B1 still adds from its schematic (not priced here)
- The D4a ReSpeaker connector.
- The GPIO landing's 2.54 headers, if B1 uses headers rather than pads (option 1).
- Anything else the schematic needs beyond §2.2. The TAS5756M network and the radar TX resistor are already in §2.2 as provisional lines.

## Owned — not ordered
- Raspberry Pi 5 + Active Cooler
- Waveshare 8" DSI LCD (C)
- BME680 breakout = CJMCU-680 (https://www.aliexpress.com/item/1005007530190637.html)
- VEML6030 breakout (https://www.aliexpress.com/item/1005010560871926.html)
- rev-C touch PCB
- Ugreen Nexode 200 W
- USB cables, incl. a 5 A e-marked USB-C cable. The Pi → ReSpeaker USB-A → USB-C lead comes from these; A1 sets its length and plug angle.
- heat-set inserts M2.5 and M3
- Dupont housings (for plugs A/B, option 1)
- TPU filament: Overture TPU (95A) and Bambu TPU (variant not stated), for the fabric spline
- Bambu ASA (enclosure, decision 26) and Bambu PETG
- 100 nF 0402 (CL05B104KO5NNNC) for the mic strips
- **Home Assistant Voice PE: retired from this build (spare)**

## Decisions (Daniel, 2026-11-01 to 2026-11-03)
1. **V7:** BME680 = CJMCU-680, VEML6030 = the listing above, heat-set inserts in stock.
2. **LCD screws:** ISO 4762 M2.5 socket head, 2 mm hex; 2 mm ball-end driver added.
3. **65 W contract:** 5 A e-marked C–C cable; cut the 5V and 1A jumpers on the 5807.
4. **Defaults:** 5.0 V ±2 % (no trim); fallback = second NID100-5; EU shop SoundImports.
5. **Voice architecture (16:06):** integrated on the Pi 5.
   - ReSpeaker Lite with its mics moved to the strips.
   - Pi I²S playback through the amp on the main board.
   - Software mute only.
   - Voice PE, AA-AB32472 and EG1249 dropped.
   - LD2410C on the Pi UART.
6. **Bench (2026-11-01 16:13, clarified 2026-11-02):** Daniel will test on a bench. No test equipment is bought until research shows what each test needs. The rev 2 bench kit was proposed without that research and stays out.
7. **Bench uses final parts only (2026-11-02):** tests run on the proposed final solution, never on intermediate stand-ins that become redundant.
8. **Objective tests only (2026-11-02):** every pass criterion is a measured number. The ~CHF 700 scope was rejected as too expensive for one test.
9. **D6 = (a), no oscilloscope (2026-11-02).** U8 is designed out:
   - the SN74LVC1G17 Schmitt buffer is fitted on each mic strip;
   - bench test 2.5 verifies it objectively;
   - a scope is borrowed only if 2.5 fails.
10. **D1 = (a), TAS5756M (2026-11-02).**
11. **D3 = (a), back-feed safety diode fitted (2026-11-02) — superseded by H2 = a the same day:** CSD25404Q3 + BCM856BSH + 10 k/47 k, in the DigiKey basket. B1 validates the substitution for the guide's parts.
12. **D4 = (a), 0 Ω links for both echo topologies on the main board (2026-11-02).** Input for B1's layout.
13. **D5 = (a), `uhubctl` power-cycle, no parts (2026-11-02).**
14. **Bench thresholds accepted as written (2026-11-02).** They are frozen; see the bench plan.
15. **Mic-cable strain relief: a zip tie to a tie-down point (2026-11-02).** No adapter PCB. The cable's ReSpeaker end is cut and soldered to the pads; A1 provides the anchors.
16. **H1 = (a), no hand crimping anywhere (2026-11-02):** pre-made cables only; see Harness.
17. **H2 = (a), the Pi is powered through its own USB-C (2026-11-02).** The ribbon part is superseded by decision 25.
    - Power comes from a 5 A USB4105 receptacle on the main board over a 0.2 m 5 A cable.
    - Signals run over a pre-made 40-pin ribbon, with pins 2/4 unconnected.
    - The D3 diode is removed.
18. **L1 = (a), the LCD lead ends in 2.54 mm Dupont sockets (2026-11-02).** The main board gets a 1 × 4 header; B4B-PH-K-S is removed. Superseded by decision 25: the LCD is fed from the Pi.
19. **D2 = (a), one ReSpeaker Lite (2026-11-02).**
20. **5807 at the inlet (2026-11-02, architect log D13):** a separate board at the USB-C inlet grommet with a 2-wire 22 AWG pigtail into a B2B-XH-A on the main board.
21. **Caliper measurements deferred to the second design pass (2026-11-02, D14).**
22. **Order sequence (2026-11-02, D18):** nothing is ordered until the enclosure and electronics designs are complete; then a bench-test order, bench tests, then the full order. Two order lists (rev 4).
23. **AliExpress cart parked (2026-11-02, D16):** 14 lines, ≈ CHF 76; it is the current AliExpress build-parts list.
24. **ReSpeaker Lite firmware (2026-11-02):** board-only variant; if it ships with the I²S firmware, flash the USB firmware with Seeed's `dfu-util` procedure (bench test 0).
25. **GPIO link option 1 (2026-11-02 23:00):** two custom Dupont plugs on the Pi header built from pre-crimped F-F leads in Daniel's housings — A 2 × 8 on pins 1–16, B 2 × 3 on pins 35–40, 13 leads to the main board; the LCD is powered from the Pi's pins 2/6 through its own lead's re-housed terminals; Daniel marks each plug's orientation. The ribbon, both Würth headers and the LCD PTC are removed.
26. **Enclosure filament (2026-11-03):** unfilled ASA or PETG (Bambu, both owned), interchangeable per part: heat is designed to PETG, tip-over to ASA's density, fit through a per-filament Shrinkage % in Bambu Studio, and fabric adhesion is tested on PETG. The K13 coupon is printed in both. It replaces PETG-CF/ABS-GF, which were chosen for looks the cloth now hides. Nothing is bought; see `claude/E0-consumables-2026-11-02.md` §6a.
27. **V13 (2026-11-03):** SMBJ6.0A-E replaces SMBJ5.0A on the 5 V rail (power budget §3.1).
28. **V14 (2026-11-03):** 0453010.MR on the Pi branch. The ≤ 0.1 V at 5 A target is replaced by the measured criteria of bench 2.6/2.7 (power budget §3.2).
29. **V15 (2026-11-03):** Würth 860160572003 22 µF/35 V as NID C3 and Bourns SRR1260-150M as the EMC L1; KEMET polymer removed; NID start-up bench test 2.11 added.
30. **Radar branch (2026-11-03):** 0453001.MR 1 A fuse. The 0ZCJ0020FF2E moves to the 3.3 V sensor/touch branch. Radar VCC frame test 2.12 added.
31. **Inrush (2026-11-03):** TPS16630PWPT eFuse on the 20 V input (dV/dt, OVP below the TAS5756M's 30 V PVDD maximum), with 0453005.MR upstream. No hot-plug test needed.
32. **Main-board BOM (2026-11-03):** the TAS5756M network (SLAS988B Table 22, 20 dBV at 8 × f_SYNC, LC 10 µH + 0.68 µF) and the radar TX resistor are in the DigiKey list as provisional lines; B1 confirms values and packages.
33. **MAIN_env (2026-11-03):** NID upright, 90 × 50 board, 4 × Ø2.7 at an 83 × 43 pattern, candidate A (vertical in the freed Voice PE plane) as A1's default.
34. **Fabric (2026-11-03):** F1 (NO.3 Knit Store, 100 % polyester knit, 160 × 45 cm) in the full order, colour chosen with the enclosure; G is measured in A2.
35. **Adhesives (2026-11-03):** 3M Super 77 and UHU Kontaktkleber flüssig from digitec.ch (CH exception: AliExpress has no 3M 77 for CH, and its 3M 1357 listing had 3 sales).
36. **GPIO leads (2026-11-03):** YBM Connectors bare double-head Dupont leads, 26 AWG, 20 cm, 3 packs of 10 (black GND, red 3V3, yellow signals). Female terminals to be checked on arrival; the cart's F-F set is the fallback.

## Removed
- **Rev 3.9 — option 1 GPIO link** (Daniel, 2026-11-02 23:00):
  - 40-pin GPIO ribbon F-F (AliExpress 4000927738158, CHF 2.15). The parked cart's 14 lines match this list's 14 AliExpress lines, so the ribbon is in it: take it out when the cart is rebuilt for the full order.
  - Würth 61204021621 × 1, Würth 61300411121 × 2, Bel 0ZCJ0075AF2E × 2 (DigiKey, −1.79).
- **Rev 3.6 — hand-crimp parts** (H1 = a, 2026-11-02):
  - JST XHP-2 ×10, XHP-4 ×4, SXH-001T-P0.6 strip;
  - JST PHR-4 ×4, SPH-002T-P0.5S strip;
  - Molex 90142-0010 ×2, 90119-0110 ×20.
  - Total −CHF 13.28.
- **Rev 3 — bench kit** (Daniel, 2026-11-01 16:13; proposed without research):
  - MAX98357A ×2 (1005009559644499);
  - INMP441 ×2 (1005009706170677).
- **Rev 2:**
  - Wondom/Sure AA-AB32472 (amp moves onto the main board);
  - EG1249 mute switch (software mute);
  - Molex 0676430910 USB-A (Voice PE feed);
  - Yageo 33 Ω (Voice PE CLK option);
  - Bourns MF-MSMF200 PTC (Voice PE branch).

## Record — D6 oscilloscope research (rejected, not ordered)
**Status:** the recommended SDS824X HD was rejected as too expensive for one test (Daniel, 2026-11-02). Kept for reference.
**Vendor exception:**
- DigiKey CH carries no Siglent: "SDS824X HD", "SDS824XHD" and "siglent oscilloscope" all return no results. Its only Rigol scope is a Marketplace MSO8064, and the DHO models aren't listed (searched 2026-11-02).
- AliExpress has only trader listings, priced well above EU dealers once shipping is added. Example: JF Test Equipment Store (Trader), https://www.aliexpress.com/item/1005010205681353.html: SDS824X HD CHF 1'043.43 + CHF 113.69 shipping = **CHF 1'157.12**, SDS814X HD CHF 604.04 + 113.69.
- The traders give their own warranty, not Siglent's 3 years through a dealer.
- An EU/CH dealer is therefore proposed instead. Daniel decides.

**Requirements from the bench plan (rev 2):**
1. **Mic-clock edges (test 2.4):**
   - The edges are estimated at 12–27 ns against 13–20 ns limits.
   - Scope + probe rise time must be ≤ ~4 ns, so ≥ 100 MHz.
   - Reading a 12 ns edge (calculation): ~6 % high at 100 MHz with 150 MHz probes; ~2 % at 200 MHz with 200 MHz probes.
2. **Near and far end captured together:** ≥ 1 GSa/s per channel with 2 channels on.
3. **Four channels:**
   - I²S timing for Option B: BCLK, LRCLK, DOUT, DIN;
   - amp start-up (2.10): BCLK plus both BTL outputs.
4. **12-bit vertical resolution:** for the 5 V dip check (2.6), which needs ≥ 4.87 V against 5.0 V nominal.
5. **I²C and UART decode:** TAS5756M and sensors on I²C; the LD2410C on UART at 256000 baud.

| Model | Bandwidth | Sample rate per ch (1 / 2 / 4 ch on) | Memory (1 / 2 / 4 ch) | Probes | Decode included | Growth options | Price (Batronix DE, net) |
|---|---|---|---|---|---|---|---|
| **Siglent SDS824X HD** (was recommended; rejected) | 200 MHz, 12-bit, 70 µVrms noise | 2 G / 1 G / 500 MSa/s | 100 / 50 / 25 Mpts | 4 × PP215, 200 MHz | I²C, SPI, UART, CAN, LIN | SLA1016 16-ch logic probe €328; SAG1021I 25 MHz AWG €239 | €699 |
| Siglent SDS814X HD (budget alternative) | 100 MHz, 12-bit | same platform as above (per-model figures not checked) | as above | not checked | as above | as above | €499 |
| Rigol DHO814 (rejected) | 100 MHz, 12-bit, rise ≤ 3.5 ns | 1.25 G / 625 M / 312.5 MSa/s | 25 / 10 / 1 Mpts | 4 × PVP3150, 150 MHz | I²C, SPI, UART, CAN | no logic option listed | €489 |
| Rigol DHO924 (rejected) | 250 MHz, 12-bit | 1.25 G / 625 M / 312.5 MSa/s | 50 / 25 / 10 Mpts | 4 × PVP2350 | I²C, SPI, UART, CAN, LIN | PLA2216 logic probe €287 | €669 |

**Why the rejects:**
- DHO814: 1 Mpts and 312.5 MSa/s per channel with 4 channels on.
- DHO924: with 4 channels on, its 312.5 MSa/s per channel is below twice its 250 MHz bandwidth.
- DHO814 costs about the same as the SDS814X HD, which keeps 500 MSa/s and 25 Mpts per channel on 4 channels.
- None of the four lists I²S decode.

**Sources** (seen 2026-11-02):
- Batronix: https://www.batronix.com/shop/oscilloscopes/Siglent-SDS824X-hd.html, …/Siglent-SDS800X-hd.html, …/Rigol-DHO814.html, …/Rigol-DHO924.html
- Rigol DHO800/900 datasheet (probe models)
- YOTAVIS: https://yotavis.ch/?p=3561

**Use note for test 2.4:**
- Use each probe's short ground spring on B1's probe pads, not the long ground lead.
- Never clip a probe ground to a TAS5756M speaker output: they are BTL.

## Open issues
1. **5 V margin at the Pi — resolved by decision 28** (re-budget on measured values); kept for the record:
   - At 5 A the Pi-branch fuse 0453007.MR (9 mΩ) drops 45 mV, already more than the review's 40 mV worst-case budget (NID 5.0 V −2 % against the 4.63 V +5 % detector).
   - The Pi is now fed through the main board's USB-C receptacle and a 0.2 m cable (H2a). That path's drop is measured in bench tests 2.6/2.7.
   - Since option 1 the LCD's 0.52 A flows through the same path (+12–43 mV at the Pi; power budget §3.2).
   - Block 3 sets the budget against a measured Pi load (U11). The review's fallback is a converter set to ~5.1 V.
2. **Echo path unproven (R2/R3, U1/U2).** See `claude/E0-bench-plan-2026-11-02.md`.
   - Stage 1, before the main board:
     - U1 with a software-only I²S sink (gate B);
     - the stock-AEC control run with a DMA45-4 on the ReSpeaker's own output (gate A). Seeed sells a 4 Ω 5 W speaker for that output.
   - The split test (U2) needs the TAS5756M and runs on main-board spin 1. D4a keeps the I²S-reference fallback on that board.
3. **ReSpeaker mic network unknown (R5, U7).** The strip schematic is final only after a continuity map of the stock board. With one board (D2a), take the stock baselines first (bench test 1.8), then map and rework that same board.
4. **MSM261DHP006 datasheet:** rev 1.0 (2022-09-27) is hosted only by LCSC. It gives the pinout (1 VDD, 2 L/R, 3 CLK, 4 DATA, 5–8 GND) and the port Ø0.325. It gives no port position (copy the Voice PE footprint). A clock rise-time limit is not established; the Schmitt buffer covers it.
5. **SMBJ5.0A standoff — resolved by decision 27** (SMBJ6.0A-E).
6. **KEMET 100 µF polymer — resolved by decision 29** (Würth 22 µF/35 V).
7. **Hand-crimped harness: resolved** (H1 = a, 2026-11-02). Crimp parts removed; pre-made cables listed under Harness. H2 and L1 are decided too (decisions 17–18).
8. **Cable plug angles (V11): alternates found (block 5.1, 2026-11-03), choice after the enclosure design.** See §2.1b. No right-angle 5 A C-to-C shorter than 0.5 m was found; the 90° adapter adds a mated contact pair to the Pi path (bench 2.7 measures it). No listing gives overmould dimensions: A1 models an allowance, A2 measures.
9. **Prices are 11.11 sale prices (to 2026-11-18).** The orders come after the design (D18), so every AliExpress price is re-checked at order time.
10. **Choice shipping below CHF 9 (bench order).** The PH2.0 lead is the bench order's only Choice line (CHF 1.11), so a Choice shipping fee applies; its amount was not shown (not verified).
11. **Checks on arrival:** YBM leads have female terminals (decision 36); an angled USB-A-to-C cable carries USB data (the ReSpeaker must enumerate); F1 thickness and stretch (G, A2).
