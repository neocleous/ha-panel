# Bill of Materials

Everything needed to build one panel. Prices are what the maintainer paid (CHF, 2026) and will drift; AliExpress listings come and go, so search the product name if a link dies.

## Core

| Item | Qty | Source | Notes |
|---|---|---|---|
| Raspberry Pi 5, 4 GB | 1 | Any Pi reseller | 2 GB would likely work; untested |
| Waveshare 8inch DSI LCD (C) 1280×800 | 1 | Waveshare / reseller | Includes DSI cable |
| microSD card, 16 GB+ (A1/A2) | 1 | — | The OS + software use well under 8 GB |
| USB-C power supply, 5 V / 5 A | 1 | — | Official Pi 5 PSU recommended |
| Adafruit USB Type C vertical breakout | 1 | Adafruit / [Kiwi Electronics](https://www.kiwi-electronics.com) | Panel-mount power inlet in the stand |

## Sensor breakouts (AliExpress)

| Item | Qty | Link | Paid |
|---|---|---|---|
| BME680 breakout (CJMCU-680) | 1 | [1005007530190637](https://www.aliexpress.com/item/1005007530190637.html) | CHF 32.39 / 5 pcs |
| VL53L0X ToF module (TOF200C) | 1 | [1005008140349819](https://www.aliexpress.com/item/1005008140349819.html) | CHF 2.47 |
| VEML6030 ambient light module | 1 | [1005010560871926](https://www.aliexpress.com/item/1005010560871926.html) | CHF 2.79 |

All three sit on I2C bus 1 — addresses 0x77, 0x29, 0x48 (touch controller 0x1B). No conflicts.

## Touch button PCB (custom)

Custom 100×44 mm 2-layer board with four Ø12 mm capacitive electrodes under soldermask, all components on the back face. Fabbed at [JLCPCB](https://jlcpcb.com) (ENIG finish; order the stencil with it — solder paste + hot air needed for the SOIC-14).

| Part | Qty | DigiKey P/N | Notes |
|---|---|---|---|
| AT42QT1070-SSUR touch controller | 1 | AT42QT1070-SSUR-ND | SOIC-14. **MODE pin (2) must be tied to GND** for I2C — floating = dead chip |
| 4.7 kΩ 0402 (KEY line ESD series R) | 4 | RC0402FR-074K7L | Per datasheet §3.1 |
| 100 nF 0402 | 1 | CL05B104KO5NNNC | Decoupling |
| 10 µF 0603 | 1 | CL10A106KP8NNNC | Bulk |
| Solder paste, Sn63/Pb37 no-clean T4 | — | SMD291AXT4 | Assembly consumable |

## Enclosure & fasteners

3D-printed desk stand — [STEP file](https://github.com/neocleous/ha-panel/blob/docs/enclosure/HA%20Panel%20Final.step) on the `docs` branch. Printed in PETG-CF on a Bambu Lab X1C (0.4 mm nozzle, 0.2 mm layers); plain PETG or PLA should also work dimensionally.

| Item | Qty | Link | Notes |
|---|---|---|---|
| M2×5 mm self-tapping screws | — | [4000242681698](https://www.aliexpress.com/item/4000242681698.html) | Sensor breakouts + PCB mounting (pick the M2×5 variant) |
| M3×10 mm self-tapping screws | — | same listing | Case assembly (pick the M3×10 variant) |
| Sticky rubber feet | 4 | [1005006258927235](https://www.aliexpress.com/item/1005006258927235.html) | Base of the stand |

## Wiring

| Item | Link | Notes |
|---|---|---|
| 22 AWG silicone hook-up wire | [1005007206094421](https://www.aliexpress.com/item/1005007206094421.html) | I2C + power runs |
| Dupont connector kit | [1005007103751497](https://www.aliexpress.com/item/1005007103751497.html) | Pi GPIO end |
| 2.54 mm pin headers | [1005003722173404](https://www.aliexpress.com/item/1005003722173404.html) | Breakout boards |
| Heat-shrink tubing kit | [1005005336957133](https://www.aliexpress.com/item/1005005336957133.html) | — |
