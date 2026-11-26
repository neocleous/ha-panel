# Model scripts: version 69 → 79 (the audit's fixes)

These scripts changed the Fusion model "HA Panel v5 - tapered" from version 69 to version 79 in the enclosure pass
"the audit's fixes" (2026-11-24 to 2026-11-26). The adversarial audit of version 69 left 69 findings; the pass built
the decided changes into the model, and added the unit's 17th printed part, the holder that carries the radar board
behind the touch board.

**The model is at version 79 (g34). It is work in progress, not for print, and waits for its print re-check.** One
block of the pass, the speaker boxes' front faces (block 8), is held and not built.

Lengths are in mm, volumes in mm³. World coordinates: x + = the viewer's left, y + toward the screen, z up from the
base plate's underside.

## Which script made which version
| Version | Block | What changed | Scripts that build and put in |
|---|---|---|---|
| 70 (g25) | 0 | hidden `_v69` copies of the bodies the pass changes | `p03` |
| 71 (g26) | 3 | the USB-C grommet, the rear door, the base plate | `p32`–`p36` |
| 72 (g27) | 4 | base plate, door, grommet again; the display slab and the screen plate | `p43b`, `p43c`, `p46`, `p47` |
| 73, 74 (g28, g29) | 5 | the shell | `p55b`, `p55d`, `p57` |
| 75 (g30) | 6 | the top cap, the two clamps, the strip envelopes and keep-outs | `p62`, `p62b`, `p57` |
| 76, 77 (g31, g32) | 7 | the chin wall and the touch board's bodies, the carrier, the clips, the hood, the boxes | `p68`, `p70`, `p57` |
| 78 (g33) | 7b | five corrections to blocks 6 and 7 | `p79`, `p57` |
| 79 (g34) | 9 | the radar's holder (`RADAR_HOLDER`), its block on the left box, the radar, its two screws and its lead | `p86`, `p88` |

The versions and their names are as `p04_save.py` logged each save (`p04_save.txt`, beside the scripts on the Mac).
Blocks 1 and 2 were studies and saved nothing; block 8 is held.

## The files
- **`v70_lib.py`** loads the helper libraries (below) once per Fusion session and catches a script's output into a file.
- **`p01`–`p04`** preflight, the interference table (`p02`, compared by `p48`), the hidden copies, the save.
- **`p10`–`p21`** block 1 and 2: the radar's layout study, meshes, faces.
- **`p30`–`p38`** block 3. **`p40`–`p51`** block 4, with the layer-grid check (`p50`) and the guard volumes (`p51`).
- **`p52`–`p59`** block 5 and the preflight of the rest; `p52b` walks the shell's way down, `p57` puts bodies in.
- **`p60`–`p65`** block 6; `p65` writes section outlines for pictures.
- **`p66`–`p74`** block 7. **`p78`–`p81`** block 7b.
- **`p75`–`p77`, `p82`–`p93`** block 9. `p82` is the first build of the holder; `p86` is the build that is in the
  model, and reads some constants from `p82`. `p92` draws the two section pictures with matplotlib; `p93` takes the views.
- **`p94`–`p97`** the close: `p94` exports the archive and runs earlier checks again, reporting what changed in their
  outputs (`p94b` compares outputs outside Fusion); `p95` reads the door's stand, the display module's ride-in, the layer
  grid over all 17 printed parts and the main board 0.1 out; `p96` and `p97` repeat the checks of the pass before this
  one (`../model-v68/`) that no script here repeats.
- **`calc_b9_arm_and_lead.py`** plain Python: the holder's spring arm and the radar lead's free run as a hanging chain.
  It was written at the close from the block 9 report's inputs and gives that report's figures again.

Scripts that were replaced are kept with their outputs' story in their headers: `p43_s6` (replaced by `p43b`), `p44` and
`p44b` (by `p44c`), `p55` and `p55c` (by `p55b` and `p55d`), `p52` (by `p52b`), `p82` (by `p86`).

Each file's first lines say what it does, whether it changes the document, and how it is run. Only `p03`, `p04`, `p36`,
`p47`, `p57`, `p70` and `p88` change the document; `p93` changes which bodies are shown and puts that back; every other
script works on temporary bodies, or adds `TMP_*` bodies for measuring and deletes them again.

## How they run
Inside Autodesk Fusion's Python, sent through Fusion's MCP connector with the design open. In this pass the files lay
on the Mac in `~/Documents/HA_panel_renders/audit_fixes_v70/` (the path is written in each file as `D`), each beside
its outputs `pNN_<stage>.txt`. Every call was a short runner that checks the file's sha256 and calls its `main()`:

```python
import runpy, hashlib
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
def run(_context: str):
    if hashlib.sha256(open(D + 'p95_close_checks.py', 'rb').read()).hexdigest() != '<sha256>':
        raise RuntimeError('sha256 differs')
    runpy.run_path(D + 'p95_close_checks.py')['main']('door')
```

A build script keeps its result as a temporary body in the library's cache (`k.c['b9_holder']` and the like); a put
script moves it into the document. **The cache is lost when Fusion restarts.** Check stages that read a block's
temporary bodies (`p44d`, `p63`, `p69` and the `put=False` stages of `p83` and `p87`) therefore run only in the session
that built them; `p96` repeats `p44d` on the model.

## Files they need that are not in this tree
As `../model-v68/`: the two helper libraries and the unit checks of the earlier passes, read from the tree at commit
[`45a38e4`](https://github.com/neocleous/ha-panel/tree/45a38e49d72cf125aab3f4aa91dd065b3bc4f7ee) and sha256-checked by
`v70_lib.py`:

| File at `45a38e4` | Loaded as | What it gives |
|---|---|---|
| `enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py` | `c3k` | the model's frames, temporary solids, distances, the list of the unit's bodies, a tool's reach along a line |
| `enclosure/fusion/revF/split/change3/c3_lib.py` | `c3` | the cloth reference for the outer-skin check, faces of a body in a box |
| `enclosure/fusion/revF/floor_plate/fusion/v5f_k4a_unit_checks.py` | `c3k.K4NS` | the display module's ride-in, the left box's slide, the interference table |

## Records
The reports, with every figure and its source, are in the Project "HA Touch Panel": the block reports
`claude/report-enclosure-audit-fixes-block<n>-<date>.md`, the closing report
`claude/report-enclosure-audit-fixes-closing-2026-11-26.md`, and the hand-over for the print re-check
`claude/handover-print-recheck-v79-2026-11-26.md`. The archive of version 79 is on the Mac:
`~/Documents/HA Panel v5 - tapered revF-g34.f3d` (sha256 `2a7edf7e50b71ab2d2a40021a32a3dbbe11222d26867fb14c5167db7ec4d6ce2`).
