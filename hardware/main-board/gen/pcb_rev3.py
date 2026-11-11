"""Main board rev 3 - board builder (KiCad 9 pcbnew).

Reads the rev 3 netlist and the floor plan (rev3/floorplan.json), places every footprint, carries the amplifier
block's copper over from rev 2.1 (turned 90 degrees clockwise with the block), sets the rules, net classes and plane
areas. Routing is route_rev3.py.

Board frame as the site document: KiCad X = u + 43.5, Y = 28.95 - v, front copper = door side.
Run: python3 pcb_rev3.py <rev3 netlist> <floorplan.json> <rev 2.1 board> <out.kicad_pcb>
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('HA_PRETTY', os.path.join(HERE, '..', 'lib', 'ha_panel.pretty'))
import pcbnew                      # noqa: E402
import pcb_main as pm              # noqa: E402
import route_main as rm            # noqa: E402

MM, TO = pcbnew.FromMM, pcbnew.ToMM
U0, V0 = 43.5, 28.95
W, H = 2 * U0, 2 * V0


def X(u):
    return u + U0


def Y(v):
    return V0 - v


def K(pts):
    """(u, v) points -> KiCad (x, y)."""
    return [(X(u), Y(v)) for u, v in pts]


AMP = ['U100'] + ['L%d' % i for i in range(100, 104)] + ['C%d' % i for i in range(100, 124)] + ['R%d' % i for i in range(100, 106)]
U100_21 = (60.0, 25.5)             # rev 2.1 position of the amplifier chip (KiCad mm)
AMP_UV = (28.8, 9.4)               # rev 3 position (board frame)
R_BLOCK = (47.6, 10.6, 89.4, 40.4)     # rev 2.1 box of the block: copper of the supply and speaker nets is taken inside it
R_CHIP = (51.5, 16.5, 68.5, 34.5)      # rev 2.1 box round the chip: pin stubs and fan-out vias of the signal nets


def turn(x, y):
    """rev 2.1 KiCad point -> rev 3 KiCad point (block turned 90 degrees clockwise about the chip)."""
    dx, dy = x - U100_21[0], y - U100_21[1]
    return X(AMP_UV[0]) - dy, Y(AMP_UV[1]) + dx


# plane areas on layer 3 (In2), board frame (u, v)
P5 = K([(3.0, -9.6), (14.2, -9.6), (14.2, 20.5), (3.0, 20.5)])                       # +5V: module +Vout pins, C7, D2, F2
P20 = K([(-19.4, -21.5), (1.6, -21.5), (1.6, 8.0), (2.4, 8.0), (2.4, 20.8), (6.6, 20.8), (6.6, 28.4), (-21.2, 28.4),
         (-21.2, 8.0), (-19.4, 8.0)])                                              # +20V: U1 out, up the pin gap, C5, L1, F5
PPV_21 = [(62.8, 9.4), (89.4, 9.4), (89.4, 39.0), (66.0, 39.0), (66.0, 34.6), (47.2, 34.6), (47.2, 21.0), (59.5, 21.0),
          (59.5, 15.2), (62.8, 15.2)]                                              # rev 2.1 PVDD area, turned with the block
PPV = [turn(x, y) for x, y in PPV_21]
PPV_FEED = K([(9.6, 21.2), (26.0, 21.2), (26.0, 27.6), (9.6, 27.6)])                # F5 pad 2 to the block
FULL = [(-1.0, -1.0), (W + 1.0, -1.0), (W + 1.0, H + 1.0), (-1.0, H + 1.0)]


def inside_box(pt, box):
    return box[0] <= TO(pt.x) <= box[2] and box[1] <= TO(pt.y) <= box[3]


def carry_amp_copper(old, new):
    """Copy the amplifier block's tracks and vias from rev 2.1, turned with the block."""
    amp_nets = {}
    for ref in AMP:
        for p in old.FindFootprintByReference(ref).Pads():
            if p.GetNetname():
                amp_nets.setdefault(p.GetNetname(), set())
    for fp in old.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() in amp_nets:
                amp_nets[p.GetNetname()].add(fp.GetReference())
    internal = {n for n, refs in amp_nets.items() if refs <= set(AMP)}
    supply = {'GND', '/Amplifier/PVDD', '3V3_AMP', '/Amplifier/SPK_L_P', '/Amplifier/SPK_L_N', '/Amplifier/SPK_R_P',
              '/Amplifier/SPK_R_N'}
    conn = old.GetConnectivity()
    spk_box = {}                       # speaker nets: only the coil-to-capacitor piece (the run to the socket is new)
    for n in supply:
        if 'SPK_' not in n:
            continue
        bb = None
        for ref in AMP:
            for p in old.FindFootprintByReference(ref).Pads():
                if p.GetNetname() == n:
                    r = p.GetBoundingBox()
                    q = (TO(r.GetX()) - 0.3, TO(r.GetY()) - 0.3, TO(r.GetRight()) + 0.3, TO(r.GetBottom()) + 0.3)
                    bb = q if bb is None else (min(bb[0], q[0]), min(bb[1], q[1]), max(bb[2], q[2]), max(bb[3], q[3]))
        spk_box[n] = bb

    def box_of(n):
        return spk_box.get(n) or (R_BLOCK if n in supply else R_CHIP)

    def ok_item(t, box):
        if t.Type() == pcbnew.PCB_VIA_T:
            return inside_box(t.GetPosition(), box)
        return inside_box(t.GetStart(), box) and inside_box(t.GetEnd(), box)
    keep = {}
    tracks = list(old.GetTracks())
    by_id = {t.m_Uuid.AsString(): t for t in tracks}       # properly typed objects (vias as PCB_VIA)
    for t in tracks:
        if t.GetNetname() in internal:
            keep[t.m_Uuid.AsString()] = t
    # the other nets: walk outward from the block's pads, staying inside the box for that net
    frontier = []
    for t in tracks:
        n = t.GetNetname()
        if n in internal or n not in amp_nets:
            continue
        box = box_of(n)
        if not ok_item(t, box):
            continue
        if any(p.GetParentFootprint().GetReference() in AMP for p in conn.GetConnectedPads(t)):
            keep[t.m_Uuid.AsString()] = t
            frontier.append(t)
    while frontier:
        t = frontier.pop()
        box = box_of(t.GetNetname())
        for q in conn.GetConnectedTracks(t):
            k = q.m_Uuid.AsString()
            q = by_id.get(k, q)
            if k not in keep and ok_item(q, box):
                keep[k] = q
                frontier.append(q)
    n_t = n_v = 0
    for t in keep.values():
        net = new.FindNet(t.GetNetname())
        if net is None:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            v = pcbnew.PCB_VIA(new)
            x, y = turn(TO(t.GetPosition().x), TO(t.GetPosition().y))
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            v.SetWidth(pcbnew.F_Cu, t.GetWidth(pcbnew.F_Cu)); v.SetDrill(t.GetDrillValue())
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True)
            new.Add(v); n_v += 1
        else:
            s = pcbnew.PCB_TRACK(new)
            a = turn(TO(t.GetStart().x), TO(t.GetStart().y)); b = turn(TO(t.GetEnd().x), TO(t.GetEnd().y))
            s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            s.SetWidth(t.GetWidth()); s.SetLayer(t.GetLayer()); s.SetNet(net); s.SetLocked(True)
            new.Add(s); n_t += 1
    return n_t, n_v, sorted(n.split('/')[-1] for n in internal)


def prune_dangling(board, path, rounds=12, keep=()):
    """Remove carried-over track pieces that end in nothing (runs that left the block in rev 2.1). Vias stay: a pin
    stub ending in a via is a fan-out waiting for its route."""
    import subprocess
    total = 0
    for _ in range(rounds):
        tmp = path.replace('.kicad_pcb', '_prune.kicad_pcb')
        pcbnew.SaveBoard(tmp, board)
        subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', tmp + '.json', tmp], capture_output=True)
        d = json.load(open(tmp + '.json'))
        hits = [(it['pos']['x'], it['pos']['y']) for x in d['violations'] if x['type'] == 'track_dangling' for it in x['items'][:1]]
        n = 0
        for x, y in hits:
            P = pcbnew.VECTOR2I(MM(x), MM(y))
            for t in list(board.GetTracks()):
                if t.GetClass() == 'PCB_VIA' or t.GetNetname() in keep:
                    continue
                s, e = t.GetStart(), t.GetEnd()
                mid = pcbnew.VECTOR2I((s.x + e.x) // 2, (s.y + e.y) // 2)
                if min((s - P).EuclideanNorm(), (e - P).EuclideanNorm(), (mid - P).EuclideanNorm()) < MM(0.01):
                    board.Remove(t); n += 1
                    break
        total += n
        if not n:
            break
    for f in (tmp, tmp + '.json', tmp.replace('.kicad_pcb', '.kicad_pro'), tmp.replace('.kicad_pcb', '.kicad_prl')):
        if os.path.exists(f):
            os.remove(f)
    return total


def rules(board):
    """Rules and net classes as rev 2.1 (JLC 4-layer capabilities, hardware/notes/jlc-fab.md). They live in the
    .kicad_pro file, so every script that loads the board applies them again."""
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = MM(0.10); ds.m_MinClearance = MM(0.15); ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.2); ds.m_ViasMinAnnularWidth = MM(0.1); ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleToHoleMin = MM(0.25); ds.m_SolderMaskMinWidth = MM(0.1); ds.m_MinResolvedSpokes = 1
    ds.SetBoardThickness(MM(1.6))
    ns = ds.m_NetSettings
    ns.ClearNetclassPatternAssignments()
    ns.ClearNetclasses()
    for name, (tw, cl, vd, vdr, nets) in rm.CLASSES.items():
        nc = pcbnew.NETCLASS(name)
        nc.SetTrackWidth(MM(tw)); nc.SetClearance(MM(cl)); nc.SetViaDiameter(MM(vd)); nc.SetViaDrill(MM(vdr))
        ns.SetNetclass(name, nc)
        for n in nets:
            ns.SetNetclassPatternAssignment(n.replace('+', '\\+').replace('.', '\\.'), name)
    ns.RecomputeEffectiveNetclasses()


def keepout(board, x, y, r, layer, name):
    """Round area without tracks, vias or poured copper on one outer layer (KiCad mm)."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetLayer(layer)
    z.SetZoneName(name)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowCopperPour(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ol = z.Outline()
    ol.NewOutline()
    for k in range(48):
        ol.Append(MM(x + r * math.cos(2 * math.pi * k / 48)), MM(y + r * math.sin(2 * math.pi * k / 48)))
    board.Add(z)
    return z


def setup(board):
    """Rules, then the plane areas for rev 3."""
    # no outer copper under the screw heads (door side, 7 mm circle) or under the post faces (back, 8 mm + 0.1).
    # H2 is the exception on the back: the amplifier block's own tracks (carried over unchanged) reach 2.9 mm from its
    # centre, under the outer rim of the post face; the area there stops at 2.8 mm so that nothing new is added.
    for fp in board.GetFootprints():
        if fp.GetReference() in ('H1', 'H2', 'H3', 'H4'):
            c = fp.GetPosition()
            keepout(board, pcbnew.ToMM(c.x), pcbnew.ToMM(c.y), 3.3 if fp.GetReference() == 'H2' else 3.5, pcbnew.F_Cu,
                    fp.GetReference() + ' screw head')       # H2: two of the amplifier's own vias start 3.39 from its centre
            keepout(board, pcbnew.ToMM(c.x), pcbnew.ToMM(c.y), 2.8 if fp.GetReference() == 'H2' else 4.1, pcbnew.B_Cu,
                    fp.GetReference() + ' post face')
    rules(board)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    rm.zone(board, 'GND', pcbnew.In1_Cu, FULL, prio=0, thermal=False)
    rm.zone(board, '+5V', pcbnew.In2_Cu, P5, prio=1)
    rm.zone(board, '+20V', pcbnew.In2_Cu, P20, prio=1)
    rm.zone(board, '/Amplifier/PVDD', pcbnew.In2_Cu, PPV, prio=1)
    rm.zone(board, '/Amplifier/PVDD', pcbnew.In2_Cu, PPV_FEED, prio=2)


def build(netlist, plan_json, old_board, out):
    plan = json.load(open(plan_json))['parts']
    outline = [(0, 0), (W, 0), (W, H), (0, H)]
    board, placed, missing = pm.build(netlist, out, {}, layers=4, poly=outline)
    for fp in board.GetFootprints():
        p = plan[fp.GetReference()]
        fp.SetOrientationDegrees(p['rot'])
        fp.SetPosition(pcbnew.VECTOR2I(MM(X(p['u'])), MM(Y(p['v']))))
    pcbnew.SaveBoard(out, board)
    board = pcbnew.LoadBoard(out)          # reload: the zone filler otherwise works from the parts' parking positions
    old = pcbnew.LoadBoard(old_board)
    nt, nv, internal = carry_amp_copper(old, board)
    # the chip's control and audio pins keep their rev 2.1 way out from under the chip (stub, via, first run on the back):
    # the router starts from the end of each; whatever stays unused is removed after routing
    classed = {n for c in rm.CLASSES.values() for n in c[4]}
    keep = {p.GetNetname() for p in board.FindFootprintByReference('U100').Pads()} - classed - {'GND'}
    pruned = prune_dangling(board, out, keep=keep)
    setup(board)
    rm.efuse_bridges(board)
    rm.usb_links(board)
    tb = board.GetTitleBlock()
    tb.SetTitle('HA panel main board'); tb.SetRevision('3'); tb.SetDate('2026-11-11')
    tb.SetCompany('HA panel (neocleous/ha-panel)')
    tb.SetComment(0, 'Rev 3: laid out for the site behind the display (claude/main-board-site-2026-11-10.md issue 2)')
    tb.SetComment(1, '87.0 x 57.9 x 1.6, 4 layers: parts + signals / GND / +5V, +20V, PVDD / signals + GND')
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(out, board)
    print('footprints', len(board.GetFootprints()), '| amplifier copper carried over: tracks', nt, 'vias', nv,
          '| loose ends removed', pruned, '| nets wholly inside the block:', len(internal))
    return board


if __name__ == '__main__':
    build(*sys.argv[1:5])
