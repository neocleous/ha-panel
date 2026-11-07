# MAIN_env confirmation — main board, single-sided SMD (rev 2, 2026-11-08)

Replaces the 2026-11-07 two-sided issue. Daniel 2026-11-07 22:48: no SMD on the back; the board grows instead. Outline from
the design chat's answer `claude/report-main-board-outline-2026-11-07.md` (outline T). The layout left T's tab empty (no
parts, no tracks), so the tab was cut off: the board is **T's base, 90 × 55**.
Board frame: KiCad top = Pi side (front), x_board = 45 − x_rel, y_board = 84 − z (y < 0 above the old top edge).

## Board
- **Outline, 90 × 55 × 1.6.** −x top corner cut for the K5 lower LCD-screw lane.

  | world (x_rel, z) | (45, 34) | (45, 89) | (−43, 89) | (−45, 88.5) | (−45, 34) |
  |---|---|---|---|---|---|
  | KiCad (x, y) | (0, 50) | (0, −5) | (88, −5) | (90, −4.5) | (90, 50) |

- **Holes unchanged:** 4 × Ø2.7 NPTH at (x_rel ±41.5, z 37.5 / 80.5); bracket bosses Ø8 clear on the front, screw heads (≥ Ø6.8) clear on the back.
- **4 layers:** L1 front parts + signals, L2 GND plane, L3 power planes (+5V, +20V, PVDD), L4 back signals.
- **Front:** every SMD part, plus the through-hole parts (NID100-5, C5–C7, connectors).
- **Back:** J2 USB4085 (THT), LK1 wire link (THT), through-hole solder joints, and 19 bare test pads (nothing to solder).
- **Assembly:**
  1. Front SMD on the hotplate.
  2. Through-hole parts by iron.
  3. No SMD by iron.

## Heights
| Side | Max | Part | Source | Limit (design chat 2026-11-07) |
|---|---|---|---|---|
| Front | **27.5** | NID100-5 upright, z ≥ 35.8 (unchanged position) | NID100-SPEC 2024-10-30 | ≤ 30 on the base; K7 ≤ 24.2 below z 35.8 ✓ |
| Front | 16 | C5, C6 EEU-FR1J121B Ø10 × 16 | order list rev 4 | |
| Front | 12.5 | C7 Würth 860160572003 | order list rev 4 | |
| Front | 9.8 | JST XH plugs mated | JST XH catalog | |
| Front | 6.5 | L1 SRR1260-150M | order list rev 4 | |
| Front | 5.4 | L100–L103 CSBA0850 | CODACA 2026-03-16 | |
| Front | 2.94 | F1–F4 NANO2 (now on the front) | Littelfuse 451/453 rev 2013-12-19 | |
| Front | < 2.7 | D1, D2 SMB | package standard | |
| Front | 1.80 | F5 2920L260/33DR (now on the front) | DigiKey listing | |
| Back | **3.46** | J2 USB4085-GF-A | GCT drawing rev B 2023-02-28 | ≤ 3.5 ✓ (back gap ≥ 10 at J2) |
| Back | 2.9 | NID pins below the board (4.5 − 1.6); other through-hole joints lower | NID100-SPEC | ≤ 2.9 outside the bare zones ✓ |

Zone checks:
- **K5 −x top corner** (x_rel < −41.5, z > 83.5; front 26 → 6): no parts.
- **New top strip z 84–89** (front ≤ 30): F3 NANO2, D2 SMB and R19 only.
- **Strip z 34–35.8** (front ≤ 24.2 in the K7 band): R11 and R18 (0603), plus the edges of the J1/J8 courtyards. The J1 and J8 bodies stay at z ≥ 35.8 as before.
- **Back bare zones** (top corners: x_rel < −38 or > 43.5, above z 82): no test pads and no through-hole joints.

## Connector positions
Unchanged from the 2026-11-07 issue (same world positions, same KiCad coordinates); every K20 cut length stands:

| Ref | Function | Side | Position |
|---|---|---|---|
| J1 | 20 V pigtail, B2B-XH-A | front | pins x_rel ±1.25, z 39.23; body z 35.82–41.57 |
| J2 | Pi USB-C, USB4085-GF-A | back | x_rel 25.0 ± 4.47, mouth flush with the bottom edge (z 34); axis 1.88 behind the back face (y −66.88) |
| J3 | GPIO landing A, 2 × 5 wire pads | front | odd pins z 46.45, even z 48.99; x_rel −9.42 … −19.58 |
| J4 | GPIO landing B, 2 × 2 wire pads | front | pins 1/2 z 49.01, 3/4 z 46.47; x_rel −0.02 / −2.56 |
| J5 | radar, B4B-XH-A | front | pins z 80.53, x_rel −26.95 … −34.45 |
| J6 | touch board, B4B-XH-A | front | pins z 60.52, x_rel 7.75 … 0.25 |
| J7 | D4a tap, 1 × 8 wire pads | front | z 42.0, x_rel −9.11 … −26.89 |
| J8 | speaker L, B2B-XH-A (90°) | front | pins x_rel 34.02, z 38.75 / 41.25 |
| J9 | speaker R, B2B-XH-A | front | pins z 40.52, x_rel −31.75 / −34.25 |
| J10 | BME680 + VEML6030 landing, 2 × 4 | front | pins x_rel −18.42 / −20.97, z 73.69 … 81.31 |
| LK1 | Pi-branch wire link | back | pads x_rel 10.19 / 17.81, z 37.7 |

## For the enclosure session
- Main-board body: the outline above. The base top edge rises 84 → 89 (5 mm), within T.
- **No tab:**
  - The reach over the board's top centre stays as the design chat measured it for the base. The front-face leads (J1, J5, J6, J8, J9) may go back to being plugged after mounting; please confirm with the 5 mm higher edge.
  - The door's closest approach is the design chat's base value, not the tab's 1.1 mm.
- **Door and clash checks** to re-run on this outline.
- **V23** (BME680/VEML6030 leads to J10) still open; J10 doesn't move.
