# Main board rev 3: reply to the enclosure chat (2026-11-11)

From the electronics session, step 2, block 3 (`claude/brief-electronics-step2-2026-11-10.md`). It answers section 8 of
`claude/main-board-site-2026-11-10.md`, issue 2. Repo `neocleous/ha-panel`, branch `docs`, folder `hardware/main-board/`.
Everything is in the site document's board frame, seen from the door: **u** to the right (toward the left speaker),
**v** up, **w** out of the door-side face, origin in the middle of the board, mm.

The board is routed and checked (schematic check 0 errors; board check 0 errors, 0 open connections). It is a draft like
everything else until the whole unit is shown to be buildable. No fab files exist for it.

## 1. Answer
- **The board fits the site.** Outline 87.0 x 57.9 x 1.6, four holes of 3.2, all 120 parts on the door-side face, no
  part on the back face.
- **30 of the site's 32 rules are met. Two are not** (section 7): the radar socket sits 5.6 lower than the lead span, and
  the VEML6030 header sits 11.5 below the point where zone E was probed. Both come from the supply module.
- **Three things are asked of the enclosure chat:**
  1. Post at H2 (u +30.0, v +25.0): its face must not touch the board beyond 5.5 across. Section 2.
  2. Repeat the fingertip probe for four connectors with this board in the model. Section 5.
  3. Decide which face the 13 Pi signal wires leave the board from. Section 5.
- **STEP files** of the populated board and of the plug envelopes: section 6.

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

## 5. Connectors and leads
"Box" is the part's outline on the board plus about 0.5 all round (wire pads: the pads plus 0.3). Pin 1 is the square pad.

| Ref | Lead | Type | Pin 1 (u, v) | Last pin (u, v) | Box on the board u | Box v | Mating | Plugged |
|---|---|---|---|---|---|---|---|---|
| J9 | Speaker right | JST B2B-XH-A, through-hole, top entry | -40.25, -25.00 | -37.75, -25.00 | -43.24...-34.76 | -28.95...-22.11 | plug toward the board (-w) | in place, door off |
| J3 | Pi signal leads, 9 (10 pads) | wire pads 2 x 5, 2.54 pitch, hole dia 1.0 | -25.30, -27.00 | -15.14, -24.46 | -26.45...-13.99 | -28.15...-23.31 | wires soldered | bench |
| J1 | 20 V from the inlet board | JST B2B-XH-A | -1.25, -25.00 | +1.25, -25.00 | -4.25...+4.25 | -28.95...-22.11 | plug toward the board (-w) | in place, door off |
| J4 | Pi signal leads, 4 | wire pads 2 x 2, 2.54 pitch | +5.65, -27.00 | +8.19, -24.46 | +4.50...+9.34 | -28.15...-23.31 | wires soldered | bench |
| J6 | Touch board | JST B4B-XH-A, long side along v | +12.30, -25.94 | +12.30, -18.44 | +9.40...+16.25 | -28.93...-15.45 | plug toward the board (-w) | in place, door off |
| J2 | Pi power | GCT USB4085-GF-A, through-hole, door-side face | +18.65, -20.34 | +24.60, -20.34 | +16.30...+26.95 | -29.50...-19.23 | plug upward (+v) into the bottom edge | in place, door off |
| J8 | Speaker left | JST B2B-XH-A | +37.50, -25.00 | +40.00, -25.00 | +34.51...+42.99 | -28.95...-22.11 | plug toward the board (-w) | in place, door off |
| J5 | Radar | JST B4B-XH-A, long side along v | -40.30, -17.60 | -40.30, -10.10 | -43.20...-36.35 | -20.59...-7.11 | plug toward the board (-w) | in place, door off |
| J10 | BME680 | 1 x 4 pin header 2.54, for a 1 x 4 Dupont housing | -34.30, -10.30 | -34.30, -17.92 | -36.12...-32.48 | -19.73...-8.48 | housing toward the board (-w) | in place, door off |
| J11 | VEML6030 | 1 x 4 pin header 2.54, for a 1 x 4 Dupont housing | -4.50, -12.00 | +3.12, -12.00 | -6.32...+4.93 | -13.81...-10.19 | housing toward the board (-w) | in place, cap held above, door off |
| J7 | Echo-reference tap to the ReSpeaker (second option only) | wire pads 1 x 8, 2.54 pitch | -29.50, +24.20 | -11.72, +24.20 | -30.65...-10.57 | +23.05...+25.35 | wires soldered | bench, only if the second option is built |

- **Order along the bottom edge from -u to +u:** speaker right, post, Pi signal 9, 20 V fuse, 20 V in, Pi signal 4,
  touch, Pi power, post, speaker left. This is the site's order.
- **Speaker pins:** J8 pin 1 = left +, pin 2 = left -. J9 pin 1 = right +, pin 2 = right -.
- **Soldered on the bench:** the 9 Pi signal wires at J3 and the 4 at J4; the wire link LK1 (on the board itself); the
  8 wires at J7, only if the second echo-reference option is ever built (J7 to the ReSpeaker's empty XIAO pad rows
  behind the board at u -37.2...-21.9, v -11.2 and +4.1, about 40 mm). The first option, the default, has no lead.
- **Plugged in place with the door off:** 20 V, both speakers, touch, radar, BME680, VEML6030, Pi power. All are below
  v -7 and are pushed toward the board, except the Pi power plug, which goes upward into the bottom edge.
- **Pi signal wires (your decision):** J3 and J4 are plain plated holes of 1.0. The wires can enter from either face.
  I suggest from the back face, with the joint on the door side, so that nothing lies across the sockets on the bottom
  edge. Pad-by-pad table and the three housings at the Pi (1 x 3 on pins 1-3-5, 2 x 5 on pins 7 to 16, 2 x 3 on pins
  35 to 40; the display's own lead keeps its 1 x 3 on pins 2-4-6): `hardware/main-board/gpio-leads.md`.
- **Fingertip probe to repeat with this board in the model:** J11 VEML6030 (u -0.7, v -12.0), J5 radar (u -40.3,
  v -13.9), J10 BME680 (u -34.3, v -14.1), J6 touch (u +12.3, v -22.2). J5 and J10 stand 0.2 apart (box to box).
- **Lead lengths against the site's estimates:** the radar lead is about 6 mm longer; the VEML6030 lead ends 11.5 lower.

## 6. STEP files (`hardware/main-board/`)
1. **`main-board-rev3.step`**: the populated board, 3.6 MB, 140 solids.
   - Frame: X = u, Y = v, origin in the middle of the board. **Z = 0 is the back face, Z = 1.6 the door-side face**, so
     w = Z - 1.6. The board's own solid is 1.51 thick; the parts stand at Z 1.6.
   - 71 parts have the shape from KiCad's part library (resistors, capacitors, diodes, the two chips, the JST sockets,
     the pin headers, the USB-C socket).
   - 14 parts are plain blocks with the height of section 3: the supply module (with its 13 pins, 2.9 beyond the back
     face), the four amplifier coils, the four large fuses, the wire link, and four parts whose library shape is
     lower than the real part: the capacitors C5 and C6 (library 10.0, real 16.0), C7 (5.0, real 12.5), drawn as
     cylinders, and the 20 V filter coil L1 (6.0, table 6.5).
   - No solid: the wire pads J3, J4 and J7, the 19 test pads, the four holes (they are holes in the board).
   - Left out: the 9 parts that are not fitted in the default build (R8, R9, R20 to R25, R27).
   - Where the file and the tables of this document differ, the tables govern: the library shapes are generic.
2. **`main-board-rev3-plug-envelopes.step`**: same frame, seven blocks, one over each socket that is plugged in place,
   from the door-side face up to the height its plug and lead bend are allowed in section 3:

   | Socket | u | v | w |
   |---|---|---|---|
   | J9 speaker right | -43.24...-34.76 | -28.95...-22.11 | 0...20 |
   | J1 20 V in | -4.24...+4.24 | -28.95...-22.11 | 0...20 |
   | J6 touch | +9.41...+16.24 | -28.93...-15.45 | 0...20 |
   | J8 speaker left | +34.50...+43.00 | -28.95...-22.11 | 0...20 |
   | J5 radar | -43.20...-36.36 | -20.60...-7.11 | 0...20 |
   | J10 BME680 | -36.12...-32.48 | -19.74...-8.49 | 0...25 |
   | J11 VEML6030 | -6.31...+4.94 | -13.82...-10.18 | 0...25 |

   The Pi power plug is not in it.
3. Made by `gen/step_rev3.py` from `main-board.kicad_pcb`. Pictures: `main-board-3d-door-side.png`,
   `main-board-3d-back.png` (bare board), `rev3/floorplan.png` (the plan with part outlines and heights).

## 7. What does not fit the site, with the dimension that is missing
1. **Radar socket J5:** its pins are at v -17.6...-10.1; the lead's span is v -12...-2. It is 5.6 too low. At the span
   the plug would run into the end of the supply module (27.5 tall; the two outlines overlap by 0.1 along u, and the
   module's length is +/- 1). It is still inside zone D. Missing along u at that height: 0.1 nominal, up to 0.6 with
   the module's length tolerance, before any room for a fingertip beside a part 27.5 tall. As built: 5.6 along v.
2. **VEML6030 header J11:** it is at v -12.0, 11.5 below the point where zone E was probed. That point lies inside
   the supply module's outline (v -4.6...+8.0); the module cannot go higher (upright only below v +8) and is 50.8
   long. Missing: 11.5 along v. Reach to be probed again.
3. **Post face at H2:** section 2. Missing: 1.1 of radius (copper from 2.9, post face to 4.0).

## 8. What is where, for noise (brief, point 9)
- **Amplifier chip:** u +24.1...+33.6, v +1.6...+17.3, in front of the ReSpeaker's upper +u corner. Its output filter
  coils: u +20.4...+40.8, v -19.0...+0.2; the left-channel pair stands in front of the +u microphone lead's strip
  (u +34.5...+36.5).
- **Supply module:** u -37.1...+13.8, v -4.3...+7.7. 20 V filter coil L1: u -21.5...-8.5, v +8.6...+21.7.
- **Layers between them and the ReSpeaker:** layer 2 is one unbroken ground plane. The back layer is ground pour,
  stitched to it, with these tracks under solder mask:
  - signal lines (I2C, audio clock and data, UART, status lines), 0.2 wide;
  - **the right speaker's two conductors, 1.0 wide, side by side**: along v -1.8...-4.1 from u +13 to u -38, then down
    at u -38.4...-36.1 to the socket at v -25. They cross the -u microphone strip once (at v -2 to -4) and then run
    beside it, 1.6 from its edge, for about 19 mm. They carry the filtered audio signal, not the switching waveform;
  - the Pi's 5 V, 0.6 to 2.0 wide, u +13.5...+27.9, v -20.6...-10.2 (from the wire link to the USB-C socket);
  - short 5 V branches, 0.8 wide, 15 mm in all, between u -29.6...+5.3, v -18.3...+1.7;
  - 20 V into the supply module, 1.6 to 1.8 wide, u -28.9...-23.6, v -1.2...+14.8 (1.6 from the -u strip's edge);
  - one hop of 1.4 mm of one amplifier output ahead of its filter coil, at the chip, as on rev 2.1.
- This is more on the back than the floor plan announced ("only long low-current signal runs"). The bench test of the
  relocated microphones (noise floor within 1 dB of the baseline, no clicks) is the check. If it fails near the -u
  strip, the right speaker pair is the first thing to move.
- Not known: where the switching parts sit on the supply module, and whether the ReSpeaker's board has a ground plane.

## 9. Part changes against rev 2.1 (for the parts list in step 5; no basket touched)
| Item | Rev 2.1 | Rev 3 |
|---|---|---|
| Sensor header | one 2 x 4 male pin header, 2.54 (J10) | two 1 x 4 male pin headers, 2.54 (J10 BME680, J11 VEML6030). Generic part, in no basket, as before |
| Board screws | four M2.5 (holes 2.7) into the bracket | four M3 x 8 button head into Ruthex M3 x 5.7 inserts in the posts (the unit's standard; counts are yours) |
| Housings at the Pi | 2 x 8 and 2 x 3 | 1 x 3, 2 x 5 and 2 x 3 (Daniel's stock) |
| Everything else | | unchanged: same part numbers and values, same connector types |

The wire pads J3, J4 and J7 are holes in the board, not parts.

## 10. Assumed or not verified
- Dupont housing on a pin header about 16.5 high, 25 with the lead bend: estimates.
- JST socket 7.0 high and its post 3.48 below the seating plane: from KiCad's model of the JST part; 9.8 mated: JST catalogue.
- Supply module: which of its two faces carries the parts is not on Mean Well's drawing. The footprint puts the 8 mm
  side upward (+v) and the 4 mm side downward.
- Size of the Pi power plug below the bottom edge: not in my documents.
- Whether the microphone leads are sensitive to the audio current in the right speaker pair: not known; bench test.

## 11. Files
`hardware/main-board/`: `main-board.kicad_pcb` and the schematic, `main-board-rev3.step`,
`main-board-rev3-plug-envelopes.step`, `MAIN_env.md` (sections 2 to 4 of this document), `gpio-leads.md`,
`rev3/README.md` (the floor plan with the 32-rule table in section 8, the routed board in section 14),
`rev3/site-rules.md`, `rev3/floorplan.png`.
