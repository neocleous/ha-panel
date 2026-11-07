"""Main board: net classes, plane zones (In1 GND, In2 +5V/+20V/PVDD), Specctra export, Freerouting, SES import,
outer GND pours. Run: python3 route_main.py <board> [passes]"""
import os
import subprocess
import sys
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_main as pm
import fanout as fo
import amp
import mroute
import silk

MM = pm.MM
JAVA = '/usr/lib/jvm/java-25-openjdk-amd64/bin/java'
FR = '/home/claude/tools/fr/fr_g.jar'      # Freerouting 2.5.0 executable (Maven Central mirror, SHA-1 checked)

CLASSES = {   # name: (track, clearance, via_d, via_drill, nets) - widths that still escape 0.5 mm-pitch pins
    'PWR5': (0.8, 0.15, 0.8, 0.4, ['+5V', '/5 V supply and outputs/5V_PI_F', '/5 V supply and outputs/VBUS_PI']),
    'PWR20': (0.8, 0.2, 0.8, 0.4, ['+20V', '/20 V inlet and eFuse/VIN_PIGTAIL', '/20 V inlet and eFuse/VIN_EF',
                                   '/5 V supply and outputs/NID_VIN']),
    'PV': (0.3, 0.15, 0.6, 0.3, ['/Amplifier/PVDD']),
    'SPK': (0.4, 0.15, 0.6, 0.3, ['/Amplifier/OUT_AP', '/Amplifier/OUT_AN', '/Amplifier/OUT_BP', '/Amplifier/OUT_BN',
                                  '/Amplifier/SPK_L_P', '/Amplifier/SPK_L_N', '/Amplifier/SPK_R_P', '/Amplifier/SPK_R_N']),
    'BST': (0.25, 0.15, 0.6, 0.3, ['/Amplifier/BST_AP', '/Amplifier/BST_AN', '/Amplifier/BST_BP', '/Amplifier/BST_BN']),
    'GNDC': (0.3, 0.15, 0.6, 0.3, ['GND']),
    'SUP': (0.25, 0.15, 0.6, 0.3, ['+3V3', '3V3_AMP', '5V_RADAR', '/3.3 V, Pi link, sensors, radar, echo-ref/3V3_SENS',
                                   '/3.3 V, Pi link, sensors, radar, echo-ref/LDO_IN', '/3.3 V, Pi link, sensors, radar, echo-ref/PI_3V3',
                                   '/Amplifier/GVDD', '/Amplifier/DVDD_REG', '/Amplifier/CPVSS', '/Amplifier/CP', '/Amplifier/CN']),
}
P5 = [(0.6, -4.4), (25.9, -4.4), (25.9, -31.4), (64.1, -31.4), (64.1, -4.4), (72.5, -4.4), (72.5, 8.8), (62.2, 8.8), (62.2, 14.6), (58.9, 14.6), (58.9, 20.4), (39.6, 20.4),
      (39.6, 27.6), (33.4, 27.6), (33.4, 14.6), (20.6, 14.6), (20.6, 40.0), (0.6, 40.0)]
P20 = [(21.2, 15.2), (32.8, 15.2), (32.8, 28.2), (44.3, 28.2), (44.3, 40.5), (34.0, 40.5), (34.0, 47.6), (25.0, 47.6),
       (25.0, 40.5), (21.2, 40.5)]
PPV = [(62.8, 9.4), (89.4, 9.4), (89.4, 39.0), (66.0, 39.0), (66.0, 34.6), (47.2, 34.6), (47.2, 21.0), (59.5, 21.0),
       (59.5, 15.2), (62.8, 15.2)]
FULL = [(-1.0, -33.0), (91.0, -33.0), (91.0, 51.0), (-1.0, 51.0)]   # clipped to the T outline by the filler


def zone(board, net, layer, pts, prio=0, thermal=False, clearance=0.3, minw=0.25):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(board.FindNet(net))
    ol = z.Outline()
    ol.NewOutline()
    for x, y in pts:
        ol.Append(MM(x), MM(y))
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(MM(clearance))
    z.SetMinThickness(MM(minw))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL if thermal else pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(MM(0.4))
    z.SetThermalReliefSpokeWidth(MM(0.6))
    board.Add(z)
    return z


def setup(board):
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = MM(0.15); ds.m_MinClearance = MM(0.15); ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.2); ds.m_ViasMinAnnularWidth = MM(0.1); ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleToHoleMin = MM(0.25); ds.m_SolderMaskMinWidth = MM(0.1); ds.m_MinResolvedSpokes = 1
    ns = board.GetDesignSettings().m_NetSettings
    ns.ClearNetclassPatternAssignments()
    ns.ClearNetclasses()
    for name, (tw, cl, vd, vdr, nets) in CLASSES.items():
        nc = pcbnew.NETCLASS(name)
        nc.SetTrackWidth(MM(tw)); nc.SetClearance(MM(cl)); nc.SetViaDiameter(MM(vd)); nc.SetViaDrill(MM(vdr))
        ns.SetNetclass(name, nc)
        for n in nets:
            ns.SetNetclassPatternAssignment(n.replace('+', '\\+').replace('.', '\\.'), name)
    ns.RecomputeEffectiveNetclasses()
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    zone(board, 'GND', pcbnew.In1_Cu, FULL, prio=0, thermal=False)
    zone(board, '+5V', pcbnew.In2_Cu, P5, prio=1)
    zone(board, '+20V', pcbnew.In2_Cu, P20, prio=1)
    zone(board, '/Amplifier/PVDD', pcbnew.In2_Cu, PPV, prio=1)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def outer_pours(board):
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = zone(board, 'GND', lay, FULL, prio=0, thermal=True, clearance=0.3)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def usb_links(board):
    """J2 USB4085: tie the VBUS pin pairs (A4-B9, A9-B4) on the back with short locked links."""
    j2 = board.FindFootprintByReference('J2')
    pos = {p.GetNumber(): p.GetPosition() for p in j2.Pads()}
    net = board.FindNet('/5 V supply and outputs/VBUS_PI')
    for a, c in (('A4', 'B9'), ('A9', 'B4')):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pos[a]); t.SetEnd(pos[c]); t.SetWidth(MM(0.4)); t.SetLayer(pcbnew.B_Cu); t.SetNet(net); t.SetLocked(True)
        board.Add(t)


def efuse_bridges(board):
    """U1 TPS16630: join IN pins 1-3 and OUT pins 18-20 across their pads, GND pins 9/12 to the exposed pad."""
    u = board.FindFootprintByReference('U1')
    pads = {p.GetNumber(): p for p in u.Pads() if p.GetNumber()}
    ep = max([p for p in u.Pads() if p.GetNumber() == '21' and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD],
             key=lambda p: p.GetBoundingBox().GetWidth() * p.GetBoundingBox().GetHeight())
    def trk(a, b, net, w):
        t = pcbnew.PCB_TRACK(board); t.SetStart(a); t.SetEnd(b); t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu)
        t.SetNet(net); t.SetLocked(True); board.Add(t)
    for chain in (('1', '2', '3'), ('18', '19', '20')):
        for a, b in zip(chain, chain[1:]):
            trk(pads[a].GetPosition(), pads[b].GetPosition(), pads[a].GetNet(), 0.4)
    c = ep.GetPosition()
    for n in ('9', '12'):
        p = pads[n].GetPosition()
        rows_horizontal = abs(pads['1'].GetPosition().y - pads['2'].GetPosition().y) < MM(0.1)
        trk(p, pcbnew.VECTOR2I(p.x, c.y) if rows_horizontal else pcbnew.VECTOR2I(c.x, p.y), pads[n].GetNet(), 0.3)


PREROUTES = [   # (net, from, to, width, layers, box[, forbid]); a point is (x, y) or (ref, pad)
    ('/Amplifier/OUT_AN', (67.3, 19.825), (74.0, 21.9), 0.6, ('F',), (65.5, 16.0, 77.0, 24.0)),
    ('/Amplifier/OUT_AP', (65.295, 19.35), (83.6, 21.9), 0.6, ('F',), (63.0, 13.0, 87.5, 24.0)),
    ('/Amplifier/OUT_BN', (67.3, 31.175), (74.0, 25.5), 0.6, ('F',), (65.5, 23.5, 77.0, 35.0)),
    ('/Amplifier/OUT_BP', (65.295, 31.65), (83.6, 25.5), 0.6, ('F',), (63.0, 23.5, 87.5, 38.0)),
    ('/20 V inlet and eFuse/VIN_EF', ('F1', '2'), (34.73, 41.26), 0.8, ('F', 'B'), (20.0, 30.0, 60.0, 50.0),
     [('F', 35.7, 41.0, 41.5, 44.0)]),     # keep the front escape below U1 pins 4-10 free
    ('/20 V inlet and eFuse/VIN_EF', (37.32, 41.26), ('C2', '1'), 0.3, ('F', 'B'), (30.0, 36.0, 46.0, 50.0)),
]


def _pt(b, p):
    if isinstance(p[0], str):
        fp = b.FindFootprintByReference(p[0])
        q = [x for x in fp.Pads() if x.GetNumber() == p[1]][0].GetPosition()
        return (q.x * 1e-6, q.y * 1e-6)
    return p


def preroute(b):
    for pr in PREROUTES:
        net, a, c, w, lays, box = pr[:6]
        a, c = _pt(b, a), _pt(b, c)
        forbid = pr[6] if len(pr) > 6 else ()
        via = (0.8, 0.4) if w >= 0.8 else (0.6, 0.3)
        ok, info = mroute.route(b, net, a, c, w, CLASSES, via=via, layers=lays, box=box, forbid=forbid)
        print('preroute', net.split('/')[-1], ok, info)


N3 = '/3.3 V, Pi link, sensors, radar, echo-ref/'
NEF = '/20 V inlet and eFuse/'
POSTROUTES = [   # filled from the single-sided run's leftovers
]


def postroute(b, items=None):
    for it in (items if items is not None else POSTROUTES):
        kind, net = it[0], it[1]
        if kind == 'x':
            ok, info = True, 'removed %d' % mroute.remove_segments(b, net, it[2])
        elif kind == 'xv':
            ok, info = True, 'removed %d' % mroute.rip_at(b, it[2][0], it[2][1], net, chain=False)
        elif kind == 'm':
            fp = b.FindFootprintByReference(net)
            fp.SetOrientationDegrees(it[3]); fp.SetPosition(pcbnew.VECTOR2I(MM(it[2][0]), MM(it[2][1])))
            ok, info = True, 'moved'
        elif kind == 'r':
            a, c, w, lays, box = it[2:7]
            ok, info = mroute.route(b, net, a, c, w, CLASSES, layers=lays, box=box)
        elif kind == 't':
            a, c, w, lays = it[2:6]
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            t.SetWidth(MM(w)); t.SetLayer(mroute.LAYERS[lays[0]]); t.SetNet(b.FindNet(net)); t.SetLocked(True)
            b.Add(t)
            ok, info = True, 'link'
        else:
            ok, info = mroute.drop_via(b, net, it[2], CLASSES, w=it[4], layer=it[5][0])
        print('postroute', kind, net.split('/')[-1], ok, info)


def autoroute(board_path, passes=40):
    b = pcbnew.LoadBoard(board_path)
    for t in list(b.GetTracks()):
        b.Remove(t)
    for z in list(b.Zones()):
        if not z.GetIsRuleArea():
            b.Remove(z)
    setup(b)
    usb_links(b)
    efuse_bridges(b)
    print('tas stage vias', len(amp.stage(b)))
    preroute(b)
    added, failed = fo.fanout(b, {'+5V': P5, '+20V': P20, '/Amplifier/PVDD': PPV})
    print('fanout vias', added, 'failed', failed)
    pcbnew.SaveBoard(board_path, b)
    dsn = board_path.replace('.kicad_pcb', '.dsn')
    ses = board_path.replace('.kicad_pcb', '.ses')
    pcbnew.ExportSpecctraDSN(b, dsn)
    cmd = [JAVA, '-jar', FR, '-de', dsn, '-do', ses, '-mp', str(passes)]
    if os.environ.get('FR_MT'):
        cmd += ['-mt', os.environ['FR_MT']]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3000)
    log = [l for l in (r.stdout + r.stderr).splitlines() if 'INFO' in l or 'WARN' in l or 'ERROR' in l]
    b = pcbnew.LoadBoard(board_path)
    ok = pcbnew.ImportSpecctraSES(b, ses)
    pcbnew.SaveBoard(board_path.replace('.kicad_pcb', '_fr.kicad_pcb'), b)
    finish(b)
    pcbnew.SaveBoard(board_path, b)
    return ok, log


def finish(b):
    """After Freerouting: maze-routed leftovers, neck widening, outer GND pours, stitching vias, final fill."""
    b.GetDesignSettings().m_TrackMinWidth = MM(0.12)   # Freerouting necks that cannot widen (JLC: 0.10/0.10)
    postroute(b)
    print('widened', widen_necks(b))
    outer_pours(b)
    for _ in range(2):                         # stitch every GND pour island that has no via to In1
        print('stitch vias', len(mroute.stitch(b, CLASSES)))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    print('dangling removed', clean_dangling(b))
    trim_silk_past_edge(b)
    shown, hidden = silk.place(b)
    print('silk refs shown', shown, 'hidden', len(hidden), hidden)


def trim_silk_past_edge(b, H=50.0):
    """J2 (USB4085, flush with the door edge) draws its receptacle outline past the board edge: drop those lines."""
    fp = b.FindFootprintByReference('J2')
    for g in list(fp.GraphicalItems()):
        if g.GetLayer() in (pcbnew.B_SilkS, pcbnew.F_SilkS) and g.GetClass() == 'PCB_SHAPE':
            if max(g.GetStart().y, g.GetEnd().y) > MM(H - 0.5):
                fp.Remove(g); mroute.GRAVE.append(g)


def clean_dangling(b, rounds=5):
    """Remove vias / track segments that KiCad's DRC reports as dangling (leftovers of rerouting), refill, repeat."""
    import json
    import tempfile
    total = 0
    for _ in range(rounds):
        tmp = tempfile.mkdtemp() + '/t.kicad_pcb'
        pcbnew.SaveBoard(tmp, b)
        subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json', '-o', tmp + '.json', tmp], capture_output=True)
        d = json.load(open(tmp + '.json'))
        hits = [(x['type'], it['pos']['x'], it['pos']['y'], it['description']) for x in d['violations']
                if x['type'] in ('via_dangling', 'track_dangling') for it in x['items'][:1]]
        if not hits:
            break
        n = 0
        for typ, x, y, desc in hits:
            P = pcbnew.VECTOR2I(MM(x), MM(y))
            for t in list(b.GetTracks()):
                if typ == 'via_dangling' and t.GetClass() == 'PCB_VIA' and (t.GetPosition() - P).EuclideanNorm() < MM(0.01):
                    mroute.remove(b, t); n += 1; break
                if typ == 'track_dangling' and t.GetClass() != 'PCB_VIA':
                    s, e = t.GetStart(), t.GetEnd()
                    mid = pcbnew.VECTOR2I((s.x + e.x) // 2, (s.y + e.y) // 2)
                    if min((s - P).EuclideanNorm(), (e - P).EuclideanNorm(), (mid - P).EuclideanNorm()) < MM(0.01):
                        mroute.remove(b, t); n += 1; break
        total += n
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        if not n:
            break
    return total


def widen_necks(b, wmin=0.15):
    """Freerouting necks tracks down at pads (0.10-0.125); widen to wmin (or the widest legal step) where the
    rasterised clearance check passes along the whole segment."""
    import numpy as np
    n, kept = 0, []
    for t in list(b.GetTracks()):
        if t.GetClass() == 'PCB_VIA' or t.GetWidth() >= MM(wmin):
            continue
        s, e = t.GetStart(), t.GetEnd()
        x0, y0 = min(s.x, e.x) * 1e-6 - 1.0, min(s.y, e.y) * 1e-6 - 1.0
        x1, y1 = max(s.x, e.x) * 1e-6 + 1.0, max(s.y, e.y) * 1e-6 + 1.0
        bx0, by0, bx1, by1 = mroute.board_box(b)
        reg = mroute.Region(max(bx0, x0), max(by0, y0), min(bx1, x1), min(by1, y1))
        dist, edist, same = mroute.build(b, reg, t.GetNetname(), CLASSES)
        ln = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
        done = False
        for w in (wmin, 0.14, 0.13):
            if w * 1e6 <= t.GetWidth():
                break
            ok = mroute.allowed(dist, edist, ln, w, mroute.net_clearance(t.GetNetname(), CLASSES), margin=0.07)
            good = True
            for k in range(21):
                px = (s.x + (e.x - s.x) * k / 20) * 1e-6; py = (s.y + (e.y - s.y) * k / 20) * 1e-6
                i, j = [int(v) for v in reg.px(px, py)]
                if not ok[j, i]:
                    good = False; break
            if good:
                t.SetWidth(MM(w)); n += 1; done = True
                break
        if not done or t.GetWidth() < MM(wmin):
            kept.append('%s %.3f' % (t.GetNetname().split('/')[-1], t.GetWidth() * 1e-6))
    if kept:
        print('narrow tracks kept:', kept)
    return n


if __name__ == '__main__':
    if sys.argv[2:3] == ['--post']:            # re-run only the post-Freerouting steps from <board>_fr.kicad_pcb
        b = pcbnew.LoadBoard(sys.argv[1].replace('.kicad_pcb', '_fr.kicad_pcb'))
        finish(b)
        pcbnew.SaveBoard(sys.argv[1], b)
        sys.exit(0)
    ok, log = autoroute(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    print('import', ok)
    for l in log[-12:]:
        print(l[:220])
