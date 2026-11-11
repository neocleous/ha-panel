# HA panel — main board

> **Rev 3 (2026-11-11): schematic and routed board for the site behind the display are in this folder.**
> 87.0 x 57.9, four layers, every part on the door side. ERC 0 errors 0 warnings; DRC 0 errors, 0 open connections,
> schematic comparison clean, 2 warnings. Report: [`rev3/README.md`](rev3/README.md) (floor plan: sections 1 to 13, routed
> board: section 14). Pi lead table: [`gpio-leads.md`](gpio-leads.md). No fab files for rev 3.
> **Everything below this note describes rev 2.1**, whose files are now in [`rev2.1/`](rev2.1/). All of it is a draft
> until the whole unit is shown to be buildable (architect log 2026-11-10, section 0).

Status: **block 3 done (2026-11-09) — layout rev 2.1, single-sided SMD, routed, DRC clean; fab files, BOM, assembly notes and drawing issued.** Rev 2.1 moves C7 to the top strip so every front lead plugs after mounting (`MAIN_env.md`).

- **KiCad 9.0.9.** Open `main-board.kicad_pro`. Project libraries: `lib/ha_panel.kicad_sym` (custom symbols: TAS5756M, TPS16630, NID100-5, TPS70933, +20V power symbol) and `lib/ha_panel.pretty` (custom footprints, created in block 2).
- **Schematic PDF:** `main-board-schematic.pdf` (5 pages).
- **ERC:** 0 errors, 0 warnings (`erc-report.txt`). **DRC:** 0 errors, 0 unconnected, parity clean, 2 warnings (J2 silk trimmed at the board edge, J4 courtyard trimmed to its wire pads) (`drc-report.txt`).
- **Board:** 90 × 55, 4 layers (F parts + signals / In1 GND / In2 +5V, +20V, PVDD / B signals). Every SMD part on the front; the back carries only J2, LK1, through-hole joints and bare test pads. Renders: `main-board-routed-3d.png` (front, back), `main-board-copper-F-B.png` (front copper, back copper mirrored). Layout notes: `NOTES.md` §7; envelope: `MAIN_env.md`.
- **Fab (JLC, bare board):** `fab/main-board-jlc-2026-11-08.zip`; order options and what the files use against JLC's limits in `../notes/jlc-fab.md`. **Stencil:** the main-board area of the combined stencil `../stencil/` (D57).
- **Assembly drawing:** `main-board-assembly.pdf` (A3; front and back, DNP crossed out), from `gen/assembly_drawings.py`. Assembly and bring-up: below.
- **Notes with every value's source:** `NOTES.md`. **GPIO lead pin table and plug maps:** `gpio-leads.md`.
- `gen/` holds the Python that generated the schematic and the layout (sheet builder, footprints, placement, TAS escape, maze router, Freerouting driver, silk placement). The KiCad files are the source of truth; the scripts are kept for provenance (symbol UUIDs are deterministic, so a schematic regeneration keeps the PCB links; a layout regeneration routes differently, see NOTES §7).

## Sheets
1. Root — index.
2. **20 V inlet and eFuse** — J1 (5807 pigtail) → F1 0453005.MR → TPS16630 (UVLO 17.05 V, OVP 24.06 V, I_OL 3.28 A, dV/dt 19.6 ms) → +20V bus with SMBJ22A.
3. **5 V supply and outputs** — Mean Well EMC circuit (120 µF – SRR1260-150M – 120 µF) → NID100-5 (enabled by the eFuse PGOOD) → 22 µF + SMBJ6.0A-E → Pi branch (0453010.MR → wire link LK1 → USB4085-GF-A, Rp 10 kΩ) and radar branch (0453001.MR). DNP trim network R8/R9.
4. **3.3 V, Pi link, XH, D4a** — TPS70933 LDO (EN = Pi 3V3) → sensor PTC and amp logic rail; GPIO landing J3/J4 (13 wire pads); radar and touch XH headers; D4a ReSpeaker tap J7 with six DNP 0 Ω links.
5. **Amplifier** — TAS5756M stereo BTL per SLAS988B Fig. 79 / Table 22 with the DigiAMP+ wiring (`rpi-digiampplus`: I²C 0x4C, GPIO22 mute), 20 dBV at 768 kHz, type-2 LC 10 µH + 0.68 µF, speaker XH headers.

## Default fit (spin 1)
| Option | Default | Alternative |
|---|---|---|
| Echo reference (D4a) | **Topology A, USB reference**: R20–R25 open | Topology B, I²S reference: fit R20–R23 (+R24/R25), I²S firmware, Pi as I²S clock consumer |
| NID trim (V20) | R8, R9 open (5.0 V) | R8 Trim→Com raises Vout; value found on the bench via TP13 |
| Amp logic rail | R26 fitted (board LDO) | R27 instead of R26 (Pi 3V3) |
| I²S series | R14–R16 0 Ω | 22–47 Ω if edges ring |
| NID enable | R7 0 Ω (eFuse PGOOD) | R7 open = NID free-running |
| Pi branch | LK1 wire fitted | LK1 open + 10 A meter (bench 2.7) |

## Assembly (block 3, 2026-11-09)
One hotplate pass for every SMD part (front), then the THT parts with the iron. Drawing: `main-board-assembly.pdf`.

**Before you start**
- Paste: Sn63/Pb37 no-clean, as on rev C (Chip Quik SMD291AXT4, `hardware/rev-c/README.md`). Stencil: the main-board area of `../stencil/`, 0.12 mm.
- U100 (TAS5756M) is MSL 3: "Level-3-260C-168 HR" (TI package option addendum in the datasheet), i.e. 168 h at ≤ 30 °C / 60 % RH once its moisture bag is open. Open the bag on build day. If it has been open longer, bake per J-STD-033 before reflow.
- Bare board, meter on ohms: +20V (TP2), PVDD (F5 pin 2), +5V (TP9) and 3V3 (TP16) to GND (TP7) must read open.

**Build order**
1. Paste the front through the stencil. Place every SMD part except the DNPs: R8, R9, R20–R25, R27 (crossed out on the drawing).
   - Polarity: D1 SMBJ22A, D2 SMBJ6.0A-E (band = cathode).
   - Pin 1: U1 TPS16630, U2 TPS70933, U100 TAS5756M (chamfered corner on the drawing).
2. Hotplate with the back down (nothing is on the back yet). Profile below.
3. Inspect U100 (0.5 mm pitch) and U1 (0.65 mm) under magnification for bridges and lifted pins.
4. Iron, door side first, because these joints are on the front among the SMD parts:
   - J2 USB4085 (16 contacts, 4 shell stakes), mouth flush with the bottom edge;
   - LK1, 1.0 mm tinned copper wire.
5. Iron, front parts soldered on the back, low to high: J10 (2 × 4 header), J1, J5, J6, J8, J9 (XH), C7, C5, C6 (+ to the + mark), PS1 NID100-5 last.
6. J3/J4 take the GPIO lead wires (`gpio-leads.md`, `../notes/harness.md`). J7 stays empty in topology A.

**Hotplate profile**
- Follow the paste maker's profile. Chip Quik's chart for SMD291AX (datasheet rev 1.1) runs 25 → 100 → 150 °C (preheat and soak), crosses the 183 °C liquidus and tops at 235 °C, about 240 s in all.
- U100 is rated 260 °C peak (TI, above), so a Sn63/Pb37 profile stays below its limit.
- Thermal pad (pin 49): the stencil's 2 × 4 windows give 72.8 % paste coverage. SLAS988B 11.1.3.2 asks for 70–80 %. The 39 vias under the pad are in the footprint.
- The paste's flux is "Synthetic No-Clean" (Chip Quik), so nothing is washed.

**Default fit:** the table above. All D4a links open (topology A), R26 fitted, LK1 fitted.

## Bring-up (bench, board out of the enclosure)
Meter only; test pads are on the back (`NOTES.md` §5). Ground: TP7, TP15, TP17 or TP20.

**Stage 1: 20 V only.** The 5807 + charger on J1; no Pi, leads or sensors.

| Probe | Expect | Why |
|---|---|---|
| TP1 VIN, TP2 20V, TP8 NID_IN, F5 pin 2 (PVDD; front, bench only) | ≈ 20 V, all equal | eFuse on above UVLO 17.05 V; OVP at 24.06 V (`NOTES.md` §1) |
| TP3 IMON | 0.279 V/A × bus current: record it | eq. 9, `NOTES.md` §1 |
| TP6 SHDN | ≈ 2.7 V | internal open-circuit voltage (SLVSET9G 6.5) |
| TP9 5V; TP10 5V_F, TP11 EXT5V, TP12 RADAR | 4.90–5.10 V, all ≈ equal | NID100-5 ± 2 % (bench plan 2.12) |
| TP13 TRIM | record (V20) | `NOTES.md` §2 |
| TP16 3V3, TP19 FAULT, TP4 FLT | ≈ 0 V | The LDO waits for the Pi's 3V3 on lead A1 (EN, R13 pull-down); FLT and FAULT are pulled up to rails that are still off. |

**Stage 2: Pi on.**
- Connect:
  - J2 → Pi USB-C;
  - GPIO plugs A and B;
  - the LCD lead per `../notes/harness.md`: 5 V and GND at Pi pins 2/6. Insulate and tie back its SDA/SCL wires (V22).
- Expect:

| Probe | Expect | Why |
|---|---|---|
| TP16 3V3 | 3.267–3.333 V | TPS70933 ± 1 % (SBVS186H) |
| TP4 FLT, TP19 FAULT | ≈ 3.3 V | no eFuse fault, no amp fault |
| `vcgencmd get_throttled` | `0x0` | bench plan 2.6 |
| `vcgencmd pmic_read_adc EXT5V_V` | ≥ 4.87 V under load | bench plan 2.6 |

**Stage 3: config and buses.** Apply `../notes/pi-config.md`, then plug the sensors (J10), the touch lead (J6) and the radar (J5).
- `sudo i2cdetect -y 1`: **1b** (touch), **48** (VEML6030), **UU** at 4c (TAS5756M, held by the `rpi-digiampplus` driver), **77** (BME680).
- Radar: record TP12 with the LD2410C running (the rail's worst case is 4.90 V; the LD2410C manual gives 5–12 V). Expect 0 invalid frames at 256000 8N1 on `/dev/ttyAMA0` (bench plan 1.5, 2.12).
- Then bench plan stage 2 (2.1–2.12).
