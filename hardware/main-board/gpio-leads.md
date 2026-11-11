# GPIO leads — pin assignment and plug maps (main board ↔ Pi 5 header)

Rev 3.1, 2026-11-11 (main board laid out for the site behind the display). KiCad 9.0.9 schematic sheet "3.3 V, Pi link, XH, D4a"
(`io.kicad_sch`), wire pads J3/J4. Earlier versions of this file: `rev3/gpio-leads.md`, `rev2.1/gpio-leads.md`.

**Rev 3.1 against rev 3:** one thing is new, the face the wires enter from (next line and the section "Entry face").
Pads, nets, Pi pins, housings and colours are unchanged; J3 and J4 have not moved.

- **The 13 wires enter from the back face and are soldered on the door-side face.** Settled in step 3
  (`claude/main-board-rev3-enclosure-findings-2026-11-11.md`, section 5; brief of 2026-11-11, "What must stay", point 5).

- **13 leads**, pre-crimped F-F Dupont leads (YBM 26 AWG UL1007: black = GND, red = 3V3, yellow = signal). Cut length: set in
  the harness step, not here.
- **Pi end: three Dupont housings** (Daniel's decision 2026-11-11, he has the housings):
  **housing 1, 1 × 3 on header pins 1-3-5**; **housing 2, 2 × 5 on pins 7–16**; **housing 3, 2 × 3 on pins 35–40**.
  The LCD's own lead keeps its own 1 × 3 housing on pins 2-4-6 and is not part of this set.
- **Main-board end: wire pads, not headers.** J3 (2 × 5) and J4 (2 × 2), 2.54 mm pitch, Ø1.0 mm plated holes, at the bottom
  edge of the board; the lead's main-board terminal is cut off, the wire is pushed in from the back face and soldered on
  the door side.
- **What changed against rev 2.1:** the pads of J3 are in the order of the housings (housing 1 on pads 1–3, housing 2 on
  pads 4–9); J4 is unchanged. Nets and Pi pins are the same as before.

## Lead table

| Lead | Housing | Pi pin | Pi function | Net on the main board | Main-board pad | Colour | Notes |
|---|---|---|---|---|---|---|---|
| A1 | 1 | 1 | 3V3 | PI_3V3 → TPS70933 EN (U2.3) | J3.1 | red | Enable sense only: ≈ 33 µA into R13 100 kΩ. Board 3.3 V comes from U2, not from the Pi. |
| A2 | 1 | 3 | GPIO2 SDA1 | I2C_SDA | J3.2 | yellow | I²C1; pull-ups 1.8 kΩ on the Pi. TAS5756M 0x4C, AT42QT1070 0x1B, VEML6030 0x48, BME680 0x76/0x77. |
| A3 | 1 | 5 | GPIO3 SCL1 | I2C_SCL | J3.3 | yellow | |
| A4 | 2 | 8 | GPIO14 TXD0 | PI_TXD → J5.4 (LD2410C RX) | J3.4 | yellow | UART0, 256000 8N1. |
| A5 | 2 | 9 | GND | GND | J3.5 | black | |
| A6 | 2 | 10 | GPIO15 RXD0 | PI_RXD ← R19 4.7 kΩ ← J5.3 (LD2410C TX) | J3.6 | yellow | R19 limits back-feed into an unpowered Pi to (3.3 − 0.3) V / 4.7 kΩ = 0.64 mA. |
| A7 | 2 | 12 | GPIO18 PCM_CLK | PI_BCLK → R14 0 Ω → I2S_BCLK (U100.23 SCLK) | J3.7 | yellow | I²S bit clock, Pi = clock producer (overlay). Next to GND pin 14 in the housing. |
| A8 | 2 | 14 | GND | GND | J3.8 | black | |
| A9 | 2 | 15 | GPIO22 | AMP_MUTE_N → U100.27 ~SPK_MUTE | J3.9 | yellow | `mute-gpios = <&gpio 22 0>`: driver drives 1 = play. R17 100 kΩ holds the amp muted while the Pi is off or booting. |
| B1 | 3 | 35 | GPIO19 PCM_FS | PI_LRCLK → R15 0 Ω → I2S_LRCLK (U100.25) | J4.1 | yellow | |
| B2 | 3 | 38 | GPIO20 PCM_DIN | PI_DIN ← R23 (DNP) ← J7.5 | J4.2 | yellow | Used only in echo topology B (ReSpeaker I²S out). R18 100 kΩ keeps it defined in topology A. |
| B3 | 3 | 39 | GND | GND | J4.3 | black | |
| B4 | 3 | 40 | GPIO21 PCM_DOUT | PI_DOUT → R16 0 Ω → I2S_DOUT (U100.24 SDIN) | J4.4 | yellow | Also the echo reference via R22 (DNP) in topology B. |

Not used: J3.10 (spare pad, no connect). Pi pins 2/4/6 = the LCD lead.

## Housing 1 — 1 × 3 on Pi pins 1-3-5 (the odd row, at the corner of the header)

| Pi pin | 1 | 3 | 5 |
|---|---|---|---|
| Lead | A1 3V3 (red) | A2 SDA | A3 SCL |

## Housing 2 — 2 × 5 on Pi pins 7–16

| Pi pin | 7 | 9 | 11 | 13 | 15 |
|---|---|---|---|---|---|
| Lead | — | A5 GND (black) | — | — | A9 MUTE |
| **Pi pin** | **8** | **10** | **12** | **14** | **16** |
| Lead | A4 TXD | A6 RXD | A7 BCLK | A8 GND (black) | — |

## Housing 3 — 2 × 3 on Pi pins 35–40

| Pi pin | 35 | 37 | 39 |
|---|---|---|---|
| Lead | B1 LRCLK | — | B3 GND (black) |
| **Pi pin** | **36** | **38** | **40** |
| Lead | — | B2 DIN | B4 DOUT |

## Main-board landing — J3 (2 × 5) and J4 (2 × 2), 2.54 mm, seen from the door side

Both sit at the bottom edge. Pad 1 is the square pad, bottom left of each block. The odd pads are the row at the board
edge, the even pads the row above it. Positions in the board frame of the site document (u to the right, v up, mm).

| J3, upper row (v −24.46) | .2 A2 SDA | .4 A4 TXD | .6 A6 RXD | .8 A8 GND | .10 spare |
|---|---|---|---|---|---|
| **J3, edge row (v −27.00)** | **.1 A1 3V3** | **.3 A3 SCL** | **.5 A5 GND** | **.7 A7 BCLK** | **.9 A9 MUTE** |
| u | −25.30 | −22.76 | −20.22 | −17.68 | −15.14 |

| J4, upper row (v −24.46) | .2 B2 DIN | .4 B4 DOUT |
|---|---|---|
| **J4, edge row (v −27.00)** | **.1 B1 LRCLK** | **.3 B3 GND** |
| u | +5.65 | +8.19 |

Silkscreen: the board is too full on the door side for a name at every pad. The back carries "PI 1-15" at J3 and
"PI 35-40" at J4; the pad-by-pad assignment is this table.

## Entry face (rev 3.1)

- **Back face = the face without parts, toward the display.** The wire goes in there. The joint, with the wire's end, is
  on the door side among the parts: 3.0 or less above that face (estimate, as in `MAIN_env.md`).
- **Why:** nothing then lies across the sockets on the bottom edge; the joints can be reworked with the board mounted;
  the three bundles drop behind the bottom edge to the Pi's header (the enclosure's route).
- **On the bench:** the wires are soldered before the board is mounted, as before. The back is the face you look at
  while pushing them in, and it carries the names "PI 1-15" and "PI 35-40". Seen from there the board is mirrored left
  to right:

| J3 seen from the back, upper row (v −24.46) | .10 spare | .8 A8 GND | .6 A6 RXD | .4 A4 TXD | .2 A2 SDA |
|---|---|---|---|---|---|
| **J3, edge row (v −27.00)** | **.9 A9 MUTE** | **.7 A7 BCLK** | **.5 A5 GND** | **.3 A3 SCL** | **.1 A1 3V3** |
| u | −15.14 | −17.68 | −20.22 | −22.76 | −25.30 |

| J4 seen from the back, upper row (v −24.46) | .4 B4 DOUT | .2 B2 DIN |
|---|---|---|
| **J4, edge row (v −27.00)** | **.3 B3 GND** | **.1 B1 LRCLK** |
| u | +8.19 | +5.65 |

- **Not here:** cut lengths and the route of the bundles. The enclosure routed them at 58 mm each from the back face to
  the Pi (findings, section 5); the lengths are set in the harness step.
- No layout change came from this: the pads are plain plated holes and take a wire from either face.

## What the stock overlay expects (`dtoverlay=rpi-digiampplus`)
From `arch/arm/boot/dts/overlays/rpi-digiampplus-overlay.dts` and the `iqaudio-dacplus-overlay.dts` it includes (raspberrypi/linux, read 2026-11-07):
- `i2s_clk_producer` enabled → the Pi drives BCLK/LRCLK (GPIO18/19), sends on GPIO21, receives on GPIO20.
- `i2c1` enabled with `pcm5122@4c` (`compatible = "ti,pcm5122"`) → TAS5756M at **0x4C** (ADR0 = ADR1 = GND), no MCLK (MCLK pin tied to GND; the codec's PLL runs from BCLK).
- `mute-gpios = <&gpio 22 0>` with `iqaudio-dac,auto-mute-amp` → **GPIO22**, high = unmuted.
- No other GPIO is used by the overlay.
