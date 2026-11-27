# Block 3: the new grommet (Daniel's 1a: even frame 3.8 all round; block 2's saddle), built on temporary bodies from p32's
# flange. CHANGES NOTHING IN THE DOCUMENT: the result is kept in k.c['b3_grommet'] (p36 puts it in the model).
# World mm. The grommet prints on its side, world z up (print audit F3), at 0.12 after a 0.20 first layer (the record's
# 0.12 profile; the brief's tab "1.76 or 1.88" is on that grid): its level faces at bed + 0.20 + 0.12 k. The bed is z 10.0:
# the tab's underside and the flange's bottom edge, on the door's level seats (door grid: 7.2 above the door's bed at 2.8).
# Run: runpy.run_path(D + 'p33_grommet.py')['main']()  -> p33_grommet.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')

ZT = 10.0


def h(kk): return round(ZT + 0.20 + 0.12 * kk, 4)


TAB_TOP = h(14)        # 11.88: the tab 1.88 thick
CEIL = h(18)           # 12.36: the slot's ceiling over the door wall (the cut-out's bottom edge at 12.0: 0.36)
BORE0 = h(30)          # 13.80: the opening's bottom; the frame below it 3.80; 0.70 under the cradle's bezel (14.5)
BORE1 = h(144)         # 27.48: 0.78 over the bezel (26.7)
SLV1 = h(151)          # 28.32: the sleeve's top; its top wall 0.84
STRIP1 = h(166)        # 30.12: the opening's top at the flange (room for the plug's moulding, 30.1 at version 69)
FL1 = h(198)           # 33.96: the flange's top; the frame above the opening 3.84
XH, RC = 15.6, 2.0     # the flange's half width (frame 3.8 at the sides) and corner radius (Daniel's 1a)
XB, XS = 11.8, 12.6    # the opening's and the sleeve's half widths
Y_END = -81.2          # the sleeve's inner end (version 69)
Y_LEG = -81.6          # the leg's and tab's back face, 0.1 off the door wall's inner face
Y_LEG1 = -80.0         # the leg's front face
TAB_END = -76.95
SX, SY = 9.0, -79.3    # the screw axes cross the bed (z 10.0) at x +-9.0, y -79.3
LEAN = math.radians(18.0)
EAR_R = 2.35
T_CS0, T_CS1, T_SF1 = 0.93, 1.88, 5.0      # along the screw from the bed: countersink start, spot-face floor, spot-face end
R_HOLE, R_CS, R_SF = 1.1, 2.05, 2.4        # M2 clearance; 90 deg countersink to r 2.05 (head r 1.9); spot face


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    if k.c.get('b3_flange') is None:
        raise RuntimeError('run p32_flange first')
    U = (0.0, math.sin(LEAN), math.cos(LEAN))
    # 1. the flange onto the seat (bottom z 9.9 -> 10.0) and cut to its outline with the new top
    fl = X.tbm.copy(k.c['b3_flange'])
    X.move(fl, 0.0, 0.0, ZT - 9.9)
    o = X.wbox(-XH + RC, XH - RC, -90, -80, ZT, FL1)
    X.uni(o, X.wbox(-XH, XH, -90, -80, ZT + RC, FL1 - RC))
    for sx in (-1, 1):
        for zz in (ZT + RC, FL1 - RC):
            X.uni(o, X.cyl((sx * (XH - RC), -90.0, zz), (sx * (XH - RC), -80.0, zz), RC))
    X.sec(fl, o)
    print('flange: volume %.3f faces %d lumps %d' % (X.vol(fl), fl.faces.count, fl.lumps.count))
    # 2. the sweep: the flange pushed back in steps of 0.9 (less than its thickness), so the sleeve starts at its front face
    sw = X.tbm.copy(fl)
    for s in range(1, 7):
        t = X.tbm.copy(fl); X.move(t, 0.0, 0.9 * s, 0.0); X.uni(sw, t)
    # 3. the opening through the flange
    X.dif(fl, X.wbox(-XB, XB, -90, -75, BORE0, STRIP1))
    # 4. the sleeve, from the flange's front face to its inner end
    sl = X.wbox(-XS, XS, -87.0, Y_END, CEIL, SLV1)
    X.sec(sl, sw)
    g = fl
    X.uni(g, sl)
    # 5. the leg and the tab (the saddle's inner side), with the ears round the screws
    X.uni(g, X.wbox(-12.0, 12.0, Y_LEG, Y_LEG1, ZT, BORE0))
    X.uni(g, X.wbox(-12.0, 12.0, Y_LEG, TAB_END, ZT, TAB_TOP))
    ye = SY + U[1] * T_CS1          # the ears centred on the screw's axis at the spot-face floor
    for sx in (-1, 1):
        X.uni(g, X.cyl((sx * SX, ye, ZT), (sx * SX, ye, TAB_TOP), EAR_R))
    # 6. the bore through, and the strip above it in front of y -84.3 (the sleeve's top wall stays behind it)
    X.dif(g, X.wbox(-XB, XB, -90, -75, BORE0, BORE1))
    X.dif(g, X.wbox(-XB, XB, -90, -84.3, BORE1 - 0.01, STRIP1))
    # 7. the two screw seats: hole, countersink, spot face square to the screw
    for sx in (-1, 1):
        P = (sx * SX, SY, ZT)

        def at(t, P=P):
            return (P[0], P[1] + U[1] * t, P[2] + U[2] * t)
        X.dif(g, X.cyl(at(-0.6), at(4.0), R_HOLE))
        X.dif(g, X.cyl(at(T_CS0), at(T_CS1), R_HOLE, R_CS))
        X.dif(g, X.cyl(at(T_CS1), at(T_SF1), R_SF))
    k.c['b3_grommet'] = g
    v = X.add(X.tbm.copy(g), 'TMP_grommet_view', show=False)
    bb = [round(q, 3) for q in k.wbb(X, v)]
    v.deleteMe()
    print('grommet: volume %.3f, faces %d, lumps %d, solid %s, box %s' % (X.vol(g), g.faces.count, g.lumps.count, g.isSolid, bb))
    print('level faces (z): bed %.2f, tab top %.2f, slot ceiling %.2f, opening %.2f-%.2f, sleeve top %.2f, strip top %.2f, '
          'flange top %.2f' % (ZT, TAB_TOP, CEIL, BORE0, BORE1, SLV1, STRIP1, FL1))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p33_grommet.txt', _main)
