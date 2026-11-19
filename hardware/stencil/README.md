# Paste stencil: main board rev 3.2 and touch board rev D

One JLC stencil holds two paste patterns: the main board's door side and the touch board's back. The mic strips have no
area on it; their parts are pasted by syringe.

**State (2026-11-19):** issued 2026-11-16 with the paste of main board rev 3.2 as it goes to the fab. The earlier
stencil of 2026-11-09 (for main board rev 2.1) is superseded and must not be ordered; the history keeps it.

| Area | Apertures | Orientation |
|---|---|---|
| Main board rev 3.2, door side (KiCad front) | 241, of which 18 on the 9 parts not fitted by default | as drawn (seen from the door) |
| Touch board rev D, back (U1, C1, C2, R1–R4) | 26 | mirrored left-right: seen from the back, the way the stencil meets the touch board lying front-down |

- The touch area sits 10.1 mm below the main board (edge to edge), left edges aligned. Both outlines are drawn.
- The pattern extent is 90.1 × 112.1 mm with both outlines; the apertures alone span 81.75 × 86.89 mm.
- Smallest aperture 0.300 × 1.475 (the TAS5756M's 48 pins); area ratio at 0.12 mm: 1.07.

## Files
| File | What |
|---|---|
| `fab/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` | **the upload for JLC's stencil line:** F.Paste (`.gtp`), both outlines (`.gm1`) and the job file. No copper layer, on purpose |
| [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md) | every order option, the remark for JLC and the pattern in numbers |
| `fab/gerbers/` | the same files unzipped |
| `fab/stencil-check-2026-11-16.txt`, `fab/check-2026-11-16/` | the check of the stencil against both boards, and the main board's own paste plot it compares against |
| `stencil-main-touch.kicad_pcb`, `.kicad_pro` | the stencil-only KiCad file: both boards' footprints and outlines. It has no tracks, vias or zones, so **it is not a PCB**: export nothing but F.Paste and Edge.Cuts from it |
| `stencil-preview.png` | a render of the upload's files: main board above, touch board below |

## How to order
- **Upload** the zip as its own line ("SMT Stencil"), not through the stencil switch on a board's line. sha256
  `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2`.
- **Options in short:** no frame, top only, custom 190 × 190 mm, 0.12 mm, multiple PCBs on one stencil (and yes to
  re-arranging), electropolishing, no fiducials, apertures "1:1 as per Paste Layer", with the remark asking JLC to keep
  each pattern's orientation. JLC may change the spacing between the two patterns.
- Every option and the remark's exact text: [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md).

## How to use it
- Use the same face of the stencil up for both boards. The touch pattern is already mirrored to match the touch board's
  back seen from above, with the board lying front-down.
- Paste one board at a time. Keep the squeegee off the other pattern.

## How it is made
Rebuild it whenever either board's paste changes. The tools are in [`../main-board/tools/`](../main-board/tools/).
1. `python3 hardware/main-board/tools/stencil_main_touch.py hardware/main-board/main-board.kicad_pcb hardware/touch-board/touch-board.kicad_pcb hardware/stencil/stencil-main-touch.kicad_pcb`
   - copies both boards' footprints into a fresh board;
   - flips the touch board's footprints left-right onto the front (their B.Paste becomes F.Paste) and moves them below
     the main board; their references get a `T-` prefix;
   - stops if either board has a board-level paste margin other than 0, or board graphics on a paste layer.
2. `sh hardware/main-board/tools/stencil_export.sh hardware/stencil/stencil-main-touch.kicad_pcb stencil-main-rev3.2-touch-revD hardware/stencil/fab 2026-11-16`
   plots F.Paste and Edge.Cuts only (`kicad-cli pcb export gerbers --layers F.Paste,Edge.Cuts --exclude-value`,
   KiCad 9.0.9) from a copy named after both revisions, and zips the three files.
3. `python3 hardware/main-board/tools/stencil_check.py <stencil .gtp> <stencil .gm1> <main board F_Paste.gtp> hardware/touch-board/fab/gerbers/touch-board-B_Paste.gbp hardware/stencil/stencil-preview.png`
   The main board's paste file is plotted for this check alone (`kicad-cli pcb export gerbers --layers F.Paste`); it is
   not in the main board's upload.

## Checks (2026-11-16)
- **Generator:** 267 paste pads = main 241 + touch 26. Each sits at its expected position within 1 nm, and no pad is
  left on B.Paste.
- **File against file** (`fab/stencil-check-2026-11-16.txt`), by reading every aperture:
  - each of the 241 apertures of the main board's own paste plot is in the stencil file, same place, same size;
  - each of the 26 apertures of `touch-board-B_Paste.gbp` is in it, mirrored left-right and moved by one common shift;
  - there are no others, and nothing drawn or filled;
  - the outline file holds two closed loops, and every aperture lies inside its own board's outline.
- **Render:** `stencil-preview.png` shows both patterns, including the windows in the centre pads of the TAS5756M
  (2 × 4) and the eFuse U1 (2 × 2).
