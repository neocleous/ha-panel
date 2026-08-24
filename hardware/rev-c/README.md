# HA Panel — Touch Board rev C

Capacitive 4-button touch board for the wall-mounted Home Assistant panel.
Carries the touch controller and acts as the wiring hub for the panel's I2C
sensor breakouts. Designed 2026-07; fabricated at JLCPCB.

Rev C is a ground-up redesign (KiCad 7, programmatically generated) replacing
the rev-A/rev-B EasyEDA design.

## Specifications

| Parameter | Value |
|---|---|
| Dimensions | 100 x 44 mm, rounded corners r2, 1.6 mm FR-4 |
| Layers | 2 (front: electrodes + bus, back: all components) |
| Finish | ENIG, green mask, white silk |
| Holes | None (tented vias only) — front face is completely flat |
| Touch controller | AT42QT1070-SSUR (SOIC-14), I2C addr 0x1B |
| Electrodes | 4x Ø12 mm top copper, mask-covered (intentional — no exposed metal), 24 mm pitch |
| I2C | No on-board pull-ups; bus relies on host (Pi 1.8k) + breakout pull-ups |

## Design notes / changes vs rev A

- **MODE (pin 2) tied to GND** — hard requirement for I2C mode. Floating MODE
  was the probable root cause of rev A never appearing at 0x1B.
- **4.7k series resistors (R1–R4) added in each KEY sense line** per
  AT42QT1070 datasheet §3.1 (ESD/RFI). Rev A had none.
- **4.7k series resistors in SDA/SCL removed** — with the Pi's 1.8k hardware
  pull-ups they broke logic levels (V_OL ≈ 2.4 V at the host).
- Unused pins (KEY4–6, RESET#, CHANGE#) left unconnected per datasheet;
  disable keys 4–6 in software (AVE/AKS = 0).
- All silkscreen is human-readable: every part carries designator + value,
  every wire pad is net-labelled, U1 has a pin-1 dot.

## Wire pad clusters (bottom edge, viewed from the back)

Left to right: **HOST (PI)** · **BME680** · **VL53L0X** · **VEML6030**
Each cluster: `VCC  GND  SDA  SCL` (labelled). Pads 2x3 mm, 3.5 mm pitch,
sized for 24 AWG (power) / 28 AWG (signal) silicone stranded wire.

All three sensor clusters are parallel drops on the same I2C bus
(0x77 / 0x29 / 0x48; controller at 0x1B — no conflicts).

## Electrode / key mapping

Viewed from the FRONT of the panel, left to right the electrodes are
**KEY3, KEY2, KEY1, KEY0** (routing-optimised order). Map keys to actions
in `sensor-daemon` accordingly.

## Assembly

1. Stencil (bottom side, 0.12 mm) + Sn63/Pb37 no-clean paste (SMD291AXT4).
   Paste apertures exist only for U1, R1–R4, C1, C2 — wire pads are
   intentionally paste-free.
2. Place: U1 (mind the pin-1 dot), 4x 4k7 0402, C1 100n 0402, C2 10u 0603.
3. Hot air ~320 °C, low-mid airflow, until reflow + a few seconds.
4. Solder harness wires to the clusters with an iron (pre-tin wire + pad).
5. Bring-up: power via HOST cluster, then `sudo i2cdetect -y 1` on the Pi —
   0x1B present validates MODE strap, solder and bus in one shot.

## Files

- `ha_touch_revC.kicad_pcb` — board source (KiCad 7). DRC-clean. This is
  the canonical file; the fabrication set regenerates from it exactly:
  `kicad-cli pcb export gerbers ha_touch_revC.kicad_pcb -o gerbers/ \
   --layers "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,B.Paste,Edge.Cuts" \
   --subtract-soldermask` plus
  `kicad-cli pcb export drill --format excellon --excellon-separate-th`.
  The zip as actually ordered (2026-07-26) is archived offline.
- `BOM.csv` — bill of materials with DigiKey part numbers.

JLCPCB order settings: 2 layer, 1.6 mm, ENIG, tented vias, remove mark,
flying-probe test; stencil bottom-only, custom 190x190 mm.
