# Combined stencil, main board rev 3.2 + touch board rev D — JLC order sheet (2026-11-16; sheet corrected 2026-11-17)

**Upload:** `stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip`
sha256 `f83d86d130e1cd6dd12528dfa11b598b52d56163d8d25fc2e75cec845d8e9dc2`

- One stencil, ordered as its own line ("SMT Stencil"), not through the stencil switch on a board's line.
- It replaces `superseded/stencil-main-touch-jlc-2026-11-09.zip`, which holds the rev 2.1 main board's pattern and **must not be ordered**.
- **Uploaded on 2026-11-16 and in JLC's cart,** as the stencil line `SO12611170159`: 1 stencil, €11.05 (6.54 + electropolishing 4.50), build 1–2 days (`claude/parts-list-2026-11-16.md` §1). Nothing is ordered. Daniel ticks the line at checkout.
- **The part change of 2026-11-17** (C101, C102, C122, C123 become 4.7 µF 50 V on the same pads) does not change this zip: a fresh export gives the same 3 files (`../../main-board/rev3.2/parts-2026-11-17/`).
- JLC's stencil figures were read on jlcpcb.com on **2026-11-16** (https://jlcpcb.com/capabilities/pcb-stencil-manufacturing).
- The option names are the order page's own of 2026-11-16, as the parts-list session read them (`claude/parts-list-2026-11-16.md` §1; corrected here on 2026-11-17).

## What is in the zip (3 files)
| File | Content |
|---|---|
| `stencil-main-rev3.2-touch-revD-F_Paste.gtp` | 267 apertures: 241 of the main board's door side as drawn, and 26 of the touch board's back, mirrored left-right, below it |
| `stencil-main-rev3.2-touch-revD-Edge_Cuts.gm1` | both board outlines, for orientation |
| `stencil-main-rev3.2-touch-revD-job.gbrjob` | job file |

No copper layer, on purpose. The mic strip has no area on the stencil; its parts are pasted by syringe.

## Order options
| Option | Choice | Note |
|---|---|---|
| Product | SMT Stencil, its own line | |
| Framework | No | hand use on the hotplate |
| Stencil side | **Top only** | both patterns are on the file's top paste layer; the touch board's is already mirrored |
| Dimensions | **Custom 190 × 190 mm** | holds the 90.1 × 112.1 pattern. JLC accepts custom sizes up to 650 × 580. |
| Thickness | "Select by Customer", then **0.12 mm** | Daniel's standing decision; one of JLC's standard thicknesses |
| Stencil process type | solder paste stencil | |
| Multiple PCBs on one stencil | **Yes**; the page then asks in a dialog whether JLC may re-arrange the patterns: **Yes** | JLC cuts several designs into one stencil and may change their spacing |
| Polishing | **Electropolishing** | Daniel's standing decision; JLC names it for ICs of 0.5 mm pitch and below (the TAS5756M) |
| Fiducials | **"No Fiducial"** | aligned by hand to the pads |
| Stencil aperture openings | **"1:1 as per Paste Layer"** | by default JLC's engineers resize apertures. The windows in the two chips' centre pads are designed and must stay as drawn. |
| Stencil remark | "Two PCBs on one stencil: main board top paste + touch board bottom paste (already mirrored). No copper layer on purpose. Keep each orientation; spacing may change. Apertures 1:1 as in paste layer." | 196 characters, as entered on 2026-11-16. The page takes 200 at most; this sheet's earlier text had 224 and was shortened with every point kept (D194) |

## The pattern in numbers
| Item | Value |
|---|---|
| Apertures | 267 = 241 (main board) + 26 (touch board) |
| Main board area | outline 87.00 × 57.90, at the top |
| Touch board area | outline 90.00 × 44.00, 10.1 below the main board, left edges in line |
| Extent with both outlines | 90.1 × 112.1 mm (apertures alone 81.75 × 86.89) |
| Smallest aperture | 0.300 × 1.475 (48 of them: the TAS5756M's pins, 0.5 pitch). JLC's stencil page: apertures larger than 0.08 mm. |
| Smallest area ratio at 0.12 | 1.07 (aperture area ÷ wall area; 0.66 is the usual lower limit) |
| Paste area in all | 398.8 mm² |

Of the main board's 241 apertures, 18 belong to the 9 parts that are not fitted by default (R8, R9, R20–R25, R27). They get paste and stay empty; the paste reflows flat on the pads.

## Checks (2026-11-16)
`stencil-check-2026-11-16.txt` (made by `../../main-board/gen/stencil_check.py`), all passed:
1. each of the 241 apertures of the main board's own door-side paste plot is in the stencil, same place, same size;
2. each of the 26 apertures of the touch board's back paste file is in it, mirrored left-right and moved by one common shift;
3. there is nothing else in the file: 267 = 241 + 26 apertures, nothing drawn, nothing filled;
4. the outline file holds two closed loops; every aperture lies inside its own board's outline.

The generator's own check: 267 paste pads, each at its expected place within 1 nm.
Picture: `../stencil-preview.png`.
