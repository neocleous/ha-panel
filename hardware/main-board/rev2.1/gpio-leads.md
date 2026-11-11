# GPIO leads — pin assignment and plug maps (main board ↔ Pi 5 header)

Checkpoint 1, 2026-11-07. KiCad 9.0.9 schematic sheet "3.3 V, Pi link, XH, D4a" (`io.kicad_sch`), connectors J3/J4.

- **13 leads**, option 1 (order list rev 4 decision 25): pre-crimped F-F Dupont leads (decision 36: YBM 26 AWG UL1007, black = GND, red = 3V3, yellow = signal), cut to **150 mm** (K20).
- **Pi end:** two custom Dupont plugs in Daniel's housings — **plug A 2 × 8 on header pins 1–16**, **plug B 2 × 3 on pins 35–40**. Plug A also carries the LCD's own lead on pins 2 (5 V) and 6 (GND) (decision 25); that lead is not one of the 13.
- **Main-board end: wire pads, not headers.** J3 (2 × 5) and J4 (2 × 2), 2.54 mm pitch, Ø1.0 mm plated holes; the lead's main-board terminal is cut off and the wire soldered in (as the radar/mic leads). Reason: lowest height in the MAIN_front_env (a header + Dupont housing stands ≈ 17 mm off the board), no extra parts, and the Pi-side plugs stay removable. The footprint is a standard 2.54 header pattern, so a male header can still be fitted later without a board change.

## Lead table

| Lead | Plug | Pi pin | Pi function | Net on the main board | Main-board pad | Colour | Notes |
|---|---|---|---|---|---|---|---|
| A1 | A | 1 | 3V3 | PI_3V3 → TPS70933 EN (U2.3) | J3.1 | red | Enable sense only: ≈ 33 µA into R13 100 kΩ. Board 3.3 V comes from U2, not from the Pi (V17). |
| A2 | A | 3 | GPIO2 SDA1 | I2C_SDA | J3.3 | yellow | I²C1; pull-ups 1.8 kΩ on the Pi. TAS5756M 0x4C, AT42QT1070 0x1B, VEML6030 0x48, BME680 0x76/0x77. |
| A3 | A | 5 | GPIO3 SCL1 | I2C_SCL | J3.5 | yellow | |
| A4 | A | 8 | GPIO14 TXD0 | PI_TXD → J5.4 (LD2410C RX) | J3.2 | yellow | UART0, 256000 8N1. |
| A5 | A | 9 | GND | GND | J3.7 | black | |
| A6 | A | 10 | GPIO15 RXD0 | PI_RXD ← R19 4.7 kΩ ← J5.3 (LD2410C TX) | J3.4 | yellow | R19 limits back-feed into an unpowered Pi to (3.3 − 0.3) V / 4.7 kΩ = 0.64 mA. |
| A7 | A | 12 | GPIO18 PCM_CLK | PI_BCLK → R14 0 Ω → I2S_BCLK (U100.23 SCLK) | J3.6 | yellow | I²S bit clock, Pi = clock producer (overlay). Next to GND pin 14 in the plug. |
| A8 | A | 14 | GND | GND | J3.8 | black | |
| A9 | A | 15 | GPIO22 | AMP_MUTE_N → U100.27 ~SPK_MUTE | J3.9 | yellow | `mute-gpios = <&gpio 22 0>`: driver drives 1 = play. R17 100 kΩ holds the amp muted while the Pi is off or booting. |
| B1 | B | 35 | GPIO19 PCM_FS | PI_LRCLK → R15 0 Ω → I2S_LRCLK (U100.25) | J4.1 | yellow | |
| B2 | B | 38 | GPIO20 PCM_DIN | PI_DIN ← R23 (DNP) ← J7.5 | J4.2 | yellow | Used only in echo topology B (ReSpeaker I²S out). R18 100 kΩ keeps it defined in topology A. |
| B3 | B | 39 | GND | GND | J4.3 | black | |
| B4 | B | 40 | GPIO21 PCM_DOUT | PI_DOUT → R16 0 Ω → I2S_DOUT (U100.24 SDIN) | J4.4 | yellow | Also the echo reference via R22 (DNP) in topology B. |

Not used: J3.10 (spare pad, no connect). Pi pins 2/6 = the LCD lead.

## Plug A — 2 × 8 on Pi pins 1–16 (header view, pin 1 marked by Daniel)

| Pi pin | 1 | 3 | 5 | 7 | 9 | 11 | 13 | 15 |
|---|---|---|---|---|---|---|---|---|
| Lead | A1 3V3 (red) | A2 SDA | A3 SCL | — | A5 GND (black) | — | — | A9 MUTE |
| **Pi pin** | **2** | **4** | **6** | **8** | **10** | **12** | **14** | **16** |
| Lead | LCD 5 V (LCD lead) | — | LCD GND (LCD lead) | A4 TXD | A6 RXD | A7 BCLK | A8 GND (black) | — |

## Plug B — 2 × 3 on Pi pins 35–40

| Pi pin | 35 | 37 | 39 |
|---|---|---|---|
| Lead | B1 LRCLK | — | B3 GND (black) |
| **Pi pin** | **36** | **38** | **40** |
| Lead | — | B2 DIN | B4 DOUT |

## Main-board landing — J3 (2 × 5) and J4 (2 × 2), 2.54 mm

| J3 odd row | .1 A1 3V3 | .3 A2 SDA | .5 A3 SCL | .7 A5 GND | .9 A9 MUTE |
|---|---|---|---|---|---|
| **J3 even row** | **.2 A4 TXD** | **.4 A6 RXD** | **.6 A7 BCLK** | **.8 A8 GND** | **.10 spare** |

| J4 odd row | .1 B1 LRCLK | .3 B3 GND |
|---|---|---|
| **J4 even row** | **.2 B2 DIN** | **.4 B4 DOUT** |

Silkscreen in block 2 carries the lead names (A1…B4) next to each pad.

## What the stock overlay expects (`dtoverlay=rpi-digiampplus`)
From `arch/arm/boot/dts/overlays/rpi-digiampplus-overlay.dts` and the `iqaudio-dacplus-overlay.dts` it includes (raspberrypi/linux, read 2026-11-07):
- `i2s_clk_producer` enabled → the Pi drives BCLK/LRCLK (GPIO18/19), sends on GPIO21, receives on GPIO20.
- `i2c1` enabled with `pcm5122@4c` (`compatible = "ti,pcm5122"`) → TAS5756M at **0x4C** (ADR0 = ADR1 = GND), no MCLK (MCLK pin tied to GND; the codec's PLL runs from BCLK).
- `mute-gpios = <&gpio 22 0>` with `iqaudio-dac,auto-mute-amp` → **GPIO22**, high = unmuted.
- No other GPIO is used by the overlay.
