# rev F - the ribbon pass: the DSI ribbon and the ReSpeaker's USB cable as flat strips (2026-11-12 / 13)

Brief `claude/brief-enclosure-ribbon-pass-2026-11-12.md`. Reports in the claude.ai project: `claude/report-enclosure-ribbon-pass-2026-11-13.md`
(closing report), `claude/handover-enclosure-ribbon-pass-2026-11-13.md` (lead table, instruction steps, tests, pictures),
`claude/brief-architect-update-2026-11-13-ribbon-pass.md`, `claude/finding-usbc-unplug-for-service-2026-11-13.md`,
`claude/report-enclosure-ribbon-pass-block2-2026-11-13.md` (station tables). Earlier: `../fixpass/README.md`.

## Model "HA Panel v5 - tapered"
| Version | Name | What |
|---|---|---|
| 61 | rev F WIP 2026-11-12 g16 | block 1: the ADT USB-C plug from the sheet's tables, the cable's first run and fold, the ribbon's two creases behind the display (first parts only) |
| 62 | rev F WIP 2026-11-13 g17 | block 2: ribbon to the Pi (200.0, three creases, arch over the Pi's connector), USB cable at 300.0 with its spare as a flat roll behind the left box, the ADT USB-A plug, the left speaker lead re-laid; `USBA_cable_env` retired |

Archives `~/Documents/HA Panel v5 - tapered revF-g16.f3d`, `revF-g17.f3d`. No printed part changed: the volumes of the front shell, both boxes,
the carrier, the base plate, the door and the cap equal version 60. Bodies of version 60 that were replaced stay hidden as `<name>_v60`:
`LEAD_DSI`, `LEAD_USB_RESP`, `RESP_usbc_plug_env`, `USBA_plug_env`, `USBA_cable_env`, `LEAD_SPK_L`. The unit has 95 bodies.

## Scripts (`../fusion/`)
Pushed to `docs` from the session and loaded into Fusion by commit from raw.githubusercontent.com with their sha256 checked. The fix pass's
library is `sys.modules['v5f_k']`; this pass's strip library is `sys.modules['v5f_m']` (its dict `c` keeps namespaces, crops and results).

| Script | What |
|---|---|
| `v5f_m_lib.py` | flat leads as strips: straight, bend through the thickness, fold (crease), twist; clearances against every current body; the ADT USB-C plug |
| `v5f_m0_preflight.py` | block 0: state, the old leads and plugs, the room behind the display |
| `v5f_m1_behind_display.py`, `v5f_m1b_calls.py` | block 1: plug, cable and ribbon behind the display; the calls as run |
| `v5f_m2_rest.py`, `v5f_m2b_calls.py` | block 2: the whole ribbon, the whole cable with its roll, the USB-A plug, the left speaker lead; the calls as run |
| `v5f_m3a_usbc_reach.py` | read-only: can the USB-C plug be pulled and put back at the ReSpeaker in place (results at the file's end) |
| `v5f_m3b_unit_checks.py`, `v5f_m3c_calls.py` | block 3: the fix pass's unit checks (`v5f_k4a_unit_checks.py`, `v5f_k4b_addenda.py`) on version 62; the calls as run with their results |
| `m_strips.json` | the two flat leads: widths, thickness, length, stations and centre line |
| `k3_routes.json` | the left speaker lead's new nodes; the two flat leads' centre lines as nodes (their bodies are built by `v5f_m2_rest.py`, not by `rebuild()`) |

## Results in short
- Ribbon: 200.0 drawn (shortest way 185.6), 16.0 wide and 11.5 at the Pi, three creases (45, 45, 39 degrees) and six bends. Stock length 200.
- USB cable: 300.0 drawn, two folds and six bends, 169.9 of spare in a roll 17.3 x 40.7 behind the left box; the roll's two inner half turns
  are at radius 3.0. Daniel's decision of 2026-11-13: the lead is unplugged at the ReSpeaker for service and the cable is only as long as the
  build needs; the roll is not redrawn and stays as the largest case.
- Ride-in at 23 positions, the left box's slide, the plate unit's way in and out with the cable on it: 0 mm3.
- 76 pairs not zero, as at version 60: four gone, four new (each a lead in its own connector), two changed.
- Reach: the left speaker plug has no direction free of leads any more (the ribbon's and the cable's drops stand behind it).

## Lessons (numbers continue the fix pass's)
- **158** A flat lead bends only through its thickness. A turn within its own width is a fold: a crease at an angle t turns the lead by 2 t and
  turns it over. Model the lead as a frame (point, heading, width direction) moved by straight, bend and fold; a round line hides all of this.
- **159** Every fold moves the lead one layer to one side. Which side decides what it clears: crease 3 folded the other way gained 1.6 beside
  the left speaker lead.
- **160** A way made of straight runs and quarter bends between two fixed ends has one length however its corners are placed. Spare length
  needs a way that goes out and comes back: an arch, a lap, a roll.
- **161** A flat cable doubled and rolled needs a width of four inner radii plus its strands. Check that against the room before drawing a
  roll; here radius 4 did not fit and radius 3 did.
- **162** A crop cache keyed by a body's volume reads that volume on every call: 12 s for the shell. Key by name when no printed part changes,
  and compare the volumes once at the end.
- **163** `Document.save` returns before the version number moves. Save in one call, export in the next, read the version back in a third.
- **164** Key-path bodies (`KO_*`) are not solid. Leave them out when a tool's or a finger's way is tested, and report them separately.
- **165** The reach standard puts a fingertip on a plug's top. A plug whose cable leaves from its top, or which is pulled sideways, needs its
  own check: the way out of the socket, a fingertip on each flat face, jaws on its edges.
- **166** Results of an earlier pass stay in the library's dict as long as Fusion is not restarted (`k.c[('k4m', 'v60')]`): diff against them
  instead of copying numbers from a report.
- **167** A rigid check of a lead that hangs free says only where it is drawn. Say for each lead which part is held and which part hangs.
