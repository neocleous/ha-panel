# HA panel — main board, rev 3.2 (fab issue 2026-11-16)

**The board in this folder is rev 3.2 as it goes to the fab.** Same parts, outline, holes and heights as rev 3.2 of
2026-11-14, so `main-board-rev3.2.step`, `MAIN_env.md` and the plug envelopes stand. Changed with the fab files, copper
and texts only (details: [`rev3.2/fab-2026-11-16/README.md`](rev3.2/fab-2026-11-16/README.md)):

1. 39 vias moved out of pasted pads and 1 taken out, so that no hole can take a pad's solder on the hotplate;
2. the pours kept 0.50 back from the relief in the side edge (0.30 everywhere else, as before);
3. the stack-up JLC04161H-7628 written into the board file;
4. the revision text on the back reads `REV 3.2 2026-11-16`.

Checks (KiCad 9.0.9, 2026-11-16): schematic check 0 errors, 0 warnings (`erc-report.txt`); board check 0 errors, 0 open
connections, 0 differences to the schematic, 2 warnings (the footprints of J6 and J2 differ from KiCad's library copies,
on purpose) (`drc-report.txt`). **Nothing is ordered.** Everything is a draft until the unit is built and tested.

## Files
| File | What |
|---|---|
| `main-board.kicad_pro`, `main-board.kicad_pcb`, five `.kicad_sch` | the design, KiCad 9.0.9. Project libraries: `lib/ha_panel.kicad_sym`, `lib/ha_panel.pretty` |
| `main-board-schematic.pdf` | schematic, 5 pages (unchanged since 2026-11-14) |
| **`main-board-rev3.2-assembly.pdf`** | **assembly drawing, A3, 4 pages:** all 120 part names; all values; the placing list with the maker's part numbers; the test pads, connectors and the back face. Previews of pages 1 and 2: `main-board-rev3.2-assembly-names.png`, `-values.png`. Made by `gen/assembly_rev32.py` |
| **`fab/main-board-rev3.2-jlc-2026-11-16.zip`** | **the upload for JLC** (bare board). Every option: [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md). Unzipped: `fab/gerbers/`; holes: `fab/drill-report.txt` |
| `../stencil/` | the combined stencil (this board's door side and the touch board's back): `../stencil/fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` |
| `../notes/bom-2026-11-16.md` | the parts list of all three boards and its difference to the DigiKey lines |
| `NOTES.md` | every value with its source; test pads (§5); layout (§7) |
| `gpio-leads.md` | the 13 Pi signal wires: pad, Pi pin, housing, colour |
| `main-board-rev3.2.step`, `main-board-rev3.1-plug-envelopes.step`, `MAIN_env.md` | for the enclosure model: the populated board, the plug envelopes, outline, holes and heights. Unchanged by the fab issue |
| `main-board-copper-F-B.png` | both outer copper layers, drawn from the board of this issue |
| `main-board-3d-door-side.png`, `main-board-3d-back.png` | renders of 2026-11-14 (the parts have not moved since) |
| `rev3.2/` | rev 3.2 of 2026-11-14 (`main-board-rev3.2-2026-11-14.kicad_pcb`, its reports and checks) and the fab issue's record (`fab-2026-11-16/`) |
| `rev3.1/`, `rev3/`, `rev2.1/` | earlier revisions with their own reports; `rev2.1/` also holds the README and NOTES as they stood on 2026-11-14 |
| `gen/` | the scripts that made the schematic, the layout and each change. The KiCad files are the source of truth |

## The board in numbers
- **87.0 × 57.9 × 1.6 mm, 4 layers,** with a relief 1.5 deep in the side edge toward the left speaker (floor over
  v +1.5 … +13.0, inner corners r 1.0). Four 3.2 holes for M3 × 8 screws.
- **Layers:** door side parts and signals · layer 2 ground · layer 3 +5 V, +20 V and the amplifier's supply · back
  signals and ground. Stack-up JLC04161H-7628: copper 0.035 / 0.0152 / 0.0152 / 0.035, prepreg 0.2104, core 1.065.
- **120 names:** 72 surface-mount parts fitted and 9 not fitted, 13 through-hole parts, 3 blocks of wire pads
  (J3, J4, J7), 19 test pads, 4 holes. **Every part is on the door side; nothing is fitted on the back.**
- **Sizes:** nothing smaller than 0603; the finest pitches are U100 (0.5) and U1 (0.65). Connectors are through-hole.
- **Vias:** 244 — 87 of 0.2/0.45, 132 of 0.3/0.6, 25 of 0.4/0.8. Tracks 0.15 and wider. Copper to the edge 0.30;
  the pours 0.50 at the relief.
- **Frame used in every document:** seen from the door, u to the right (toward the left speaker), v up, origin in the
  middle of the board. "From the left edge" is u + 43.5; "from the bottom edge" is v + 28.95.

## Sheets
1. Root — index.
2. **20 V inlet and protection** — J1 (from the USB-C inlet board) → F1 5 A → TPS16630 (under-voltage 17.05 V,
   over-voltage 24.06 V, current limit 3.28 A, soft start 19.6 ms) → +20 V with D1 SMBJ22A.
3. **5 V supply and outputs** — 120 µF – L1 15 µH – 120 µF → NID100-5 (enabled by the protection chip's power-good) →
   22 µF + D2 SMBJ6.0A-E → Pi branch (F2 10 A → wire link LK1 → USB-C socket J2, 10 kΩ on each CC pin) and radar
   branch (F3 1 A). Trim network R8/R9 not fitted.
4. **3.3 V, Pi link, sensors, radar, echo tap** — TPS70933 (enabled by the Pi's 3.3 V) → sensor branch through F4 and
   the amplifier's logic rail; 13 wire pads for the Pi's signals (J3, J4); radar (J5) and touch (J6) sockets; one
   4-pin header each for the BME680 (J10) and the VEML6030 (J11); echo tap J7 with six links not fitted.
5. **Amplifier** — TAS5756M stereo, I²C address 0x4C, mute on GPIO22, 10 µH + 0.68 µF output filters, speaker sockets
   J8 (left) and J9 (right).

Every value's source: `NOTES.md` §1 to §4.

## Default fit
| Option | Default | Alternative |
|---|---|---|
| Echo reference | **from USB:** R20–R25 not fitted, J7 empty | from I²S: fit R20–R23 (and R24/R25), other firmware |
| 5 V trim | R8, R9 not fitted (5.0 V) | R8 raises the output; value found on the bench at TP13 |
| Amplifier logic rail | R26 fitted (from the board's 3.3 V) | R27 instead of R26 (from the Pi's 3.3 V) |
| I²S series resistors | R14–R16 0 Ω | 22–47 Ω if the edges ring |
| 5 V module enable | R7 0 Ω (from power-good) | R7 open: the module runs whenever 20 V is there |
| Pi branch | LK1 fitted | LK1 open with a 10 A meter in its place (bench) |

## Assembly
One pass on the hotplate for every surface-mount part, then the through-hole parts by iron.
**Work from `main-board-rev3.2-assembly.pdf`:** page 1 names, page 2 values, page 3 the placing list, page 4 the back.

**Before you start**
- **Paste:** Sn63/Pb37 no-clean, as on the rev C touch board (Chip Quik SMD291AXT4). Check its date.
- **Stencil:** the main-board area of the combined stencil, 0.12 thick. The touch board's pattern is on the same sheet:
  keep the squeegee off it.
- **U100 (TAS5756M) is moisture-sensitive, level 3:** 168 hours at 30 °C / 60 % humidity or less once its bag is open
  (TI's package information in the datasheet). Open the bag on the day. If it has been open longer, bake it per
  J-STD-033 first.
- **Bare board, meter on ohms:** TP2 (20 V), pad 2 of F5 (amplifier supply), TP9 (5 V) and TP16 (3.3 V) each read open
  to TP7 (ground).

**Order**
1. **Paste** the door side through the stencil.
2. **Place the 72 surface-mount parts,** one line of the placing list at a time.
   - Leave nine places empty: R8, R9, R20 to R25, R27. Their pads get paste like the others.
   - D1 and D2: the band is the cathode and goes to pad 1 (red dot on the drawing).
   - U1, U2, U100: pin 1 at the red dot.
   - F1, F2 and F3 share one body: 5 A, 10 A and 1 A. Read the marking.
3. **Hotplate,** door side up. The back is bare, so the board lies flat. Profile below.
4. **Inspect** U100 and U1 under magnification for bridges and lifted pins, then every other joint.
5. **By iron: 13 through-hole parts,** fitted from the door side and soldered on the back, low to high:
   LK1 (tinned copper wire, 1.0 across) · J2 · J1, J8, J9, J5, J6 · J10, J11 · C7 · C5, C6 · PS1.
   - C5, C6, C7: the + lead in pad 1 (red dot). The stripe on the can marks the − lead.
   - PS1: pin 1 at the end the board marks "+Vo".
   - J2: its pin ends reach only 0.5 behind the board. Solder all 16 contacts and the 4 shell stakes.
   - **Cut the leads of C5, C6, C7 and LK1 to 1.5 or less behind the board.** In the unit the ReSpeaker and the
     display's power lead lie behind the board, and pin ends may stand out 4.0 at most there (`MAIN_env.md` §5).
6. **The 13 Pi signal wires** (J3, J4): cut the terminal off the board end, push the wire in **from the back** and
   solder it **on the door side**. Pad by pad: `gpio-leads.md`. The back prints "PI 1-15" and "PI 35-40".
7. **J7 stays empty.**

**Hotplate profile**
- Follow the paste maker's profile. Chip Quik's chart for SMD291AX (datasheet rev 1.1) runs 25 → 100 → 150 °C, crosses
  the 183 °C melting point and tops at 235 °C, about 240 s in all.
- U100 is rated for 260 °C peak (TI), above that profile.
- U100's thermal pad: the stencil's 2 × 4 windows cover 72.8 % of it; TI asks for 70 to 80 % (SLAS988B 11.1.3.2). The
  39 holes under the pad are part of the footprint and take some solder by design.
- The flux is no-clean: nothing is washed.

**In the unit** (the project's assembly instructions hold the steps): the display's power lead is plugged onto the
display before the board is screwed on. Plugging order on the board: speakers and 20 V, then touch and radar, then the
BME680 and the VEML6030, the Pi's power last.

## Test pads
19 bare round pads, 1.5 across, **on the door side**. No paste, no part. Distances in mm to the pad's centre, from the
board's left edge and from its bottom edge (the edge with the sockets), seen from the door. Map: page 4 of the drawing.

| Pad | Name | Net | From the left edge | From the bottom edge | What it is | Beside it |
|---|---|---|---|---|---|---|
| TP1 | VIN | VIN_EF | 22.5 | 10.3 | 20 V after the fuse F1, before the protection chip | left of R17; below D1 |
| TP2 | 20V | +20V | 31.1 | 19.6 | 20 V after the protection chip | above R5; left of R6 |
| TP3 | IMON | EF_IMON | 40.3 | 12.7 | current monitor, 0.279 V per A on the 20 V bus. **Moved on rev 3.1** (rev 3: 40.3, 13.2) | right of R3; below J11 |
| TP4 | FLT | EF_FLT_N | 37.7 | 20.3 | protection chip fault (low = fault) | right of R6; above R4 |
| TP5 | PG | EF_PGOOD | 34.5 | 21.5 | power good (enables the 5 V module) | above R6; below PS1 |
| TP6 | SHDN | EF_SHDN | 40.8 | 20.4 | shutdown pin | above J11; below PS1 |
| TP7 | GND | GND | 42.3 | 9.2 | ground | right of C3; above J1 |
| TP8 | NID_IN | NID_VIN | 15.5 | 49.8 | 5 V module input, after the coil L1 | above C6; left of R21 |
| TP9 | 5V | +5V | 47.6 | 41.2 | 5 V module output | left of C7; right of C5 |
| TP10 | 5V_F | 5V_PI_F | 50.2 | 14.5 | 5 V after the Pi fuse F2 | right of J11; below LK1 |
| TP11 | EXT5V | VBUS_PI | 51.1 | 11.6 | 5 V at the Pi's USB-C socket | left of J6; above R16 |
| TP12 | RADAR | 5V_RADAR | 9.3 | 10.4 | radar 5 V, after its fuse F3. **Moved on rev 3.1** (rev 3: 12.8, 17.3) | below C10; left of J10 |
| TP13 | TRIM | NID_TRIM | 4.6 | 26.1 | 5 V module trim pin | left of PS1; below R7 |
| TP14 | RC | NID_RC | 4.6 | 32.5 | 5 V module on/off pin | left of PS1; above R7 |
| TP15 | GND | GND | 48.3 | 11.4 | ground | above R18; above R16 |
| TP16 | 3V3 | +3V3 | 27.2 | 21.2 | 3.3 V | right of C12; above D1 |
| TP17 | GND | GND | 21.4 | 14.6 | ground | left of D1; below U2 |
| TP19 | FAULT | AMP_FAULT_N | 67.5 | 52.5 | amplifier fault (low = fault) | above R26; above C119 |
| TP20 | GND | GND | 67.8 | 55.4 | ground | above R26; left of C118 |

- **There is no TP18.** The amplifier's supply is probed at **pad 2 of the fuse F5**, the pad nearer the right-hand
  edge (54.9 from the left edge, 53.3 from the bottom).
- **LK1** is the place for a meter in series with the Pi's 5 V (bench only).
- Seven test pads and the amplifier's thermal pad each have a via in them (TP2, TP7, TP9, TP15, TP17, TP19, TP20;
  U100). No paste goes there, so they were left as they are.

## Bring-up (on the bench, board out of the enclosure)
A meter is enough. Ground: TP7, TP15, TP17 or TP20.

**Stage 1: 20 V only.** The USB-C inlet board and its charger on J1; no Pi, no leads, no sensors.

| Probe | Expect | Why |
|---|---|---|
| TP1, TP2, TP8, pad 2 of F5 | about 20 V, all equal | the protection chip is on above 17.05 V and off above 24.06 V (`NOTES.md` §1) |
| TP3 | 0.279 V per A of bus current: record it | `NOTES.md` §1 |
| TP6 | about 2.7 V | the pin's own open-circuit voltage (SLVSET9G 6.5) |
| TP9; TP10, TP11, TP12 | 4.90 to 5.10 V, all about equal | NID100-5, ± 2 % |
| TP13 | record it | 5 V trim (`NOTES.md` §2) |
| TP16, TP19, TP4 | about 0 V | the 3.3 V regulator waits for the Pi's 3.3 V on wire A1; both fault lines are pulled up to rails that are still off |

**Stage 2: Pi on.**
- Connect J2 to the Pi's USB-C; the three housings of the Pi signal wires (1 × 3 on pins 1-3-5, 2 × 5 on pins 7 to 16,
  2 × 3 on pins 35 to 40); the display's power lead on pins 2-4-6.
- Expect:

| Probe | Expect | Why |
|---|---|---|
| TP16 | 3.267 to 3.333 V | TPS70933, ± 1 % (SBVS186H) |
| TP4, TP19 | about 3.3 V | no fault at the protection chip, none at the amplifier |
| `vcgencmd get_throttled` | `0x0` | bench plan 2.6 |
| `vcgencmd pmic_read_adc EXT5V_V` | 4.87 V or more under load | bench plan 2.6 |

**Stage 3: configuration and buses.** Apply `../notes/pi-config.md`, then plug the BME680 (J10), the VEML6030 (J11), the
touch lead (J6) and the radar (J5).
- `sudo i2cdetect -y 1`: **1b** (touch), **48** (VEML6030), **UU** at 4c (TAS5756M, held by its driver), and the
  BME680 at **76 or 77** (set by the sensor board's own strap).
- Radar: record TP12 with the LD2410C running (the rail's lowest is 4.90 V; the LD2410C manual gives 5 to 12 V). Expect
  no invalid frame at 256000 8N1 on `/dev/ttyAMA0`.
- Then the bench plan's stage 2.

## Earlier revisions
- **Rev 3.2 of 2026-11-14:** rev 3.1 with the relief in the side edge. Report `rev3.2/README.md`; board file
  `rev3.2/main-board-rev3.2-2026-11-14.kicad_pcb`.
- **Rev 3.1 (2026-11-11):** rev 3 with the top right hole moved, two headers moved, wider supply copper and ground
  pours on both outer layers. Report `rev3.1/README.md`.
- **Rev 3 (2026-11-11):** the board laid out again for its site behind the display, every part on the door side.
  Report `rev3/README.md`.
- **Rev 2.1 (2026-11-08):** the board for the earlier site, 90 × 55. Files in `rev2.1/`, with its fab set of
  2026-11-08, which is **not** for this board.
