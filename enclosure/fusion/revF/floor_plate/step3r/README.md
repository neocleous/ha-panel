# Step 3 repeated, part 1 – main board rev 3.1 placed, fourth post, reach, two leads (i, 2026-11-11)

Brief: `claude/brief-enclosure-step3-repeat-2026-11-11.md` (blocks 0–4). Inputs: `claude/main-board-rev3-1-reply-2026-11-11.md`, the
board's STEP files of `docs` `110497a`. Report: `claude/report-enclosure-step3-repeat-part1-2026-11-11.md`.
This file stands in for a section of `enclosure/fusion/revF/README.md`: that file is 222 KB and this session could not push with git
(lesson 127). Merge it there when a session can.

Lengths in mm. Board frame of the site document, seen from the door: u to the right, v up, w out of the door-side face (w 0), origin
in the middle of the board; the back face is at w −1.6, depth 31.1 from the glass.

## Versions (model "HA Panel v5 - tapered")
| Version | Name begins | Bodies | Archive on the Mac |
|---|---|---|---|
| 51 | rev F WIP 2026-11-11 g6: main board rev 3.1 … placed in place of rev 3 | 367 | `~/Documents/HA Panel v5 - tapered revF-g6.f3d` |
| 52 | rev F WIP 2026-11-11 g7: carrier with its fourth post | 368 | `…revF-g7.f3d` |
| 53 | rev F WIP 2026-11-11 g8: BME680 and VEML6030 leads re-routed | 370 | `…revF-g8.f3d` |

Replaced bodies are kept hidden as `<name>_v50`: the six rev 3 board bodies, `RESP_CARRIER_v50`, `LEAD_BME680_v50`, `LEAD_VEML_v50`.
No `AUD_*` body. 36 bodies visible.

## Result
- **Version 51 (g6):** rev 3.1 at its site. 140 solids and 7 plug envelopes; against rev 3 exactly 7 solids and 2 envelopes moved.
  Holes read from the board: (−37.0, +22.0), (+19.2, +25.0), (−31.0, −25.25), (+31.0, −25.25). Overlap 0 mm³ with every body that is
  not a lead. Display-screw key paths 0.45 / 0.55 from the board's edge, 0.71 / 1.06 from the plug envelopes; cap side-screw key path
  1.22 from the supply module at 28.5 (2.01 at 27.5), back-screw path 3.96. The 58 pairs that rev 3 had within 12 of the board keep
  their figures; one pair is new (low parts to the key path of the lower display screw at −u, 11.3: the radar fuse moved there).
  Ride-in on the display module 0 mm³ (real bodies, 23 positions to 60 out). Back-face pin ends above the display's power lead:
  radar socket 1.8, C5 and C6 1.5 (limit 4.0); clearance to the lead 3.85 and 3.48.
- **Display power lead behind the board** (measured on the lead): v +14.05…+17.05 along the top run; u −43.6…−40.6 down the −u edge,
  leaving below the bottom edge; and the rise to the display's header at u +28.4…+32.1, v +14.0…+26.3.
- **Version 52 (g7):** `RESP_CARRIER` with four posts dia 8 × 13.9, holes dia 4.0 × 6.7, at (−37.0, +22.0), (+19.2, +25.0),
  (−31.0, −25.25), (+31.0, −25.25). One lump, 12 583.9 mm³ (three posts: 11 969.4). The new post: 0 mm³ against everything at dia 8 and
  dia 9; 4.05 from the plug box assumed on the display's power header; 3.95 from the display's power lead; 10.6 from the left
  microphone lead; 7.5 from the ReSpeaker; whole foot on the plate, 0.65 inside its top edge; 2.6 from the shell. Carrier's ride-in
  0 mm³. With the board in place and the door off, a straight key on the board's normal meets the rim above the door opening over
  both top screws; the key is free tilted down by 10° (top right) and 20° (top left). The bottom two are free straight.
- **Reach (i3)**, free directions out of six, flat dia 24 / rounded dia 24 / rounded dia 16 (the standard), every other plug in:

  | Connector | Rev 3 | Rev 3.1 |
  |---|---|---|
  | Radar J5 | 0 / 0 / 0 | 0 / 0 / 2 |
  | VEML6030 J11 | 0 / 2 / 2 | 0 / 2 / 5 |
  | BME680 J10 | 0 / 2 / 5 | 1 / 2 / 5 |
  | Touch J6 | 1 / 4 / 6 | 0 / 4 / 6 |
  | 20 V J1 | 0 / 5 / 5 | 0 / 2 / 5 |
  | Speaker left J8 | 0 / 0 / 2 | 0 / 0 / 2 |
  | Speaker right J9 | 0 / 0 / 2 | 0 / 0 / 3 |
  | Pi power plug J2 | 2 / 2 / 3 | 2 / 2 / 3 |
  | At the Pi (of five): 1 × 3, display's 1 × 3, 2 × 5, 2 × 3 | 3, 3, 4, 4 (rounded 16) | 3, 3, 4, 4 |

  Radar socket with larger rounded fingertips: 2 of 6 at dia 17, 0 at dia 18 (BME680 housing, 2 to 4 mm³). With the BME680 plug out:
  3 at dia 16 and 18, 1 at dia 20, 0 at dia 24.
- **Version 53 (g8):** `LEAD_BME680` and `LEAD_VEML` re-routed (`h3_routes.json` in this folder holds all 14 routes; 12 are those of
  `step3/h3_routes.json`). BME680 69.1 (rev 3: 66.3), VEML6030 101.5 (100.8). The BME680 lead's last leg runs in the lead slot of the
  sensor's tray, read from the shell's faces (i4a2): 4.0 wide, from the corner wall to 8.7 out, z 84.7…93.3. The lead is now on the
  slot's centre plane: 0.50 from the shell (was 0.03). Its end moved 0.37 onto that plane; the sensor's header itself is not modelled.
  VEML6030 lead to the supply module 2.30 (1.63 at 28.5). BME680 lead crosses the radar plug at w 24.8…28.8. Lead against lead: one
  overlap, the 3-wire Pi bundle and the display's power lead where their housings sit side by side on the Pi (20.8 mm³, as before);
  the two re-routed leads are more than 6 from every other lead.
- **Read back at the close (i5, version 53, unmodified):** the board's eight bodies and the carrier against all 93 current bodies,
  792 pairs. Not zero: seven leads in the envelope of their own plug, the Pi power cable in its plug's envelope, the three Pi signal
  bundles in their pad holes, the carrier's bosses in the ReSpeaker's microphone envelope (148.1, as before), and three pairs inside
  the board itself (pins in the board's holes 0.03 and 0.29, sockets in their own envelopes).

## Leads (centre-line length from the plug's top or the pad to the far end)
| Lead | Board end | Far end | Rev 3 | Rev 3.1 |
|---|---|---|---|---|
| 20 V | J1 | inlet board's pads | 74 | 74 |
| Speaker left | J8 | left box's wire hole | 76 | 76 |
| Speaker right | J9 | right box's wire hole | 75 | 75 |
| Radar | J5 | radar board | 60 | 60 |
| Touch | J6 | touch board's pads | 72 | 72 |
| BME680 | J10 | sensor's header | 66 | **69** |
| VEML6030 | J11 | sensor in the cap | 101 | **101** (100.8 → 101.5) |
| Pi signal, 3 wires | J3.1–.3, back face | Pi pins 1-3-5 (1 × 3) | 58 | 58 |
| Pi signal, 6 wires | J3.4–.9, back face | Pi pins 7–16 (2 × 5) | 58 | 58 |
| Pi signal, 4 wires | J4, back face | Pi pins 35–40 (2 × 3) | 58 | 58 |
| Pi power (cable between the two plugs) | J2's plug | Pi's USB-C adapter | 65 | 65 |
| Display power (not on the board) | display's header | Pi pins 2-4-6 | 190 | 190 |
| DSI ribbon (not on the board) | display | Pi | 142 | 142 |
| Microphone right (not on the board) | ReSpeaker | cap | 66 | 66 |
| Microphone left (not on the board) | ReSpeaker | cap | 70 | 70 |
| ReSpeaker USB (not on the board) | ReSpeaker | Pi | 129 | 129 |

## Scripts (`floor_plate/fusion/`, on the Mac in `~/Documents/HA_panel_renders/fp/scripts/`)
| Script | What |
|---|---|
| `v5f_i_lib.py` | the h library with this pass's data folder (`fp/step3r`), `purge()` and `run_h()` |
| `v5f_i_wrap.py` | the h scripts run again unchanged (distances, ride-in, closest points, pictures, carrier, carrier checks, reach, leads, lead checks, save); lists every text replacement |
| `v5f_i1a_step_import.py` | fetches the rev 3.1 STEP files (sha256 checked), imports them, compares the solids with rev 3's |
| `v5f_i1b_place_board.py` | places rev 3.1; rev 3 bodies → `_v50` |
| `v5f_i1d_pins_over_lead.py` | back-face pin ends in the shadow of the display's power lead; where the lead runs |
| `v5f_i2a_post4_probe.py` | the fourth post: overlaps, distances, screw head, straight and tilted key over the board screws |
| `v5f_i4a_bme_end_probe.py`, `v5f_i4a2_bme_slot.py` | what stands round the BME680 lead's end; the tray's lead slot from the shell's faces |
| `v5f_i4g_lead_extra.py` | lead against lead (distances), named pairs, crossing heights |
| `v5f_i5_verify.py` | the saved model read back |

Data in this folder: `h3_routes.json`, `i5_status.json`. The other 30 status files and the pictures (`i1_board`, `i2_posts`,
`i2_ghost`, `i2_post4`, `i4_leads`, each as `.png` and `_check.jpg`) are on the Mac in `~/Documents/HA_panel_renders/fp/step3r/`.

## Tool lessons 125–131 (continue the list in `README.md`)
125. The cache's temporary copies are keyed by name and volume. A body that moves without changing its volume (the board's connector
     group between rev 3 and rev 3.1, a re-routed lead of equal length) is answered from the old copy. `purge()` the copies and the
     result tables after every change to the model.
126. To run an earlier script on a changed model, exec its text with the status file's name and the backup suffix replaced
     (`run_h`), and list the replacements in one wrapper. A replacement that is not found raises.
127. Without git push in the session: text files go to the Mac through the Filesystem connector (write, then line edits) and come
     back as one zip through its media read. The GitHub connector takes whole text files only: no pictures, and a 222 KB README
     cannot be amended through it.
128. Needles against a large cropped body are slow (56 needles against the rear crop and the door: 44 s). Crop again to the region
     in question first (99 needles: 9 s).
129. Read a slot from the body's planar faces (normal, position, extents) before moving a lead by trial. The BME680 tray's lead
     slot is 4.0 wide; nodes typed on a 0.5 grid in world coordinates put a 3.0 lead 0.03 from one side.
130. `measureMinimumDistance` needs model bodies. For a part that is not built yet, add `AUD_*` bodies hidden, measure, and delete
     them in the same call (i2a).
131. A straight key on the board's normal over each screw head is a cheap addition to a post check: it showed that both top board
     screws need the ball end once the board is in place.
