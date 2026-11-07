"""Reference-designator placement on the silkscreen: try positions round each footprint, keep the first one clear of
exposed copper (pads), other silk and the board edge; hide the reference where nothing fits (the assembly drawing
on the fab layers still carries every reference). Mounting holes and logos never get a silk reference."""
import pcbnew

T = 1e-6
MM = pcbnew.FromMM
EDGE = 0.5
PAD_GAP = 0.15
SILK_GAP = 0.1


def _box(bb, g=0.0):
    return (bb.GetX() * T - g, bb.GetY() * T - g, bb.GetRight() * T + g, bb.GetBottom() * T + g)


def _hit(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def place(board, W=90.0, H=50.0, skip_prefix=('H', 'LOGO')):
    obst = {pcbnew.F_SilkS: [], pcbnew.B_SilkS: []}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            for silk, cu in ((pcbnew.F_SilkS, pcbnew.F_Cu), (pcbnew.B_SilkS, pcbnew.B_Cu)):
                if p.IsOnLayer(cu):
                    obst[silk].append(_box(p.GetBoundingBox(), PAD_GAP))
        for g in fp.GraphicalItems():
            if g.GetLayer() in obst and g.GetClass() != 'PCB_FIELD' and g.GetClass() != 'PCB_TEXT':
                obst[g.GetLayer()].append(_box(g.GetBoundingBox(), SILK_GAP))
    for d in board.GetDrawings():
        if d.GetLayer() in obst:
            obst[d.GetLayer()].append(_box(d.GetBoundingBox(), SILK_GAP))
    shown, hidden = 0, []
    fps = sorted(board.GetFootprints(), key=lambda f: -_area(f))
    for fp in fps:
        ref = fp.Reference()
        if fp.GetReference().startswith(skip_prefix):
            ref.SetVisible(False)
            continue
        lay = ref.GetLayer()
        if lay not in obst:
            continue
        side = pcbnew.B_CrtYd if fp.GetLayer() == pcbnew.B_Cu else pcbnew.F_CrtYd
        cy = fp.GetCourtyard(side)
        cb = _box(cy.BBox()) if cy.OutlineCount() else _box(fp.GetBoundingBox(False))
        cx, cyy = (cb[0] + cb[2]) / 2, (cb[1] + cb[3]) / 2
        ref.SetVisible(True)
        done = False
        for ang in (0, 90):
            ref.SetTextAngleDegrees(ang)
            tb = _box(ref.GetBoundingBox())
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            cands = [(cx, cb[1] - th / 2 - 0.15), (cx, cb[3] + th / 2 + 0.15), (cb[0] - tw / 2 - 0.15, cyy),
                     (cb[2] + tw / 2 + 0.15, cyy), (cx, cyy)]
            for dx in (-1.0, 1.0, -2.0, 2.0):
                cands += [(cx + dx, cb[1] - th / 2 - 0.15), (cx + dx, cb[3] + th / 2 + 0.15)]
            for (x, y) in cands:
                ref.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
                tb = _box(ref.GetBoundingBox())
                if tb[0] < EDGE or tb[1] < EDGE or tb[2] > W - EDGE or tb[3] > H - EDGE:
                    continue
                if any(_hit(tb, o) for o in obst[lay]):
                    continue
                obst[lay].append(_box(ref.GetBoundingBox(), SILK_GAP))
                done = True
                break
            if done:
                break
        if done:
            shown += 1
        else:
            ref.SetVisible(False)
            hidden.append(fp.GetReference())
    return shown, hidden


def _area(fp):
    bb = fp.GetBoundingBox(False)
    return bb.GetWidth() * bb.GetHeight()


def trim_edge(board, W, H, margin=0.25, keep=None):
    """Remove footprint silkscreen graphics that come within `margin` of the board edge (pin-1 marks on tiny boards)."""
    n = 0
    for fp in board.GetFootprints():
        for g in list(fp.GraphicalItems()):
            if g.GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS) or g.GetClass() in ('PCB_FIELD', 'PCB_TEXT'):
                continue
            b = _box(g.GetBoundingBox())
            if b[0] < margin or b[1] < margin or b[2] > W - margin or b[3] > H - margin:
                fp.Remove(g)
                if keep is not None:
                    keep.append(g)
                n += 1
    return n
