# HA panel — main board

Status: **block 2 — layout rev 2.1, single-sided SMD, routed, DRC clean (2026-11-08).** Rev 2.1 moves C7 to the top strip so every front lead plugs after mounting (`MAIN_env.md`). Fab files, BOM and assembly notes follow in block 3.

- **KiCad 9.0.9.** Open `main-board.kicad_pro`. Project libraries: `lib/ha_panel.kicad_sym` (custom symbols: TAS5756M, TPS16630, NID100-5, TPS70933, +20V power symbol) and `lib/ha_panel.pretty` (custom footprints, created in block 2).
- **Schematic PDF:** `main-board-schematic.pdf` (5 pages).
- **ERC:** 0 errors, 0 warnings (`erc-report.txt`). **DRC:** 0 errors, 0 unconnected, parity clean, 2 warnings (J2 silk trimmed at the board edge, J4 courtyard trimmed to its wire pads) (`drc-report.txt`).
- **Board:** 90 × 55, 4 layers (F parts + signals / In1 GND / In2 +5V, +20V, PVDD / B signals). Every SMD part on the front; the back carries only J2, LK1, through-hole joints and bare test pads. Renders: `main-board-routed-3d.png` (front, back), `main-board-copper-F-B.png` (front copper, back copper mirrored). Layout notes: `NOTES.md` §7; envelope: `MAIN_env.md`.
- **Fab (JLC, bare board):** `fab/main-board-jlc-2026-11-08.zip`; order options and what the files use against JLC's limits in `../notes/jlc-fab.md`.
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
