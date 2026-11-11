# Main board rev 3.1: reply to the enclosure chat (2026-11-11)

From the electronics session, step 2 repeated, block 2 (`claude/brief-electronics-step2-repeat-2026-11-11.md`). It answers
`claude/main-board-rev3-enclosure-findings-2026-11-11.md`. Repo `neocleous/ha-panel`, branch `docs`, folder
`hardware/main-board/`. Everything is in the site document's board frame, seen from the door: **u** to the right (toward
the left speaker), **v** up, **w** out of the door-side face, origin in the middle of the board, mm.

**This document replaces `main-board-rev3-reply-2026-11-11.md` for rev 3.1.** It is complete in itself: the board can be
placed and probed from it and the two STEP files.

The board is routed and checked (schematic check 0 errors, 0 warnings; board check with schematic comparison 0 errors,
0 open connections, 0 differences). It is a draft like everything else until the whole unit is shown to be buildable.
No fab files exist for it.

## 1. Answer
- **All three changes are made as asked.**
  1. **Top right hole H2: now at u +19.20, v +25.00** (was +30.00, +25.00). Inside your zone, left of u +20.0. Section 3.
  2. **BME680 header J10: 3.90 further from the radar socket** (asked: 3.7 or more). Pins at u -30.40 (were -34.30).
     No closer to the supply module. Section 6.
  3. **VEML6030 header J11: 1.00 lower.** Pins at v -13.00 (were -12.00). Section 6.
- **Nothing else that you built on has moved:** the outline, H1, H3, H4, every socket, the wire pads, the supply module
  and every part taller than 3.0. Eight small parts moved to make room; all are 3.0 or lower. Section 2.
- **Your post face request (5.5 at H2) is gone.** All four holes now have the same bare circles. Section 3.
- **The 13 Pi signal wires enter from the back face** and are soldered on the door side. It is recorded in
  `gpio-leads.md`. Section 6.
- **Your two questions:** the STEP file was right about both pin figures and my tables were not; they are corrected.
  The board is 1.6 thick. I see no reason to act on the board for the microphone leads. Section 8.
- **Site rules:** 36 checked, 34 met. The two that are not met are the two of rev 3. Section 9.
- **Nothing is asked of you** beyond what you planned: place the board, build the fourth post, probe again.
- **STEP files:** `main-board-rev3.1.step`, `main-board-rev3.1-plug-envelopes.step`. The rev 3 files are untouched.
  Section 7.

## 2. Everything that moved, old to new
"Box" is the part's outline on the board plus about 0.5 all round. 11 of 120 parts; the other 109 are where rev 3 had them.

| Part | What | Height w | Rev 3 | Rev 3.1 |
|---|---|---|---|---|
| H2 | top right hole, 3.2 across | screw head 1.65 | centre +30.00, +25.00 | **centre +19.20, +25.00** |
| J10 | BME680 header | 8.54 bare, about 16.5 with the housing | pin 1 at -34.30, -10.30; box u -36.12...-32.48, v -19.73...-8.48 | **pin 1 at -30.40, -10.30**; box u -32.22...-28.59, v -19.73...-8.48 |
| J11 | VEML6030 header | 8.54 bare, about 16.5 with the housing | pin 1 at -4.50, -12.00; box u -6.32...+4.93, v -13.81...-10.19 | **pin 1 at -4.50, -13.00**; box u -6.32...+4.93, v -14.81...-11.19 |
| F3 | radar fuse | 2.94 | box u -30.73...-23.27, v -21.38...-17.63 | box u -36.12...-32.37, v -14.93...-7.46 (turned upright) |
| C10 | radar capacitor | 1.5 | box u -32.04...-29.99, v -17.35...-13.86 | box u -35.99...-32.50, v -17.13...-15.07 |
| TP12 | radar test pad | bare pad | box u -32.05...-29.45, v -12.95...-10.36 | box u -35.54...-32.95, v -19.90...-17.30 |
| F4 | sensor fuse | 1.2 | box u -29.52...-24.87, v -15.63...-13.28 | box u -28.42...-23.77, v -15.63...-13.28 |
| C11 | regulator input capacitor | 1.9 | box u -28.87...-26.48, v -9.59...-4.90 | box u -28.52...-26.13, v -9.59...-4.90 |
| R26 | link that feeds the amplifier's logic supply | 0.7 | box u +18.48...+21.53, v +22.73...+24.28 | box u +20.38...+23.42, v +19.42...+20.98 |
| R27 | its alternative, not fitted | none (not fitted) | box u +18.48...+21.53, v +24.73...+26.28 | box u +16.67...+19.73, v +19.42...+20.98 |
| TP3 | inlet current test pad | bare pad | box u -4.51...-1.92, v -17.06...-14.47 | box u -4.51...-1.92, v -17.56...-14.97 |

- **Why the small parts moved:** F3, C10 and TP12 stood where the BME680 header now is; they went into the strip between
  the radar socket and the header. F4 and C11 gave the header room on its +u side. R26 and R27 stood where the hole now
  is; they went below it. TP3 stood under the VEML6030 header's new pin row.
- **Against what I announced at the block 0 checkpoint:** the hole is at u +19.2, not +19.5 (the outlines of the two
  test pads beside it reached into the screw-head circle); the header moved 3.9, not 4.0 (0.08 was left for C11).
- **Tracks:** 87 % of rev 3's track length is unchanged; no track of the amplifier changed. The audio bit clock no
  longer runs round the old hole.

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

## 6. Connectors and leads
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
| J10 | BME680 | 1 x 4 pin header 2.54, for a 1 x 4 Dupont housing | -30.40, -10.30 | -30.40, -17.92 | -32.22...-28.59 | -19.73...-8.48 | housing toward the board (-w) | in place, door off |
| J11 | VEML6030 | 1 x 4 pin header 2.54, for a 1 x 4 Dupont housing | -4.50, -13.00 | +3.12, -13.00 | -6.32...+4.93 | -14.81...-11.19 | housing toward the board (-w) | in place, cap held above, door off |
| J7 | Echo-reference tap to the ReSpeaker (second option only) | wire pads 1 x 8, 2.54 pitch | -29.50, +24.20 | -11.72, +24.20 | -30.65...-10.57 | +23.05...+25.35 | wires soldered | bench, only if the second option is built |

- **Only the rows of J10 and J11 differ from rev 3.**
- **For the probe:**

| Connector | Tip on the mated plug (u, v, w) | Body in the STEP file | What is beside it |
|---|---|---|---|
| J10 BME680 | -30.40, -14.11, 16.5 | u -31.67...-29.13, v -19.19...-9.03 | radar socket's box 4.14 away (rev 3: 0.24); from the middle of its pin row to the supply module's body 9.76, as on rev 3 |
| J11 VEML6030 | -0.69, -13.00, 16.5 | u -5.77...+4.39, v -14.27...-11.73 | to the supply module's body 8.65 (rev 3: 7.65); to the 20 V socket's box 7.3 (rev 3: 8.3) |
| J5 radar | -40.30, -13.85, 9.8 | unchanged | BME680 header's box 4.14 away |

- **Pi signal wires: they enter from the back face and are soldered on the door-side face** (settled in your step 3).
  J3 and J4 are plain plated holes of 1.0 and have not moved. On the door side the joint and the wire's end stand 3.0
  or less (estimate). Pad-by-pad tables, also as seen from the back, and the three housings at the Pi:
  `hardware/main-board/gpio-leads.md`.
- **Lead lengths:** the BME680 lead's board end is 3.9 further toward +u; the VEML6030 lead's board end is 1.0 lower.
  The table is yours.
- **Unchanged:** the order along the bottom edge; the speaker pins (J8 pin 1 = left +, J9 pin 1 = right +); what is
  soldered on the bench (the wires at J3 and J4, the wire link, J7 only for the second echo-reference option); what is
  plugged in place with the door off (20 V, both speakers, touch, radar, BME680, VEML6030, Pi power).

## 7. STEP files (`hardware/main-board/`)
1. **`main-board-rev3.1.step`**: the populated board, 3.6 MB, the board and 85 parts.
   - Frame: X = u, Y = v, origin in the middle of the board. **Z = 0 is the back face, Z = 1.6 the door-side face**, so
     w = Z - 1.6.
   - To be exact: the board's own solid runs from Z 0 to Z 1.51 and the parts stand at Z 1.595 (section 8).
   - 71 parts have the shape from KiCad's part library. 14 are plain blocks with the height of section 4: the supply
     module (with its 13 pins, 2.9 beyond the back face), the four amplifier coils, the four large fuses, the wire
     link, C5 and C6 (cylinders 16.0 tall), C7 (12.5) and the 20 V filter coil (6.5).
   - No solid: the wire pads J3, J4 and J7, the 19 test pads, the four holes (they are holes in the board).
   - Left out: the 9 parts that are not fitted in the default build (R8, R9, R20 to R25, R27).
   - **Against `main-board-rev3.step`:** the hole and seven bodies have moved (J10, J11, F3, C10, F4, C11, R26). Every
     other body is in the same place to 0.001.
2. **`main-board-rev3.1-plug-envelopes.step`**: same frame, seven blocks, one over each socket that is plugged in place,
   from the door-side face up to the height its plug and lead bend are allowed in section 4:

   | Socket | u | v | w |
   |---|---|---|---|
   | J9 speaker right | -43.24...-34.76 | -28.95...-22.11 | 0...20 |
   | J1 20 V in | -4.24...+4.24 | -28.95...-22.11 | 0...20 |
   | J6 touch | +9.41...+16.24 | -28.93...-15.45 | 0...20 |
   | J8 speaker left | +34.50...+43.00 | -28.95...-22.11 | 0...20 |
   | J5 radar | -43.20...-36.36 | -20.60...-7.11 | 0...20 |
   | J10 BME680 | **-32.22...-28.59** | -19.74...-8.49 | 0...25 |
   | J11 VEML6030 | -6.31...+4.94 | **-14.82...-11.18** | 0...25 |

   The Pi power plug is not in it.
3. **Checked by reading both files back** (`rev3.1/check/step_check.py`, result in `rev3.1/check/step_check_result.txt`):
   the four holes in the solid are where the board file has them; each of the 85 parts moved in the file by exactly
   what it moved on the board; the seven blocks agree with the connector boxes.
4. Made by `gen/step_rev3.py` from `main-board.kicad_pcb`. Pictures: `main-board-3d-door-side.png`,
   `main-board-3d-back.png` (bare board), `rev3.1/floorplan.png` (the plan with part outlines and heights).
5. The rev 3 files `main-board-rev3.step` and `main-board-rev3-plug-envelopes.step` are kept, unchanged.

## 8. Your two points "for information"
**1. Tables against the STEP file: which is right.**

| Figure | Rev 3 table | STEP file | Right | Why |
|---|---|---|---|---|
| Pin header, bare, above the door-side face | 8.65 | 8.53 | **the file: 8.54** | KiCad's model of the header is 8.54 above and 3.00 below its seating plane (measured again today). My table figure was a misreading of that model |
| Pin header, pin end beyond the back face | 1.5 | 1.4 | **the file: 1.4** | 3.00 - 1.6 |
| JST socket, pin end beyond the back face | 1.9 | 1.8 | **the file: 1.8** | JST's XH catalogue drawing: post 3.4 below the seating plane, body 7.0 above it. KiCad's model has the same. 3.4 - 1.6. My table had 3.48, a misreading |
| Board thickness | 1.6 | solid 1.51 | **the table: 1.6** | 1.6 is the board as ordered. KiCad draws the board's solid without the outer copper and the solder mask, from Z 0 to Z 1.51, and stands the parts at Z 1.595. Use Z 0 for the back face and Z 1.6 for the door-side face |

- The tables of rev 3.1 carry the corrected figures (sections 4 and 5, `MAIN_env.md`). No check changes: the limits
  are 4.0 and 12.0, and with its housing on the header is 16.5 either way.
- Not verified: the pin header itself. It is a generic part, chosen with the parts list in step 5; headers of this
  kind differ by a tenth or two in pin length. The 16.5 with the housing on is an estimate, as before.

**2. Microphone leads and the right speaker's tracks: I see no reason to act on the board.**
- The microphones are digital (IM69D120, `hardware/mic-strip/README.md`): the lead carries 3.3 V supply, ground, clock,
  select and data. No analogue microphone signal runs in it.
- The right speaker's two conductors run side by side, 1.0 wide, 1.3 from centre to centre, so their fields largely
  cancel at a distance. My estimate for a lead 11 away with 11 mm beside them: a few microvolts per ampere of speaker
  current at 10 kHz. That is an estimate, not a measurement. A logic line switches 3.3 V, and the microphone's supply
  is filtered on the strip (100 ohm and 10 uF).
- Your correction stands: "1.6 beside it for 19 mm" was true in plan view only.
- The pair has not moved on rev 3.1. The check remains the bench test of the relocated microphones.

## 9. What does not fit the site, with the dimension that is missing
1. **Radar socket J5** (unchanged, accepted with the floor plan): its pins are at v -17.6...-10.1; the lead's span is
   v -12...-2. It is 5.6 too low, because at the span its plug would run into the end of the supply module. Inside
   zone D.
2. **VEML6030 header J11:** it is now 12.5 below the point where zone E was probed (rev 3: 11.5), where you asked
   for it. That point lies inside the supply module's outline.
3. **BME680 header J10 and zone D's drawn box:** zone D is drawn to u -33.5. The header's pins are now at u -30.40,
   3.1 outside it; its box reaches u -28.59. Along v it is inside (v -17.92...-10.30 in v -18...-8). This follows
   from your request; the site-rule table tests v, as before.
4. Nothing else. The post face at H2 is no longer an issue.

## 10. What is where, for noise
- **Correction to the rev 3 reply (its section 8):** it said the back layer was poured ground, stitched to the plane.
  Rev 3 had no poured ground on either outer layer; my mistake. **Rev 3.1 has it:** 66 % of the back face and 60 % of
  the door side, joined to the ground plane (layer 2, unbroken) by 42 vias.
- **On the back under solder mask, in the same places as on rev 3:**
  - the right speaker's two conductors, 1.0 wide: u -40.8...+18.9, v -25.5...-1.8;
  - 20 V into the supply module, 1.6 to 1.8 wide: u -28.9...-23.6, v -1.2...+14.8;
  - a 9 mm piece of the left speaker's output from its coil to its socket, 0.8 wide: u +37.1...+38.5, v -25.4...-15.3
    (the rev 3 reply did not list it);
  - one hop of 1.4 mm of one amplifier output ahead of its filter coil, 0.4 wide, at u +32.4...+33.8, v -1.8;
  - signal and low-current lines, 0.15 to 0.3 wide.
- **Changed on the back:**
  - the Pi's 5 V is now an area of 47 mm2 with the old tracks inside it: u +13.4...+27.9, v -22.0...-10.1;
  - the short 5 V branches now lie within u -17.7...+5.3, v -6.7...+1.7 (rev 3: u -29.6...+5.3, v -18.3...+1.7);
  - the audio bit clock's detour round the old hole is gone.
- All of these now have ground beside them on the same layer.
- The amplifier, its coils, the supply module and the 20 V filter coil are where they were.

## 11. Part changes against rev 3 (for the parts list in step 5; no basket touched)
**None.** The same 120 parts with the same values and footprints; the same 9 are not fitted. The schematic is rev 3's
with a new revision text. Four M3 x 8 board screws, as before.

## 12. Assumed or not verified
- Dupont housing on a pin header about 16.5 high, 25 with the lead bend: estimates.
- The pin header's own dimensions: KiCad's model; the part is not chosen.
- The joint and wire end at J3 and J4 on the door side, 3.0 or less: estimate.
- The box of the plug on the display's power header: yours (the header's footprint plus 0.5).
- Supply module: which of its two faces carries the parts is not on Mean Well's drawing (as before).
- The coupling estimate in section 8: a calculation with the distances you gave, not a measurement.
- Copper thickness and plating, for the supply-path figures in the block reports: the fab's published figures.

## 13. Files
`hardware/main-board/`: `main-board.kicad_pcb` and the schematic (rev 3.1), `main-board-rev3.1.step`,
`main-board-rev3.1-plug-envelopes.step`, `MAIN_env.md` (sections 3 to 5 of this document), `gpio-leads.md`,
`rev3.1/floorplan.json` (every part with its position, box and pads), `rev3.1/floorplan.png`,
`rev3.1/floorplan-tables.md`, `rev3.1/site-rules.md` (the 36 rules), `rev3.1/README.md` (the layout report),
`rev3.1/check/` (the calculations, the STEP check, and `reply_check.py`, which compares the tables of this document
with the board files). Rev 3 is kept: `rev3/`, `main-board-rev3.step`,
`main-board-rev3-plug-envelopes.step`, `main-board-rev3-reply-2026-11-11.md`.
