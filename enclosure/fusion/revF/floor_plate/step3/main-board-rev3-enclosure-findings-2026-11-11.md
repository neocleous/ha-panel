# Main board rev 3 in the model: what the enclosure chat found (2026-11-11)

From the enclosure chat, step 3 of the agreed order (Daniel's brief of 2026-11-11). It answers
`claude/main-board-rev3-reply-2026-11-11.md`. Model "HA Panel v5 - tapered", **version 50**. Repo `neocleous/ha-panel`,
branch `docs`, `enclosure/fusion/revF/floor_plate/step3/` (the same text is there, with the data and pictures).
Positions are in the site document's board frame, seen from the door: **u** to the right, **v** up, **w** out of the
door-side face, origin in the middle of the board, mm. "Depth" is measured from the glass; the board's back face is at
depth 31.1.

Everything here is a draft until the whole unit is shown to be buildable.

## 1. Answer
- **The board fits its site.** 0 mm³ with every body that stays, the key paths are clear, and it rides in on the display
  module (section 3).
- **Three changes are asked of the electronics session** (Daniel, 2026-11-11 12:58 and 19:04):
  1. **Top right hole (H2): move it.** A post cannot stand at (+30.0, +25.0). New zone for its centre:
     **u −12.0…+22.7, v +21.6…+25.5.** Section 2.
  2. **BME680 header (J10): at least 3.7 further from the radar socket (J5).** Section 4.
  3. **VEML6030 header (J11): 0.5 lower.** Section 4.
- **Your three requests to the enclosure chat:**
  1. Post face at H2 no larger than 5.5 across: falls away with the hole's move (section 2).
  2. Fingertip probe: done for every connector (section 4).
  3. The 13 Pi signal wires: **they leave from the back face**, the joint on the door side, as you suggested (section 5).
- Nothing else has to move. No connector type, no outline, no other hole.

## 2. Top right hole (H2)
**Finding.** H2 at (+30.0, +25.0) stands 0.35 from the centre of the display's own 4-pin power header
(u +27.75…+32.95, v +21.92…+27.12, rising to depth 15.4). The display's power lead plugs onto that header and the
carrier plate has its notch there (u +26.25…+34.45 above v +20.42). Measured: 0.9 of 100.5 mm³ of plate lies under the
post's foot; the post would fill the plug's space. A boss hanging over the plug does not work: the insert needs 6.7 of
depth and the plug's top is 7.2 below the board.

**The mistake is in the site document** (`claude/main-board-site-2026-11-10.md`, section 2). Its post zones left the
leads out, including this plug, which cannot move. The top band "u −12.0…+32.0" and the example post at (+30, +22) were
wrong. H2 was placed correctly inside the band it was given.

**New zone for the right-hand top post (centre of a post 8 across, 0.5 clear):**

| Limit | Value | From |
|---|---|---|
| u, left | −12.0 | display mounting screw at (−18.95, +24.52), 7.0 away (unchanged) |
| u, right | **+22.7** (up to +24.3 at v +18.0, not usable: see v) | plug box u +27.25…+33.45, v +21.42…+27.62 (the header's footprint plus 0.5; the lead has not been measured), 0.5 clear, post radius 4.0 |
| v, bottom | **+21.6** | the display's power lead now runs under the board along v +14.0…+17.1 (section 5); 0.5 clear; post radius 4.0 |
| v, top | +25.5 | the plate's top edge at v +29.65 (unchanged) |

- The right limit rests on the assumed plug size (section 8). A centre at u +20.0 or less stays clear even if the plug
  is 2.7 larger on that side than assumed.
- The left-hand top band is unchanged (u −38.5…−26.0, v +18.0…+25.5); H1 is fine. The bottom line is unchanged; H3 and H4
  are fine.
- Clear zones on the board as before: 9 across on the back face, 7 across on the door side; hole 3.2.
- On the board, by your `rev3/floorplan.json`: the amplifier block ends at v +21.0 and the fuse F5's box at u +12.64.
  R26, R27 (not fitted), TP19 and TP20 stand at u +18.5…+25.6, v +22.2…+27.7. A hole in that area lies above the amplifier
  block, so the tracks that led to the 5.5 request are no longer under the post.
- **The 5.5 contact face**, for the record: it prints, as a post top with its rim outside 5.5 set back by 0.4. The face
  is then a ring 0.75 wide round the insert hole, and setting the insert (4.6 across, hole 4.0, wall 1.6 by Ruthex's
  table) reshapes it; the board would sit on the insert's brass. Not built.
- The carrier has three posts today. I add the fourth when the hole's new position is known.

## 3. Fit of the board as it is (version 48 to 50)
| Check | Result |
|---|---|
| Overlap with every body that stays (84) | 0 mm³ |
| Display screws' key paths (drawn 7 across) | board edge 0.45 (−u) and 0.55 (+u); plug envelopes 0.7 (J5 / J9 side) and 1.1 (J8 side); the carrier 2.5…2.8 |
| Cap side screw's key path (drawn 5 across for the 2.5 key; the 2.0 key is used) | supply module 2.0 at 27.5 tall, **1.2 at 28.5**; 2.5 for the 2.0 key |
| Cap back screw's key path | supply module 4.0 at 28.5; C6 7.4 |
| ReSpeaker behind the board | board to its header 0.56; to its USB plug 2.4; supply module's pin ends to its parts 2.2; JST pins 3.3 |
| Shell and door | supply module at 28.5: 7.4 to the shell, 8.8 to the door; board 16.3 to the shell |
| Speaker boxes | board to the left box 5.4, to the right box 7.3; J8's plug envelope 1.3 from the left box's roof corner |
| Pi power plug below the edge (12.4 × 20 × 6.5 assumed) | 38 to the Pi's cooler, 16 to the left box |
| Ride-in on the display module, 60 mm along the slab normal | 0 mm³. The outline's hull is free up to 21 tall (tallest part apart from the supply module: 16.0); the supply module's box at 28.5 is free with 8 to spare all round; 1.0 to the LCD opening in the board's plane |
| Carrier posts | bottom posts 0.7 from the ReSpeaker; H4's post 1.2 from J2's shell stake and 1.6 from the display mounting screw's head |

Small differences between your tables and the STEP file (the tables govern, none changes a check): pin headers 8.53
tall in the file (table 8.65); JST pins 1.8 behind the back face (table 1.9); the board's own solid is 1.51 thick.

## 4. Reach
**Method.** The probe of the site document (cylinder 60 long, tip on the plug, six directions toward the door:
straight, 25° and 45° down, 25° up, 25° to −u and to +u), with these differences: the tip is on the **mated plug's real
top** (w 9.8 for JST, 16.5 for a Dupont housing, your figures); **every other plug is in**, as a block on its socket's
outline; the board and all its parts are obstacles. Three tools: flat 24 across (the site document's), rounded 24,
rounded 16. A direction is blocked above 1.0 mm³. Leads are left out: they can be pushed aside.

**Standard (Daniel, 2026-11-11 19:04): the rounded 16 fingertip.** A connector passes with one free direction or more.

| Connector | Tip (u, v, w) | Flat 24 | Rounded 24 | Rounded 16 | What blocks |
|---|---|---|---|---|---|
| J11 VEML6030 | −0.7, −12.0, 16.5 | 0 | 2 | 2 (25° and 45° down) | supply module |
| J5 radar | −40.3, −13.9, 9.8 | 0 | 0 | **0** | J10's housing 0.2 beside it and 6.7 taller, in all six; then supply module, right speaker box, shell |
| J10 BME680 | −34.3, −14.1, 16.5 | 0 | 2 | 5 | supply module |
| J6 touch | +12.3, −22.2, 9.8 | 1 | 4 | 6 | |
| J1 20 V | 0.0, −25.0, 9.8 | 0 | 5 | 5 | J11 and J6, by little |
| J8 speaker left | +38.75, −25.0, 9.8 | 0 | 0 | 2 (25° up, 25° to −u) | left speaker box |
| J9 speaker right | −39.0, −25.0, 9.8 | 0 | 0 | 2 (25° and 45° down) | right speaker box; J10, J5 |
| J2 Pi power plug | +21.6, −40.5, 5.0 | 2 | 2 | 3 | |
| Pi housing 1 × 3, pins 1-3-5 | on the Pi | 0 of 5 | 2 | 3 | touch clip beside it |
| Pi housing 1 × 3, display lead | on the Pi | 0 of 5 | 1 | 3 | touch clip |
| Pi housing 2 × 5 | on the Pi | 1 of 5 | 3 | 4 | |
| Pi housing 2 × 3 | on the Pi | 1 of 5 | 3 | 4 | |

The site document's "fingertip: yes" rows were probed on an empty board, with the tip 10 higher (on an assumed 20 mm plug
and bend) and at other points. They do not hold for the populated board.

**Request 2: BME680 header (J10).** Today its box is u −36.12…−32.48; the radar socket's pin line is at u −40.3.
Probed with the header moved toward +u:

| J10 moved by | Radar socket, rounded 16 | J10 itself, rounded 16 |
|---|---|---|
| 0 (today) | 0 of 6 | 5 of 6 |
| 3.7 | 2 of 6 (straight, 25° down) | 5 of 6 |
| 5.0 | 2 of 6 | 5 of 6 |

- At least 3.7 between the two is what is asked; the direction is yours. The header's own reach depends on its distance
  from the supply module (today 9.75 from its centre to the module's edge): keep that or more.
- The BME680 lead arrives from −u and passes over the radar plug at w 23 or more. Its length grows by the move.
- With the rounded 24 the radar socket stays at 0 of 6 at either distance (supply module's corner 10.0 from its centre,
  right speaker box, shell). That is accepted with the standard.

**Request 3: VEML6030 header (J11).** Probed with the header lower:

| J11 lower by | J11, rounded 16 | J1 20 V, rounded 16 |
|---|---|---|
| 0 (today) | 2 of 6 | 5 of 6 |
| 0.5 | **5 of 6** | 5 of 6 (not re-probed; the header is still 10.7 from J1's centre, 7.9 needed) |
| 4.4 | 5 of 6 (and 4 of 6 with the flat 24) | 2 of 6 |

- 0.5 lower is what is asked. Not 4.4: it takes three directions from the 20 V plug.

**Not asked:** the speaker sockets. The boxes set their limit; they pass with the rounded 16. Do not move J8 toward
+u or lower: the DSI ribbon passes 0.1 from its plug envelope (0.9 from the socket).

**Plugging order this gives** (for the build instructions): bottom row first (speakers, 20 V), then touch and radar,
then the two Dupont housings (BME680, VEML6030), Pi power last.

## 5. Leads
Routed centre-line lengths from the plug's top (or the pad) to the far end, mm. Stock lengths are chosen from these
afterwards. Nodes: `h3_routes.json`.

| Lead | Board end | Far end | Length | Site's estimate |
|---|---|---|---|---|
| 20 V | J1 | inlet board's pads | 74 | 65–70 |
| Speaker left | J8 | left box's wire hole | 76 | 65 |
| Speaker right | J9 | right box's wire hole | 75 | 65–70 |
| Radar | J5 | radar board | 60 | 50 |
| Touch | J6 | touch board's pads | 72 | 65–70 |
| BME680 | J10 | sensor's header | 66 | 50 |
| VEML6030 | J11 | sensor in the cap | 101 | 70 |
| Pi signal, 3 wires | J3.1–.3, back face | Pi pins 1-3-5 (1 × 3) | 58 | 58 |
| Pi signal, 6 wires | J3.4–.9, back face | Pi pins 7–16 (2 × 5) | 58 | 58 |
| Pi signal, 4 wires | J4, back face | Pi pins 35–40 (2 × 3) | 58 | 58 |
| Pi power (cable between the two plugs) | J2's plug | Pi's USB-C adapter | 65 | 55 |
| Display power (not on the board) | display's header | Pi pins 2-4-6 | 190 | — |
| DSI ribbon (not on the board) | display | Pi | 142 | — |
| Microphone right / left (not on the board) | ReSpeaker | cap | 66 / 70 | — |
| ReSpeaker USB (not on the board) | ReSpeaker | Pi | 129 | — |

- **Pi signal wires: from the back face.** Nothing then lies across the sockets on the bottom edge; the joints are on
  the door side and can be reworked with the board mounted; the Pi's header lies 51 below the bottom edge in the board's
  own plane (w −3). The bundles drop behind the bottom edge. Nearest part: the H3 post, 1.1 from the 3-wire bundle.
- **Display power lead, new route behind the board:** from the header down to v +15.5, then along v +14.0…+17.1 to
  u −42.1, then down the −u edge inside the outline (u −43.6…−40.6), 5.6 to 8.6 behind the back face. It is 0.5 from
  the ReSpeaker and 0.3 from the lower right display screw's key path (in version 49 it lay inside that path). Back-face
  pin ends in that strip today: J5 1.9, J10 1.5. Keep them at 4.0 or less, the site's limit.
- **BME680 lead** passes over the radar plug at w 24…29; **VEML6030 lead** passes over the supply module at w 31…34
  (2.6 above it, 1.6 at 28.5 tall).
- **Microphone leads and the right speaker's tracks on the back** (12 segments, 1.0 wide, u −40.3…+18.4, v −25.0…−2.2,
  read from `main-board.kicad_pcb`): the right lead's nearest point is its start on the ReSpeaker at (u −34.5, v −3.2,
  depth 20.0), 11.1 centre to centre and 9.6 between surfaces, with the ReSpeaker's board between them. Only its first
  11 mm are within 15 of the tracks; it then runs up, away from them. The left lead: 22.4 centre to centre. The reply's
  "1.6 beside it for 19 mm" holds only in plan view.
- **Unchanged from version 49, for the record:** the DSI ribbon lies in the lower left display screw's key path
  (54.7 mm³) and has to be pushed aside to drive that screw; the BME680 lead is 0.03 from the shell at the sensor.

## 6. Fasteners that changed
| Item | Before | Now |
|---|---|---|
| Carrier to the display's mounting points, M2.5 × 5 | 3 (or 4) | 4 |
| Main board, M3 × 8 button head and Ruthex M3 × 5.7 | 4 planned | 3 built; the fourth with the moved hole |

## 7. What the enclosure needs back
1. The new position of the top right hole.
2. The new positions of J10 and J11, and anything that moved with them.
3. The STEP file and the plug envelopes again, same frame.

## 8. Assumed or not verified
- The plug on the display's power header: taken as the header's footprint plus 0.5, 14 tall. The lead is Daniel's own and
  has not been measured.
- Dupont housing 16.5 tall and JST plug 9.8: your figures.
- The fingertip is a rigid rod. Whether Daniel's finger behaves like the rounded 16 shows on the first build.
- The Pi power plug's size (12.4 × 20 × 6.5) is carried over from the earlier model.
