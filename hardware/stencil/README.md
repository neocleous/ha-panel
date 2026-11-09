# HA panel — combined SMT stencil: main board front + touch board back (D57, 2026-11-09)

One JLC stencil holds two paste patterns (Daniel 2026-11-09, architect log 2026-11-08 D57):

| Area | Apertures | Orientation |
|---|---|---|
| Main board rev 2.1, front | 241 | as drawn (seen from the front) |
| Touch board rev D, back (U1, C1, C2, R1–R4) | 26 | mirrored left-right: seen from the back, the way the stencil meets the touch board lying front-down |

- The touch area sits 10 mm below the main board, left edges aligned. Both outlines are drawn.
- The pattern extent is 90.1 × 109.2 mm.
- The mic strip has no area on this stencil. Its 12 parts are pasted by syringe (`../notes/jlc-fab.md`).

| File | Content |
|---|---|
| `fab/stencil-main-touch-jlc-2026-11-09.zip` | **Upload for the JLC stencil line:** F.Paste (`.gtp`), both outlines (`.gm1`) and the job file. No copper layer, on purpose. |
| `fab/gerbers/` | the same files unzipped |
| `stencil-main-touch.kicad_pcb` | Generated stencil-only file: both boards' footprints and outlines. It has no tracks, vias or zones, so **it is not a PCB**: export nothing but F.Paste and Edge.Cuts from it. |
| `stencil-preview.png` | render of the uploaded gerbers (pygerber 2.4.3): main board above, touch board below |

## How it is made
1. `python3 hardware/main-board/gen/stencil_main_touch.py hardware/main-board/main-board.kicad_pcb hardware/touch-board/touch-board.kicad_pcb hardware/stencil/stencil-main-touch.kicad_pcb`
   - It copies both boards' footprints into a fresh board.
   - It flips the touch board's footprints left-right onto the front (their B.Paste becomes F.Paste) and moves them below the main board.
   - References get a `T-` prefix.
   - It stops if either board has a board-level paste margin other than 0, or board graphics on a paste layer. Both are 0 and none today.
2. `kicad-cli pcb export gerbers --layers F.Paste,Edge.Cuts --exclude-value -o hardware/stencil/fab/gerbers/ hardware/stencil/stencil-main-touch.kicad_pcb` (KiCad 9.0.9).

Rebuild both whenever either board's paste changes.

## Checks (2026-11-09)
- **Generator:** 267 paste pads = main 241 + touch 26. Each sits at its expected position within 1 nm, and no pad is left on B.Paste.
- **Gerber against gerber**, by parsing every flash:
  - every flash of `main-board-F_Paste.gtp` is in the stencil file unchanged (position, aperture shape and size);
  - every flash of `touch-board-B_Paste.gbp` is in it mirrored about the touch board's centre line and moved below the main board;
  - there are no other flashes.
- **Render:** `stencil-preview.png` shows both patterns, including the TAS5756M thermal-pad windows (2 × 4).

The order options and the remark for JLC are in `../notes/jlc-fab.md` ("Stencil").
