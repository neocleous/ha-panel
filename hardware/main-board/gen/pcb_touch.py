"""Touch board rev D layout (decision 5A). Run: python3 pcb_touch.py <netlist> <out.kicad_pcb>"""
import os, sys
import pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_main as pm
MM = pm.MM
W, H = 90.0, 44.0
EX = (9.0, 33.0, 57.0, 81.0)   # electrode centres, front-view X (rev F), KiCad x
EY = 31.0                     # front-view Y 13 -> KiCad y 44 - 13
PLAN = {
    'E0': (EX[0], EY, 0, 'F'), 'E1': (EX[1], EY, 0, 'F'), 'E2': (EX[2], EY, 0, 'F'), 'E3': (EX[3], EY, 0, 'F'),
    'U1': (45.0, 14.0, 270, 'B'),
    'R1': (39.0, 20.5, 270, 'B'), 'R2': (42.5, 20.5, 270, 'B'), 'R3': (46.0, 20.5, 270, 'B'), 'R4': (49.5, 20.5, 270, 'B'),
    'C1': (39.6, 14.0, 270, 'B'), 'C2': (37.8, 14.0, 270, 'B'),
    'J1': (33.0, 4.2, 0, 'B'),
}


def extra(board, nets):
    route(board, nets, ROUTES)
    B = pcbnew.B_SilkS
    pm.set_ref(board, 'U1', 47.6, 14.0, 0)
    pm.set_ref(board, 'C1', 39.3, 17.4, 0); pm.set_ref(board, 'C2', 36.4, 17.4, 0)
    for i, x in enumerate((39.0, 42.5, 46.0, 49.5)):
        pm.set_ref(board, 'R%d' % (i + 1), x + 1.6, 20.5, 90)
    pm.set_ref(board, 'J1', 24.4, 4.2, 0)
    for s, x in (('VCC', 38.25), ('GND', 34.75), ('SDA', 31.25), ('SCL', 27.75)):
        pm.text(board, s, x, 7.1, B)
    pm.text(board, 'HOST', 24.4, 6.0, B, size=1.0)
    for i, x in enumerate(EX):
        pm.text(board, 'KEY%d' % i, x, 26.6, B)
    pm.text(board, 'HA panel touch board rev D 2026-11  -  AT42QT1070 0x1B', 45.0, 41.0, B)
    pm.text(board, 'front: KEY0..KEY3 left to right', 45.0, 38.6, B)
    for r in ('E0', 'E1', 'E2', 'E3'):
        board.FindFootprintByReference(r).Reference().SetVisible(False)
    # electrode vias at the top edge of each electrode (inside the copper), tented both sides
    for i, x in enumerate(EX):
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(EY - 8.0 + 1.0)))
        v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
        v.SetNet(nets['/E%d' % i])
        board.Add(v)
    # B.Cu track keep-outs behind the electrodes (below the via row)
    for x in EX:
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetLayer(pcbnew.B_Cu)
        ol = z.Outline(); ol.NewOutline()
        for (a, b) in ((x - 8.5, EY - 6.0), (x + 8.5, EY - 6.0), (x + 8.5, EY + 8.5), (x - 8.5, EY + 8.5)):
            ol.Append(MM(a), MM(b))
        board.Add(z)
    ds = board.GetDesignSettings()
    ds.m_TentViasFront = True
    ds.m_TentViasBack = True


ROUTES = [  # (net, width, points) on B.Cu
    ('/KEY0', 0.25, [(42.46, 16.475), (42.46, 17.9), (40.685, 19.675), (39.0, 19.675)]),
    ('/KEY1', 0.25, [(43.73, 16.475), (43.73, 18.45), (42.505, 19.675)]),
    ('/KEY2', 0.25, [(45.0, 16.475), (45.0, 18.675), (46.0, 19.675)]),
    ('/KEY3', 0.25, [(46.27, 16.475), (46.27, 17.9), (48.045, 19.675), (49.5, 19.675)]),
    ('/E0', 0.25, [(39.0, 21.325), (39.0, 22.1), (9.9, 22.1), (9.0, 23.0), (9.0, 24.0)]),
    ('/E1', 0.25, [(42.5, 21.325), (42.5, 23.1), (33.9, 23.1), (33.0, 24.0)]),
    ('/E2', 0.25, [(46.0, 21.325), (46.0, 22.6), (56.0, 22.6), (57.0, 23.6), (57.0, 24.0)]),
    ('/E3', 0.25, [(49.5, 21.325), (49.5, 21.9), (80.1, 21.9), (81.0, 22.8), (81.0, 24.0)]),
    ('+3V3', 0.4, [(38.25, 4.2), (38.25, 10.4), (39.6, 11.75), (39.6, 13.175)]),
    ('+3V3', 0.4, [(39.6, 11.75), (41.19, 11.75)]),
    ('+3V3', 0.4, [(38.25, 10.4), (37.8, 10.85), (37.8, 13.175)]),
    ('GND', 0.4, [(34.75, 4.2), (34.75, 15.9), (41.19, 15.9), (41.19, 16.475)]),
    ('GND', 0.4, [(37.8, 14.825), (37.8, 15.9)]),
    ('GND', 0.4, [(39.6, 14.825), (39.6, 15.9)]),
    ('GND', 0.3, [(41.19, 15.9), (41.19, 14.2), (42.46, 13.0), (42.46, 11.525)]),
    ('/SDA', 0.25, [(31.25, 4.2), (31.25, 1.35), (43.73, 1.35), (43.73, 11.525)]),
    ('/SCL', 0.25, [(27.75, 4.2), (27.75, 0.75), (47.54, 0.75), (47.54, 11.525)]),
]


def route(board, nets, routes, layer=pcbnew.B_Cu):
    for net, w, pts in routes:
        for a, b in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
            t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(nets[net])
            board.Add(t)


if __name__ == '__main__':
    pm.FP_OVERRIDE.clear()
    os.environ.setdefault('HA_PRETTY', '/home/claude/work/fp/ha_panel.pretty')
    b, placed, missing = pm.build(sys.argv[1], sys.argv[2], PLAN, layers=2, extra=extra, size=(W, H), radius=2.0)
    print('placed', len(placed), 'missing', missing)
    for r in ('U1', 'J1'):
        fp = b.FindFootprintByReference(r)
        print(r, [(p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x), 2), round(pcbnew.ToMM(p.GetPosition().y), 2)) for p in fp.Pads()][:14])
