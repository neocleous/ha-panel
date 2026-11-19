# DigiKey BOM — main board, mic strips, touch board, harness (basket of 2026-11-16; capacitor lines of 2026-11-17)

> **This file is the panel's DigiKey lines,** as they stand in the DigiKey basket with the customer reference "HA-PANEL": 55 lines.
> - **Quantities, prices, amounts and stock** were read on 2026-11-16: the basket for price and amount, each product page for stock.
> - **The line for C101, C102, C122 and C123** was read on 2026-11-17. The basket changed on 2026-11-17 at about 11:30.
> - **C12 is on that line too since the evening of 2026-11-17,** and the Samsung line `1276-2873-1-ND` left the basket at 19:56. **Read back at 19:57, after a reload: 75 lines, 55 of them "HA-PANEL"; no other line changed; the whole basket is CHF 253.31 excl. VAT (it was 253.94), CHF 273.83 incl.; shipping free.**
> - The first issue, of 2026-11-08, had 55 lines at that day's prices (CHF 176.11). What changed since is under "DigiKey basket" below.

Derived from the schematics on `docs` (main board rev 3.2, mic strip, touch board rev D) and checked against them in `bom-2026-11-17.md`. Prices are DigiKey CH, CHF excl. VAT, cut tape at the quantity bought. Build: one main board, two mic strips, one touch board. Spares (set 2026-11-08): at least 3 for 0603 and smaller parts (SC-70 and SOD-523 included), at least 2 for 0805 and 1206 and for the MEMS mic, 1 for larger parts and ICs; the next price break is taken where it costs CHF 0.40 or less more. L1 and C5/C6 have no spare (large, robust).

**Total: CHF 164.62 excl. VAT** (55 lines; CHF 177.95 incl. 8.1 % VAT). About CHF 0.88 of it is HM-V2's share of the three merged lines. The quick-add list is `digikey-bom.csv`; it carries the panel's own quantity on those three lines.

Where a note names another part "at 0 stock", that is the reason for the choice made on 2026-11-08; those parts were not looked up again.


## Main board

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| C1, C10 | KYOCERA AVX 08055C105KAT2A — 1UF 50V X7R 0805 | [478-KGM21AR71H105KUCT-ND](https://www.digikey.ch/en/products/result?keywords=478-KGM21AR71H105KUCT-ND) | 2 | 4 | 0.650 | 2.60 | 88'442 | Samsung, Yageo, TDK, Taiyo Yuden 1 µF 50 V 0805 at 0 stock |
| C2, C4, C9, C100, C121; strip C2, C3 ×2; touch C1 | Yageo CC0603KRX7R9BB104 — 0.1UF 50V X7R 0603 | [311-1344-1-ND](https://www.digikey.ch/en/products/detail/yageo/CC0603KRX7R9BB104/2103082) | 10 | 14 | 0.066 | 0.92 | 3'096'096 | Samsung CL10B104KB8NNNC at 0 stock (61 wk) |
| C3 | Samsung CL10B473KB8NNNC — 0.047UF 50V X7R 0603 | [1276-1063-1-ND](https://www.digikey.ch/en/products/result?keywords=1276-1063-1-ND) | 1 | 10 | 0.031 | 0.31 | 726'604 |  |
| C5, C6 | Panasonic EEU-FR1J121B — CAP ALUM 120UF 20% 63V RADIAL TH | [P15289CT-ND](https://www.digikey.ch/en/products/detail/panasonic-industry/EEU-FR1J121B/3072306) | 2 | 2 | 0.960 | 1.92 | 145 |  |
| C7 | Würth 860160572003 — CAP ALUM 22UF 20% 35V RADIAL TH | [732-9541-1-ND](https://www.digikey.ch/en/products/detail/w%C3%BCrth-elektronik/860160572003/5727771) | 1 | 2 | 0.120 | 0.24 | 19'370 |  |
| C8, C11 | KEMET C1206C106K4RACTU — 10UF 16V X7R 1206 | [399-C1206C106K4RACTUCT-ND](https://www.digikey.ch/en/products/result?keywords=399-C1206C106K4RACTUCT-ND) | 2 | 4 | 0.410 | 1.64 | 155'484 | 16 V instead of 25 V (5 V rails); the 25 V X7R/X5R 1206 parts checked are at 0 stock or 2'193 |
| C12, C101, C102, C122, C123 | TDK C2012X7R1H475K125AC — CAP CER 4.7UF 50V X7R 0805 | [445-C2012X7R1H475K125ACCT-ND](https://www.digikey.ch/en/products/detail/tdk/C2012X7R1H475K125AC/10413507) | 5 | 10 | 0.301 | 3.01 | 112'666 | **read 2026-11-17**: replaces 6 × Cal-Chip GMC21X5R226M35NT, 22 µF 35 V X5R (`4713-GMC21X5R226M35NTCT-ND`, CHF 17.52), out of stock with a 30-week lead time. 10 is the price break, CHF 0.07 more than 6. About 1.9 µF each at 20 V, as the 22 µF part (`../main-board/NOTES.md` §4). **C12 on this line since 2026-11-17,** in place of 3 × Samsung CL21B475KOFNNNE, 4.7 µF 16 V (`1276-2873-1-ND`, CHF 0.63): one 4.7 µF part on the boards. About 4.6 µF at 3.3 V (`NOTES.md` §3). 5 needed, 5 spare |
| C103 | Taiyo Yuden UMK107AB7105KA-T — 1UF 50V X7R 0603 | [587-3247-1-ND](https://www.digikey.ch/en/products/detail/taiyo-yuden/UMK107AB7105KA-T/3660085) | 1 | 10 | 0.097 | 0.97 | 371'465 |  |
| C104, C108, C111, C115 | Samsung CL10B224KB8NNNC — 0.22UF 50V X7R 0603 | [1276-CL10B224KB8NNNCCT-ND](https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL10B224KB8NNNC/10479537) | 4 | 10 | 0.065 | 0.65 | 133'629 |  |
| C105, C112, C118, C119, C120 | Yageo CC0603KRX7R8BB105 — 1UF 25V X7R 0603 | [311-1802-1-ND](https://www.digikey.ch/en/products/result?keywords=311-1802-1-ND) | 5 | 10 | 0.160 | 1.60 | 64'046 |  |
| C106, C107, C113, C114 | Yageo CC0603KRX7R7BB225 — 2.2UF 16V X7R 0603 | [311-3490-1-ND](https://www.digikey.ch/en/products/result?keywords=311-3490-1-ND) | 4 | 10 | 0.369 | 3.69 | 4'634 | 16 V instead of 25 V (≤ 3.3 V audio coupling); no 25 V X7R 0603 in stock on 2026-11-08 |
| C109, C110, C116, C117 | Samsung CL21B684KBFVPNE — 0.68UF 50V X7R 0805 | [1276-7009-1-ND](https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL21B684KBFVPNE/7320514) | 4 | 10 | 0.132 | 1.32 | 53'731 |  |
| D1 | Littelfuse SMBJ22A — TVS DIODE 22VWM 35.5VC DO214AA | [SMBJ22ALFCT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/SMBJ22A/285992) | 1 | 2 | 0.410 | 0.82 | 3'401 |  |
| D2 | Littelfuse SMBJ6.0A-E — TVS SURF MT DO214AA - SMBJ6.0A C | [18-SMBJ6.0A-ECT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/SMBJ6-0A-E/27575275) | 1 | 2 | 0.440 | 0.88 | 2'972 |  |
| F1 | Littelfuse 0453005.MR — FUSE BRD MNT 5A 125VAC/VDC 2SMD | [F3139CT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/0453005-MR/552261) | 1 | 2 | 1.850 | 3.70 | 9'544 |  |
| F2 | Littelfuse 0453010.MR — FUSE BRD MNT 10A 125VAC/VDC 2SMD | [F3141CT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/0453010-MR/552264) | 1 | 2 | 2.820 | 5.64 | 7'854 | product page 2026-11-16: 2.98 at 2; the basket still showed 2.82 |
| F3 | Littelfuse 0453001.MR — FUSE BRD MNT 1A 125VAC/VDC 2SMD | [F3137CT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/0453001-MR/552257) | 1 | 2 | 1.850 | 3.70 | 4'732 |  |
| F4 | Bel 0ZCJ0020FF2E — PTC RESET FUSE 30V 200MA 1206 | [5923-0ZCJ0020FF2ECT-ND](https://www.digikey.ch/en/products/detail/bel-fuse-inc/0ZCJ0020FF2E/4156326) | 1 | 5 | 0.156 | 0.78 | 445'673 |  |
| F5 | Littelfuse 2920L260/33DR — POLYSWITCH RESETTABLE PPTC | [18-2920L260/33DRCT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/2920L260-33DR/21801850) | 1 | 2 | 1.230 | 2.46 | 26'778 |  |
| J1, J8, J9 | JST B2B-XH-A — CONN HEADER VERT 2POS 2.5MM | [455-B2B-XH-A-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/B2B-XH-A/1651045) | 3 | 4 | 0.080 | 0.32 | 206'605 |  |
| J5, J6 | JST B4B-XH-A — CONN HEADER VERT 4POS 2.5MM | [455-B4B-XH-A-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/B4B-XH-A/1651047) | 2 | 3 | 0.140 | 0.42 | 55'585 |  |
| J2 | GCT USB4085-GF-A — CONN RCPT USB2.0 TYPE C 16+8POS | [2073-USB4085-GF-ACT-ND](https://www.digikey.ch/en/products/result?keywords=2073-USB4085-GF-ACT-ND) | 1 | 2 | 0.750 | 1.50 | 77'045 |  |
| J10, J11 | Sullins PRPC004SAAN-RC — CONN HEADER VERT 4POS 2.54MM | [35-PRPC004SAAN-RC-ND](https://www.digikey.ch/en/products/result?keywords=35-PRPC004SAAN-RC-ND) | 2 | 10 | 0.056 | 0.56 | 6'299 | added 2026-11-16: one 1 × 4 header each for the BME680 and the VEML6030 lead. 10 is the price break, CHF 0.32 more than 3 |
| L1 | Bourns SRR1260-150M — FIXED IND 15UH 5A 27 MOHM SMD | [SRR1260-150MCT-ND](https://www.digikey.ch/en/products/detail/bourns-inc/SRR1260-150M/1969956) | 1 | 1 | 0.920 | 0.92 | 1'049 |  |
| L100–L103 | CODACA CSBA0850-100M — SMD HIGH CURRENT POWER INDUCTOR | [4044-CSBA0850-100MCT-ND](https://www.digikey.ch/en/products/detail/codaca/CSBA0850-100M/29538896) | 4 | 5 | 1.470 | 7.35 | 690 |  |
| PS1 | Mean Well NID100-5 — DC DC CONVERTER 5V 55W | [1866-NID100-5-ND](https://www.digikey.ch/en/products/detail/mean-well-usa-inc/NID100-5/10659917) | 1 | 2 | 9.210 | 18.42 | 1'523 | 2nd = fallback |
| R1 | Yageo RC0603FR-07412KL — RES 412K OHM 1% 1/10W 0603 | [311-412KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-412KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 43'901 |  |
| R2 | Yageo RC0603FR-079K09L — RES 9.09K OHM 1% 1/10W 0603 | [311-9.09KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-9.09KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 33'414 |  |
| R3 | Yageo RC0603FR-0722K1L — RES 22.1K OHM 1% 1/10W 0603 | [311-22.1KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-22.1KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 424'608 |  |
| R4 | Yageo RC0603FR-075K49L — RES 5.49K OHM 1% 1/10W 0603 | [311-5.49KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-5.49KHRCT-ND) | 1 | 10 | 0.025 | 0.25 | 370'392 |  |
| R5, R10, R11 | Stackpole RMCF0603FT10K0 — RES 10K OHM 1% 1/10W 0603 | [RMCF0603FT10K0CT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT10K0CT-ND) | 3 | 10 | 0.018 | 0.18 | 2'230'279 | Yageo RC0603FR-0710KL at 0 stock |
| R6, R13, R17, R18, R100, R102–R105; strip R2 ×2 | Stackpole RMCF0603FT100K — RES 100K OHM 1% 1/10W 0603 | [RMCF0603FT100KCT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT100KCT-ND) | 11 | 25 | 0.0132 | 0.46 | 668'857 | Yageo RC0603FR-07100KL at 0 stock. **Merged line of 35** in the basket, reference "HM-V2 10 + HA-PANEL 25"; the amount is the whole line's |
| R7, R14–R16, R26; strip R5 ×2; options R20–R25, R27 | Yageo RC0603JR-070RL — RES 0 OHM JUMPER 1/10W 0603 | [311-0.0GRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-0.0GRCT-ND) | 7 | 25 | 0.0092 | 0.23 | 7'576'856 | includes the 7 DNP option links |
| R12 | Stackpole RMCF0805FT2R20 — RES 2.2 OHM 1% 1/8W 0805 | [RMCF0805FT2R20CT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0805FT2R20CT-ND) | 1 | 10 | 0.026 | 0.26 | 69'276 | Yageo RC0805FR-072R2L at 0 stock |
| R19; touch R1–R4 | Yageo RC0603FR-074K7L — RES 4.7K OHM 1% 1/10W 0603 | [311-4.70KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-4.70KHRCT-ND) | 5 | 10 | 0.023 | 0.23 | 2'376'022 |  |
| R101 | Yageo RC0603FR-07150KL — RES 150K OHM 1% 1/10W 0603 | [311-150KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-150KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 75'269 |  |
| U1 | TI TPS16630PWPT — IC ELECTRONIC FUSE 2% 20HTSSOP | [296-TPS16630PWPTCT-ND](https://www.digikey.ch/en/products/detail/texas-instruments/TPS16630PWPT/10715348) | 1 | 2 | 4.380 | 8.76 | 256 |  |
| U2 | TI TPS70933QDBVRQ1 — IC REG LINEAR 3.3V 150MA SOT23-5 | [296-40931-1-ND](https://www.digikey.ch/en/products/result?keywords=296-40931-1-ND) | 1 | 2 | 1.730 | 3.46 | 19'569 | **substitute**: TPS70933DBVR at 0 stock (26 wk); the -Q1 version has the same DBV pinout and 2.7–30 V input (SLVSCE6D) |
| U100 | TI TAS5756MDCAR — IC AUDIO AMP D 48-HTSSOP | [296-40565-1-ND](https://www.digikey.ch/en/products/detail/texas-instruments/TAS5756MDCAR/4914148) | 1 | 2 | 5.370 | 10.74 | 5'508 |  |

## Mic strip (two boards)

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| strip C1 ×2; touch C2 | Taiyo Yuden EMK107BBJ106MA-T — 10UF 16V X5R 0603 | [587-3238-1-ND](https://www.digikey.ch/en/products/result?keywords=587-3238-1-ND) | 3 | 10 | 0.153 | 1.53 | 230'095 | 16 V instead of 10 V; every 10 µF 6.3–10 V 0603 checked is at 0 stock |
| strip D1–D3 ×2 | TI ESD321DYAR — TVS DIODE 3.6VWM 6.3VC SOT5X3 | [296-ESD321DYARCT-ND](https://www.digikey.ch/en/products/detail/texas-instruments/ESD321DYAR/17394968) | 6 | 10 | 0.391 | 3.91 | 375'530 | chosen 2026-11-08 (see the end of this file): replaces TPD1E05U06DYAR (0 stock, 26 wk). 0.9 pF, 3.6 V VRWM; DYA pin 1 = GND, so the footprints are turned 180° |
| strip MK1 ×2 | Infineon IM69D120V01XTSA1 — MIC MEMS DIGITAL PDM OMNI -26DB | [IM69D120V01XTSA1CT-ND](https://www.digikey.ch/en/products/result?keywords=IM69D120V01XTSA1CT-ND) | 2 | 4 | 2.150 | 8.60 | 4'364 |  |
| strip U1 ×2 | TI SN74LVC1G17DCKR — IC BUFF 1.65V SC-70-5 | [296-11934-1-ND](https://www.digikey.ch/en/products/detail/texas-instruments/SN74LVC1G17DCKR/389053) | 2 | 10 | 0.147 | 1.47 | 22'385 |  |
| strip R1 ×2 (+2 for the R4 100 Ω option) | Stackpole RMCF0603FT100R — RES 100 OHM 1% 1/10W 0603 | [RMCF0603FT100RCT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT100RCT-ND) | 2 | 10 | 0.0124 | 0.31 | 1'757'747 | Yageo at 0 stock; +2 for the R4 100 Ω option. **Merged line of 25** in the basket, reference "HM-V2 10 + HA-PANEL 10 + 5 spare"; the amount is the whole line's |
| strip R4 ×2 | Stackpole RMCF0603FT33R0 — RES 33 OHM 1% 1/10W 0603 | [RMCF0603FT33R0CT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT33R0CT-ND) | 2 | 10 | 0.017 | 0.17 | 361'152 | Yageo RC0603FR-0733RL: 3 in stock |

## Harness

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| 20 V, speaker, radar and touch leads: J1, J5, J6, J8, J9 (14 conductors) | JST ASXHSXH22K305 — JUMPER SXH-001T-P0.6 X2 12" | [455-3241-ND](https://www.digikey.ch/en/products/result?keywords=455-3241-ND) | 7 | 10 | 0.598 | 5.98 | 24'790 | black only on DigiKey; mark + leads with a pen or heat-shrink. Product page 2026-11-16: 0.633 at 10; the basket still showed 0.598 |
| J1, J8, J9 plugs | JST XHP-2 — CONN RCPT HSG 2POS 2.50MM | [455-2266-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/XHP-2/555485) | 3 | 4 | 0.080 | 0.32 | 192'516 |  |
| J5, J6 plugs | JST XHP-4 — CONN RCPT HSG 4POS 2.50MM | [455-2267-ND](https://www.digikey.ch/en/products/result?keywords=455-2267-ND) | 2 | 3 | 0.080 | 0.24 | 76'161 |  |
| Pi signal wires (13), BME680 lead, VEML6030 lead, display lead extension | Adafruit 3141 — JUMPER WIRE F TO F 6" 28AWG (40 wires, 152 mm) | [1528-2176-ND](https://www.digikey.ch/en/products/result?keywords=1528-2176-ND) | 1 | 1 | 2.440 | 2.44 | 408 | added 2026-11-16 in place of Adafruit 266 (`1528-1379-ND`, 0 in stock); 23 of the 40 wires used |
| microphone leads (2 + 2 spare) | JST A05SR05SR30K305B — JUMPER 05SR-3S - 05SR-3S 12" | [455-3712-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/A05SR05SR30K305B/6708516) | 4 | 4 | 1.620 | 6.48 | 1'268 | both ends cut and soldered |

## System

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| 20 V PD sink at the inlet (2nd = spare) | Adafruit 5807 — EVAL BOARD FOR HUSB238 | [1528-5807-ND](https://www.digikey.ch/en/products/detail/adafruit-industries-llc/5807/21839778) | 2 | 2 | 4.930 | 9.86 | 1'894 |  |
| voice front end | Seeed 107990273 — RESPEAKER LITE USB 2MIC ARRAY AI | [1597-107990273-ND](https://www.digikey.ch/en/products/result?keywords=1597-107990273-ND) | 1 | 1 | 20.620 | 20.62 | 182 |  |

## Bench

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| LD2410C bench test (20 × F-F 305 mm) | Adafruit 1949 — JUMPER WIRE F TO F 12" 28AWG | [1528-1960-ND](https://www.digikey.ch/en/products/detail/adafruit-industries-llc/1949/6827083) | 1 | 1 | 3.270 | 3.27 | 1'111 | for the LD2410C bench test only; no longer needed for the VEML6030 lead |
| ReSpeaker speaker out → DMA45-4 (bench) | Adafruit 261 — CABLE ASSY JST PH 2PIN 4" | [1528-261-ND](https://www.digikey.ch/en/products/result?keywords=1528-261-ND) | 1 | 1 | 0.620 | 1.24 | 27'876 | **Merged line of 2** in the basket, reference "HM-V2 1 + HA-PANEL 1"; the amount is the whole line's |

## Enclosure

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| feet | 3M SJ-5012 black — Ø12.7 × 3.5, sheet of 56 | [SJ5012-0-ND](https://www.digikey.ch/en/products/result?keywords=SJ5012-0-ND) | 4 | 56 | 0.11339 | 6.35 | 470'714 | the sheet is the least DigiKey sells; 4 used |

## Not bought
- **LK1** (Pi-branch wire link): tinned copper wire, 1.0 across, into the Ø1.3 holes. From stock.
- **R8, R9** (NID trim network): not fitted. Values come from the bench only if the 5.1 V option is needed (`../main-board/NOTES.md` §2).
- **R20–R25, R27** (echo-tap and amplifier options): not fitted. They are covered by the 25 × 0 Ω on the 0 Ω line.
- **Test pads, J3, J4, J7:** bare pads. Nothing to buy.
- **Touch board rev D, U1 AT42QT1070:** from stock. Its passives sit on the 100 nF, 4.7 kΩ and 10 µF 0603 lines above.
- **The plugs on J10 and J11:** two 1 × 4 Dupont female housings from stock. The two headers themselves are a DigiKey line since 2026-11-16.
- **Raspberry Pi SC1132 display cable** (`2648-SC1132-ND`, 2): taken out of the basket on 2026-11-16. The display uses a Waveshare 200 mm ribbon from stock.
- **Adafruit 266** (`1528-1379-ND`): taken out on 2026-11-16, 0 in stock. Adafruit 3141 takes its place.
- **Samsung CL21B475KOFNNNE** (`1276-2873-1-ND`, 3; 4.7 µF 16 V for C12): taken out of the basket on 2026-11-17. C12 takes the TDK 4.7 µF 50 V part on the line above.

## Removed from order list rev 4 §2.2 (provisional lines, 2026-11-08)
- **0402 parts, replaced by the 0603 parts above:**
  - Murata GRM155R71H104KE14D
  - Taiyo Yuden LMK105BJ105KVHF and TMK105CBJ225MV-F
  - Yageo CC0402MPX5R5BB106
  - Yageo RC0402 33 Ω, 100 Ω, 0 Ω, 100 kΩ, 150 kΩ, 10 kΩ and 1 kΩ (R19 4.7 kΩ replaces the 1 kΩ)
- **Samsung CL21B104KBCNNNC** (100 nF 0805) and **CL32B106KBJNNNE** (10 µF 1210): not in the schematic.
- **JST BM05B-SRSS-TB**: no strip connector.
- **GCT USB4105-GF-A**: replaced by the through-hole USB4085-GF-A.
- **TI TPD1E05U06DPYR** (0402): replaced by the SOD-523 footprint. The SOD-523 TPD1E05U06DYAR then gave way to the ESD321DYAR (see the end of this file).

## DigiKey basket
How the basket stood at each change.

**State of 2026-11-16:**
- **Customer reference "HA-PANEL"** on 56 of the basket's 76 lines.
- **Added:** `35-PRPC004SAAN-RC-ND` × 10 and `1528-2176-ND` × 1.
- **Removed:** `2648-SC1132-ND` × 2 and `1528-1379-ND` × 1 (0 in stock, one expected 2027-01-15).
- **Three lines are merged with HM-V2's,** each as one basket line:
  - `RMCF0603FT100KCT-ND`: a line of 35, reference "HM-V2 10 + HA-PANEL 25";
  - `RMCF0603FT100RCT-ND`: a line of 25, reference "HM-V2 10 + HA-PANEL 10 + 5 spare";
  - `1528-261-ND`: a line of 2, reference "HM-V2 1 + HA-PANEL 1".
- **Two prices had risen on the product pages** and not yet in the basket: `F3141CT-ND` 2.98 at 2 (basket 2.82) and `455-3241-ND` 0.633 at 10 (basket 0.598). DigiKey may reprice at checkout: + CHF 0.67.
- **The 56 lines:** CHF 179.76 excl. VAT with the 22 µF line. **The whole basket:** CHF 268.45 excl. VAT, CHF 290.19 incl.; shipping free. It also holds HM-V2's 18 lines and two lines without a reference (`CQ2LF-1.0-ND`, `473-8342-10ML-ND`).

**Change of 2026-11-17:**
- **out:** `4713-GMC21X5R226M35NTCT-ND` × 6, CHF 17.52. Out of stock, on backorder, 30 weeks.
- **in:** `445-C2012X7R1H475K125ACCT-ND` × 10, CHF 3.01, reference "HA-PANEL". 112'666 in stock on 2026-11-17.
- The 56 lines then come to CHF 165.25 excl. VAT, CHF 14.51 less.
- **Made on 2026-11-17 at about 11:30.** Read back afterwards: 76 lines as before, 56 of them "HA-PANEL"; no other line changed; the whole basket is CHF 253.94 excl. VAT (it was 268.45), CHF 274.51 incl.; shipping free.

**Change of 2026-11-17, evening:**
- **out:** `1276-2873-1-ND` × 3 (Samsung CL21B475KOFNNNE, C12), CHF 0.63. C12 takes the TDK part; its 10 pieces cover the 5 needed.
- **Made on 2026-11-17 at 19:56.** Nothing was added and no other line was touched.
- **Read back twice, at 19:56 and after a reload at 19:57:**
  - 75 lines (76 before); 55 of them "HA-PANEL" (56 before): 52 with that reference alone and the three merged lines;
  - the 74 other lines are as before in part, quantity, reference, unit price, amount and availability, and in the same order; every line "Immediate"; no line ticked;
  - HM-V2's 18 lines and the two lines without a reference are as before.
- **The 55 lines:** CHF 164.62 excl. VAT, CHF 0.63 less; CHF 177.95 incl. 8.1 % VAT.
- **The whole basket:** CHF 253.31 excl. VAT, VAT 20.52, CHF 273.83 incl.; shipping free (UPS Worldwide Saver 0.00).
- **Read a third time at 20:06, against this list:** its 55 numbers are the basket's 55 "HA-PANEL" lines, with the same quantities except on the three merged lines; totals as above.
- The two price rises of 2026-11-16 are still not in the basket's prices (`F3141CT-ND` 2.82, `455-3241-ND` 0.598).

**History, 2026-11-08:** the basket was rebuilt from the first issue of this list: 55 lines with the reference "HA panel", CHF 176.11 excl. VAT at that day's prices, beside the feet (CHF 6.35). The 39 older lines of order list rev 4 §2.2 were removed then.

## Strip ESD diodes (D1–D3 on each strip), chosen 2026-11-08
TPD1E05U06DYAR was at 0 stock with a 26-week factory lead time (DigiKey, 2026-11-08), so **TI ESD321DYAR** is fitted.
- 0.9 pF typ / 1.1 pF max, VRWM 3.6 V, leakage 50 nA max at 3.6 V, SOD-523 (ESD321 datasheet rev C, 2025-06-04). The 3.3 V lines stay below its 3.6 V standoff.
- Its DYA pinout is the reverse of the TPD1E05U06 DYA: pin 1 = GND, pin 2 = IO. The strip schematic has an ESD321 symbol and the three footprints are turned 180°; the copper is unchanged and the silk pin-1 mark sits at the GND pad.
