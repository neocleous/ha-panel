# Two stencils: main board rev 3.3, and touch board rev E with mic strip rev 3 — JLC order sheet (2026-11-21)

Since 2026-11-21 there are two stencils of 100 × 100 mm in place of the one combined stencil of 190 × 190: one for the
main board, and one for the touch board and the mic strip together.

| Line | Upload | sha256 |
|---|---|---|
| Main board stencil | `stencil-main-rev3.3-jlc-2026-11-21.zip` | `e0097f6055bd09322dac74cab5a10de7c6d13a2cca149c6fb7ec895b5aba6ffe` |
| Touch board and mic strip stencil | `stencil-touch-revE-strip-rev3-jlc-2026-11-21.zip` | `599ac64241dd84a9f7ddcb3c070b1c8a13831d882f812d0e3574a1854434f42c` |

- Each stencil is its own line ("SMT Stencil"), not the stencil switch on a board's line.
- **The paste did not change.** Each board's paste plot of 2026-11-21 has the same apertures, place and size, as the
  plots the combined stencil of 2026-11-16 was checked against (241 on the main board, 26 on the touch board).
- **The mic strip's pattern is new on 2026-11-21** (Daniel, 20:39: he wants a stencil for the strip). It is the strip's
  own back paste, as in its upload, put on the touch board's sheet. Before, the strip was to be pasted by syringe.
- **In the cart since 2026-11-21:**
  - `stencil-main-rev3.3-jlc-2026-11-21-SO12611220098`, **€7.35** (100 × 100 €2.82 + electropolishing €4.53), build
    1–2 days;
  - `stencil-touch-revE-strip-rev3-jlc-2026-11-21-SO12611220107`, **€7.35**, the same make-up: the page
    charged nothing for "Multiple PCBs on one stencil". Its options were read back from the line's details.
  - Replaced and deleted: the combined stencil's line (€11.10), then the touch board's stencil without the strip,
    `stencil-touch-revE-jlc-2026-11-21-SO12611220099` (€7.35).
- **JLC's stencil page was read on 2026-11-21** (https://jlcpcb.com/capabilities/pcb-stencil-manufacturing):
  - custom sizes "within 650*580mm", no smallest custom size and no margin rule stated; "1:1 as PCB" is named as a
    custom size;
  - apertures larger than 0.08 mm;
  - several designs on one stencil are supported. If the stencil is large enough, JLC keeps the layout as drawn; if
    not, it may adjust it; a remark asks it not to. The page names no fee for this.
- The option names are the order page's own, as read on 2026-11-21.

## What is in each zip (3 files)
| File | Content |
|---|---|
| `stencil-main-rev3.3-F_Paste.gtp` | 241 apertures of the main board's door side, as drawn |
| `stencil-main-rev3.3-Edge_Cuts.gm1` | the main board's outline, for orientation |
| `stencil-main-rev3.3-job.gbrjob` | job file |
| `stencil-touch-revE-strip-rev3-F_Paste.gtp` | 61 apertures: 26 of the touch board's back and, 10 below it, 35 of the mic strip's back; both mirrored left-right onto the top layer: seen from the back, the way the stencil meets each board lying front-down |
| `stencil-touch-revE-strip-rev3-Edge_Cuts.gm1` | both outlines, mirrored with their patterns |
| `stencil-touch-revE-strip-rev3-job.gbrjob` | job file |

No copper layer, on purpose.

## Order options
| Option | Main board line | Touch board and strip line | Note |
|---|---|---|---|
| Product | SMT Stencil, its own line | the same | one line per stencil |
| Framework | No | No | hand use on the hotplate |
| Step stencil, nano-coating | No | No | |
| Stencil side | **Top only** | **Top only** | the touch and strip patterns are already mirrored onto the top layer |
| Dimensions | **Custom 100 × 100 mm** | **Custom 100 × 100 mm** | main outline 87.0 × 57.9: 6.5 and 21.05 of margin a side. Touch board and strip together 90.0 × 60.0: 5.0 and 20.0. The line's details show "Dimension: 380mm*280mm" as well as "Custom size: 100*100mm"; the price is the 100 × 100 one |
| Stencil quantity | 1 | 1 | |
| Thickness | "Select by Customer", **0.12 mm** | the same | standing choice |
| Stencil process type | solder paste stencil | the same | |
| Multiple PCBs on one stencil | **No** | **Yes**, and Yes to "Do you allow JLC to re-arrange the typesetting or distance of the patterns?" | the page asks that question when Yes is chosen. A moved pattern does no harm: each pattern stays whole |
| Polishing | **Electropolishing** | **Electropolishing** | standing choice; JLC names it for ICs of 0.5 mm pitch and below (the TAS5756M on the main board) |
| Fiducials | **"No Fiducial"** | **"No Fiducial"** | aligned by hand to the pads |
| Confirm Production file | No | No | |
| Engrave text | No | No | |
| Stencil aperture openings | **"1:1 as per Paste Layer"** | **"1:1 as per Paste Layer"** | the windows in the main board's two chips' centre pads, and the microphone's ring in six pieces, are designed and must stay as drawn |
| Package box | with JLCPCB logo | the same | the page's default |
| Stencil remark | "Main board top paste, one PCB. No copper layer on purpose. Apertures 1:1 as in paste layer. Centre the pattern on the 100x100 sheet." | "Two PCBs on one stencil: touch board and mic strip bottom paste, already mirrored onto the top layer: cut as drawn, do not mirror again. No copper layer on purpose. Apertures 1:1. Centre the layout." | 132 and 198 characters; the page takes 200 at most |

## The patterns in numbers
| Item | Main board | Touch board | Mic strip |
|---|---|---|---|
| Apertures | 241, of which 18 on the 9 parts not fitted by default (R8, R9, R20–R25, R27) | 26 (U1, C1, C2, R1–R4) | 35 (MK1: 4 pads and the ring in 6 pieces; U1; D1–D3; C1–C3; R1, R2, R4, R5) |
| Outline | 87.00 × 57.90 | 90.00 × 44.00 | 28.00 × 6.00, 10.00 below the touch board, centred under it |
| Smallest aperture | 0.300 × 1.475 (the TAS5756M's 48 pins, 0.5 pitch; area ratio 1.07 at 0.12) | 0.600 × 1.950 (lowest area ratio 1.92) | 0.400 × 0.650 (MK1's four pads; area ratio 1.06, the lowest) |

0.66 is the usual lower limit for the area ratio (aperture area ÷ wall area).

## Checks (2026-11-21)
`stencil-main-check-2026-11-21.txt` (made by `../../main-board/tools/stencil_check_single.py`) and
`stencil-touch-strip-check-2026-11-21.txt` (made by `../../main-board/tools/stencil_check_touch_strip.py`), all passed:
1. each aperture of each board's own paste file is in its stencil: the main board's as drawn; the touch board's and the
   strip's mirrored left-right and moved, each by its board's shift; same size. The second stencil is compared shape by
   shape, so the microphone's custom apertures are checked too, and each board's outline must be a loop of the stencil
   moved by the same shift as its apertures;
2. nothing else in the paste files, nothing drawn or filled;
3. every aperture lies inside its own board's outline, and the outlines fit 100 × 100;
4. the smallest aperture is above JLC's 0.08, and every aperture of the second stencil has an area ratio of 0.66 or
   more at 0.12.

The generators' own checks: every paste pad at its expected place within 1 nm (`stencil_single.py`,
`stencil_touch_strip.py`). A fresh export of each stencil file gives the same files as its zip, apart from the export's
time (`fab_same.sh stencil`). Pictures: `../stencil-main-preview.png`, `../stencil-touch-strip-preview.png`. The main
board's paste plot the check compares against is in `check-2026-11-21/`; it is not in the main board's upload.

## Earlier sets
- **Touch board stencil of 2026-11-21 without the strip** (custom 100 × 100):
  `superseded/stencil-touch-revE-jlc-2026-11-21.zip` (sha256 `49050423…2a708`), with its check and preview. Replaced
  the same evening by the stencil with the strip; its 26 apertures are the same.
- **Combined stencil of 2026-11-16** (main rev 3.2 + touch rev D, custom 190 × 190):
  `superseded/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip` (sha256 `f83d86d1…9dc2`), with its check and preview.
  Replaced by the two stencils of 2026-11-21; its apertures equal the main and touch boards' current paste.
- The stencil set of 2026-11-09 held the rev 2.1 main board's pattern and must not be ordered; the history keeps it.
