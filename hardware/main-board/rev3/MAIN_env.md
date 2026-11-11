# MAIN_env: main board rev 3, outline, holes and heights (2026-11-11)

For the enclosure model. These are sections 2 to 4 of the reply to the enclosure chat
(`main-board-rev3-reply-2026-11-11.md`, also `claude/main-board-rev3-reply-2026-11-11.md` in the project); the connector
table, the STEP files and the open points are in that document. The rev 2.1 file is `rev2.1/MAIN_env.md`.
Frame: the site document's board frame, seen from the door: u to the right, v up, w out of the door-side face, origin
in the middle of the board, mm.

## 2. Outline, holes, mounting
- **Outline:** rectangle, u -43.5...+43.5, v -28.95...+28.95, square corners, 1.6 thick. Nothing overhangs the top or
  side edges. At the bottom edge only the Pi power plug passes (it leaves downward).
- **Holes:** four, 3.2 across, not plated, for the unit's standard M3 x 8 button-head screw (head 5.7 across, 1.65 high,
  site section 2).

| Hole | u | v | Band (site section 2) | Nearest display mounting point |
|---|---|---|---|---|
| H1 | -37.00 | +22.00 | top band v +18.0...+25.5 | 18.2 |
| H2 | +30.00 | +25.00 | top band v +18.0...+25.5 | 9.1 |
| H3 | -31.00 | -25.25 | bottom band v -25.25 +/- 0.2 | 12.1 |
| H4 | +31.00 | -25.25 | bottom band v -25.25 +/- 0.2 | 8.1 |

- **Copper-free circles round the holes** (no track, via or poured copper on the outer layers): door side 3.5 radius
  (H2: 3.3), back face 4.1 radius (H2: 2.8). No part stands inside the site's clear zones (7 across on the door side,
  9 across on the back).
- **H2 is the exception, and the request.** The amplifier's own tracks and two vias, carried over unchanged from rev 2.1,
  lie on the back face 2.9 to 3.7 from the centre of H2, under solder mask. A post face of 8 across (4.0 radius) would
  sit on them. Daniel decided (2026-11-11) to ask you for this: **the face of the H2 post that touches the board no
  larger than 5.5 across.** With the insert in the post (hole 4.0, 1.6 of wall round it) the post itself cannot be
  5.5; what is meant is a contact face of 5.5, for example the rim of the post set back by a few tenths outside 5.5.
  If that cannot be printed, say so: the alternatives are leaving the post as it is (mask on plastic, no electrical
  contact) or re-routing that corner of the amplifier. H1, H3 and H4 need nothing.

## 3. Heights on the door side (w above the door-side face)
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
| J10 | BME680 socket | -36.1...-32.5 | -19.7...-8.5 | 8.65 bare; about 16.5 with the housing (estimate); 25 with the lead bend | 41.9 | cap side-screw key path | pin header, KiCad model (with a Dupont housing about 16.5, estimate) |
| J11 | VEML6030 socket | -6.3...+4.9 | -13.8...-10.2 | 8.65 bare; about 16.5 with the housing (estimate); 25 with the lead bend | 47.0 | door | pin header, KiCad model (with a Dupont housing about 16.5, estimate) |
| J2 | Pi power socket | +16.3...+26.9 | -29.5...-19.2 | 3.46; the plug hangs below the edge | 48.0 | door | GCT drawing USB4085 rev B |

- "Allowed there" is the lowest allowed height over the part's box, from the site document's height grid and key paths.
- **Plugs:** the JST sockets are 7.0 bare, 9.8 with the plug in (JST catalogue), and I allow 20 for plug plus the bend of
  the lead (the site's figure). The two sensor headers are 8.65 bare, about 16.5 with a Dupont housing on (estimate),
  and I allow 25 with the bend (my estimate). The Pi power plug hangs below the bottom edge; its size is that of the
  lead chosen and is not in my documents.
- **Supply module PS1:** 50.8 x 12 on the board, 27.5 +/- 1 tall, standing on one row of 13 pins at v -0.3. It is the
  tallest part by 11.5.

Plugged connectors and the nearest part that is taller than the mated plug (for the reach check):

| Connector | Plug top w | Nearest taller part | Its height | Gap between the boxes | Direction from the connector |
|---|---|---|---|---|---|
| J9 | 9.8 | J10 | 16.5 | 2.4 | above (+v) |
| J1 | 9.8 | J11 | 16.5 | 8.3 | above (+v) |
| J6 | 9.8 | J11 | 16.5 | 4.8 | above (+v) toward -u |
| J8 | 9.8 | PS1 | 27.5 | 26.9 | above (+v) toward -u |
| J5 | 9.8 | J10 | 16.5 | 0.2 | toward +u |
| J10 | 16.5 | PS1 | 27.5 | 3.9 | above (+v) |
| J11 | 16.5 | PS1 | 27.5 | 5.6 | above (+v) |

## 4. Back face
No parts. Under solder mask: tracks, ground pour, and printed connector names. What stands out of the face are the
ends of the through-hole pins:

| Part | Pin ends at u | at v | Beyond the back face | Allowed there | Zone | Basis |
|---|---|---|---|---|---|---|
| C5 | -5.5...-0.5 | +13.9...+13.9 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| C6 | -29.5...-24.5 | +13.9...+13.9 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| C7 | +7.5...+9.5 | +11.4...+11.4 | 1.5 | 4.0 | over the ReSpeaker | leads cut after soldering (assumed, to be kept to on the bench) |
| J1 | -1.2...+1.2 | -25.0...-25.0 | 1.9 | 12.0 | bottom band | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J2 | +17.3...+25.9 | -24.7...-20.3 | 0.5 | 4.0 | over the ReSpeaker | shell stakes 2.10, signal tails 1.60 (GCT drawing) - 1.6 |
| J3 | -25.3...-15.1 | -27.0...-24.5 | 1.5 | 12.0 | bottom band | wire pads: wire end or solder cone (assumed); the lead itself may leave this face |
| J4 | +5.7...+8.2 | -27.0...-24.5 | 1.5 | 12.0 | bottom band | wire pads: wire end or solder cone (assumed); the lead itself may leave this face |
| J5 | -40.3...-40.3 | -17.6...-10.1 | 1.9 | 4.0 | over the ReSpeaker | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J6 | +12.3...+12.3 | -25.9...-18.4 | 1.9 | 4.0 | over the ReSpeaker | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J7 | -29.5...-11.7 | +24.2...+24.2 | 1.5 | 5.0 | top band | wire pads (second echo-reference option only) |
| J8 | +37.5...+40.0 | -25.0...-25.0 | 1.9 | 12.0 | bottom band | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J9 | -40.2...-37.8 | -25.0...-25.0 | 1.9 | 12.0 | bottom band | post 3.48 below the seating plane (KiCad model of JST XH) - 1.6 |
| J10 | -34.3...-34.3 | -17.9...-10.3 | 1.5 | 4.0 | over the ReSpeaker | pin 3.11 below the seating plane (KiCad model) - 1.6 |
| J11 | -4.5...+3.1 | -12.0...-12.0 | 1.5 | 4.0 | over the ReSpeaker | pin 3.11 below the seating plane (KiCad model) - 1.6 |
| LK1 | +6.9...+14.5 | -11.2...-11.2 | 1.5 | 4.0 | over the ReSpeaker | wire cut after soldering (assumed) |
| PS1 | -35.8...+12.5 | -0.3...-0.3 | 2.9 | 4.0 | over the ReSpeaker | pins 4.5 long (NID100-SPEC) - 1.6 |

- Pin protrusion assumed: JST sockets 1.9, pin headers 1.5, supply module 2.9, USB-C socket 0.5, wire pads 1.5. The
  leads of C5, C6, C7 and the wire link are cut to 1.5 or less after soldering (an assembly instruction).
- No through-hole joint stands over the ReSpeaker's header (bare), over its jack (0.9 allowed), beside its USB plug
  (1.4) or inside a post zone.
- In front of the -u microphone lead's strip (u -34.5...-30.5): supply module pins 11 and 12 at u -30.7 and -33.2,
  v -0.3 (2.9 beyond the face) and the BME680 header J10 at u -34.3, v -17.9...-10.3 (1.5).

