"""Main board rev 3 - floor plan for the site behind the display (brief step 2, block 1; nothing is routed).

Builds a plan board (footprints only) in the site's board frame and writes
  plan/main-board-rev3-plan.kicad_pcb   footprints at their planned places, outline, no copper
  floorplan.json                        every part: u, v, rotation, courtyard, heights, pad positions
Big parts and connectors are placed by hand (FIXED). The amplifier block is rev 2.1's block turned 90 degrees
clockwise as one piece. Small parts are dropped next to the pin they serve by a spiral search; they are provisional
and move in block 2.

Run: python3 floorplan.py <netlist> <out dir>      (KiCad 9 pcbnew; block 1 used rev 2.1's netlist, block 2 on uses rev 3's:
     kicad-cli sch export netlist --format kicadsexpr -o rev3.net ../main-board.kicad_sch)
"""
import json
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'gen'))
import sitedata as S              # noqa: E402
from sexpr import parse              # noqa: E402

KLIB = '/usr/share/kicad/footprints/'
MINE = os.path.join(HERE, '..', 'lib', 'ha_panel.pretty')
MM, TOMM = pcbnew.FromMM, pcbnew.ToMM
GAP = 0.25                           # courtyard to courtyard for the small parts
EDGE = 0.4                           # courtyard to board edge for the small parts


def X(u):
    return u + S.U0


def Y(v):
    return S.V0 - v


def UV(x, y):
    return x - S.U0, S.V0 - y


# ---------------------------------------------------------------- parts ----
def sub(l, key):
    return [e for e in l if isinstance(e, list) and e and str(e[0]) == key]


def read_netlist(path):
    x = parse(open(path).read())[0]
    comps = {}
    for c in sub(sub(x, 'components')[0], 'comp'):
        ref = str(sub(c, 'ref')[0][1])
        comps[ref] = {'value': str(sub(c, 'value')[0][1]), 'footprint': str(sub(c, 'footprint')[0][1])}
    nets = {}
    for n in sub(sub(x, 'nets')[0], 'net'):
        name = str(sub(n, 'name')[0][1])
        nets[name] = [(str(sub(nd, 'ref')[0][1]), str(sub(nd, 'pin')[0][1])) for nd in sub(n, 'node')]
    return comps, nets


HDR4 = 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'
HOLE = 'MountingHole:MountingHole_3.2mm_M3'


def rev3_parts(comps, nets):
    """Rev 2.1 parts with the changes this site needs (change list, block 0)."""
    comps = dict(comps)
    if 'J11' in comps:                 # already the rev 3 netlist (block 2 on): nothing to change
        return comps, nets
    for h in ('H1', 'H2', 'H3', 'H4'):
        comps[h] = {'value': 'M3 x 8, hole 3.2', 'footprint': HOLE}
    comps['J10'] = {'value': '1x04 male header 2.54, BME680', 'footprint': HDR4}
    comps['J11'] = {'value': '1x04 male header 2.54, VEML6030', 'footprint': HDR4}
    new = {}
    for name, nodes in nets.items():
        out = []
        for ref, pin in nodes:
            if ref == 'J10':                       # 2 x 4: odd column BME680, even column VEML6030
                p = int(pin)
                out.append(('J10' if p % 2 else 'J11', str((p + 1) // 2)))
            else:
                out.append((ref, pin))
        new[name] = out
    return comps, new


def load_fp(fpid):
    lib, name = fpid.split(':')
    fp = pcbnew.FootprintLoad(MINE if lib == 'ha_panel' else KLIB + lib + '.pretty', name)
    if fp is None:
        raise RuntimeError('footprint not found: ' + fpid)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


WIRE_PADS = ('J3', 'J4', 'J7')        # wire landings: no header body, so the box is the pads + 0.3 (own footprints in block 2)


def crt(fp):
    """Front courtyard box in the board frame: (u0, v0, u1, v1)."""
    if fp.GetReference() in WIRE_PADS:
        us, vs = [], []
        for p in fp.Pads():
            u, v = UV(TOMM(p.GetPosition().x), TOMM(p.GetPosition().y))
            b = p.GetBoundingBox()
            us += [u - TOMM(b.GetWidth()) / 2 - 0.3, u + TOMM(b.GetWidth()) / 2 + 0.3]
            vs += [v - TOMM(b.GetHeight()) / 2 - 0.3, v + TOMM(b.GetHeight()) / 2 + 0.3]
        return (min(us), min(vs), max(us), max(vs))
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    u0, v1 = UV(TOMM(bb.GetX()), TOMM(bb.GetY()))
    u1, v0 = UV(TOMM(bb.GetRight()), TOMM(bb.GetBottom()))
    return (u0, v0, u1, v1)


def pad_uv(fp, num):
    p = [p for p in fp.Pads() if p.GetNumber() == num][0]
    return UV(TOMM(p.GetPosition().x), TOMM(p.GetPosition().y))


def put_centre(fp, u, v, rot):
    fp.SetOrientationDegrees(rot)
    c = crt(fp)
    fp.Move(pcbnew.VECTOR2I(MM(u - (c[0] + c[2]) / 2), -MM(v - (c[1] + c[3]) / 2)))


def put_pad(fp, num, u, v, rot):
    fp.SetOrientationDegrees(rot)
    pu, pv = pad_uv(fp, num)
    fp.Move(pcbnew.VECTOR2I(MM(u - pu), -MM(v - pv)))


# ---------------------------------------------------------------- plan ----
# ('pad', pad, u, v, rot) puts that pad there; ('c', u, v, rot) puts the courtyard centre there.
FIXED = {
    # mounting: four holes dia 3.2 for the unit's standard M3 x 8 (site section 2)
    'H1': ('c', -37.0, 22.0, 0), 'H2': ('c', 30.0, 25.0, 0), 'H3': ('c', -31.0, -25.25, 0), 'H4': ('c', 31.0, -25.25, 0),
    # bottom edge, from -u to +u: speaker right, Pi signal 9, 20 V, Pi signal 4, touch, Pi power, speaker left
    'J9': ('pad', '1', -40.25, -25.0, 0),          # speaker right, B2B-XH-A, plug toward the board
    'J3': ('pad', '1', -25.3, -27.0, 90),          # Pi signal leads, 9 of 10 pads, 5 columns x 2 rows
    'F1': ('c', -9.3, -25.5, 180),                # 20 V fuse next to J1 pin 1
    'J1': ('pad', '1', -1.25, -25.0, 0),           # 20 V in, B2B-XH-A
    'J4': ('pad', '1', 5.65, -27.0, 90),           # Pi signal leads, 4 pads, 2 x 2
    'J6': ('pad', '1', 12.3, -25.94, 90),          # touch board, B4B-XH-A, long side up the board
    'J2': ('pad', 'A1', 18.65, -20.34, 0),         # Pi power, USB4085, mouth flush with the bottom edge, opening down
    'J8': ('pad', '1', 37.5, -25.0, 0),            # speaker left, B2B-XH-A
    # -u side edge, lower half (zone D)
    'J5': ('pad', '1', -40.3, -17.6, 90),          # radar, B4B-XH-A
    'J10': ('pad', '1', -34.3, -10.3, 0),           # BME680, 1 x 4 pin header
    # middle of the board, below the supply module (which stands on zone E's probed point)
    'J11': ('pad', '1', -4.5, -12.0, 90),         # VEML6030, 1 x 4 pin header
    # supply module upright, body v -4.3...+7.7, +Vout end toward the Pi power socket
    'PS1': ('pad', '1', 12.5, -0.3, 180),
    # 20 V filter in front of the supply module (Mean Well's circuit): C5 - L1 - C6, C6 over the +Vin pins
    'C6': ('c', -27.0, 13.9, 180), 'L1': ('c', -15.0, 15.15, 180), 'C5': ('c', -3.0, 13.9, 180),
    'C7': ('c', 8.5, 11.4, 0),                     # supply module's output capacitor
    'F5': ('c', 8.0, 24.3, 0),                     # amplifier's resettable fuse, +20V on the left, PVDD on the right
    'J7': ('pad', '1', -29.5, 24.2, 90),           # echo-reference tap, 8 wire pads (second option only)
    'U1': ('c', -10.2, -16.9, 90),                 # 20 V inlet protection
    'F2': ('c', 8.0, -7.0, 180),                   # Pi branch fuse under the +Vout pins
    'LK1': ('pad', '1', 6.9, -11.2, 0),            # Pi branch wire link, VBUS end toward the socket
}
AMP_CENTRE = (28.8, 9.4)                           # TAS5756M; block = rev 2.1's, turned 90 degrees clockwise
AMP = ['U100'] + ['L%d' % i for i in range(100, 104)] + ['C%d' % i for i in range(100, 124)] + \
      ['R%d' % i for i in range(100, 106)]
AMP_KEEP_21 = [   # rev 2.1 front keep-outs round the amplifier (KiCad mm, gen/plan_main1s.py)
    (53.6, 19.3, 63.5, 21.0), (53.6, 30.0, 63.5, 31.7),          # fan-out via rows
    (64.4, 17.3, 81.0, 19.4),                                     # OUT_AP corridor
    (64.4, 31.6, 70.0, 33.6), (69.0, 26.0, 80.5, 33.6),           # OUT_BP corridor
]
U100_21 = (60.0, 25.5)

# small parts: target = (ref, pad) of the pin they serve, or a point (u, v); placed in this order
ANCHOR = [
    # 20 V inlet protection
    ('C1', ('U1', '1')), ('C2', ('U1', '2')), ('R1', ('U1', '7')), ('R2', ('U1', '7')), ('R3', ('U1', '8')),
    ('C3', ('U1', '10')), ('R4', ('U1', '11')), ('R5', ('U1', '14')), ('R6', ('U1', '15')), ('C4', ('U1', '19')),
    ('D1', ('U1', '19')),
    # Pi branch
    ('C8', (18.3, -16.5)), ('C9', (18.3, -13.0)), ('R10', ('J2', 'A5')), ('R11', ('J2', 'B5')),
    ('D2', ('C7', '1')),
    # radar branch
    ('F3', (-27.0, -19.5)), ('C10', ('J5', '1')), ('R19', ('J5', '3')),
    # 3.3 V regulator and the sensor branch
    ('U2', (-24.0, -11.0)), ('R12', (-24.0, -8.5)), ('C11', (-24.0, -6.5)), ('C12', (-21.0, -11.0)),
    ('R13', (-27.0, -11.0)), ('F4', (-27.5, -13.5)),
    # Pi signal leads: series positions and pull-downs at the pads
    ('R14', ('J3', '7')), ('R17', ('J3', '9')), ('R15', ('J4', '1')), ('R16', ('J4', '4')), ('R18', ('J4', '2')),
    # supply module: enable link and the unpopulated trim network
    ('R7', ('PS1', '13')), ('R8', ('PS1', '12')), ('R9', ('PS1', '12')),
    # echo-reference links (unpopulated)
    ('R20', ('J7', '2')), ('R21', ('J7', '3')), ('R22', ('J7', '4')), ('R23', ('J7', '5')), ('R24', ('J7', '7')),
    ('R25', ('J7', '8')),
    # amplifier logic rail links
    ('R26', (20.0, 23.5)), ('R27', (20.0, 25.5)),
]
TPS = [   # bare test pads on the door-side face
    ('TP1', ('U1', '1')), ('TP2', ('U1', '18')), ('TP3', ('U1', '14')), ('TP4', ('U1', '15')), ('TP5', ('U1', '16')),
    ('TP6', ('U1', '13')), ('TP7', ('U1', '9')), ('TP8', ('C6', '1')), ('TP9', ('C7', '1')), ('TP10', ('LK1', '1')),
    ('TP11', ('LK1', '2')), ('TP12', ('J5', '1')), ('TP13', ('PS1', '12')), ('TP14', ('PS1', '13')),
    ('TP15', ('J2', 'A12')), ('TP16', (-21.0, -8.5)), ('TP17', (-19.0, -13.5)), ('TP19', (24.0, 23.5)),
    ('TP20', (24.0, 26.0)),
]


def overlap(a, b, g=0.0):
    return not (a[2] + g <= b[0] or b[2] + g <= a[0] or a[3] + g <= b[1] or b[3] + g <= a[1])


def rot_cw(x, y):
    """rev 2.1 KiCad offset from U100 -> rev 3 board-frame offset from U100 (block turned 90 degrees clockwise)."""
    dx, dy = x - U100_21[0], y - U100_21[1]
    return -dy, -dx                                    # u = -dy, v = -(KiCad y) = -dx


def tht_ok(fp, protrusion, holes):
    """Through-hole pin ends against the back-face heights and the post zones (site sections 1 and 2)."""
    for p in fp.Pads():
        if not p.HasHole():
            continue
        u, v = UV(TOMM(p.GetPosition().x), TOMM(p.GetPosition().y))
        hx, hy = TOMM(p.GetSizeX()) / 2, TOMM(p.GetSizeY()) / 2
        r = max(hx, hy)
        if S.back_allowed_rect((u - r, v - r, u + r, v + r))[0] < protrusion:
            return False
        for (hu, hv) in holes:
            if math.hypot(max(abs(u - hu) - hx, 0), max(abs(v - hv) - hy, 0)) < S.POST_ZONE_BACK / 2:
                return False
    return True


PROTRUSION = {'CP_Radial': 1.5, 'WireLink': 1.5}      # leads cut after soldering (assumption, stated in the report)


def spiral(board, fp, target, obs, holes, rots=(0, 90, 180, 270), rmax=22.0, step=0.25, keep=()):
    tu, tv = target
    name = str(fp.GetFPID().GetLibItemName())
    prot = next((h for k, h in PROTRUSION.items() if name.startswith(k)), None)
    r = 0.0
    while r <= rmax:
        n = max(1, int(2 * math.pi * r / step))
        for k in range(n):
            a = 2 * math.pi * k / n
            u, v = tu + r * math.cos(a), tv + r * math.sin(a)
            for rot in rots:
                put_centre(fp, u, v, rot)
                c = crt(fp)
                if c[0] < -S.U0 + EDGE or c[2] > S.U0 - EDGE or c[1] < -S.V0 + EDGE or c[3] > S.V0 - EDGE:
                    continue
                if any(overlap(c, o, GAP) for o in obs) or any(overlap(c, o) for o in keep):
                    continue
                if prot is not None and not tht_ok(fp, prot, holes):
                    continue
                obs.append(c)
                return round(r, 2)
        r += step
    raise RuntimeError('no place for ' + fp.GetReference())


def build(netlist, outdir):
    comps, nets = rev3_parts(*read_netlist(netlist))
    os.makedirs(os.path.join(outdir, 'plan'), exist_ok=True)
    out = os.path.join(outdir, 'plan', 'main-board-rev3-plan.kicad_pcb')
    board = pcbnew.NewBoard(out)
    board.SetCopperLayerCount(4)
    ds = board.GetDesignSettings()                     # rev 2.1's board rules, so the plan opens without rule noise
    ds.m_TrackMinWidth = MM(0.10); ds.m_MinClearance = MM(0.15); ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.2); ds.m_ViasMinAnnularWidth = MM(0.1); ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleToHoleMin = MM(0.25)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(MM(0.15)); nc.SetTrackWidth(MM(0.2)); nc.SetViaDiameter(MM(0.6)); nc.SetViaDrill(MM(0.3))
    pts = [(0, 0), (2 * S.U0, 0), (2 * S.U0, 2 * S.V0), (0, 2 * S.V0)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)
    ninfo = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); ninfo[name] = ni
    pin_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
    fps = {}
    for ref, c in sorted(comps.items()):
        fp = load_fp(c['footprint'])
        fp.SetReference(ref); fp.SetValue(c['value'])
        fp.SetPosition(pcbnew.VECTOR2I(MM(X(0)), MM(Y(0))))
        board.Add(fp)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(ninfo[n])
        fps[ref] = fp

    # rev 2.1 positions of the amplifier block
    old = pcbnew.LoadBoard(os.path.join(HERE, '..', 'rev2.1', 'main-board.kicad_pcb'))
    for ref in AMP:
        o = old.FindFootprintByReference(ref)
        du, dv = rot_cw(TOMM(o.GetPosition().x), TOMM(o.GetPosition().y))
        fp = fps[ref]
        fp.SetOrientationDegrees(o.GetOrientationDegrees() - 90)
        fp.SetPosition(pcbnew.VECTOR2I(MM(X(AMP_CENTRE[0] + du)), MM(Y(AMP_CENTRE[1] + dv))))
    amp_keep = []
    for (x0, y0, x1, y1) in AMP_KEEP_21:
        a, b = rot_cw(x0, y0), rot_cw(x1, y1)
        amp_keep.append((AMP_CENTRE[0] + min(a[0], b[0]), AMP_CENTRE[1] + min(a[1], b[1]),
                         AMP_CENTRE[0] + max(a[0], b[0]), AMP_CENTRE[1] + max(a[1], b[1])))

    for ref, p in FIXED.items():
        if p[0] == 'c':
            put_centre(fps[ref], p[1], p[2], p[3])
        else:
            put_pad(fps[ref], p[1], p[2], p[3], p[4])

    holes = [((crt(fps[h])[0] + crt(fps[h])[2]) / 2, (crt(fps[h])[1] + crt(fps[h])[3]) / 2) for h in ('H1', 'H2', 'H3', 'H4')]
    obs = [crt(fps[r]) for r in list(FIXED) + AMP]
    dist = {}
    for ref, a in ANCHOR + TPS:
        tgt = a if isinstance(a[0], (int, float)) else pad_uv(fps[a[0]], a[1])
        dist[ref] = spiral(board, fps[ref], tgt, obs, holes, rots=(0,) if ref.startswith('TP') else (0, 90, 180, 270),
                           keep=amp_keep)
    left = [r for r in fps if r not in FIXED and r not in AMP and r not in dist]
    pcbnew.SaveBoard(out, board)

    data = {'outline': [-S.U0, -S.V0, S.U0, S.V0], 'amp_keep': amp_keep, 'parts': {}}
    for ref, fp in fps.items():
        c = crt(fp)
        u, v = UV(TOMM(fp.GetPosition().x), TOMM(fp.GetPosition().y))
        data['parts'][ref] = {
            'value': fp.GetValue(), 'footprint': str(fp.GetFPID().GetLibItemName()),
            'u': round(u, 3), 'v': round(v, 3), 'rot': round(fp.GetOrientationDegrees(), 1),
            'crt': [round(t, 3) for t in c],
            'placed': 'fixed' if ref in FIXED else 'amp block' if ref in AMP else 'auto',
            'from_anchor': dist.get(ref),
            'pads': [{'n': p.GetNumber(), 'u': round(UV(TOMM(p.GetPosition().x), 0)[0], 3),
                      'v': round(UV(0, TOMM(p.GetPosition().y))[1], 3), 'tht': bool(p.HasHole()),
                      'sx': round(TOMM(p.GetBoundingBox().GetWidth()), 2), 'sy': round(TOMM(p.GetBoundingBox().GetHeight()), 2),
                      'net': p.GetNetname()} for p in fp.Pads()],
        }
    json.dump(data, open(os.path.join(outdir, 'floorplan.json'), 'w'), indent=1)
    far = sorted(((d, r) for r, d in dist.items()), reverse=True)[:10]
    print('placed', len(fps) - len(left), 'of', len(fps), '| unplaced', left)
    print('farthest from the pin they serve:', far)
    return data


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
