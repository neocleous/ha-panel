"""A stencil-only KiCad file for one board, to cut a stencil of its own (100 x 100 mm, chosen 2026-11-21).

    python3 stencil_single.py main  <main-board.kicad_pcb>  <out.kicad_pcb>
    python3 stencil_single.py touch <touch-board.kicad_pcb> <out.kicad_pcb>

- main: the main board's footprints where they are (all its SMD parts are on the front, F.Paste), and its outline;
- touch: the touch board's footprints flipped left-right onto the front, i.e. its back paste as seen from the back,
  which is how the stencil meets the touch board when it lies front-down on the hotplate; its outline flipped with it.
No tracks, vias, zones or board graphics, so the file cannot pass for a PCB. Only F.Paste and Edge.Cuts are exported
from it (stencil_export.sh). Prints a position check: every paste pad must land where it belongs (tolerance 1 nm), and
the outline's extent, which must fit the stencil with room to spare."""
import sys

import pcbnew


def build(kind, path, out_path):
    src = pcbnew.LoadBoard(path)
    ds = src.GetDesignSettings()
    if ds.m_SolderPasteMargin != 0 or ds.m_SolderPasteMarginRatio != 0:
        raise SystemExit('board-level paste margin is not 0; copy it into the stencil board first')
    if any(d.GetLayer() in (pcbnew.F_Paste, pcbnew.B_Paste) for d in src.GetDrawings()):
        raise SystemExit('board graphics on a paste layer; copy them too')
    flip = kind == 'touch'
    layer = pcbnew.B_Paste if flip else pcbnew.F_Paste
    bb = src.GetBoardEdgesBoundingBox()
    centre = pcbnew.VECTOR2I(bb.GetCenter().x, bb.GetCenter().y)
    expect = {}
    for fp in src.GetFootprints():
        for i, p in enumerate(fp.Pads()):
            if p.GetLayerSet().Contains(layer):
                pos = p.GetPosition()
                expect[(fp.GetReference(), p.GetNumber(), i)] = ((2 * centre.x - pos.x) if flip else pos.x, pos.y)
    # a fresh board, so nothing but footprints and the outline comes across
    st = pcbnew.BOARD()
    for fp in src.GetFootprints():
        n = pcbnew.FOOTPRINT(fp)
        st.Add(n)
        if flip:
            n.Flip(centre, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        for p in n.Pads():
            p.SetNetCode(0)
    for d in src.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            n = d.Duplicate()
            st.Add(n)
            if flip:
                n.Flip(centre, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    got = {}
    for fp in st.GetFootprints():
        for i, p in enumerate(fp.Pads()):
            if p.GetLayerSet().Contains(pcbnew.F_Paste):
                got[(fp.GetReference(), p.GetNumber(), i)] = (p.GetPosition().x, p.GetPosition().y)
            if p.GetLayerSet().Contains(pcbnew.B_Paste):
                raise SystemExit('B.Paste pad left on ' + fp.GetReference())
    bad = [k for k in expect if k not in got or max(abs(expect[k][0] - got[k][0]), abs(expect[k][1] - got[k][1])) > 1]
    extra = [k for k in got if k not in expect]
    sb = st.GetBoardEdgesBoundingBox()
    print('%s: F.Paste pads expected %d, placed %d, misplaced %s, unexpected %s; outline extent %.2f x %.2f mm' % (
        kind, len(expect), len(got), bad, extra, pcbnew.ToMM(sb.GetWidth()), pcbnew.ToMM(sb.GetHeight())))
    if bad or extra:
        raise SystemExit('position check failed')
    pcbnew.SaveBoard(out_path, st)


if __name__ == '__main__':
    build(*sys.argv[1:4])
