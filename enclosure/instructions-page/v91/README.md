# Instructions page, version 91 (2026-11-27)

Scripts that read the Fusion model "HA Panel v5 - tapered" at version 91, render the step pictures and build the interactive assembly page.

- **The model is only read.** `p91_10_render.py` hides and shows bodies and colours them as temporary graphics for the pictures; it records the visibility state in `out/bulbs.json` and restores it. Nothing is saved; the document was closed without saving and reopened at version 91 at the end.
- Each Fusion script runs from a small loader that checks its sha256 before it runs. Output goes to files under `~/Documents/HA_panel_renders/instructions_page_v91/out/`.

| Script | What it does |
|---|---|
| `p91_00_preflight.py` | version, body counts and the 17 printed parts' volumes (start and end) |
| `p91_01_bodies.py` … `p91_08_holes.py` | read-only probes: bodies, the screen plate's rest on its lands, the lower posts, sections, the cap's walk up the bay, screw lumps, holes |
| `p91_10_render.py` | modes `hide`, `shots`, `restore`: renders the shots in `spec/<name>.json` |
| `p91_20_crop.py` | crops each render and rescales its marks |
| `p91_21_mkspec.py` | writes `spec/full.json` (42 shots) |
| `p91_22_mkdata.py`, `mkinfo.py` | write the page's `steps.json` from the instructions, harness list, parts list and print sheet of 2026-11-27 |
| `p91_23_check.py` | Playwright: walks every page on phone and wide screens |

The page itself, its pictures and data are on the Mac in `~/Documents/HA_panel_renders/instructions_page_v91/site/`.
