"""One 100 x 100 JLC stencil for the touch board's back paste and the mic strip's back paste (chosen 2026-11-21).

Builds a stencil-only KiCad file from the two boards:
- the touch board's footprints flipped left-right onto the front: its back paste as seen from the back, which is how the
  stencil meets the touch board lying front-down; its outline flipped with it, in place (as stencil_single.py touch);
- the mic strip's footprints flipped the same way: its parts are on its back too, and it lies front-down (gasket side
  down) in a jig; placed GAP mm below the touch board and centred under it; references prefixed "S-";
- both outlines on Edge.Cuts; no tracks, vias, zones or board graphics, so the file cannot pass for a PCB.
Only F.Paste and Edge.Cuts are exported from it (stencil_export.sh).

    python3 stencil_touch_strip.py <touch-board.kicad_pcb> <mic-strip.kicad_pcb> <out.kicad_pcb>

Prints a position check: every paste pad must land at its mirrored (and, for the strip, moved) place within 1 nm; and
the extent of the two outlines, which must fit the stencil with room to spare."""
import sys

import pcbnew

GAP = 10.0  # mm between the touch board's bottom edge and the strip's top edge, as on the combined stencil of 2026-11-09


def _edges(board):
    """The outline's extent along its line centres: each shape's own box (arcs included) less half its line width,
    which KiCad's box adds."""
    xs, ys = [], []
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        bb, h = d.GetBoundingBox(), d.GetWidth() // 2
        xs += [bb.GetLeft() + h, bb.GetRight() - h]
        ys += [bb.GetTop() + h, bb.GetBottom() - h]
    return min(xs), min(ys), max(xs), max(ys)


def _check_source(b):
    ds = b.GetDesignSettings()
    if ds.m_SolderPasteMargin != 0 or ds.m_SolderPasteMarginRatio != 0:
        raise SystemExit('board-level paste margin is not 0; copy it into the stencil board first')
    if any(d.GetLayer() in (pcbnew.F_Paste, pcbnew.B_Paste) for d in b.GetDrawings()):
        raise SystemExit('board graphics on a paste layer; copy them too')
    if any(p.GetLayerSet().Contains(pcbnew.F_Paste) for fp in b.GetFootprints() for p in fp.Pads()):
        raise SystemExit('front paste on a board whose paste should all be on the back')


def _copy(src, dst, centre, off, prefix):
    for fp in src.GetFootprints():
        n = pcbnew.FOOTPRINT(fp)
        dst.Add(n)
        n.Flip(centre, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        n.Move(off)
        n.SetReference(prefix + fp.GetReference())
        for p in n.Pads():
            p.SetNetCode(0)
    for d in src.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts:
            n = d.Duplicate()
            dst.Add(n)
            n.Flip(centre, pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            n.Move(off)


def _expect(src, centre, off, prefix):
    out = {}
    for fp in src.GetFootprints():
        for i, p in enumerate(fp.Pads()):
            if p.GetLayerSet().Contains(pcbnew.B_Paste):
                pos = p.GetPosition()
                out[(prefix + fp.GetReference(), p.GetNumber(), i)] = (2 * centre.x - pos.x + off.x, pos.y + off.y)
    return out


def build(touch_path, strip_path, out_path):
    touch, strip = pcbnew.LoadBoard(touch_path), pcbnew.LoadBoard(strip_path)
    for b in (touch, strip):
        _check_source(b)
    # A fresh board, so nothing but footprints and outlines comes across.
    st = pcbnew.BOARD()
    sds = st.GetDesignSettings()
    if sds.m_SolderPasteMargin != 0 or sds.m_SolderPasteMarginRatio != 0:
        raise SystemExit('new board paste margin is not 0')

    tx0, ty0, tx1, ty1 = _edges(touch)
    sx0, sy0, sx1, sy1 = _edges(strip)
    tc = pcbnew.VECTOR2I((tx0 + tx1) // 2, (ty0 + ty1) // 2)
    sc = pcbnew.VECTOR2I((sx0 + sx1) // 2, (sy0 + sy1) // 2)
    t_off = pcbnew.VECTOR2I(0, 0)
    # A left-right flip about the centre keeps the extent, so the strip's move can be worked out before flipping:
    # centred under the touch board, its top edge GAP below the touch board's bottom edge.
    s_off = pcbnew.VECTOR2I(tc.x - sc.x, ty1 + pcbnew.FromMM(GAP) - sy0)

    expect = _expect(touch, tc, t_off, '')
    n_touch = len(expect)
    expect.update(_expect(strip, sc, s_off, 'S-'))
    _copy(touch, st, tc, t_off, '')
    _copy(strip, st, sc, s_off, 'S-')

    got = {}
    for fp in st.GetFootprints():
        for i, p in enumerate(fp.Pads()):
            if p.GetLayerSet().Contains(pcbnew.F_Paste):
                got[(fp.GetReference(), p.GetNumber(), i)] = (p.GetPosition().x, p.GetPosition().y)
            if p.GetLayerSet().Contains(pcbnew.B_Paste):
                raise SystemExit('B.Paste pad left on ' + fp.GetReference())
    bad = [k for k in expect if k not in got or max(abs(expect[k][0] - got[k][0]), abs(expect[k][1] - got[k][1])) > 1]
    extra = [k for k in got if k not in expect]
    x0, y0, x1, y1 = _edges(st)
    print('F.Paste pads: touch %d + strip %d = expected %d | placed %d | misplaced %s | unexpected %s' % (
        n_touch, len(expect) - n_touch, len(expect), len(got), bad, extra))
    print('touch outline %.2f x %.2f, strip outline %.2f x %.2f at (%.2f, %.2f) to (%.2f, %.2f); extent of both %.2f x %.2f mm' % (
        pcbnew.ToMM(tx1 - tx0), pcbnew.ToMM(ty1 - ty0), pcbnew.ToMM(sx1 - sx0), pcbnew.ToMM(sy1 - sy0),
        pcbnew.ToMM(sx0 + s_off.x), pcbnew.ToMM(sy0 + s_off.y), pcbnew.ToMM(sx1 + s_off.x), pcbnew.ToMM(sy1 + s_off.y),
        pcbnew.ToMM(x1 - x0), pcbnew.ToMM(y1 - y0)))
    if bad or extra:
        raise SystemExit('position check failed')
    pcbnew.SaveBoard(out_path, st)


if __name__ == '__main__':
    build(*sys.argv[1:4])
