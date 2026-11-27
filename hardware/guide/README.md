# Electronics guide

`ha-panel-electronics.html` is the panel's electronics page: every board to scale as it sits in the enclosure, every part
and every wire, the leads, before-you-solder steps, first power-up with expected readings, and every connection by net.
It is generated; do not edit it by hand.

```
pip install kiutils shapely
python3 hardware/guide/build.py
```

The build reads one data model and stops (exit 1) before writing anything if a check fails.

## Sources
| What | From |
|---|---|
| Boards: outlines, pads, nets, bodies, holes | the three `.kicad_pcb` files and their schematics (DNP), via `src/kicad_extract.py` |
| Pi signal wires (leads 8 to 10) | `hardware/main-board/gpio-leads.md`, parsed |
| Part numbers | `hardware/notes/bom-2026-11-17.csv` |
| Bought modules, other leads, colours, open points | `data/panel.py`, each fact with its source |
| Places in the unit | the Fusion model "HA Panel v5 - tapered", version 91, read-only: `src/fusion_read_meshes.py` in Fusion, `src/decode_mesh.py`, then `src/model_outlines.py` writes `data/positions.json` |

## Checks
- `gpio-leads.md` against the board's nets;
- every wire end exists; no pin, pad or hole takes two wires;
- no short: inside each connected group every board net and every pin's role agree; microphone wires match by function;
- no split: every pin and socket pad that carries a net is wired; spares stay free;
- each Pi signal wire in its own housing;
- main board: nothing under an M3 head (the fabrication circle of H1–H4), no two courtyards overlapping;
- J1 is the middle of the three 2-way sockets and plugged first.

## Files
- `build.py` — model, checks, page.
- `src/model.py` — the data model; `src/checks.py` — the checks; `src/render.py`, `src/svgboard.py` — drawings and tables.
- `data/panel.py`, `data/positions.json` — the data not in KiCad.
