# MAIN_env: main board rev 3.1, outline, holes and heights (2026-11-11)

For the enclosure model. These are sections 3 to 5 of the reply to the enclosure chat
(`main-board-rev3-1-reply-2026-11-11.md`, also `claude/main-board-rev3-1-reply-2026-11-11.md` in the project); what
moved, the connector table, the STEP files and the open points are in that document. Earlier files:
`rev3/MAIN_env.md` (rev 3), `rev2.1/MAIN_env.md`.
Frame: the site document's board frame, seen from the door: u to the right, v up, w out of the door-side face, origin
in the middle of the board, mm.
Section numbers in the text are those of the reply.

**Changed against rev 3:** hole H2 at u +19.20, v +25.00 (was +30.00, +25.00); the same bare circles at all four
holes; the boxes and pin ends of the BME680 header J10 (pins at u -30.40) and the VEML6030 header J11 (pins at
v -13.00); three corrected figures: pin headers 8.54 bare (was 8.65), JST pin ends 1.8 (was 1.9), pin header pin ends
1.4 (was 1.5).

## 3. Outline, holes, mounting
- **Outline:** rectangle, u -43.5...+43.5, v -28.95...+28.95, square corners, 1.6 thick. Unchanged. Nothing overhangs
  the top or side edges. At the bottom edge only the Pi power plug passes (it leaves downward).
- **Holes:** four, 3.2 across, not plated, for the unit's standard M3 x 8 button-head screw (head 5.7 across, 1.65 high,
  site section 2).

| Hole | u | v | Band (site section 2) | Nearest display mounting point |
|---|---|---|---|---|
| H1 | -37.00 | +22.00 | top band v +18.0...+25.5 | 18.2 |
| H2 | +19.20 | +25.00 | new zone u -12.0...+22.7, v +21.6...+25.5 | 19.9 |
| H3 | -31.00 | -25.25 | bottom band v -25.25 +/- 0.2 | 12.1 |
| H4 | +31.00 | -25.25 | bottom band v -25.25 +/- 0.2 | 8.1 |

- **Bare circles round all four holes, the same at each** (no track, via or poured copper on the outer layers): door
  side 3.5 radius, back face 4.1 radius. Measured on the board file: the nearest copper is the poured ground, 3.49 and
  4.09 from each centre. **The post's whole 8 mm face sits on bare board at all four.** The exception at H2 and the
  request for a 5.5 contact face are gone.
- **Clear zones** (7 across on the door side, 9 across on the back): no part outline inside the 7, no through-hole
  joint inside the 9.
- **Round the new H2:**
  - Door side, nearest part outlines to its centre: two bare test pads at 3.51 and 3.76 (their copper is 0.55 further),
    R27's place (not fitted) at 4.03, R26 (0.7 tall) at 4.19, two capacitors (1.0 tall) at 6.35 and 6.49, the amplifier
    fuse (1.8 tall) at 6.55. The screw head is 2.85 radius.
  - Back face: one via of the audio bit clock, 0.45 across, has its edge 4.25 from the hole's centre: 0.25 outside the
    post's face, inside the 9 mm zone. It is flush with the face (the fab note has plugged vias for this board,
    `../notes/jlc-fab.md`). No joint, nothing that stands out.
  - A post 8 across at (+19.20, +25.00) covers u +15.2...+23.2, v +21.0...+29.0. To the box you assumed for the
    display's power plug (u +27.25...+33.45): 4.05.
- **Fasteners:** four M3 x 8 button head into Ruthex M3 x 5.7 inserts, as planned.

## 4. Heights on the door side (w above the door-side face)
Everything not listed is 3.0 or lower. Screw heads at the four holes: 1.65.

| Part | What | u | v | Height w | Allowed there | Limit from | Source of the height |
|---|---|---|---|---|---|---|---|
| PS1 | NID100-5 | -37.4...+14.0 | -4.6...+8.0 | 27.5 | 28.9 | cap side-screw key path | NID100-SPEC 2024-10-30 (27.5 +/- 1) |
| C5 | 120u 63V | -8.3...+2.3 | +8.6...+19.2 | 16.0 | 33.0 | door | EEU-FR1J121B dia 10 x 16 (MAIN_env rev 2.1) |
| C6 | 120u 63V | -32.3...-21.7 | +8.6...+19.2 | 16.0 | 24.0 | cap back-screw key path | EEU-FR1J121B dia 10 x 16 (MAIN_env rev 2.1) |
| C7 | 22u 35V | +5.7...+11.3 | +8.6...+14.2 | 12.5 | 35.0 | door | Wurth 860160572003, 12.5 max (MAIN_env rev 2.1) |
| L1 | 15u SRR1260 | -21.5...-8.5 | +8.6...+21.7 | 6.5 | 32.0 | door | MAIN_env rev 2.1 (KiCad model: 6.0) |
| L100 | 10u | +30.6...+40.8 | -19.0...-9.4 | 5.4 | 40.0 | door | MAIN_env rev 2.1 (CODACA: body 5.1) |
| L101 | 10u | +30.6...+40.8 | -9.4...+0.2 | 5.4 | 33.0 | door | MAIN_env rev 2.1 (CODACA: body 5.1) |
| L102 | 10u | +20.4...+30.6 | -9.4...+0.2 | 5.4 | 35.0 | cap side-screw key path | MAIN_env rev 2.1 (CODACA: body 5.1) |
| L103 | 10u | +20.4...+30.6 | -19.0...-9.4 | 5.4 | 42.0 | door | MAIN_env rev 2.1 (CODACA: body 5.1) |
| J1 | 20 V in socket | -4.2...+4.2 | -28.9...-22.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 51.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J8 | speaker left socket | +34.5...+43.0 | -28.9...-22.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 44.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J9 | speaker right socket | -43.2...-34.8 | -28.9...-22.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 46.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J6 | touch board socket | +9.4...+16.2 | -28.9...-15.4 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 48.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J5 | radar socket | -43.2...-36.4 | -20.6...-7.1 | 7.00 bare; 9.8 mated (JST); 20 with the lead bend | 40.0 | door | JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue) |
| J10 | BME680 socket | -32.2...-28.6 | -19.7...-8.5 | 8.54 bare; about 16.5 with the housing (estimate); 25 with the lead bend | 41.9 | cap side-screw key path | pin header, KiCad model 8.54 (generic part, chosen with the parts list: not verified; with a Dupont housing about 16.5, estimate) |
| J11 | VEML6030 socket | -6.3...+4.9 | -14.8...-11.2 | 8.54 bare; about 16.5 with the housing (estimate); 25 with the lead bend | 47.0 | door | pin header, KiCad model 8.54 (generic part, chosen with the parts list: not verified; with a Dupont housing about 16.5, estimate) |
| J2 | Pi power socket | +16.3...+26.9 | -29.5...-19.2 | 3.46; the plug hangs below the edge | 48.0 | door | GCT drawing USB4085 rev B |

- "Allowed there" is the lowest allowed height over the part's box, from the site document's height grid and key paths.
- **Changed against rev 3:** the boxes of J10 and J11 (section 2), and the bare height of the two pin headers, 8.54
  (the rev 3 table said 8.65; section 8). No height limit is touched by either.
- **Plugs:** the JST sockets are 7.0 bare, 9.8 with the plug in (JST catalogue), and I allow 20 for plug plus the bend of
  the lead (the site's figure). The two sensor headers are 8.54 bare, about 16.5 with a Dupont housing on (estimate),
  and I allow 25 with the bend (my estimate). The Pi power plug hangs below the bottom edge; its size is that of the
  lead chosen and is not in my documents.
- **Between the radar socket and the BME680 header** (4.14 between their boxes) now stand the radar fuse (2.94 tall),
  the radar capacitor (1.5) and a bare test pad. The radar plug's top is at 9.8.
- **Supply module PS1:** 50.8 x 12 on the board, 27.5 +/- 1 tall, standing on one row of 13 pins at v -0.3. Unchanged.

Plugged connectors and the nearest part that is taller than the mated plug (for the reach check):

| Connector | Plug top w | Nearest taller part | Its height | Gap between the boxes | Direction from the connector |
|---|---|---|---|---|---|
| J9 | 9.8 | J10 | 16.5 | 3.5 | above (+v) toward +u |
| J1 | 9.8 | J11 | 16.5 | 7.3 | above (+v) |
| J6 | 9.8 | J11 | 16.5 | 4.5 | above (+v) toward -u |
| J8 | 9.8 | PS1 | 27.5 | 26.9 | above (+v) toward -u |
| J5 | 9.8 | PS1 | 27.5 | 2.5 | above (+v) |
| J10 | 16.5 | PS1 | 27.5 | 3.9 | above (+v) |
| J11 | 16.5 | PS1 | 27.5 | 6.6 | above (+v) |

## 5. Back face
No parts. Under solder mask: tracks, poured ground, vias, and printed connector names. What stands out of the face are
the ends of the through-hole pins:

| Part | Pin ends at u | at v | Beyond the back face | Allowed there | Zone | Basis |
|---|---|---|---|---|---|---|
| C5 | -5.5...-0.5 | +13.9...+13.9 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| C6 | -29.5...-24.5 | +13.9...+13.9 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| C7 | +7.5...+9.5 | +11.4...+11.4 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| J1 | -1.2...+1.2 | -25.0...-25.0 | 1.8 | 12.0 | bottom band | post 3.4 below the seating plane (JST XH catalogue; the KiCad model agrees) - 1.6 |
| J2 | +17.3...+25.9 | -24.7...-20.3 | 0.5 | 4.0 | over the ReSpeaker | shell stakes 2.10, signal tails 1.60 (GCT drawing) - 1.6 |
| J3 | -25.3...-15.1 | -27.0...-24.5 | 1.5 | 12.0 | bottom band | wire pads: the Pi signal wires enter from this face and are soldered on the door side (step 3). No joint here; the wire itself leaves the face on the route of the enclosure. 1.5 kept as an allowance (assumed) |
| J4 | +5.7...+8.2 | -27.0...-24.5 | 1.5 | 12.0 | bottom band | wire pads: the Pi signal wires enter from this face and are soldered on the door side (step 3). No joint here; the wire itself leaves the face on the route of the enclosure. 1.5 kept as an allowance (assumed) |
| J5 | -40.3...-40.3 | -17.6...-10.1 | 1.8 | 4.0 | over the ReSpeaker | post 3.4 below the seating plane (JST XH catalogue; the KiCad model agrees) - 1.6 |
| J6 | +12.3...+12.3 | -25.9...-18.4 | 1.8 | 4.0 | over the ReSpeaker | post 3.4 below the seating plane (JST XH catalogue; the KiCad model agrees) - 1.6 |
| J7 | -29.5...-11.7 | +24.2...+24.2 | 1.5 | 5.0 | top band | wire pads (second echo-reference option only) |
| J8 | +37.5...+40.0 | -25.0...-25.0 | 1.8 | 12.0 | bottom band | post 3.4 below the seating plane (JST XH catalogue; the KiCad model agrees) - 1.6 |
| J9 | -40.2...-37.8 | -25.0...-25.0 | 1.8 | 12.0 | bottom band | post 3.4 below the seating plane (JST XH catalogue; the KiCad model agrees) - 1.6 |
| J10 | -30.4...-30.4 | -17.9...-10.3 | 1.4 | 4.0 | over the ReSpeaker | pin 3.0 below the seating plane (KiCad model; generic part, not verified) - 1.6 |
| J11 | -4.5...+3.1 | -13.0...-13.0 | 1.4 | 4.0 | over the ReSpeaker | pin 3.0 below the seating plane (KiCad model; generic part, not verified) - 1.6 |
| LK1 | +6.9...+14.5 | -11.2...-11.2 | 1.5 | 4.0 | over the ReSpeaker | wire cut after soldering (assumed) |
| PS1 | -35.8...+12.5 | -0.3...-0.3 | 2.9 | 4.0 | over the ReSpeaker | pins 4.5 long (NID100-SPEC) - 1.6 |

- **Changed against rev 3:** the pin ends of J10 (now at u -30.4) and J11 (now at v -13.0), and two figures: JST
  sockets 1.8 (the rev 3 table said 1.9), pin headers 1.4 (1.5). Section 8.
- Pin protrusion: JST sockets 1.8, pin headers 1.4, supply module 2.9, USB-C socket 0.5. The leads of C5, C6, C7 and the
  wire link are cut to 1.5 or less after soldering (an assembly instruction).
- **Where the display's power lead runs** (v +14.0...+17.1 to u -42.1, then the -u edge u -43.6...-40.6): radar socket
  1.8, right speaker socket 1.8, C5 and C6 1.5. The limit is 4.0. The BME680 header's pins (1.4) are 10.2 from the
  -u edge strip (rev 3: 6.3).
- **In front of the -u microphone lead's strip** (u -34.5...-30.5): supply module pins 11 and 12 at u -30.7 and -33.2,
  v -0.3 (2.9 beyond the face), as before; the BME680 header's four pins now at the strip's +u edge, u -30.40,
  v -17.92...-10.30 (1.4 beyond the face). The parts that moved into that area are surface-mount: nothing of them
  comes through the board.
- **J3 and J4:** no joint on this face. The 13 wires go in here (section 6).
- No through-hole joint stands over the ReSpeaker's header (bare), over its jack (0.9 allowed), beside its USB plug
  (1.4) or inside a post zone.
