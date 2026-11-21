# Touch board, rev D

The panel's four touch keys. Four copper electrodes on the front face sit behind the shell's chin; an AT42QT1070 on the
back reads them and talks to the Pi over I²C (address 0x1B) through a four-wire lead from the main board's socket J6.

It replaces rev C ([`../rev-c/`](../rev-c/), the touch board of the first panel) with the same 90 × 44 × 1.6 outline,
R2 corners, no holes except tented vias and a flat front.

**State (2026-11-19):** the fab set of 2026-11-09 is current; it was checked again on 2026-11-16. Not built or tested yet.

**Checks (KiCad 9.0.9, 2026-11-09):** schematic 0 errors, 0 warnings (`erc-report.txt`); board (all severities, with
schematic parity) 0 violations, 0 unconnected, 0 footprint errors (`drc-report.txt`).

## Files
| File | What |
|---|---|
| `touch-board.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | the design, KiCad 9.0.9; `lib/` holds the project's symbol and footprints |
| `touch-board-schematic.pdf` | the schematic |
| `touch-board-assembly.pdf` | the assembly drawing (the back, as seen from the back) |
| `touch-board-front.png`, `touch-board-back.png` | renders of both faces |
| `erc-report.txt`, `drc-report.txt` | KiCad's checks |
| [`fab/`](fab/) | **what goes to JLC:** `touch-board-jlc-2026-11-09.zip`, the files unzipped in `gerbers/`, the hole list, the check of the set, and the order sheet |

## How to order
- **Upload** `fab/touch-board-jlc-2026-11-09.zip` to JLC as a bare board. sha256
  `2d62d7eca9126be672a78bb0a46d35bbd1463b2dc3d9a8c736272d2777056a34`.
- **Options in short:** 2 layers, 90 × 44 mm, 1.6 mm, black with white silkscreen, ENIG (the page's default for 2 layers
  is OSP: change it), vias tented, 5 pieces (1 needed). Every option: [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md).
- **Paste:** the touch board's back pattern is on the combined stencil with the main board ([`../stencil/`](../stencil/)).
  Don't tick the stencil box on the touch-board line.

## Parts
Every part with its DigiKey line: [`../notes/bom-2026-11-17.md`](../notes/bom-2026-11-17.md), section "Touch board rev D".

| Ref | Part | Note |
|---|---|---|
| U1 | Microchip AT42QT1070-SSUR, SOIC-14 | from stock; not a DigiKey line |
| C1 | Yageo CC0603KRX7R9BB104, 100 nF 50 V X7R | DigiKey 311-1344-1-ND, a line shared with the main board and the strip |
| C2 | Taiyo Yuden EMK107BBJ106MA-T, 10 µF 16 V X5R | DigiKey 587-3238-1-ND, a line shared with the strip |
| R1–R4 | Yageo RC0603FR-074K7L, 4.7 kΩ 1 % | DigiKey 311-4.70KHRCT-ND, a line shared with the main board |
| J1 | bare wire pads | — |
| E0–E3 | copper electrodes | — |

## The design
| Item | Value | Source |
|---|---|---|
| Controller | AT42QT1070 SOIC-14, comms (I²C) mode, address 0x1B; MODE (pin 2) to GND; RESET, CHANGE, KEY4–6 open | Atmel 9596C–AT42–05/2013 table 1-1 |
| Electrodes | 4 × 16 × 16 mm, r 2, front copper under the mask; centres front-view X 9/33/57/81, Y 13 | QTAN0062 §2.3: electrode ≥ 4 × panel thickness; panel ≈ 2.5 wall + 0.7 cloth = 3.2 mm (from the model, not measured) → ≥ 12.8 mm. Rev C: Ø12 |
| Key order | seen from the front, left to right **KEY0, KEY1, KEY2, KEY3**, the same order as rev C, so the key map in the sensor daemon's `at42qt1070.py` applies unchanged | |
| Series resistors | R1–R4 4.7 kΩ 0603, next to U1 | datasheet §3.1 |
| Decoupling | C1 100 nF + C2 10 µF 0603 | |
| HOST pads | J1, SMD wire pads 2 × 3 mm at 3.5 pitch on the back, front-view (33, 39.8): VCC, GND, SDA, SCL (labelled); lead from main board J6 | |
| Sensors | none: the BME680 and VEML6030 leads land on the main board (J10, J11); the VL53L0X of rev C is dropped | |
| Pull-ups | none on this board (the Pi's 1.8 kΩ) | |
| Cx | the AT42QT1070 accepts 1–30 pF per key | datasheet 6.2 |

**Layout:** front copper = the electrodes only. Back: U1, R1–R4, C1, C2, the J1 pads and all traces (0.25 mm signal,
0.4 mm supply), back-copper keep-outs behind the electrodes, and a tented via at each electrode's top edge. Silk lines 0.15,
JLC's minimum (0.12 until 2026-11-21).

## How to assemble
One surface-mount face, the back. Drawing: `touch-board-assembly.pdf`.
1. Bare board: VCC–GND on the HOST pads must read open.
2. Paste the back through the touch area of the combined stencil ([`../stencil/`](../stencil/)).
   - Use the stencil the same way up as for the main board: the touch pattern is already mirrored to match the back
     seen from above.
   - The HOST pads get no paste.
3. Place U1 (pin 1 at the chamfered corner), C1 100 nF, C2 10 µF, R1–R4 4.7 kΩ.
4. Hotplate with the front face down on a clean sheet (the front has no parts). The same paste and profile as the main
   board ([`../main-board/README.md`](../main-board/README.md)).
5. Solder the touch lead to the HOST pads with the iron: VCC, GND, SDA, SCL as labelled. The lead's four wires are
   halves of JST pre-crimped XH jumpers (ASXHSXH22K305), their contacts in an XHP-4 housing for J6 on the main board;
   free length 87 mm (harness list of 2026-11-14).

## Bring-up
VCC–GND not shorted; then, on the Pi, `sudo i2cdetect -y 1` shows **1b**.

## Earlier revisions
Rev C, the touch board of the first panel, is in [`../rev-c/`](../rev-c/). The scripts that generated rev D's
schematic and layout are in the history
([`hardware/main-board/gen/` at commit 45a38e4](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee/hardware/main-board/gen));
the KiCad files are the source.
