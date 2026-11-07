# MAIN_env confirmation — main board placement (block 2, 2026-11-07)

Placement state: `main-board.kicad_pcb` (placed, routing in progress). Board frame: KiCad top = Pi side (front),
x_board = 45 − x_rel, y_board = 84 − z. World frame as the enclosure scripts (x_rel from XC −2.55, +x = viewer's left).

## Board
- 90 × 50 × 1.6, outline and holes unchanged: 4 × Ø2.7 NPTH at (x_rel ±41.5, z 37.5 / 80.5); bracket bosses Ø8 kept
  clear on the front, screw heads (Ø6, kept clear ≥ Ø6.8) on the back.
- **4 layers** (decision 6): L1 front parts + signals, L2 GND plane, L3 power planes (+5V, +20V, PVDD), L4 back parts + signals.
- **Two-sided** (decision 6): front = NID100-5, electrolytics, L1, LC inductors, TAS5756M, TPS16630, PTC F5, connectors, the
  amp's bootstrap and 0.1 µF PVDD caps; back = iron-solderable SMD (0603–1206 R/C, SOT-23-5, SMB TVS, NANO2 fuses),
  J2 USB4085 (THT), LK1 wire link (THT), all test pads (bare SMD pads, nothing to solder).

## Heights
| Side | Max | Part | Source | Envelope |
|---|---|---|---|---|
| Front | **27.5** | NID100-5 upright (seated on its pins) | NID100-SPEC 2024-10-30 | ≤ 30 (MAIN_front_env) ✓ |
| Front | 16 | C5, C6 EEU-FR1J121B Ø10 × 16 | order list rev 4 | |
| Front | 12.5 | C7 Würth 860160572003 Ø5 × 12.5 max | order list rev 4 | |
| Front | 9.8 | JST XH plugs mated | JST XH catalog (envelope sheet) | |
| Front | 6.5 | L1 SRR1260-150M | order list rev 4 | |
| Front | 5.4 | L100–L103 CSBA0850 (5.1 ± 0.3) | CODACA 2026-03-16 | |
| Back | **3.46** | J2 USB4085-GF-A | GCT drawing rev B 2023-02-28 | ≤ 3.5 (MAIN_back_env) ✓ |
| Back | 2.94 | F1–F3 NANO2 (2.69 ± 0.25) | Littelfuse 451/453 rev 2013-12-19 | |
| Back | < 2.7 | D1, D2 SMB (DO-214AA) | package standard; datasheet check in block 3 | |
| Back | 2.9 | NID pins below the board (4.5 − 1.6) | NID100-SPEC | |

- No front body below z 35.8 (K7 / MAIN_front_env): lowest bodies J1 (z 35.82), J8 (z 36.3), J9 (z 37.1).
- K19 front strip x_rel < −41.45: tallest part there is L101/L102 at 5.4 (< 26.4 allowed).
- Back top corners (door contact): no parts in the 9 × 9 mm corners, only the screw heads.

## Connector positions (world, body or pad centres)
| Ref | Function | Side | Position | Was (K20 / decision 2) |
|---|---|---|---|---|
| J1 | 20 V pigtail, B2B-XH-A | front | pins at x_rel ±1.25, z 39.23; body z 35.82–41.57 | landing (0, z 37.5): +1.2 mm in z so the body stays above z 35.8 |
| J2 | Pi USB-C, USB4085-GF-A | back | x_rel 25.0 ± 4.47, mouth flush with the bottom edge (z 34); axis 1.88 behind the back face (y −66.88) | plug x_rel 18.8–31.2, z 14.0–33.9 unchanged; axis 0.15 mm further back than the USB4105 |
| J3 | GPIO landing A (plug A, 9 leads), 2 × 5 wire pads | front | odd pins z 46.45, even pins z 48.99; pin 1/2 at x_rel −9.42, pin 9/10 at −19.58 | landing x_rel −20…0, z 45–50 ✓ |
| J4 | GPIO landing B (plug B, 4 leads), 2 × 2 | front | pins 1/2 z 49.01, 3/4 z 46.47; x_rel −0.02 / −2.56 | ✓ |
| J5 | radar, B4B-XH-A | front | pins z 80.53, x_rel −26.95 … −34.45 (body centre −30.7) | (−30.7, z 80) ✓ |
| J6 | touch board, B4B-XH-A | front | pins z 60.52, x_rel 7.75 … 0.25 (body centre 4.0) | (4, z 60) ✓ |
| J7 | D4a tap, 1 × 8 wire pads | front | z 42.0, x_rel −9.11 … −26.89 | new position (Option B only) |
| J8 | speaker L, B2B-XH-A (rotated 90°) | front | pins x_rel 34.02, z 38.75 / 41.25 (body centre x_rel 33.5, z 40) | (33, z 40): +0.5 mm, clear of the USB4085 stake pads |
| J9 | speaker R, B2B-XH-A | front | pins z 40.52, x_rel −31.75 / −34.25 (body centre −33.0, z 40) | (−33, z 40) ✓ |
| J10 | BME680 + VEML6030 landing, 2 × 4 wire pads (new, decision 5A) | front | pins x_rel −18.42 / −20.97, z 73.69 … 81.31 | new: the sensor leads now end here instead of the touch board |
| LK1 | Pi-branch wire link | back | pads x_rel 10.19 / 17.81, z 37.7 | — |

## Lead consequences for the enclosure session
- Pigtail +1.2 mm (19.4 → ≈ 20.6 routed; cut ≈ 70 unchanged). Speaker L landing 0.5 mm further out (cut ≈ 105 unchanged).
- **BME680 and VEML6030 leads** re-route from the touch board to J10 (x_rel ≈ −19.7, z ≈ 77.5, front face y −63.4):
  new routed lengths and cut lengths are the enclosure session's (V23).
- Touch lead unchanged (the rev D HOST pads keep the rev F position).
