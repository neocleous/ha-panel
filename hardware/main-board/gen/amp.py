"""TAS5756M (U100, DCA, rotated 270 at 60.0/25.5) escape: staggered signal fan-out, PVDD pin bridges + vias, GND pins to
the exposed land, and the output/bootstrap stubs to C104/C108/C115/C111 (all locked, F.Cu).
Pins: top row 1..24 at y 21.79 (x = 66.25 - 0.5 n), bottom row 25..48 at y 29.21 (x = 54.25 + 0.5 (n - 25));
pad 1.475 x 0.30, outer tips at y 21.055 / 29.945."""
import pcbnew

MM = pcbnew.FromMM
VIA = (0.45, 0.2)          # signal fan-out via
PVIA = (0.6, 0.3)          # PVDD via
W_FAN = 0.2
NEAR, FAR = 0.5, 1.25      # via centre distance beyond the pin tip

TOP_SKIP = {1, 2, 3, 4, 5, 6, 7}          # outputs/bootstrap/PVDD handled separately
BOT_SKIP = {41, 42, 43, 44, 45, 46, 47, 48}


def pin_xy(n):
    if n <= 24:
        return 66.25 - 0.5 * n, 21.79, 21.055, -1
    return 54.25 + 0.5 * (n - 25), 29.21, 29.945, 1


def _trk(board, net, pts, w, layer=pcbnew.F_Cu):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1))); t.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
        t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(net); t.SetLocked(True)
        board.Add(t)


def _via(board, net, x, y, size):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(size[0])); v.SetDrill(MM(size[1]))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True)
    board.Add(v)


def stage(board, ref='U100'):
    fp = board.FindFootprintByReference(ref)
    pads = {int(p.GetNumber()): p for p in fp.Pads() if p.GetNumber().isdigit() and int(p.GetNumber()) <= 48}
    net = {n: p.GetNet() for n, p in pads.items()}
    name = {n: p.GetNetname() for n, p in pads.items()}
    vias = []
    # --- GND pins: stub inward onto the exposed land (its copper edge is 0.475 mm inside the pin row)
    for n, nm in name.items():
        if nm == 'GND':
            x, y, tip, s = pin_xy(n)
            _trk(board, net[n], [(x, y), (x, y - s * 1.3)], 0.25)
    # --- signal fan-out, alternating near/far rows; a GND or skipped pin resets the alternation
    bridged = {31: 30}                      # 3V3_AMP pins 30/31 share pin 30's via
    for row, rng, skip in (('top', range(8, 25), TOP_SKIP), ('bot', range(25, 41), BOT_SKIP)):
        prev_near = False
        for n in rng:
            if n in skip or name[n] == 'GND' or n in bridged:
                prev_near = False
                continue
            x, y, tip, s = pin_xy(n)
            d = FAR if prev_near else NEAR
            prev_near = not prev_near
            vy = tip + s * d
            _trk(board, net[n], [(x, tip - s * 0.3), (x, vy)], W_FAN)
            _via(board, net[n], x, vy, VIA)
            vias.append((n, x, vy))
    for n, m in bridged.items():            # bridge the outer pad ends
        x1, _, tip, s = pin_xy(n); x2, _, _, _ = pin_xy(m)
        _trk(board, net[n], [(x1, tip - s * 0.3), (x2, tip - s * 0.3)], 0.25)
    # --- PVDD: bridge 6-7 and 41-43 at the outer ends, one 0.6/0.3 via each side
    pv = net[6]
    _trk(board, pv, [(63.25, 21.3), (62.75, 21.3)], 0.3)
    _trk(board, pv, [(63.0, 21.3), (63.0, 20.555)], 0.3)
    _via(board, pv, 63.0, 20.555, PVIA)
    _trk(board, pv, [(62.25, 29.7), (63.25, 29.7)], 0.3)
    _trk(board, pv, [(62.75, 29.7), (62.75, 30.445)], 0.3)
    _via(board, pv, 62.75, 30.445, PVIA)
    # --- outputs and bootstraps (caps: C104 pads 63.745/65.295 @19.35, C108 upright 67.3 @21.375 (1) / 19.825 (2),
    #     C115 mirror @31.65, C111 upright 67.3 @29.625 (1) / 31.175 (2))
    _trk(board, net[5], [(63.75, 21.3), (63.745, 19.35)], 0.25)                                  # BST_AP
    _trk(board, net[4], [(64.25, 21.3), (64.25, 20.55)], 0.3)                                   # OUT_AP neck
    _trk(board, net[4], [(64.25, 20.55), (65.0, 19.8), (65.295, 19.35)], 0.4)
    _trk(board, net[2], [(65.25, 21.3), (65.25, 20.65)], 0.3)                                   # OUT_AN neck
    _trk(board, net[2], [(65.25, 20.65), (65.75, 20.35), (67.0, 19.95)], 0.4)
    _trk(board, net[1], [(65.75, 21.375), (67.3, 21.375)], 0.25)                                 # BST_AN
    _trk(board, net[44], [(63.75, 29.7), (63.745, 31.65)], 0.25)                                 # BST_BP
    _trk(board, net[45], [(64.25, 29.7), (64.25, 30.45)], 0.3)                                  # OUT_BP neck
    _trk(board, net[45], [(64.25, 30.45), (65.0, 31.2), (65.295, 31.65)], 0.4)
    _trk(board, net[47], [(65.25, 29.7), (65.25, 30.35)], 0.3)                                  # OUT_BN neck
    _trk(board, net[47], [(65.25, 30.35), (65.75, 30.65), (67.0, 31.05)], 0.4)
    _trk(board, net[48], [(65.75, 29.625), (67.3, 29.625)], 0.25)                                # BST_BN
    return vias
