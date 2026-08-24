# Bill of Materials

Everything needed to build one panel. Prices omitted (they drift); links are the
exact listings used for the reference build. AliExpress listings are
multi-variant — select the size/quantity noted.

## Core

| Item | Qty | Source |
|------|-----|--------|
| Raspberry Pi 5 (4 GB) | 1 | Any Pi reseller |
| Waveshare 8inch DSI LCD (C), 1280×800 IPS touch | 1 | Waveshare / reseller |
| microSD card, 16 GB+ A2 | 1 | Anywhere |
| USB-C PSU, 5 V / 5 A (27 W) | 1 | Official Pi 5 PSU recommended |
| Adafruit USB Type C vertical breakout | 1 | Adafruit via [Kiwi Electronics](https://www.kiwi-electronics.com) |

## Sensors

| Item | Qty | Source |
|------|-----|--------|
| BME680 breakout (CJMCU-680) — temp/humidity/pressure/VOC, I2C 0x77 | 1 | [AliExpress](https://www.aliexpress.com/item/1005007530190637.html) |
| VEML6030 ambient light breakout, I2C 0x48 | 1 | Breakout board, various sellers |
| VL53L0X time-of-flight breakout, I2C 0x29 | 1 | Breakout board, various sellers |

## Touch-button PCB (custom)

Rev-C board: 100×44 mm, 2-layer ENIG, fabricated at JLCPCB with a bottom-side
stencil. Components (Digi-Key):

| Item | Qty/board | Part number |
|------|-----------|-------------|
| AT42QT1070-SSUR touch controller (SOIC-14), I2C 0x1B | 1 | AT42QT1070-SSUR |
| 4.7 kΩ 0402 (KEY-line series resistors) | 4 | RC0402FR-074K7L |
| 100 nF 0402 | 1 | CL05B104KO5NNNC |
| 10 µF 0603 | 1 | CL10A106KP8NNNC |
| Solder paste, Sn63/Pb37 no-clean T4 | — | Chip Quik SMD291AXT4 |

MODE pin (pin 2) must be tied to GND for I2C mode — floating it makes the chip
completely silent on the bus.

## Enclosure hardware

| Item | Qty | Source |
|------|-----|--------|
| Enclosure — 3D print, PETG-CF recommended | 1 | [STEP file](https://github.com/neocleous/ha-panel/blob/docs/enclosure/HA%20Panel%20Final.step) (`docs` branch) |
| Self-tapping screws for plastic, flat head — **M2×5 mm** (breakouts/PCB) and **M3×10 mm** (case) | 1 pack each | [AliExpress](https://www.aliexpress.com/item/4000242681698.html) — pick variants |
| Anti-slip self-adhesive silicone rubber feet, oval | 4 | [AliExpress](https://www.aliexpress.com/item/1005006258927235.html) |

## Wiring consumables

| Item | Source |
|------|--------|
| 22 AWG silicone-insulated stranded wire | [AliExpress](https://www.aliexpress.com/item/1005007206094421.html) |
| Dupont crimp connector kit, 2.54 mm | [AliExpress](https://www.aliexpress.com/item/1005007103751497.html) |
| 2.54 mm pin headers, 1×40 | [AliExpress](https://www.aliexpress.com/item/1005003722173404.html) |
| Heat-shrink tubing assortment | [AliExpress](https://www.aliexpress.com/item/1005005336957133.html) |

Sensor breakouts connect to the touch-button PCB's labelled SMD wire pads
(VCC/GND/SDA/SCL) and share the Pi's I2C bus 1. All four I2C addresses
(0x1B, 0x29, 0x48, 0x77) coexist without conflicts.
