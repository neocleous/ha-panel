"""Main board rev 3.2: a relief in the side edge on the left-speaker side (claude/brief-electronics-rev3-2-2026-11-13.md,
amended 2026-11-14), applied to rev 3.1. Nothing else is asked of the board; only what stands in the relief's way moves.

    python3 rev32.py <rev 3.1 board.kicad_pcb> <board out.kicad_pcb> [text]        (KiCad 9's Python; PYTHONHASHSEED=0)

Board frame of the site document: u = X - 43.5, v = 28.95 - Y (KiCad mm), seen from the door; the edge is at u +43.5.

What it does:
  1. relief  the +u edge line is replaced by: edge down to v +14.0, a side wall in to u +43.0, an arc of radius R
             (centre u +43.0, v +13.0) to the relief's floor at u +42.0, the floor down to v +1.5, an arc of radius R
             (centre u +43.0, v +1.5) to the lower side wall at v +0.5, and back out to u +43.5. The full depth (1.5)
             holds over v +1.5 ... +13.0; the two rounded inner corners lie outside that span.
  2. gpio2   the amplifier's GPIO2 via (strap to R105) moves from u +41.59, v +4.59 to u +40.50, v +4.75, beside its
             pad; its door-side stub and the first piece of its back-face track follow.
  3. i2c     the I2C pair's loop round that via on the back face, which reached u +43.07, is laid again inside
             u +41.62 (clock) and u +41.25 (data); the rest of both lines is kept.
  4. pours   all pours refilled (a refill of unchanged rev 3.1 gives its pours to 0.000 mm2).
  text (optional) revision text on the back and in the title block.
"""
import math
import os
import shutil
import sys

GEN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GEN)
import pcbnew                      # noqa: E402
import pcb_rev3 as pb              # noqa: E402

MM, TO = pcbnew.FromMM, pcbnew.ToMM
U0, V0 = 43.5, 28.95

DEPTH = 1.5                        # relief depth (brief: 1.5 if the copper allows, 1.0 at least)
R = 1.0                            # radius drawn at the two inner corners (covers a 2.0 mm cutter; JLC: 1.0 mm tool)
V1, V2 = 1.5, 13.0                 # span over which the full depth holds
EDGE_U = 43.5

GPIO2_OLD = (41.585, 4.589)
GPIO2_NEW = (40.50, 4.75)
SCL_X = None                       # set from the board: the u of the kept joint at v +1.02
SDA_X = 41.15                      # centre of the data line's new straight run


def P(u, v):
    return pcbnew.VECTOR2I(MM(u + U0), MM(V0 - v))


def uv(p):
    return (TO(p.x) - U0, V0 - TO(p.y))


def near(a, b, tol=0.012):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def line(b, a, c, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetWidth(MM(w))
    s.SetStart(P(*a))
    s.SetEnd(P(*c))
    b.Add(s)
    return s


def arc(b, a, mid, c, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetLayer(layer)
    s.SetWidth(MM(w))
    s.SetArcGeometry(P(*a), P(*mid), P(*c))
    b.Add(s)
    return s


def track(b, a, c, layer, net, w):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(P(*a))
    t.SetEnd(P(*c))
    t.SetLayer(layer)
    t.SetWidth(MM(w))
    t.SetNet(b.FindNet(net))
    b.Add(t)
    return t


def stage_relief(b):
    edge = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT
            and abs(TO(d.GetStart().x) - 87.0) < 1e-6 and abs(TO(d.GetEnd().x) - 87.0) < 1e-6]
    assert len(edge) == 1, 'the +u edge line not found once'
    b.Remove(edge[0])
    uf = EDGE_U - DEPTH                       # floor of the relief
    lo, hi = V1 - R, V2 + R                   # side walls
    k = R / math.sqrt(2)
    line(b, (EDGE_U, V0), (EDGE_U, hi))                                   # edge above (Y 0 ... 14.95)
    line(b, (EDGE_U, hi), (uf + R, hi))                                   # upper side wall
    arc(b, (uf + R, hi), (uf + R - k, V2 + k), (uf, V2))                  # inner corner, centre (uf + R, V2)
    line(b, (uf, V2), (uf, V1))                                           # floor, full depth over V1 ... V2
    arc(b, (uf, V1), (uf + R - k, V1 - k), (uf + R, lo))                  # inner corner, centre (uf + R, V1)
    line(b, (uf + R, lo), (EDGE_U, lo))                                   # lower side wall
    line(b, (EDGE_U, lo), (EDGE_U, -V0))                                  # edge below (Y 28.45 ... 57.9)
    print('relief: floor u %+.2f from v %+.2f to %+.2f; side walls at v %+.2f and %+.2f; inner corners r %.2f, centres '
          '(%+.2f, %+.2f) and (%+.2f, %+.2f)' % (uf, V1, V2, lo, hi, R, uf + R, V2, uf + R, V1))


def stage_gpio2(b):
    net = '/Amplifier/AMP_GPIO2'
    via = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net and near(uv(t.GetPosition()), GPIO2_OLD)]
    assert len(via) == 1
    via[0].SetPosition(P(*GPIO2_NEW))
    pad = b.FindFootprintByReference('R105').FindPadByNumber('1')
    pc = uv(pad.GetPosition())
    removed = []
    for t in list(b.GetTracks()):
        if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != net:
            continue
        s, e = uv(t.GetStart()), uv(t.GetEnd())
        if near(s, GPIO2_OLD) or near(e, GPIO2_OLD):
            removed.append((b.GetLayerName(t.GetLayer()), s, e, TO(t.GetWidth())))
            other = e if near(s, GPIO2_OLD) else s
            lay, w = t.GetLayer(), TO(t.GetWidth())
            b.Remove(t)
            if lay == pcbnew.F_Cu:            # pad centre straight up, then 45 degrees to the via
                bend = (pc[0], GPIO2_NEW[1] - (pc[0] - GPIO2_NEW[0]))
                track(b, pc, bend, lay, net, w)
                track(b, bend, GPIO2_NEW, lay, net, w)
            else:                             # 45 degrees down from the via onto the old track's line, then along it
                bend = (GPIO2_NEW[0] - (GPIO2_NEW[1] - other[1]), other[1])
                track(b, GPIO2_NEW, bend, lay, net, w)
                track(b, bend, other, lay, net, w)
    print('GPIO2 via: (%+.3f, %+.3f) -> (%+.3f, %+.3f); tracks replaced: %s' % (GPIO2_OLD + GPIO2_NEW + (removed,)))


def stage_i2c(b):
    lim = EDGE_U - DEPTH - 0.3                # copper must stay inside this u over the relief's span
    # clock: keep the run up to the joint at about (41.52, 1.02) and from the joint at about (41.47, 6.12) on
    scl = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == 'I2C_SCL' and t.GetLayer() == pcbnew.B_Cu]
    pts = [uv(t.GetStart()) for t in scl] + [uv(t.GetEnd()) for t in scl]
    a = [p for p in pts if near(p, (41.52, 1.02), 0.02)][0]
    c = [p for p in pts if near(p, (41.47, 6.12), 0.02)][0]
    gone = []
    for t in scl:
        s, e = uv(t.GetStart()), uv(t.GetEnd())
        hw = TO(t.GetWidth()) / 2
        if max(s[0], e[0]) + hw > lim + 1e-6 and min(s[1], e[1]) > 0.9 and max(s[1], e[1]) < 6.5:
            gone.append((s, e))
            b.Remove(t)
    top = (a[0], c[1] - (a[0] - c[0]))        # straight up, then 45 degrees onto the kept joint
    track(b, a, top, pcbnew.B_Cu, 'I2C_SCL', 0.2)
    track(b, top, c, pcbnew.B_Cu, 'I2C_SCL', 0.2)
    print('I2C clock: %d pieces taken out (u up to %+.2f), laid again: (%+.3f, %+.3f) -> (%+.3f, %+.3f) -> (%+.3f, %+.3f)'
          % (len(gone), max(max(s[0], e[0]) for s, e in gone), *a, *top, *c))
    # data: the long run from the lower left is shortened to end at u = SDA_X; straight up to the old return run's line;
    # that run kept from there on
    sda = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == 'I2C_SDA' and t.GetLayer() == pcbnew.B_Cu]
    long_run = [t for t in sda if near(uv(t.GetEnd()), (41.88, 3.47), 0.02) or near(uv(t.GetStart()), (41.88, 3.47), 0.02)]
    turn = [t for t in sda if (near(uv(t.GetStart()), (41.88, 3.47), 0.02) and near(uv(t.GetEnd()), (42.53, 5.12), 0.02)) or
            (near(uv(t.GetEnd()), (41.88, 3.47), 0.02) and near(uv(t.GetStart()), (42.53, 5.12), 0.02))]
    back = [t for t in sda if near(uv(t.GetStart()), (42.53, 5.12), 0.02) or near(uv(t.GetEnd()), (42.53, 5.12), 0.02)]
    back = [t for t in back if t not in turn]
    long_run = [t for t in long_run if t not in turn]
    assert len(long_run) == 1 and len(turn) == 1 and len(back) == 1, (len(long_run), len(turn), len(back))
    lr = long_run[0]
    s, e = uv(lr.GetStart()), uv(lr.GetEnd())
    far, corner = (s, e) if near(e, (41.88, 3.47), 0.02) else (e, s)
    f = (SDA_X - far[0]) / (corner[0] - far[0])
    p1 = (SDA_X, far[1] + f * (corner[1] - far[1]))
    bs, be = uv(back[0].GetStart()), uv(back[0].GetEnd())
    hi_end, lo_end = (bs, be) if near(bs, (42.53, 5.12), 0.02) else (be, bs)
    g = (SDA_X - hi_end[0]) / (lo_end[0] - hi_end[0])
    p2 = (SDA_X, hi_end[1] + g * (lo_end[1] - hi_end[1]))
    if near(uv(lr.GetStart()), far):
        lr.SetEnd(P(*p1))
    else:
        lr.SetStart(P(*p1))
    b.Remove(turn[0])
    if near(bs, hi_end):
        back[0].SetStart(P(*p2))
    else:
        back[0].SetEnd(P(*p2))
    track(b, p1, p2, pcbnew.B_Cu, 'I2C_SDA', 0.2)
    print('I2C data: run from the lower left now ends at (%+.3f, %+.3f) (was %+.3f, %+.3f); new straight run to (%+.3f, %+.3f); '
          'the return run starts there (was %+.3f, %+.3f); the turn (%+.3f, %+.3f) -> (%+.3f, %+.3f) taken out'
          % (*p1, *corner, *p2, *hi_end, *corner, *hi_end))


def stage_text(b):
    tb = b.GetTitleBlock()
    tb.SetRevision('3.2')
    tb.SetDate('2026-11-14')
    tb.SetComment(0, 'Rev 3.2: relief in the +u side edge, v +1.5 to +13.0, 1.5 deep; amplifier GPIO2 via and the I2C pair '
                     'moved for it (claude/brief-electronics-rev3-2-2026-11-13.md)')
    tb.SetComment(1, '87.0 x 57.9 x 1.6 with a relief 1.5 deep in the +u side edge, 4 layers: parts + signals / GND / '
                     '+5V, +20V, PVDD / signals + GND')
    n = 0
    for d in b.GetDrawings():
        if d.GetClass() == 'PCB_TEXT' and d.GetText().startswith('REV 3.1 '):
            d.SetText('REV 3.2 2026-11-14')
            n += 1
    print('revision texts changed: %d' % n)


def main(src, dst, stages):
    if src != dst:
        shutil.copy(src, dst)
        pro = src.replace('.kicad_pcb', '.kicad_pro')
        if os.path.exists(pro):
            shutil.copy(pro, dst.replace('.kicad_pcb', '.kicad_pro'))
    b = pcbnew.LoadBoard(dst)
    pb.rules(b)
    for st in stages:
        {'relief': stage_relief, 'gpio2': stage_gpio2, 'i2c': stage_i2c, 'text': stage_text}[st](b)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    st = ['relief', 'gpio2', 'i2c'] + (['text'] if len(sys.argv) > 3 and sys.argv[3] == 'text' else [])
    main(sys.argv[1], sys.argv[2], st)
