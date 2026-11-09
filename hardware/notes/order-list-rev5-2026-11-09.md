# E0 order list — rev 5 (2026-11-09): every order after the electronics closing report

**Supersedes rev 4** (`claude/E0-order-list-2026-11-01.md`) for what to buy and the totals. Rev 4 keeps:
- the decision history (1–36);
- the removed lines;
- the oscilloscope record.

**Nothing is ordered.** Claude builds baskets only; Daniel places every order after the electronics closing report (architect log 2026-11-08 §7).

## Rev 5 changes
1. **DigiKey:** rev 4 §2.2 is replaced by the block 3 BOM `hardware/notes/digikey-bom.md`. The basket was rebuilt and is **frozen** (D51).
2. **JLC:** quotes for the main board, the mic strip, touch board rev D and one stencil (D54, D57). Bare boards only.
3. **LCSC:** removed. The IM69D120 (DigiKey) replaced the MSM261DHP006 (D47).
4. **AliExpress:**
   - seven lines moved to DigiKey with the BOM;
   - two lines removed by the M2 screws for plastic;
   - two new items for order prep.
5. **From Daniel's stock:** the AT42QT1070 (D56). Daniel extends the LCD lead (D58).

## Totals (indicative)
| Supplier | Amount | Basis |
|---|---|---|
| DigiKey CH | **CHF 182.46 excl. VAT = 197.24 incl. 8.1 %**: HA panel lines 176.11 + SJ-5012 feet 6.35; free delivery | basket 2026-11-08 |
| JLC | **€70.89 ≈ CHF 65.08**, plus shipping and import VAT | quote page 2026-11-09; ECB 0.9180 CHF/EUR (2026-11-05) |
| AliExpress | **CHF 32.50** + 8.45 known shipping + fees not verified; the two new items are not priced | rev 4 prices (11.11 sale, ends 2026-11-18); re-check at order prep |
| SoundImports NL | **CHF 34.30 excl. VAT** (€37.08) + shipping (not published) + CH import VAT and fee | rev 4 B5 |
| digitec.ch | **CHF 31.00** + shipping below CHF 50 | rev 4 §2.4 |
| **Overall** | **≈ CHF 368.57** + JLC shipping (≈ CHF 19.33 if it ships as one DHL parcel at the page's per-line estimate) + the unverified fees | mixed: DigiKey incl. VAT; JLC and SoundImports before import VAT |

## 1. JLC (jlcpcb.com): three boards and one stencil, bare boards only
**Upload files and every order option:** `hardware/notes/jlc-fab.md`. The order goes in with the Spooky Manor boards (D54).

| Line | Upload | Options (summary) | Build | Price (2026-11-09) |
|---|---|---|---|---|
| Main board rev 2.1 | `hardware/main-board/fab/main-board-jlc-2026-11-08.zip` | 4 L, 90 × 55, 5 pcs, 1.6, ENIG 1U", plugged vias, Remove Mark | 3–4 days | **€22.56** (≈ CHF 20.71) |
| Mic strip | `hardware/mic-strip/fab/mic-strip-jlc-2026-11-08.zip` | 2 L, 28 × 6, 5 pcs, 0.8, ENIG 1U", tented, deburring | 3 days | **€18.62** (≈ CHF 17.09); worst case +€44.45 for the vias (below) |
| Touch board rev D | `hardware/touch-board/fab/touch-board-jlc-2026-11-09.zip` | 2 L, 90 × 44, 5 pcs, 1.6, ENIG 1U", tented | 3 days | **€18.80** (≈ CHF 17.26) |
| Stencil (main-board front + touch-board back) | `hardware/stencil/fab/stencil-main-touch-jlc-2026-11-09.zip` | "SMT Stencil": non-framework, top only, custom 190 × 190, 0.12, multiple PCBs = yes, electropolished, apertures 1:1 | 1–2 days | **€10.91** (≈ CHF 10.02) |
| **Total** | | | | **€70.89 (≈ CHF 65.08)** |

- **Prices:** the quote page, not signed in, no coupons.
- **Currency:** JLC offers only EUR and USD for Switzerland.
- **Shipping:** the page shows DHL Express at €21.06 (2–4 business days) for each line on its own. The shared parcel's figure appears at checkout.
- **Strip vias:** the 28 vias are 0.2 mm hole / 0.45 mm diameter on a 2-layer board, and JLC's note on its via classes reads two ways. Select the free class at order. If JLC's review applies the 0.2 mm class, it asks for up to €44.45 more before production (`jlc-fab.md` "Strip vias"). Decision in the closing report.
- **Desktop prices:** lower in JLC's desktop app (from €20.77 / €16.83 / €17.01 / €9.12).

## 2. DigiKey (digikey.ch): frozen
- **Lines:** `hardware/notes/digikey-bom.md`, 55 lines. Quick-add list `digikey-bom.csv`, customer reference "HA panel". Every line "Immediate" when the basket was checked on 2026-11-08.
- **Moved here from AliExpress:**
  - Seeed ReSpeaker Lite (1597-107990273-ND);
  - Raspberry Pi SC1132 DSI cable ×2;
  - Adafruit 266 (GPIO and BME680 leads), Adafruit 1949 (VEML6030 and bench 1.5), Adafruit 261 (bench PH lead);
  - the XH harness: JST ASXHSXH22K305 ×10, XHP-2 ×4, XHP-4 ×3 (`hardware/notes/harness.md`).
- **Also in it:** the JST A05SR05SR30K305B mic cables ×4 and the Adafruit 5807 ×2.
- **Not in it:**
  - AT42QT1070: Daniel's stock (D56);
  - J10 header and housings: §3.2;
  - M2 × 6 screws for plastic: §3.2.
- **Other lines in the basket, untouched:** 21 "V2 …" lines and 2 without a reference (Chip Quik CQ2LF-1.0, MG Chemicals 8342-10ML). Whole basket: CHF 272.12 excl. VAT + 22.04 VAT = 294.16 (2026-11-08).

## 3. AliExpress
### 3.1 Still to buy: rev 4 lines, prices from rev 4, re-check at order prep
| # | Item | Listing | Store | Variant | Qty | CHF | Shipping |
|---|---|---|---|---|---|---|---|
| B2 | Hi-Link HLK-LD2410C | https://www.aliexpress.com/item/1005005637495945.html | Shenzhen Hi-Link Module Store | HLK-LD2410C / 2PCS | 1 | 5.77 | free |
| A2 | DIN912 A2 M2.5 × 6, 55 pcs | https://www.aliexpress.com/item/1005006999030038.html | EN XIXIAN Store | M2.5 × 6 DIN912 | 1 | 2.17 | store: free over CHF 9 |
| A3 | DIN912 A2 M2.5 × 8, 55 pcs | same | same | M2.5 × 8 DIN912 | 1 | 2.31 | same |
| A4 | ISO7380 A2 M3 × 8, 55 pcs (door) | same | same | M3 × 8 ISO7380 | 1 | 2.46 | same |
| A6 | Hex button self-tapping M2.5 × 8, 100 pcs | https://www.aliexpress.com/item/1005005730916402.html | NINDEJIN Official Store | M2.5 × 8 | 1 | 1.73 | free |
| A7 | DAREX ball-end hex driver 2.0 × 200 mm | https://www.aliexpress.com/item/1005009097586025.html | AIPUSI's Tools Store | Ball Head 2.0 × 200 mm | 1 | 4.37 | 4.51 |
| A10 | USB-C to USB-C 5 A, 0.2 m (Pi power) | https://www.aliexpress.com/item/1005008666410388.html | Ali Digital Global Store (Choice) | 0.2 m | 1 | 2.88 | Choice |
| A11 | Fabric F1, polyester knit, 160 × 45 cm | https://www.aliexpress.com/item/1005004787719702.html | NO.3 Knit Store (Choice) | colour per enclosure | 1 | 5.26 | Choice |
| A12 | CR foam tape 1 × 10 mm × 10 m | https://www.aliexpress.com/item/1005009332031483.html | Spring King Store | 1 mm, black, 10 mm | 1 | 3.01 | 3.94 (A12 + A13) |
| A13 | CR foam tape 2 × 10 mm × 5 m | same | same | 2 mm, black, 10 mm | 1 | 2.54 | with A12 |

- **Subtotal:** 32.50 + 8.45 shipping.
- **Two free-shipping thresholds no longer hold:**
  - EN XIXIAN: with A5 gone, A2–A4 make 6.94, below the store's CHF 9.
  - Choice: with A14 gone, A10 + A11 make 8.14, below CHF 9.
  - Neither fee is verified.
- **Fasteners (architect log 2026-11-08 §7, for order prep, not decided here):** the log also lists M2.5 × 8 ×2 and the 2.0 mm driver as superseded, and asks to fix the seven unticked lines.

### 3.2 New for order prep (not priced)
| # | Item | Qty | Use | Source |
|---|---|---|---|---|
| N1 | M2 × 6 pan-head screws for plastic | 4 (+ spares) | ReSpeaker ×2, 5807 ×2 into Ø1.6 pilots (D52, K22) | DigiKey first (D38). The sourcing session found DigiKey's metric stainless screws limited, so AliExpress is likely. Verify. |
| N2 | 2 × 4 male pin header, 2.54, straight | 1 | J10 (D59) | AliExpress, or Daniel's stock |
| N3 | 1 × 4 Dupont female housing, 2.54 | 2 | BME680 and VEML6030 leads at J10 | Daniel's stock (rev 4 "Owned": Dupont housings) or AliExpress |

### 3.3 Moved to DigiKey: take out of the AliExpress cart
B1 ReSpeaker Lite, B3 PH2.0 2P lead, B4 Dupont F-F 30 cm, A1 DSI FPC cable ×2, A8 XH 2P leads, A9 XH 4P leads, A15 YBM Dupont leads (§2).

### 3.4 Removed
- **A5 DIN912 M2 × 6 and A14 M2 heat-set inserts:** replaced by the M2 × 6 screws for plastic. K22: "No M2 inserts anywhere" (D52).
- **The GPIO ribbon:** removed at rev 3.9; take it out if it is still in the cart.

## 4. SoundImports NL and digitec.ch: unchanged
- **SoundImports:** Dayton Audio DMA45-4 ×3, €37.08 excl. VAT (rev 4 B5).
- **digitec:** 3M Super 77 and UHU Kontaktkleber, CHF 31.00 (rev 4 §2.4).

## 5. Other baskets (architect log 2026-11-08 §7)
- **3DJake:**
  - remove ruthex M2 × 4 (70);
  - keep Support for ABS;
  - the engineering plate is Daniel's call.
- **Magnets:** per V24.

## 6. From stock, not ordered (in addition to rev 4's "Owned")
- AT42QT1070-SSUR for touch board rev D (D56).
- The LCD's own 4-pin lead, which Daniel extends to ≥ 205 mm (D58).
- **Solder paste:** the boards assume Sn63/Pb37 no-clean, as rev C used (Chip Quik SMD291AXT4, `hardware/rev-c/README.md`). Chip Quik gives 12 months shelf life when refrigerated. Check the date before the build.

## 7. Open issues
1. **Strip vias:** up to +€44.45 at JLC's review (§1). Decision in the closing report.
2. **JLC:** shipping and import VAT for the shared parcel show at checkout.
3. **AliExpress:**
   - prices are 11.11 sale prices ending 2026-11-18;
   - two free-shipping thresholds no longer hold (§3.1);
   - N1–N3 still need listings, or confirmation that they come from stock.

## Sources
- `hardware/notes/jlc-fab.md`: JLC options and quotes, seen 2026-11-09 on https://cart.jlcpcb.com/quote.
- `hardware/notes/digikey-bom.md`: DigiKey lines, basket 2026-11-08.
- ECB euro reference rate, CHF: 0.9180 on 2026-11-05, https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-chf.fi.html (read 2026-11-09).
- Rev 4 for AliExpress, SoundImports and digitec prices and listings.
- Architect logs 2026-11-08 (§7, D51–D58) and 2026-11-09 (D59).
- Chip Quik SMD291AX shelf life: DigiKey product page https://www.digikey.ph/en/products/detail/chip-quik-inc/SMD291AX250T3/3645038 (read 2026-11-09).
