"""One JLC stencil for the main board's front paste and the touch board's back paste (D57, Daniel 2026-11-09).

Builds a stencil-only KiCad file from the two boards:
- the main board's footprints where they are (all its SMD parts are on the front, F.Paste);
- the touch board's footprints flipped left-right onto the front, i.e. its back paste as seen from the back, which is how
  the stencil meets the touch board when it lies front-down on the hotplate;
- the touch board placed GAP mm below the main board, left edges aligned; references prefixed "T" (T-U1, T-R1, ...);
- both outlines on Edge.Cuts; no tracks, vias, zones or board graphics, so the file cannot pass for a PCB.

Only F.Paste and Edge.Cuts are exported from it (see hardware/stencil/README.md).
Run: python3 stencil_main_touch.py <main-board.kicad_pcb> <touch-board.kicad_pcb> <out.kicad_pcb>
Prints a position check: every main-board paste pad must stay where it is and every touch-board paste pad must land at
its mirrored, offset position (tolerance 1 nm)."""
import sys

import pcbnew

GAP = 10.0  # mm between the main board's bottom edge and the touch board's top edge


def _copy_footprints(src, dst, prefix='', flip_centre=None, off=None):
    for fp in src.GetFootprints():
        n = pcbnew.FOOTPRINT(fp)
        dst.Add(n)
        if flip_centre is not None:
            n.Flip(flip_centre, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        if off is not None:
            n.Move(off)
        n.SetReference(prefix + fp.GetReference())
        for p in n.Pads():
            p.SetNetCode(0)


def _copy_edges(src, dst, flip_centre=None, off=None):
    for d in src.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            n = d.Duplicate()
            dst.Add(n)
            if flip_centre is not None:
                n.Flip(flip_centre, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            if off is not None:
                n.Move(off)


def build(main_path, touch_path, out_path):
    main = pcbnew.LoadBoard(main_path)
    touch = pcbnew.LoadBoard(touch_path)
    for b in (main, touch):
        ds = b.GetDesignSettings()
        if ds.m_SolderPasteMargin != 0 or ds.m_SolderPasteMarginRatio != 0:
            raise SystemExit('board-level paste margin is not 0; copy it into the stencil board first')
        if any(d.GetLayer() in (pcbnew.F_Paste, pcbnew.B_Paste) for d in b.GetDrawings()):
            raise SystemExit('board graphics on a paste layer; copy them too')

    # A fresh board, so nothing but footprints and outlines comes across (removing zones from a loaded board crashes
    # pcbnew 9.0.9's Python binding).
    st = pcbnew.BOARD()
    sds = st.GetDesignSettings()
    if sds.m_SolderPasteMargin != 0 or sds.m_SolderPasteMarginRatio != 0:
        raise SystemExit('new board paste margin is not 0')

    mbb = main.GetBoardEdgesBoundingBox()
    tbb = touch.GetBoardEdgesBoundingBox()
    centre = pcbnew.VECTOR2I(tbb.GetCenter().x, tbb.GetCenter().y)
    # A left-right flip about the centre keeps the bounding box, so the offset can be taken before flipping.
    off = pcbnew.VECTOR2I(mbb.GetLeft() - tbb.GetLeft(), mbb.GetBottom() + pcbnew.FromMM(GAP) - tbb.GetTop())

    expect = {}
    for fp in touch.GetFootprints():
        for i, p in enumerate(fp.Pads()):
            if p.GetLayerSet().Contains(pcbnew.B_Paste):
                pos = p.GetPosition()
                expect[('T-' + fp.GetReference(), p.GetNumber(), i)] = (2 * centre.x - pos.x + off.x, pos.y + off.y)
    main_paste = {(fp.GetReference(), p.GetNumber(), i): (p.GetPosition().x, p.GetPosition().y)
                  for fp in main.GetFootprints() for i, p in enumerate(fp.Pads())
                  if p.GetLayerSet().Contains(pcbnew.F_Paste)}
    expect.update(main_paste)

    _copy_footprints(main, st)
    _copy_edges(main, st)
    _copy_footprints(touch, st, 'T-', centre, off)
    _copy_edges(touch, st, centre, off)

    got = {}
    for fp in st.GetFootprints():
        for i, p in enumerate(fp.Pads()):
            if p.GetLayerSet().Contains(pcbnew.F_Paste):
                got[(fp.GetReference(), p.GetNumber(), i)] = (p.GetPosition().x, p.GetPosition().y)
            if p.GetLayerSet().Contains(pcbnew.B_Paste):
                raise SystemExit('B.Paste pad left on ' + fp.GetReference())
    bad = [k for k in expect if k not in got or max(abs(expect[k][0] - got[k][0]), abs(expect[k][1] - got[k][1])) > 1]
    extra = [k for k in got if k not in expect]
    print('F.Paste pads: main', len(main_paste), '+ touch', len(expect) - len(main_paste), '= expected', len(expect),
          '| placed', len(got), '| misplaced', bad, '| unexpected', extra)
    bb = st.GetBoardEdgesBoundingBox()
    print('stencil pattern extent %.2f x %.2f mm' % (pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())))
    if bad or extra:
        raise SystemExit('position check failed')
    pcbnew.SaveBoard(out_path, st)


if __name__ == '__main__':
    build(*sys.argv[1:4])
