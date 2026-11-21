# Paste stencils: main board rev 3.3 and touch board rev E

Two JLC stencils of 100 × 100 mm, one per board: the main board's door side and the touch board's back. The mic strips
have no stencil; their parts are pasted by syringe.

**State (2026-11-21):** issued 2026-11-21 for main board rev 3.3 and touch board rev E. Their paste is the same as
rev 3.2's and rev D's, aperture for aperture. Until 2026-11-21 both patterns were on one combined stencil of 190 × 190;
that set is in `fab/superseded/` and is still right for both boards, so it stays a fallback.

| Stencil | Apertures | Orientation |
|---|---|---|
| Main board rev 3.3, door side (KiCad front) | 241, of which 18 on the 9 parts not fitted by default | as drawn (seen from the door) |
| Touch board rev E, back (U1, C1, C2, R1–R4) | 26 | mirrored left-right: seen from the back, the way the stencil meets the touch board lying front-down |

- Each stencil carries its board's outline; the main board's outline (87.0 × 57.9) leaves 6.5 and 21.05 of margin a side
  on the sheet, the touch board's (90.0 × 44.0) 5.0 and 28.0.
- Smallest aperture 0.300 × 1.475 (the TAS5756M's 48 pins); area ratio at 0.12 mm: 1.07.

## Files
| File | What |
|---|---|
| `fab/stencil-main-rev3.3-jlc-2026-11-21.zip`, `fab/stencil-touch-revE-jlc-2026-11-21.zip` | **the uploads, one stencil line each:** F.Paste (`.gtp`), the outline (`.gm1`) and the job file. No copper layer, on purpose |
| [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md) | every order option, the remarks for JLC and the patterns in numbers |
| `fab/gerbers/` | the same files unzipped |
| `fab/stencil-main-check-2026-11-21.txt`, `fab/stencil-touch-check-2026-11-21.txt`, `fab/check-2026-11-21/` | the checks of each stencil against its board, and the main board's own paste plot the first compares against |
| `stencil-main.kicad_pcb`, `stencil-touch.kicad_pcb` (with `.kicad_pro`) | the stencil-only KiCad files: one board's footprints and outline each. They have no tracks, vias or zones, so **they are not PCBs**: export nothing but F.Paste and Edge.Cuts from them |
| `stencil-main-preview.png`, `stencil-touch-preview.png` | each upload's apertures on the 100 × 100 sheet |
| `fab/superseded/` | the combined stencil of 2026-11-16 (190 × 190) with its check and preview |

## How to order
- **Upload** each zip as its own line ("SMT Stencil"), not through the stencil switch on a board's line. sha256: main
  `e0097f60…a6ffe`, touch `49050423…2a708` (in full in the order sheet).
- **Options in short:** no frame, top only, custom 100 × 100 mm, 0.12 mm, one design per stencil, electropolishing, no
  fiducials, apertures "1:1 as per Paste Layer", with a remark per line. The touch remark asks JLC not to mirror the
  pattern again.
- Every option and the remarks' exact text: [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md).

## How to use them
- Main board: lay the stencil on the door side, outline to outline.
- Touch board: lay the board front-down; the stencil's pattern is already mirrored to match its back seen from above.

## How they are made
Rebuild them whenever a board's paste changes. The tools are in [`../main-board/tools/`](../main-board/tools/).
1. `python3 hardware/main-board/tools/stencil_single.py main hardware/main-board/main-board.kicad_pcb hardware/stencil/stencil-main.kicad_pcb`
   and `python3 hardware/main-board/tools/stencil_single.py touch hardware/touch-board/touch-board.kicad_pcb hardware/stencil/stencil-touch.kicad_pcb`
   - copy one board's footprints and outline into a fresh board; for the touch board, flipped left-right onto the front
     (its B.Paste becomes F.Paste);
   - stop if the board has a board-level paste margin other than 0, or board graphics on a paste layer.
2. `sh hardware/main-board/tools/stencil_export.sh hardware/stencil/stencil-main.kicad_pcb stencil-main-rev3.3 <dir> 2026-11-21`
   (and the same for `stencil-touch.kicad_pcb`, stem `stencil-touch-revE`) plots F.Paste and Edge.Cuts only and zips
   the three files. Each export goes to its own folder, then the zip and the files are copied into `fab/`.
3. `python3 hardware/main-board/tools/stencil_check_single.py main <stencil .gtp> <stencil .gm1> <main board F_Paste.gtp> 100 <preview.png>`;
   for the touch stencil, `touch` and `hardware/touch-board/fab/gerbers/touch-board-revE-B_Paste.gbp`. The main board's
   paste file is plotted for this check alone (`kicad-cli pcb export gerbers --layers F.Paste`); it is not in the main
   board's upload.

The combined stencil of 2026-11-16 was made with `stencil_main_touch.py` and checked with `stencil_check.py`; both
scripts are kept.

## Checks (2026-11-21)
- **Generator:** 241 and 26 paste pads, each at its expected position within 1 nm; no pad left on B.Paste.
- **File against file**, by reading every aperture: each of the board's apertures is in its stencil, same place (main)
  or mirrored left-right with one common shift (touch), same size; nothing else; every aperture inside the outline; the
  outline fits 100 × 100.
- **Fresh export:** each stencil file gives the same files as its zip, apart from the export's time.
- **Paste unchanged:** the main board's paste plot of 2026-11-21 equals the one of 2026-11-16, and the touch board's
  rev E back paste equals rev D's, aperture for aperture.
