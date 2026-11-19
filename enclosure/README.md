# Enclosure

The panel's housing: rev F of the v5 "tapered" design. The display sits in a slab in front of a body that tapers gently
from the base to a flat, vented top, with the two speakers firing forward. Every printed part is black; the shell and the
door are covered with cloth.

**The model is in Autodesk Fusion, not in this repo:** document "HA Panel v5 - tapered", **version 67**. Version 67 is
the version printed. Its saved description still ends in "not for print"; that note is out of date.

**State (2026-11-19):** the print files of version 67 are made: 17 Bambu Studio projects. Four of them are sliced in
Bambu Studio's window before printing. Next: the PLA fit trial, then the black ABS set.

## The printed parts
| Plate | Parts |
|---|---|
| P1 | the base plate and both speaker boxes |
| P2 | the ReSpeaker carrier, the cradle of the USB-C inlet board, the two touch clips and the BME680 hood |
| P3b | the screen plate |
| P3a | the shell |
| P5 | the display slab |
| P4 | the top cap and the USB-C grommet |
| P6 | the rear door |

Before the set: a calibration plate (a frame, a tower and a hole block with a sideways pilot) and an adhesion test (the
shell's first 8 mm).

## Material and print settings, in short
- **Printer and slicer:** Bambu Lab X2D, both nozzles 0.4 High Flow; Bambu Studio 02.09.01.70.
- **First a fit trial in Bambu PLA Basic:** the calibration and the seven plates, 22 h 14 of printing, 502.1 g, on
  Textured PEI without glue, plain tree supports.
- **Then black Bambu ABS:** the calibration and the adhesion test, then the seven plates: about 25 h 49 of printing,
  about 451 g of black ABS and about 26 g of Bambu Support for ABS. Glue on every ABS plate; Textured PEI, except the slab
  and the cap and grommet, which go on the Engineering plate.
- **Support for ABS** feeds the auxiliary nozzle from its external spool. It prints only as a thin interface under the
  faces of the shell, the screen plate, the slab and the adhesion test; those four projects are sliced in the window.
- **Common settings:** "0.20mm Standard" (2 walls, 5 top and 3 bottom layers, 15 % grid); the cap and grommet and the
  slab on "0.12mm High Quality". Tree supports (auto, 30°), X-Y hole compensation 0.1, elephant foot 0.15. The shell has
  4 walls; both speaker boxes and the screen plate print solid.
- **Shrinkage** is 100 % in every project until it is set from the calibration; slice each project again before
  printing.
- **Inserts:** 36 Ruthex per set (32 × M3 × 5.7, 4 × M2.5).

## Where the files are
- **The print files** (Bambu Studio projects, `.3mf`) are kept outside the repo, on the Mac in
  `~/Documents/HA_panel_renders/print_files_v67/`. Every name ends in `_v67`. The scripts that make them are in
  [`print-files/`](print-files/).
- **The assembly instructions** are not in the repo yet; their final issue is still to come.

## Folders and files
| Path | What |
|---|---|
| [`print-files/`](print-files/) | the scripts that export the printed parts from the Fusion model, set them on the bed and make the Bambu Studio projects |
| `HA Panel Final.step` | **the first panel's enclosure (v1),** exported from Shapr3D and in the repo since 2026-08-24: the housing of the panel that is built and in use. `main`'s README links to it |

The build scripts of rev E and rev F, the model and print audits and the change passes are no longer in the tree; the
history keeps them ([`enclosure/fusion/` at commit 45a38e4](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee/enclosure/fusion)).
