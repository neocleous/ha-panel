# Board tools

Scripts that make or check the files that are ordered: the fab sets, the stencil and the main board's assembly drawing.
They need KiCad 9 (kicad-cli 9.0.9); the Python scripts that import `pcbnew` run with KiCad's own Python.
`fab_check.py` and `stencil_check.py` also draw a preview with pygerber.

| Script | What it does | How to run it |
|---|---|---|
| `fab_export.sh` | one JLC fab set from one board: Gerbers, drill files, drill report, job file and the zip to upload, all named after a stem with the board and its revision in it | `sh fab_export.sh <board.kicad_pcb> <stem> <fab dir> <date> <layers, comma separated>` |
| `fab_check.py` | checks a fab set against the board it was made from: files and layer functions, a flash at every via on every copper layer, no soldermask opening at a via, paste counts, outline, hole counts, the job file's stack-up, and that the stored pours are current | `python3 fab_check.py <board.kicad_pcb> <fab dir>/gerbers [render.png]` |
| `fab_same.sh` | proves that a board file still gives the set already uploaded: exports it afresh and compares it file by file with the zip, leaving out only the lines that carry the time of the export. Use it after a change that must not reach the fab (a value, a part number, a field) | `sh fab_same.sh board <board.kicad_pcb> <stem> <layers> <uploaded.zip>` or `sh fab_same.sh stencil <stencil.kicad_pcb> <stem> <uploaded.zip>` |
| `stencil_single.py` | builds the stencil-only KiCad file for one board: the main board's front paste as drawn, or the touch board's back paste mirrored onto the front (one 100 × 100 stencil each since 2026-11-21) | `python3 stencil_single.py main\|touch <board.kicad_pcb> <out.kicad_pcb>` |
| `stencil_check_single.py` | checks a one-board stencil's paste file against that board's own paste file, flash by flash, and that its outline fits the stencil | `python3 stencil_check_single.py main\|touch <stencil F_Paste.gtp> <stencil Edge_Cuts.gm1> <board paste .gtp/.gbp> <size mm> [preview.png]` |
| `stencil_main_touch.py` | (the combined stencil of 2026-11-16) builds one stencil-only KiCad file from the main board's front paste and the touch board's back paste (mirrored, placed below) | `python3 stencil_main_touch.py <main-board.kicad_pcb> <touch-board.kicad_pcb> <out.kicad_pcb>` |
| `stencil_export.sh` | a stencil's upload: F.Paste and the outline(s), zipped | `sh stencil_export.sh <stencil.kicad_pcb> <stem> <fab dir> <date>` |
| `stencil_check.py` | (the combined stencil) checks its paste file against both boards' own paste files, flash by flash | `python3 stencil_check.py <stencil F_Paste.gtp> <stencil Edge_Cuts.gm1> <main board F_Paste.gtp> <touch board B_Paste.gbp> [preview.png]` |
| `assembly.py` | the main board's assembly drawing: all 120 part names, every value, the placing list and the back. The revision and the fab issue are set at its top (`REV`, `ISSUE`) | from `hardware/main-board`: `python3 tools/assembly.py [board.kicad_pcb] [out.pdf]` |

**Example:** the main board's set of 2026-11-21 was made from `hardware/main-board/fab/` with
`sh ../tools/fab_export.sh ../main-board.kicad_pcb main-board-rev3.3 . 2026-11-21 F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts`.
The stencils' three steps are in [`../../stencil/README.md`](../../stencil/README.md); JLC's export settings in
[`../../notes/jlc-fab.md`](../../notes/jlc-fab.md).
