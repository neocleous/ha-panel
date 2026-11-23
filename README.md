# HA Panel: design files

This branch, `docs`, holds the design of a Home Assistant touch panel: its custom circuit boards and its 3D-printed
enclosure. The panel's software is on the [`main`](https://github.com/neocleous/ha-panel/tree/main) branch.

## The panel
A free-standing Home Assistant panel. A Raspberry Pi 5 shows a full-screen dashboard on a Waveshare 8-inch DSI
touchscreen (1280 × 800, landscape). Around it:
- two speakers (Dayton Audio DMA45-4), driven by the main board's TAS5756M amplifier;
- two microphones for voice, through a ReSpeaker Lite;
- a presence radar (Hi-Link LD2410C);
- air and light sensors (BME680, VEML6030);
- four touch keys below the screen;
- power from a 20 V USB-C charger.

Home Assistant runs on a separate server; the panel is its display, sensor and voice client.

## State (2026-11-23)
- **The boards:** the main board (rev 3.3), the touch board (rev E), the mic strips (rev 3) and the two paste stencils.
  Their fab files are made.
- **The enclosure: the Fusion model is at version 69 and waits for its print re-check.** Versions 68 and 69 replaced the
  melted and glued joints by screws and two printed clamps.
- **The print files are version 67's.** Until the re-check has run and they are made again, they are out of date for the
  shell, the door, the cap, the grommet and the hood, and they lack the two clamps.
- **Next:** the print re-check and the new print files, then a fit trial printed in PLA, the black ABS set, the boards'
  assembly, the build and bring-up.
- **The first panel (v1)** is built and in use. `main` installs its software.

## Folder map
```
hardware/              the three boards and the paste stencil
  main-board/          rev 3.3: power, amplifier, sockets
  mic-strip/           rev 3: one microphone per strip, two strips per panel
  touch-board/         rev E: the four touch keys
  stencil/             the paste stencils: the main board; the touch board with the mic strips
  notes/               parts lists, DigiKey and JLC notes, Raspberry Pi settings
  rev-c/               the first panel's touch board
enclosure/             the housing
  model-v68/           the scripts that made versions 68 and 69 of the Fusion model from version 67
  print-files/         the scripts that make the print files from the Fusion model
  HA Panel Final.step  the first panel's enclosure
```

Start with [`hardware/README.md`](hardware/README.md) for the boards and [`enclosure/README.md`](enclosure/README.md)
for the housing.

## Where things are that are not in this repo
- **The enclosure model:** Autodesk Fusion, document "HA Panel v5 - tapered", version 69 (work in progress).
- **The print files:** Bambu Studio projects made from version 67, kept on the Mac in
  `~/Documents/HA_panel_renders/print_files_v67/`. Five parts in them are out of date (see
  [`enclosure/README.md`](enclosure/README.md)).
- **The assembly instructions:** not in the repo yet; their final issue is still to come.

## The software
On [`main`](https://github.com/neocleous/ha-panel/tree/main): the installer, the kiosk set-up and the sensor daemon. The
panel pulls `main` every night.

## History
On 2026-11-19 this branch was cleaned up: earlier board revisions, superseded fab sets, the enclosure's build scripts and
audits, and the design's working notes were removed. The history keeps all of it. The tree as it stood
before: [commit 45a38e4](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee).

## Licence
PolyForm Noncommercial 1.0.0: see [`LICENSE.md`](LICENSE.md).
