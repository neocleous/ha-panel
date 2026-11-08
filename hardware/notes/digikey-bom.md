# DigiKey BOM — main board, mic strips, harness (block 3, 2026-11-08)

Derived from the schematics on `docs` (main board rev 2.1, mic strip decisions 9.1 and 10.1). Prices are DigiKey CH, CHF excl. VAT, cut tape at the quantity bought, seen 2026-11-08; stock as shown the same day. Build: one main board and two strips. Spares: small passives +50 % (rounded up), ICs +1, cheap discretes and connectors +1.

**Total: CHF 169.97 excl. VAT** (55 lines; CHF 183.74 incl. 8.1 % VAT). The DigiKey quick-add list is `digikey-bom.csv`.


## Main board

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| C1, C10 | KYOCERA AVX 08055C105KAT2A — 1UF 50V X7R 0805 | [478-KGM21AR71H105KUCT-ND](https://www.digikey.ch/en/products/result?keywords=478-KGM21AR71H105KUCT-ND) | 2 | 3 | 0.650 | 1.95 | 101'175 | Samsung, Yageo, TDK, Taiyo Yuden 1 µF 50 V 0805 at 0 stock |
| C2, C4, C9, C100, C121; strip C2, C3 ×2 | Yageo CC0603KRX7R9BB104 — 0.1UF 50V X7R 0603 | [311-1344-1-ND](https://www.digikey.ch/en/products/detail/yageo/CC0603KRX7R9BB104/2103082) | 9 | 14 | 0.066 | 0.92 | 3'588'632 | Samsung CL10B104KB8NNNC at 0 stock (61 wk) |
| C3 | Samsung CL10B473KB8NNNC — 0.047UF 50V X7R 0603 | [1276-1063-1-ND](https://www.digikey.ch/en/products/result?keywords=1276-1063-1-ND) | 1 | 2 | 0.090 | 0.18 | 768'520 |  |
| C5, C6 | Panasonic EEU-FR1J121B — CAP ALUM 120UF 20% 63V RADIAL TH | [P15289CT-ND](https://www.digikey.ch/en/products/detail/panasonic-industry/EEU-FR1J121B/3072306) | 2 | 2 | 0.960 | 1.92 | 146 |  |
| C7 | Würth 860160572003 — CAP ALUM 22UF 20% 35V RADIAL TH | [732-9541-1-ND](https://www.digikey.ch/en/products/detail/w%C3%BCrth-elektronik/860160572003/5727771) | 1 | 2 | 0.120 | 0.24 | 19'381 |  |
| C8, C11 | KEMET C1206C106K4RACTU — 10UF 16V X7R 1206 | [399-C1206C106K4RACTUCT-ND](https://www.digikey.ch/en/products/result?keywords=399-C1206C106K4RACTUCT-ND) | 2 | 3 | 0.410 | 1.23 | 166'752 | 16 V instead of 25 V (5 V rails); the 25 V X7R/X5R 1206 parts checked are at 0 stock or 2'193 |
| C12 | Samsung CL21B475KOFNNNE — 4.7UF 16V X7R 0805 | [1276-2873-1-ND](https://www.digikey.ch/en/products/result?keywords=1276-2873-1-ND) | 1 | 2 | 0.210 | 0.42 | 620'082 |  |
| C101, C102, C122, C123 | Cal-Chip GMC21X5R226M35NT — CAP0805 X5R 22UF 20% 35V | [4713-GMC21X5R226M35NTCT-ND](https://www.digikey.ch/en/products/detail/cal-chip-electronics-inc/GMC21X5R226M35NT/18151151) | 4 | 6 | 2.920 | 17.52 | 2'927 | dearest passive line; the TDK C2012X5R1V226M125AC alternative is at 0 stock |
| C103 | Taiyo Yuden UMK107AB7105KA-T — 1UF 50V X7R 0603 | [587-3247-1-ND](https://www.digikey.ch/en/products/detail/taiyo-yuden/UMK107AB7105KA-T/3660085) | 1 | 2 | 0.170 | 0.34 | 589'009 |  |
| C104, C108, C111, C115 | Samsung CL10B224KB8NNNC — 0.22UF 50V X7R 0603 | [1276-CL10B224KB8NNNCCT-ND](https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL10B224KB8NNNC/10479537) | 4 | 10 | 0.065 | 0.65 | 138'738 |  |
| C105, C112, C118, C119, C120 | Yageo CC0603KRX7R8BB105 — 1UF 25V X7R 0603 | [311-1802-1-ND](https://www.digikey.ch/en/products/result?keywords=311-1802-1-ND) | 5 | 10 | 0.160 | 1.60 | 171'602 |  |
| C106, C107, C113, C114 | Yageo CC0603KRX7R7BB225 — 2.2UF 16V X7R 0603 | [311-3490-1-ND](https://www.digikey.ch/en/products/result?keywords=311-3490-1-ND) | 4 | 10 | 0.369 | 3.69 | 2'295 | 16 V instead of 25 V (≤ 3.3 V audio coupling); no 25 V X7R 0603 in stock |
| C109, C110, C116, C117 | Samsung CL21B684KBFVPNE — 0.68UF 50V X7R 0805 | [1276-7009-1-ND](https://www.digikey.ch/en/products/detail/samsung-electro-mechanics/CL21B684KBFVPNE/7320514) | 4 | 10 | 0.132 | 1.32 | 54'031 |  |
| D1 | Littelfuse SMBJ22A — TVS DIODE 22VWM 35.5VC DO214AA | [SMBJ22ALFCT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/SMBJ22A/285992) | 1 | 2 | 0.410 | 0.82 | 3'431 |  |
| D2 | Littelfuse SMBJ6.0A-E — TVS SURF MT DO214AA - SMBJ6.0A C | [18-SMBJ6.0A-ECT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/SMBJ6-0A-E/27575275) | 1 | 2 | 0.440 | 0.88 | 2'985 |  |
| F1 | Littelfuse 0453005.MR — FUSE BRD MNT 5A 125VAC/VDC 2SMD | [F3139CT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/0453005-MR/552261) | 1 | 2 | 1.850 | 3.70 | 9'445 |  |
| F2 | Littelfuse 0453010.MR — FUSE BRD MNT 10A 125VAC/VDC 2SMD | [F3141CT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/0453010-MR/552264) | 1 | 2 | 2.820 | 5.64 | 7'781 |  |
| F3 | Littelfuse 0453001.MR — FUSE BRD MNT 1A 125VAC/VDC 2SMD | [F3137CT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/0453001-MR/552257) | 1 | 2 | 1.850 | 3.70 | 4'762 |  |
| F4 | Bel 0ZCJ0020FF2E — PTC RESET FUSE 30V 200MA 1206 | [5923-0ZCJ0020FF2ECT-ND](https://www.digikey.ch/en/products/detail/bel-fuse-inc/0ZCJ0020FF2E/4156326) | 1 | 2 | 0.190 | 0.38 | 455'041 |  |
| F5 | Littelfuse 2920L260/33DR — POLYSWITCH RESETTABLE PPTC | [18-2920L260/33DRCT-ND](https://www.digikey.ch/en/products/detail/littelfuse-inc/2920L260-33DR/21801850) | 1 | 2 | 1.230 | 2.46 | 28'323 |  |
| J1, J8, J9 | JST B2B-XH-A — CONN HEADER VERT 2POS 2.5MM | [455-B2B-XH-A-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/B2B-XH-A/1651045) | 3 | 4 | 0.080 | 0.32 | 215'441 |  |
| J5, J6 | JST B4B-XH-A — CONN HEADER VERT 4POS 2.5MM | [455-B4B-XH-A-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/B4B-XH-A/1651047) | 2 | 3 | 0.140 | 0.42 | 58'775 |  |
| J2 | GCT USB4085-GF-A — CONN RCPT USB2.0 TYPE C 16+8POS | [2073-USB4085-GF-ACT-ND](https://www.digikey.ch/en/products/result?keywords=2073-USB4085-GF-ACT-ND) | 1 | 2 | 0.750 | 1.50 | 78'873 |  |
| L1 | Bourns SRR1260-150M — FIXED IND 15UH 5A 27 MOHM SMD | [SRR1260-150MCT-ND](https://www.digikey.ch/en/products/detail/bourns-inc/SRR1260-150M/1969956) | 1 | 1 | 0.920 | 0.92 | 1'406 |  |
| L100–L103 | CODACA CSBA0850-100M — SMD HIGH CURRENT POWER INDUCTOR | [4044-CSBA0850-100MCT-ND](https://www.digikey.ch/en/products/detail/codaca/CSBA0850-100M/29538896) | 4 | 5 | 1.470 | 7.35 | 690 |  |
| PS1 | Mean Well NID100-5 — DC DC CONVERTER 5V 55W | [1866-NID100-5-ND](https://www.digikey.ch/en/products/detail/mean-well-usa-inc/NID100-5/10659917) | 1 | 2 | 9.210 | 18.42 | 1'523 | 2nd = fallback (decision 4) |
| R1 | Yageo RC0603FR-07412KL — RES 412K OHM 1% 1/10W 0603 | [311-412KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-412KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 44'451 |  |
| R2 | Yageo RC0603FR-079K09L — RES 9.09K OHM 1% 1/10W 0603 | [311-9.09KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-9.09KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 35'336 |  |
| R3 | Yageo RC0603FR-0722K1L — RES 22.1K OHM 1% 1/10W 0603 | [311-22.1KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-22.1KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 435'710 |  |
| R4 | Yageo RC0603FR-075K49L — RES 5.49K OHM 1% 1/10W 0603 | [311-5.49KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-5.49KHRCT-ND) | 1 | 10 | 0.025 | 0.25 | 371'427 |  |
| R5, R10, R11 | Stackpole RMCF0603FT10K0 — RES 10K OHM 1% 1/10W 0603 | [RMCF0603FT10K0CT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT10K0CT-ND) | 3 | 10 | 0.018 | 0.18 | 2'282'031 | Yageo RC0603FR-0710KL at 0 stock |
| R6, R13, R17, R18, R100, R102–R105; strip R2 ×2 | Stackpole RMCF0603FT100K — RES 100K OHM 1% 1/10W 0603 | [RMCF0603FT100KCT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT100KCT-ND) | 11 | 25 | 0.013 | 0.33 | 802'912 | Yageo RC0603FR-07100KL at 0 stock |
| R7, R14–R16, R26; strip R5 ×2; options R20–R25, R27 | Yageo RC0603JR-070RL — RES 0 OHM JUMPER 1/10W 0603 | [311-0.0GRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-0.0GRCT-ND) | 7 | 25 | 0.009 | 0.23 | 7'930'327 | includes the 7 DNP option links |
| R12 | Stackpole RMCF0805FT2R20 — RES 2.2 OHM 1% 1/8W 0805 | [RMCF0805FT2R20CT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0805FT2R20CT-ND) | 1 | 10 | 0.026 | 0.26 | 69'544 | Yageo RC0805FR-072R2L at 0 stock |
| R19 | Yageo RC0603FR-074K7L — RES 4.7K OHM 1% 1/10W 0603 | [311-4.70KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-4.70KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 3'300'117 |  |
| R101 | Yageo RC0603FR-07150KL — RES 150K OHM 1% 1/10W 0603 | [311-150KHRCT-ND](https://www.digikey.ch/en/products/result?keywords=311-150KHRCT-ND) | 1 | 10 | 0.023 | 0.23 | 123'027 |  |
| U1 | TI TPS16630PWPT — IC ELECTRONIC FUSE 2% 20HTSSOP | [296-TPS16630PWPTCT-ND](https://www.digikey.ch/en/products/detail/texas-instruments/TPS16630PWPT/10715348) | 1 | 2 | 4.380 | 8.76 | 419 |  |
| U2 | TI TPS70933QDBVRQ1 — IC REG LINEAR 3.3V 150MA SOT23-5 | [296-40931-1-ND](https://www.digikey.ch/en/products/result?keywords=296-40931-1-ND) | 1 | 2 | 1.730 | 3.46 | 14'034 | **substitute**: TPS70933DBVR at 0 stock (26 wk); the -Q1 version has the same DBV pinout and 2.7–30 V input (SLVSCE6D) |
| U100 | TI TAS5756MDCAR — IC AUDIO AMP D 48-HTSSOP | [296-40565-1-ND](https://www.digikey.ch/en/products/detail/texas-instruments/TAS5756MDCAR/4914148) | 1 | 2 | 5.370 | 10.74 | 5'508 |  |

## Mic strip (two boards)

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| strip C1 ×2 | Taiyo Yuden EMK107BBJ106MA-T — 10UF 16V X5R 0603 | [587-3238-1-ND](https://www.digikey.ch/en/products/result?keywords=587-3238-1-ND) | 2 | 3 | 0.260 | 0.78 | 258'433 | 16 V instead of 10 V; every 10 µF 6.3–10 V 0603 checked is at 0 stock |
| strip D1–D3 ×2 | TI ESD321DYAR — TVS DIODE 3.6VWM 6.3VC SOT5X3 | [296-ESD321DYARCT-ND](https://www.digikey.ch/en/products/detail/texas-instruments/ESD321DYAR/17394968) | 6 | 10 | 0.391 | 3.91 | 238'921 | decision 10.1 (Daniel 2026-11-08): replaces TPD1E05U06DYAR (0 stock, 26 wk). 0.9 pF, 3.6 V VRWM; DYA pin 1 = GND, so the footprints are turned 180° |
| strip MK1 ×2 | Infineon IM69D120V01XTSA1 — MIC MEMS DIGITAL PDM OMNI -26DB | [IM69D120V01XTSA1CT-ND](https://www.digikey.ch/en/products/result?keywords=IM69D120V01XTSA1CT-ND) | 2 | 3 | 2.150 | 6.45 | 4'464 |  |
| strip U1 ×2 | TI SN74LVC1G17DCKR — IC BUFF 1.65V SC-70-5 | [296-11934-1-ND](https://www.digikey.ch/en/products/detail/texas-instruments/SN74LVC1G17DCKR/389053) | 2 | 3 | 0.220 | 0.66 | 166'385 |  |
| strip R1 ×2 (+2 for the R4 100 Ω option) | Stackpole RMCF0603FT100R — RES 100 OHM 1% 1/10W 0603 | [RMCF0603FT100RCT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT100RCT-ND) | 2 | 10 | 0.017 | 0.17 | 1'820'162 | Yageo at 0 stock; +2 for the R4 100 Ω option |
| strip R4 ×2 | Stackpole RMCF0603FT33R0 — RES 33 OHM 1% 1/10W 0603 | [RMCF0603FT33R0CT-ND](https://www.digikey.ch/en/products/result?keywords=RMCF0603FT33R0CT-ND) | 2 | 10 | 0.017 | 0.17 | 373'329 | Yageo RC0603FR-0733RL: 3 in stock |

## XH harness

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| XH leads J1, J5, J6, J8, J9 (14 conductors) | JST ASXHSXH22K305 — JUMPER SXH-001T-P0.6 X2 12" | [455-3241-ND](https://www.digikey.ch/en/products/result?keywords=455-3241-ND) | 7 | 10 | 0.598 | 5.98 | 25'541 | black only on DigiKey; mark + leads with a pen or heat-shrink |
| J1, J8, J9 plugs | JST XHP-2 — CONN RCPT HSG 2POS 2.50MM | [455-2266-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/XHP-2/555485) | 3 | 4 | 0.080 | 0.32 | 203'699 |  |
| J5, J6 plugs | JST XHP-4 — CONN RCPT HSG 4POS 2.50MM | [455-2267-ND](https://www.digikey.ch/en/products/result?keywords=455-2267-ND) | 2 | 3 | 0.080 | 0.24 | 86'019 |  |

## System parts kept from order list rev 4

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| 20 V PD sink at the inlet (D13; 2nd = spare, as rev 4) | Adafruit 5807 — EVAL BOARD FOR HUSB238 | [1528-5807-ND](https://www.digikey.ch/en/products/detail/adafruit-industries-llc/5807/21839778) | 2 | 2 | 4.930 | 9.86 | 1'996 |  |
| mic strip → ReSpeaker leads (2 + 2 spare, as rev 4) | JST A05SR05SR30K305B — JUMPER 05SR-3S - 05SR-3S 12" | [455-3712-ND](https://www.digikey.ch/en/products/detail/jst-sales-america-inc/A05SR05SR30K305B/6708516) | 4 | 4 | 1.620 | 6.48 | 1'332 | both ends cut and soldered (decision 9.1) |

## Non-board parts moved from AliExpress

| Refs | Part | DigiKey | Need | Buy | Unit | Ext | Stock | Note |
|---|---|---|---|---|---|---|---|---|
| voice front end | Seeed 107990273 — RESPEAKER LITE USB 2MIC ARRAY AI | [1597-107990273-ND](https://www.digikey.ch/en/products/result?keywords=1597-107990273-ND) | 1 | 1 | 20.620 | 20.62 | 205 |  |
| Pi 5 DSI cable 300 mm (2nd = spare, as AliExpress A1) | Raspberry Pi SC1132 — RPI5 DISPLAY CABLE 300MM QTY 1 | [2648-SC1132-ND](https://www.digikey.ch/en/products/result?keywords=2648-SC1132-ND) | 2 | 2 | 1.660 | 3.32 | 494 |  |
| GPIO leads (40 × F-F 152 mm) | Adafruit 266 — JUMPER WIRE F/F 40-ZIPPABLE 1PC | [1528-1379-ND](https://www.digikey.ch/en/products/result?keywords=1528-1379-ND) | 1 | 1 | 3.270 | 3.27 | 50 |  |
| sensor leads and LD2410C bench (20 × F-F 305 mm) | Adafruit 1949 — JUMPER WIRE F TO F 12" 28AWG | [1528-1960-ND](https://www.digikey.ch/en/products/detail/adafruit-industries-llc/1949/6827083) | 1 | 1 | 3.270 | 3.27 | 1'199 |  |
| ReSpeaker speaker out → DMA45-4 (bench) | Adafruit 261 — CABLE ASSY JST PH 2PIN 4" | [1528-261-ND](https://www.digikey.ch/en/products/result?keywords=1528-261-ND) | 1 | 1 | 0.620 | 0.62 | 29'215 |  |

## Not bought
- **LK1** (Pi-branch wire link): tinned copper wire ≤ 1.15 mm into the Ø1.3 holes, e.g. a 1.0 mm² solid core. Owned stock is assumed.
- **R8, R9** (NID trim network): DNP. Values come from the bench only if the 5.1 V option is needed (V20).
- **R20–R25, R27** (D4a and amplifier options): DNP. They are covered by the 25 × 0 Ω on the 0 Ω line.
- **Test pads, J3, J4, J7, J10:** bare pads. Nothing to buy.

## Removed from order list rev 4 §2.2 (provisional lines)
- **0402 parts, replaced by the 0603 parts above:**
  - Murata GRM155R71H104KE14D
  - Taiyo Yuden LMK105BJ105KVHF and TMK105CBJ225MV-F
  - Yageo CC0402MPX5R5BB106
  - Yageo RC0402 33 Ω, 100 Ω, 0 Ω, 100 kΩ, 150 kΩ, 10 kΩ and 1 kΩ (R19 4.7 kΩ replaces the 1 kΩ)
- **Samsung CL21B104KBCNNNC** (100 nF 0805) and **CL32B106KBJNNNE** (10 µF 1210): not in the schematic.
- **JST BM05B-SRSS-TB**: no strip connector (decision 9.1).
- **GCT USB4105-GF-A**: replaced by the through-hole USB4085-GF-A (decision 3A).
- **TI TPD1E05U06DPYR** (0402): replaced by the SOD-523 footprint in block 1. The SOD-523 TPD1E05U06DYAR then gave way to the ESD321DYAR (decision 10.1).
- **Kept unchanged in the basket:** the 3M SJ-5012 feet.

## DigiKey basket (rebuilt 2026-11-08, not ordered)
- **Removed:** the 39 old "HA panel" / "HA panel provisional" electronics lines (order list rev 4 §2.2). **Kept:** 56 × 3M SJ-5012 feet (SJ5012-0-ND, CHF 6.35).
- **Added:** the 55 lines above from `digikey-bom.csv`, customer reference "HA panel". Quantities and prices were checked line by line against this list after the upload: CHF 169.97, every line "Immediate".
- **HA panel in the basket:** CHF 176.32 excl. VAT (list 169.97 + feet 6.35), CHF 190.60 incl. 8.1 % VAT.
- **Not touched:** 21 lines with "V2 …" references and 2 lines without a reference (Chip Quik CQ2LF-1.0, MG Chemicals 8342-10ML). Whole basket: CHF 265.98 excl. VAT + VAT 21.54 = CHF 287.52, shipping free (DigiKey, 2026-11-08).
- **Shared part numbers:** RMCF0603FT100KCT-ND, RMCF0603FT100RCT-ND and 1528-261-ND are also on V2 lines. DigiKey keeps them as separate lines and flags "Duplicate line item"; its note only asks that stock covers the combined quantity (35, 20 and 2 against 802'912, 1'820'162 and 29'215).

## Decision 10 — strip ESD diodes (D1–D3 on each strip): option 1 (Daniel, 2026-11-08)
TPD1E05U06DYAR was at 0 stock with a 26-week factory lead time (DigiKey, 2026-11-08), so **TI ESD321DYAR** is fitted (238'921 in stock).
- 0.9 pF typ / 1.1 pF max, VRWM 3.6 V, leakage 50 nA max at 3.6 V, SOD-523 (ESD321 datasheet rev C, 2025-06-04). The 3.3 V lines stay below its 3.6 V standoff.
- Its DYA pinout is the reverse of the TPD1E05U06 DYA: pin 1 = GND, pin 2 = IO. The strip schematic has an ESD321 symbol and the three footprints are turned 180°; the copper is unchanged and the silk pin-1 mark sits at the GND pad.
