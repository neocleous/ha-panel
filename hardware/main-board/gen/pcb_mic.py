"""Mic strip layout (K21: 28 x 6 x 0.8, 2 layers). x = 0 at the outer (port) end. Every part on the back (inner side);
the front faces the gasket and carries only GND pour and short crossings. Decision 9.1: wire pads instead of J1/JP1/TPs.
Run: python3 pcb_mic.py <netlist> <out.kicad_pcb>"""
import math
import os
import subprocess
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_main as pm
import mroute
import silk

MM = pcbnew.FromMM
W, H = 28.0, 6.0
PORT = (2.0, 3.0)                      # rev F: port at x_rel 35.5, strip outer end 37.5
STAKES = [(7.5, 3.0), (26.0, 3.0)]     # heat-stake pins x_rel 30.0 / 11.5, Ø1.8 in Ø2.0 holes
HEAD = 3.6                             # back keep-out for the staked head
# courtyard centres (x, y, rot, side); columns: MK1 | C2 | stake | U1 R4 C3 | R2 R5 | C1 R1 | D1 D2 D3 | J1 | stake
PLAN = {
    'MK1': (2.0, 3.0, 90, 'B'), 'C2': (4.75, 3.0, 90, 'B'),
    'U1': (11.17, 1.32, 0, 'B'), 'R4': (11.17, 3.42, 0, 'B'), 'C3': (11.17, 5.0, 180, 'B'),
    'R2': (14.58, 3.0, 0, 'B'), 'R5': (14.58, 4.75, 0, 'B'),
    'C1': (17.66, 1.25, 0, 'B'), 'R1': (17.66, 3.0, 0, 'B'),
    'D1': (20.5, 1.25, 0, 'B'), 'D2': (20.5, 3.0, 0, 'B'), 'D3': (20.5, 4.75, 0, 'B'),
    'J1': (23.05, 3.0, 0, 'B'),
}
CLASSES = {'SIG': (0.2, 0.15, 0.45, 0.2, [])}


def circle_pts(cx, cy, r, n=32):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def extra(board, ninfo):
    # MK1: put its NPTH sound hole exactly on the port
    mk = board.FindFootprintByReference('MK1')
    hole = [p for p in mk.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH][0]
    d = pcbnew.VECTOR2I(MM(PORT[0]) - hole.GetPosition().x, MM(PORT[1]) - hole.GetPosition().y)
    mk.Move(d)
    # heat-stake holes (board-only footprints, NPTH Ø2.0) + back keep-out for the staked heads
    for k, (x, y) in enumerate(STAKES):
        fp = pm.load_fp('ha_panel:HeatStake_D2.0mm_Head3.6mm')
        fp.SetReference('HS%d' % (k + 1)); fp.SetValue('heat stake')
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        board.Add(fp)
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetLayer(pcbnew.B_Cu)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowFootprints(False)
        ol = z.Outline(); ol.NewOutline()
        for px, py in circle_pts(x, y, HEAD / 2):
            ol.Append(MM(px), MM(py))
        z.SetZoneName('stake head %d' % (k + 1))
        board.Add(z)


def pours(board):
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(lay); z.SetNet(board.FindNet('GND'))
        ol = z.Outline(); ol.NewOutline()
        for px, py in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)):
            ol.Append(MM(px), MM(py))
        z.SetLocalClearance(MM(0.25)); z.SetMinThickness(MM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(MM(0.3)); z.SetThermalReliefSpokeWidth(MM(0.3))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


JAVA = '/usr/lib/jvm/java-25-openjdk-amd64/bin/java'
FR = '/home/claude/tools/fr/fr_g.jar'


CONN = [   # (net, from, to, width) in routing order; C3's ground first (it is boxed in later), then the mic runs
    ('GND', (11.95, 5.00), (13.75, 3.00), 0.25),
    ('/CLK_MIC', (10.28, 1.97), (1.15, 5.18), 0.2),
    ('/DATA_MIC', (11.99, 3.42), (2.85, 5.18), 0.2),
    ('/MIC_LR', (13.75, 4.75), (1.15, 4.48), 0.2),
    ('GND', (12.06, 1.97), (13.75, 3.00), 0.25),         # U1 pin 3 sits between its own pins: join R2's GND
    ('/DATA_C', (10.34, 3.42), (21.20, 4.75), 0.2),
    ('/DATA_C', (21.20, 4.75), (23.05, 5.20), 0.2),
    ('/VDD_MIC', (4.75, 3.77), (2.85, 4.48), 0.3),
    ('/VDD_MIC', (10.28, 0.67), (4.75, 3.77), 0.3),
    ('/VDD_MIC', (10.39, 5.00), (10.28, 0.67), 0.3),
    ('/VDD_MIC', (16.84, 3.00), (10.39, 5.00), 0.3),
    ('/VDD_MIC', (18.43, 1.25), (16.84, 3.00), 0.3),
    ('/CLK_C', (12.06, 1.32), (15.40, 3.00), 0.2),
    ('/CLK_C', (15.40, 3.00), (21.20, 3.00), 0.2),
    ('/CLK_C', (21.20, 3.00), (23.05, 3.00), 0.2),
    ('/SEL_C', (15.40, 4.75), (23.05, 4.10), 0.2),
    ('/VDD_C', (18.48, 3.00), (21.20, 1.25), 0.3),
    ('/VDD_C', (21.20, 1.25), (23.05, 0.80), 0.3),
    ('GND', (13.75, 3.00), (16.88, 1.25), 0.25),         # ... and to C1's
]
GND_PADS = [(2.81, 3.00), (4.75, 2.23), (12.06, 1.97), (11.95, 5.00), (13.75, 3.00), (16.88, 1.25), (19.80, 1.25),
            (19.80, 3.00), (19.80, 4.75), (23.05, 1.90)]


def route(path):
    b = pcbnew.LoadBoard(path)
    for net, a, c, w in CONN:
        ok, info = mroute.route(b, net, a, c, w, CLASSES, box=(-1, -1, W + 1, H + 1))
        print('route', net, ok, info)
    pours(b)
    for tgt in ((12.06, 1.97), (4.75, 2.23), (2.81, 3.00), (13.75, 3.00)):   # C3's ground onto the rest
        ok, info = mroute.route(b, 'GND', (11.95, 5.00), tgt, 0.25, CLASSES, box=(-1, -1, W + 1, H + 1))
        print('route GND C3', tgt, ok, info)
        if ok:
            break
    for p in GND_PADS:                           # every GND pad gets its own via to the front pour
        ok, info = mroute.drop_via(b, 'GND', p, CLASSES, w=0.25, via=(0.45, 0.2), layer='B', margin=2.5)
        print('gnd via', p, ok, info)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    for _ in range(2):
        print('stitch', len(mroute.stitch(b, CLASSES, via=(0.45, 0.2))))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    print('edge silk removed', silk.trim_edge(b, W, H, keep=mroute.GRAVE))
    shown, hidden = silk.place(b, W=W, H=H, skip_prefix=('HS',))
    print('silk shown', shown, 'hidden', hidden)
    pcbnew.SaveBoard(path, b)


def main(netlist, out):
    board, placed, missing = pm.build(netlist, out, PLAN, layers=2, extra=extra, size=(W, H))
    ds = board.GetDesignSettings()
    ds.m_MinResolvedSpokes = 1
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetViaDiameter(MM(0.45)); nc.SetViaDrill(MM(0.2))     # 0.8 mm strip, 6 mm wide: small vias only
    print('placed', len(placed), 'missing', missing)
    pcbnew.SaveBoard(out, board)
    route(out)
    return board


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
