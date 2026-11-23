# Model scripts: version 67 → 68 → 69

These scripts changed the Fusion model "HA Panel v5 - tapered" in two steps.

- **Version 67 → 68 (2026-11-22): screws and printed clamps instead of melted pins and glue.** Seven M2 × 6 flat-head
  screws for plastic and two printed clamps now hold the two microphone strips, the light-sensor board, the USB-C
  grommet, the radar board and the BME680 hood, so that each comes out again with a driver.
- **Version 68 → 69 (2026-11-23): four corrections** that the checks on version 68 asked for: the hood's boss and side
  plate, the two blocks beside the radar board, and the supply module's pins drawn where main board rev 3.3 has them.

**The model is at version 69. It is work in progress and waits for its print re-check.** The print files are still
version 67's: they are out of date for the shell, the door, the cap, the grommet and the hood, and they lack the two
clamps.

Lengths are in mm. World coordinates: x + = the viewer's left, y + toward the screen, z up.

## The files
| File | Loaded as | What it does |
|---|---|---|
| `v68_lib.py` | `v68` | helpers: temporary copies of bodies, what a new body adds and removes, what lies near it, section pictures |
| `v68_cap.py` | `v68_cap` | the top cap, the two clamps for the microphone strips and the light-sensor board, the moved light opening, the sensor board as measured, the two microphone leads drawn on to the strips |
| `v68_door.py` | `v68_door` | the rear door and the USB-C grommet: two lugs under the door's cutout, each with a screw into a boss inside the door |
| `v68_shell.py` | `v68_shell` | the shell and the BME680 hood as they were at version 68: two screws beside the radar board, one screw through an ear of the hood into a boss |
| `v68_commit.py` | `v68_commit` | the seven new screws as one body; puts the new bodies into the document, saves the version, exports the archive |
| `v68_cable.py` | `v68_cable` | the ReSpeaker's USB cable: its first fold moved off the lip over the door opening |
| `v69_fixes.py` | `v69` | version 68 → 69: the hood's boss, ear and side plate; the radar blocks; the supply module's pins; the hood's screw at its new place; puts them into the document, saves, exports |
| `v69_checks.py` | `v69c` | the checks on version 69's bodies: walls round the pilots, the hood seated and on its way out, the driver's reach, the display module riding in, the outer skin, the interference table, counts and volumes, the faces that look at the bed |

Only `commit()`, `save()` and `export()` change the document. Everything else works on temporary bodies.

## How they run
The scripts run inside Autodesk Fusion's Python, sent through Fusion's MCP connector, with the design open. Fusion keeps
loaded modules between calls, so each file is loaded once, by a short loader that reads it from this repo at a named
commit and checks its sha256:

```python
import sys, types, urllib.request, hashlib

def load(sha, name, module, sha256):
    url = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/enclosure/model-v68/%s' % (sha, name)
    src = urllib.request.urlopen(url, timeout=25).read()
    if hashlib.sha256(src).hexdigest() != sha256:
        raise RuntimeError('sha256 of %s differs' % name)
    m = types.ModuleType(module); sys.modules[module] = m
    exec(compile(src.decode('utf-8'), name, 'exec'), m.__dict__)
```

**Order of loading:** the two helper libraries (below), then `v68`, `v68_cap`, `v68_door`, `v68_shell`, `v68_commit`,
`v68_cable`, then `v69`, then `v69c`.

- Version 68: `build()` in `v68_cap`, `v68_door` and `v68_shell`, `cable()` in `v68_cable` and `screws()` in
  `v68_commit` make the bodies; `commit()` in `v68_commit` and in `v68_cable` put them into the document; `save()` and
  `export()` in `v68_commit` close the version.
- Version 69: `build()` in `v69`, the checks of `v69c` on the temporary bodies, `commit()`, the interference table,
  `save()`, `export()`.

Every changed body stays in the model as a hidden copy: `…_v67` for the bodies changed at version 68, `…_v68` for those
changed at version 69.

## Files they need that are not in this tree
The scripts stand on two helper libraries of the earlier passes, and the checks on one earlier check script. All three
were removed in the clean-up of 2026-11-19 and are read from the tree as it stood at commit
[`45a38e4`](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee):

| File at `45a38e4` | Loaded as | What it gives |
|---|---|---|
| `enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py` | `c3k` | the model's frames, temporary solids, distances, the list of the unit's bodies, the driver's reach along a line |
| `enclosure/fusion/revF/split/change3/c3_lib.py` | `c3` | the cloth reference for the outer-skin check, faces of a body in a box |
| `enclosure/fusion/revF/floor_plate/fusion/v5f_k4a_unit_checks.py` | the namespace `c3k.K4NS` | the display module's ride-in and the interference table, as the audits ran them |

## Which commit made which version
- Version 68: the bodies were built from this folder at commits `d2eb2e3` (cap, clamps, door, grommet, shell, hood,
  screws) and `054c447` (cable).
- Version 69: the bodies were built from `v69_fixes.py` at commit `4b7383b`.
