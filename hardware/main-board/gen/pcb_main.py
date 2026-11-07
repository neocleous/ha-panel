"""Main board layout builder (KiCad 9 pcbnew). Places parts by courtyard centre from a floorplan table,
assigns nets from the schematic netlist, writes main-board.kicad_pcb. Run: python3 pcb_main.py <netlist> <out.kicad_pcb>"""
import os
import sys
import json
import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexpr import parse

KLIB = '/usr/share/kicad/footprints/'
MINE = os.environ.get('HA_PRETTY', '/home/claude/work/fp/ha_panel.pretty')
MM = pcbnew.FromMM
W, H = 90.0, 50.0
FRONT_MAX_Y = 48.2          # MAIN_front_env starts at z 35.8 -> board y <= 84 - 35.8
HOLES = [(3.5, 3.5), (86.5, 3.5), (3.5, 46.5), (86.5, 46.5)]

# Footprint overrides (layout decisions; mirrored into the schematic generator)
FP_OVERRIDE = {}
TP_BACK = 'TestPoint:TestPoint_Pad_D1.5mm'


def sub(l, key):
    return [e for e in l if isinstance(e, list) and e and str(e[0]) == key]


def read_netlist(path):
    x = parse(open(path).read())[0]
    comps = {}
    for c in sub(sub(x, 'components')[0], 'comp'):
        ref = str(sub(c, 'ref')[0][1])
        d = {'value': str(sub(c, 'value')[0][1]), 'footprint': str(sub(c, 'footprint')[0][1]), 'props': {}}
        for p in sub(c, 'property'):
            nm = str(sub(p, 'name')[0][1])
            v = sub(p, 'value')
            d['props'][nm] = str(v[0][1]) if v else ''
        sp = sub(c, 'sheetpath')
        d['path'] = str(sub(sp[0], 'tstamps')[0][1]) + str(sub(c, 'tstamps')[0][1]) if sp else ''
        comps[ref] = d
    nets = {}
    for n in sub(sub(x, 'nets')[0], 'net'):
        name = str(sub(n, 'name')[0][1])
        nets[name] = [(str(sub(nd, 'ref')[0][1]), str(sub(nd, 'pin')[0][1])) for nd in sub(n, 'node')]
    return comps, nets


def load_fp(fpid):
    lib, name = fpid.split(':')
    path = MINE if lib == 'ha_panel' else KLIB + lib + '.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise RuntimeError('footprint not found: ' + fpid)
    return fp


def crtyd_center(fp):
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy.OutlineCount() == 0:
        cy = fp.GetCourtyard(pcbnew.B_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    c = bb.Centre()
    p = fp.GetPosition()
    return pcbnew.ToMM(c.x - p.x), pcbnew.ToMM(c.y - p.y)


def outline(board, w, h, r=0.0):
    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)
    def arc(c, st, ang):
        s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(pcbnew.VECTOR2I(MM(c[0]), MM(c[1]))); s.SetStart(pcbnew.VECTOR2I(MM(st[0]), MM(st[1])))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)
    seg((r, 0), (w - r, 0)); seg((w, r), (w, h - r)); seg((w - r, h), (r, h)); seg((0, h - r), (0, r))
    if r > 0:
        arc((w - r, r), (w - r, 0), 90); arc((w - r, h - r), (w, h - r), 90)
        arc((r, h - r), (r, h), 90); arc((r, r), (0, r), 90)


def build(netlist, out, plan, layers=2, extra=None, size=(W, H), radius=0.0):
    comps, nets = read_netlist(netlist)
    board = pcbnew.NewBoard(out)
    board.SetCopperLayerCount(layers)
    ds = board.GetDesignSettings()
    ds.m_TrackMinWidth = MM(0.15)
    ds.m_MinClearance = MM(0.15)
    ds.m_ViasMinSize = MM(0.45)
    ds.m_MinThroughDrill = MM(0.2)
    ds.m_ViasMinAnnularWidth = MM(0.1)
    ds.m_CopperEdgeClearance = MM(0.3)
    ds.m_HoleToHoleMin = MM(0.25)
    ds.m_SolderMaskMinWidth = MM(0.1)
    ds.m_MinSilkTextHeight = MM(1.0)
    ds.m_MinSilkTextThickness = MM(0.15)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(MM(0.15)); nc.SetTrackWidth(MM(0.2)); nc.SetViaDiameter(MM(0.6)); nc.SetViaDrill(MM(0.3))
    outline(board, size[0], size[1], radius)
    # nets
    ninfo = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        ninfo[name] = ni
    pin_net = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pin_net[(ref, pin)] = name
    placed, missing = [], []
    for ref, c in sorted(comps.items()):
        fpid = FP_OVERRIDE.get(ref, c['footprint'])
        fp = load_fp(fpid)
        fp.SetReference(ref)
        fp.SetValue(c['value'])
        if c['path']:
            fp.SetPath(pcbnew.KIID_PATH(c['path']))
        if 'dnp' in c['props']:
            fp.SetDNP(True)
        if 'exclude_from_bom' in c['props']:
            fp.SetExcludedFromBOM(True)
        board.Add(fp)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(ninfo[n])
        if ref in plan:
            cx, cy, rot, side = (list(plan[ref]) + [0, 'F'])[:4] if len(plan[ref]) < 4 else plan[ref]
            fp.SetOrientationDegrees(rot)
            ox, oy = crtyd_center(fp)
            fp.SetPosition(pcbnew.VECTOR2I(MM(cx - ox), MM(cy - oy)))
            if side == 'B':
                fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
                # keep the courtyard centre where asked
                bb = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
                c2 = bb.Centre()
                fp.Move(pcbnew.VECTOR2I(MM(cx) - c2.x, MM(cy) - c2.y))
            placed.append(ref)
        else:
            fp.SetPosition(pcbnew.VECTOR2I(MM(100 + 5 * (len(missing) % 10)), MM(10 + 5 * (len(missing) // 10))))
            missing.append(ref)
    if extra:
        extra(board, ninfo)
    pcbnew.SaveBoard(out, board)
    return board, placed, missing


def set_ref(board, ref, x, y, rot=0, size=1.0, hide=False):
    fp = board.FindFootprintByReference(ref)
    t = fp.Reference()
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetTextAngleDegrees(rot)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    t.SetVisible(not hide)


def text(board, s, x, y, layer, size=1.0, rot=0, mirrored=None, just=None):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    t.SetTextAngleDegrees(rot)
    if mirrored is None:
        mirrored = layer in (pcbnew.B_SilkS, pcbnew.B_Fab, pcbnew.B_Cu)
    t.SetMirrored(mirrored)
    if just == 'left':
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)
    return t
