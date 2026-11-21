# Paste stencils: main board rev 3.3, touch board rev E and mic strip rev 3

Two JLC stencils of 100 × 100 mm: one for the main board's door side, and one for the touch board's back and the mic
strip's back together.

**State (2026-11-21):** issued 2026-11-21 for main board rev 3.3, touch board rev E and mic strip rev 3.
- The main board's and touch board's paste is the same as rev 3.2's and rev D's, aperture for aperture.
- **The mic strip has had a stencil since 2026-11-21 (Daniel, 20:39).** Before that its parts were to be pasted by
  syringe. Its pattern sits on the touch board's sheet, so there is still no third stencil.
- Until 2026-11-21 the main and touch patterns were on one combined stencil of 190 × 190; that set is in
  `fab/superseded/` and is still right for both boards, so it stays a fallback. So does the touch board's stencil of
  2026-11-21 without the strip.

| Stencil | Pattern | Apertures | Orientation |
|---|---|---|---|
| Main board | rev 3.3, door side (KiCad front) | 241, of which 18 on the 9 parts not fitted by default | as drawn (seen from the door) |
| Touch board and mic strip | touch board rev E, back (U1, C1, C2, R1–R4) | 26 | mirrored left-right: seen from the back, the way the stencil meets the board lying front-down |
| | mic strip rev 3, back (MK1, U1, D1–D3, C1–C3, R1, R2, R4, R5), 10 below the touch board, centred under it | 35, of which 10 for the microphone: its four pads, and its sealing ring in six pieces round the port | mirrored left-right, the same way |

- Each stencil carries its boards' outlines. The main board's (87.0 × 57.9) leaves 6.5 and 21.05 of margin a side on the
  sheet. The touch board's and the strip's together (90.0 × 60.0) leave 5.0 and 20.0.
- Smallest aperture 0.300 × 1.475 (the TAS5756M's 48 pins), area ratio at 0.12 mm 1.07. On the second stencil: 0.400 ×
  0.650 (the microphone's four pads), area ratio 1.06; 0.66 is the usual lower limit.
- The microphone's ring is cut in six pieces, so no island of the sheet falls out over the port.

## Files
| File | What |
|---|---|
| `fab/stencil-main-rev3.3-jlc-2026-11-21.zip`, `fab/stencil-touch-revE-strip-rev3-jlc-2026-11-21.zip` | **the uploads, one stencil line each:** F.Paste (`.gtp`), the outline(s) (`.gm1`) and the job file. No copper layer, on purpose |
| [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md) | every order option, the remarks for JLC and the patterns in numbers |
| `fab/gerbers/` | the same files unzipped |
| `fab/stencil-main-check-2026-11-21.txt`, `fab/stencil-touch-strip-check-2026-11-21.txt`, `fab/check-2026-11-21/` | the checks of each stencil against its boards, and the main board's own paste plot the first compares against |
| `stencil-main.kicad_pcb`, `stencil-touch-strip.kicad_pcb` (with `.kicad_pro`) | the stencil-only KiCad files: the boards' footprints and outlines. They have no tracks, vias or zones, so **they are not PCBs**: export nothing but F.Paste and Edge.Cuts from them |
| `stencil-main-preview.png`, `stencil-touch-strip-preview.png` | each upload's apertures on the 100 × 100 sheet; the second also shows the strip's pattern enlarged |
| `fab/superseded/` | the combined stencil of 2026-11-16 (190 × 190) and the touch board's stencil of 2026-11-21 without the strip, each with its check and preview |

## How to order
- **Upload** each zip as its own line ("SMT Stencil"), not through the stencil switch on a board's line. sha256: main
  `e0097f60…a6ffe`, touch and strip `599ac642…4f42c` (in full in the order sheet).
- **Options in short:** no frame, top only, custom 100 × 100 mm, 0.12 mm, electropolishing, no fiducials, apertures
  "1:1 as per Paste Layer", with a remark per line. "Multiple PCBs on one stencil": no for the main board, **yes** for
  the touch board and strip. The second remark asks JLC not to mirror the patterns again.
- Every option and the remarks' exact text: [`fab/ORDER-SHEET.md`](fab/ORDER-SHEET.md).

## How to use them
- **Main board:** lay the stencil on the door side, outline to outline.
- **Touch board:** lay the board front-down; the stencil's pattern is already mirrored to match its back seen from above.
- **Mic strip:** lay the strip front-down (gasket side down), parts side up. At 28 × 6 × 0.8 it needs a jig that holds
  it flush with the surface round it, so the sheet lies flat over it: a pocket of the strip's size and 0.8 deep, or
  spare strips of the same thickness laid round it. **No jig is drawn yet.** The microphone's port stays covered: the
  sheet has no opening over it.
- Each board uses one pattern of a sheet: keep the squeegee off the other pattern, or tape it over.

## How they are made
Rebuild them whenever a board's paste changes. The tools are in [`../main-board/tools/`](../main-board/tools/).
1. Stencil-only KiCad files:
   - `python3 hardware/main-board/tools/stencil_single.py main hardware/main-board/main-board.kicad_pcb hardware/stencil/stencil-main.kicad_pcb`
     copies the main board's footprints and outline into a fresh board;
   - `python3 hardware/main-board/tools/stencil_touch_strip.py hardware/touch-board/touch-board.kicad_pcb hardware/mic-strip/mic-strip.kicad_pcb hardware/stencil/stencil-touch-strip.kicad_pcb`
     copies both boards' footprints and outlines into a fresh board, flipped left-right onto the front (their B.Paste
     becomes F.Paste), the strip 10 below the touch board and centred under it, its references prefixed `S-`;
   - both stop if a board has a board-level paste margin other than 0, or board graphics on a paste layer.
2. `sh hardware/main-board/tools/stencil_export.sh hardware/stencil/stencil-main.kicad_pcb stencil-main-rev3.3 <dir> 2026-11-21`
   (and the same for `stencil-touch-strip.kicad_pcb`, stem `stencil-touch-revE-strip-rev3`) plots F.Paste and
   Edge.Cuts only and zips the three files. **Export each to a folder of its own** (the script empties `<dir>/gerbers`),
   then copy the zip and the files into `fab/`.
3. Checks:
   - `python3 hardware/main-board/tools/stencil_check_single.py main <stencil .gtp> <stencil .gm1> <main board F_Paste.gtp> 100 <preview.png>`.
     The main board's paste file is plotted for this check alone (`kicad-cli pcb export gerbers --layers F.Paste`); it
     is not in the main board's upload;
   - `python3 hardware/main-board/tools/stencil_check_touch_strip.py <stencil .gtp> <stencil .gm1> <touch B_Paste.gbp> <touch Edge_Cuts.gm1> <strip B_Paste.gbp> <strip Edge_Cuts.gm1> 100 0.12 <preview.png>`,
     with the boards' files from `hardware/touch-board/fab/gerbers/` and `hardware/mic-strip/fab/gerbers/`.

The combined stencil of 2026-11-16 was made with `stencil_main_touch.py` and checked with `stencil_check.py`; the
touch board's own stencil of 2026-11-21 with `stencil_single.py touch` and `stencil_check_single.py touch`. The
scripts are kept.

## Checks (2026-11-21)
- **Generator:** 241 paste pads, and 26 + 35 on the second stencil, each at its expected position within 1 nm; no pad
  left on B.Paste.
- **File against file**, by reading every aperture: each of a board's apertures is in its stencil, same place (main)
  or mirrored left-right with its board's shift (touch, strip), same size. The second stencil is compared shape by shape,
  which takes in the microphone's custom apertures, and each board's outline must be a loop of the stencil, moved by
  the same shift as its apertures. Nothing else is in either file; every aperture lies inside its outline; the outlines
  fit 100 × 100.
- **Fresh export:** each stencil file gives the same files as its zip, apart from the export's time.
- **Paste unchanged:** the main board's paste plot of 2026-11-21 equals the one of 2026-11-16, and the touch board's
  rev E back paste equals rev D's, aperture for aperture.
