# HA panel — combined SMT stencil: main board rev 3.2 door side + touch board rev D back (D57; issue 2026-11-16)

One JLC stencil holds two paste patterns (Daniel 2026-11-09, architect log 2026-11-08 D57). **Issue 2026-11-16:** regenerated with the paste of main board rev 3.2 as it goes to the fab. The 2026-11-09 stencil (rev 2.1 main board) is in `fab/superseded/` and must not be ordered.

| Area | Apertures | Orientation |
|---|---|---|
| Main board rev 3.2, door side (KiCad front) | 241, of which 18 on the 9 parts not fitted by default | as drawn (seen from the door) |
| Touch board rev D, back (U1, C1, C2, R1–R4) | 26 | mirrored left-right: seen from the back, the way the stencil meets the touch board lying front-down |

- The touch area sits 10.1 mm below the main board (edge to edge), left edges aligned. Both outlines are drawn.
- JLC may change the spacing: its "Multiple PCBs on one stencil" option needs consent to re-arrange the patterns. The remark asks it to keep each pattern's orientation (`fab/ORDER-SHEET.md`).
- The pattern extent is 90.1 × 112.1 mm with both outlines; the apertures alone span 81.75 × 86.89 mm.
- The mic strip has no area on this stencil. Its 12 parts are pasted by syringe.

| File | Content |
|---|---|
| `fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` | **Upload for the JLC stencil line:** F.Paste (`.gtp`), both outlines (`.gm1`) and the job file. No copper layer, on purpose. sha256 `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2` |
| `fab/ORDER-SHEET.md` | **every order option, the remark for JLC and the pattern in numbers** |
| `fab/gerbers/` | the same files unzipped |
| `stencil-main-touch.kicad_pcb` | Generated stencil-only file: both boards' footprints and outlines. It has no tracks, vias or zones, so **it is not a PCB**: export nothing but F.Paste and Edge.Cuts from it. |
| `stencil-preview.png` | render of the upload's files (pygerber 2.4.3): main board above, touch board below |
| `fab/stencil-check-2026-11-16.txt`, `fab/check-2026-11-16/` | the check below and the main board's own paste plot it compares against |
| `fab/superseded/` | the 2026-11-09 stencil (main board rev 2.1): zip, files, preview. Kept for the record only. |

## How it is made
1. `python3 hardware/main-board/gen/stencil_main_touch.py hardware/main-board/main-board.kicad_pcb hardware/touch-board/touch-board.kicad_pcb hardware/stencil/stencil-main-touch.kicad_pcb`
   - It copies both boards' footprints into a fresh board.
   - It flips the touch board's footprints left-right onto the front (their B.Paste becomes F.Paste) and moves them below the main board.
   - References get a `T-` prefix.
   - It stops if either board has a board-level paste margin other than 0, or board graphics on a paste layer. Both are 0 and none today.
2. `sh hardware/main-board/gen/stencil_export.sh hardware/stencil/stencil-main-touch.kicad_pcb stencil-main-rev3.2-touch-revD hardware/stencil/fab 2026-11-16`. It plots F.Paste and Edge.Cuts only (`kicad-cli pcb export gerbers --layers F.Paste,Edge.Cuts --exclude-value`, KiCad 9.0.9) from a copy named after both revisions, so the files carry them, and zips the three files.
3. `python3 hardware/main-board/gen/stencil_check.py <stencil .gtp> <stencil .gm1> <main board F_Paste.gtp> hardware/touch-board/fab/gerbers/touch-board-B_Paste.gbp hardware/stencil/stencil-preview.png`. The main board's paste file is plotted for this check alone (`kicad-cli pcb export gerbers --layers F.Paste`); it is not in the main board's upload.

Rebuild both whenever either board's paste changes.

## Checks (2026-11-16)
- **Generator:** 267 paste pads = main 241 + touch 26. Each sits at its expected position within 1 nm, and no pad is left on B.Paste.
- **File against file** (`fab/stencil-check-2026-11-16.txt`), by reading every aperture:
  - each of the 241 apertures of the main board's own paste plot is in the stencil file, same place, same size;
  - each of the 26 apertures of `touch-board-B_Paste.gbp` is in it, mirrored left-right and moved by one common shift;
  - there are no others, and nothing drawn or filled;
  - the outline file holds two closed loops, and every aperture lies inside its own board's outline.
- **Smallest aperture:** 0.300 × 1.475 (the TAS5756M's 48 pins). Area ratio at 0.12 mm: 1.07.
- **Render:** `stencil-preview.png` shows both patterns, including the windows in the centre pads of the TAS5756M (2 × 4) and the eFuse U1 (2 × 2).

## Use
- Use the same face of the stencil up for both boards. The touch pattern is already mirrored to match the touch board's back seen from above, with the board lying front-down.
- Paste one board at a time. Keep the squeegee off the other pattern.

The order options and the remark for JLC are in `fab/ORDER-SHEET.md`.
