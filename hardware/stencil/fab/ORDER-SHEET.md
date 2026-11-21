# Two stencils, main board rev 3.3 and touch board rev E — JLC order sheet (2026-11-21)

Since 2026-11-21 each board has a stencil of its own, 100 × 100 mm, in place of the one combined stencil of 190 × 190.

| Line | Upload | sha256 |
|---|---|---|
| Main board stencil | `stencil-main-rev3.3-jlc-2026-11-21.zip` | `e0097f6055bd09322dac74cab5a10de7c6d13a2cca149c6fb7ec895b5aba6ffe` |
| Touch board stencil | `stencil-touch-revE-jlc-2026-11-21.zip` | `4905042379bd46d81aa8217ae9709bcbd5c1a186e9bffa961ae23bbe6d92a708` |

- Each stencil is its own line ("SMT Stencil"), not the stencil switch on a board's line.
- **The paste did not change.** Each board's paste plot of 2026-11-21 has the same apertures, place and size, as the
  plots the combined stencil of 2026-11-16 was checked against (241 on the main board, 26 on the touch board).
- **The combined stencil's cart line must be replaced by these two.** Its zip is kept in `superseded/`; its apertures
  are still right for both boards, so it stays a fallback if one 190 × 190 stencil is wanted after all.
- **In the cart since 2026-11-21:** lines `stencil-main-rev3.3-jlc-2026-11-21-SO12611220098` and
  `stencil-touch-revE-jlc-2026-11-21-SO12611220099`, **€7.35 each** (100 × 100 €2.82 + electropolishing €4.53), build
  1–2 days. The combined stencil's line (€11.10) was deleted.
- JLC's stencil page was read on **2026-11-21** (https://jlcpcb.com/capabilities/pcb-stencil-manufacturing): custom sizes
  "within 650*580mm", no smallest custom size and no margin rule stated; "a 1:1 stencil matching the PCB" is named as a
  custom size; apertures larger than 0.08 mm.
- The option names are the order page's own, as read on 2026-11-16 for the combined stencil.

## What is in each zip (3 files)
| File | Content |
|---|---|
| `stencil-main-rev3.3-F_Paste.gtp` | 241 apertures of the main board's door side, as drawn |
| `stencil-main-rev3.3-Edge_Cuts.gm1` | the main board's outline, for orientation |
| `stencil-main-rev3.3-job.gbrjob` | job file |
| `stencil-touch-revE-F_Paste.gtp` | 26 apertures of the touch board's back, mirrored left-right onto the top layer: seen from the back, the way the stencil meets the board lying front-down |
| `stencil-touch-revE-Edge_Cuts.gm1` | the touch board's outline, mirrored with it |
| `stencil-touch-revE-job.gbrjob` | job file |

No copper layer, on purpose. The mic strips have no stencil; their parts are pasted by syringe.

## Order options (both lines)
| Option | Choice | Note |
|---|---|---|
| Product | SMT Stencil, its own line | one line per stencil |
| Framework | No | hand use on the hotplate |
| Stencil side | **Top only** | the touch pattern is already mirrored onto the top layer |
| Dimensions | **Custom 100 × 100 mm** | main outline 87.0 × 57.9: 6.5 and 21.05 of margin a side; touch outline 90.0 × 44.0: 5.0 and 28.0 |
| Thickness | "Select by Customer", then **0.12 mm** | standing choice |
| Stencil process type | solder paste stencil | |
| Multiple PCBs on one stencil | **No** | one design per stencil |
| Polishing | **Electropolishing** | standing choice; JLC names it for ICs of 0.5 mm pitch and below (the TAS5756M on the main board) |
| Fiducials | **"No Fiducial"** | aligned by hand to the pads |
| Stencil aperture openings | **"1:1 as per Paste Layer"** | the windows in the two chips' centre pads are designed and must stay as drawn |
| Stencil remark, main | "Main board top paste, one PCB. No copper layer on purpose. Apertures 1:1 as in paste layer. Centre the pattern on the 100x100 sheet." | 132 characters; the page takes 200 at most |
| Stencil remark, touch | "Touch board bottom paste, already mirrored onto the top layer: cut as drawn, do not mirror again. No copper layer on purpose. Apertures 1:1. Centre the pattern." | 160 characters |

## The patterns in numbers
| Item | Main board | Touch board |
|---|---|---|
| Apertures | 241, of which 18 on the 9 parts not fitted by default (R8, R9, R20–R25, R27) | 26 (U1, C1, C2, R1–R4) |
| Outline | 87.00 × 57.90 | 90.00 × 44.00 |
| Smallest aperture | 0.300 × 1.475 (the TAS5756M's 48 pins, 0.5 pitch; area ratio 1.07 at 0.12) | 0.600 × 1.950 |

## Checks (2026-11-21)
`stencil-main-check-2026-11-21.txt` and `stencil-touch-check-2026-11-21.txt` (made by
`../../main-board/tools/stencil_check_single.py`), all passed:
1. each aperture of the board's own paste file is in the stencil: the main board's as drawn, the touch board's mirrored
   left-right and moved by one common shift; same size;
2. nothing else in the paste file, nothing drawn or filled;
3. every aperture lies inside the outline, and the outline fits 100 × 100;
4. the smallest aperture is above JLC's 0.08.

The generator's own check: every paste pad at its expected place within 1 nm (`stencil_single.py`). A fresh export of
each stencil file gives the same files as its zip, apart from the export's time (`fab_same.sh stencil`). Pictures:
`../stencil-main-preview.png`, `../stencil-touch-preview.png`. The main board's paste plot the check compares against
is in `check-2026-11-21/`; it is not in the main board's upload.

## Earlier sets
- **Combined stencil of 2026-11-16** (main rev 3.2 + touch rev D, custom 190 × 190): `superseded/stencil-main-rev3.2-touch-revD-jlc-2026-11-16.zip`
  (sha256 `f83d86d1…9dc2`), with its check and preview. Replaced by the two stencils above; its apertures equal the
  boards' current paste.
- The stencil set of 2026-11-09 held the rev 2.1 main board's pattern and must not be ordered; the history keeps it.
