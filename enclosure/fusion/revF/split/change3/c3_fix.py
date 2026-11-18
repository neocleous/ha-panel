# change3/c3_fix.py - the FDM fix pass (2026-11-18): every new body except the shell, built on temporary copies.
# Exec'd into sys.modules['c3'] after c3_lib.py. k = c3k (v5f_k_lib.py). World mm: x + = viewer's left, y + toward the screen, z up.
# Nothing here changes the document: the commit is in c3_calls.py.
import adsk.core, adsk.fusion, sys, math
k = sys.modules['c3k']
G = k.c.setdefault('g22', {})                           # name -> the new temporary body


# ---------- FDM2: the door's eight vent bars 4.5 deep, grown inward ----------
BARS = (3.0, 9.0, 15.0, 21.0, -3.0, -9.0, -15.0, -21.0)
ADD = 2.0                                               # added depth along the wall's normal (wall 2.5)
ZA, ZB = 57.0, 118.5                                    # where the ramps meet the wall's inner face (slots z 59.5 .. 116.0)


def yin(X, D, x, z):                                    # the door's inner face at (x, z): world y
    s = k.needle_t(X, [D], (x, -100.0, z), (x, -50.0, z), 0.02)
    return -100.0 + s[-1][1]


def build_door(X):
    b0 = X.body('HOUSING_F_door'); b = X.cp(b0); D = X.cp(b0); out = []
    for xc in BARS:
        zc = 87.75
        dydz = (yin(X, D, xc, zc + 3.0) - yin(X, D, xc, zc - 3.0)) / 6.0
        dydx = (yin(X, D, xc + 1.2, zc) - yin(X, D, xc - 1.2, zc)) / 2.4
        m = math.sqrt(1.0 + dydz * dydz); dy = 1.0 / m; dz = -dydz / m           # direction of growth in the y-z plane (inward, along the wall's normal there)
        s = ADD * math.sqrt(1.0 + dydx * dydx + dydz * dydz) / m                  # so that the offset along the true normal is ADD
        strip = X.cp(b0); X.sec(strip, X.wbox(xc - 1.5, xc + 1.5, -100.0, -50.0, 54.0, 122.0))
        X.move(strip, 0.0, s * dy, s * dz)
        # lower end: 45 degrees to the print's upright (the door stands on its bottom edge), from the wall's inner face at ZA
        ya = yin(X, D, xc, ZA); nr = (0.0, 0.70711, -0.70711)
        c = (xc, ya + nr[1] * 6.0, ZA + nr[2] * 6.0)
        X.dif(strip, c3_obox(X, c, (1.0, 0.0, 0.0), (0.0, nr[2], -nr[1]), 6.0, 40.0, 12.0))
        # upper end: 45 degrees to the wall, down to the wall's inner face at ZB
        yb = yin(X, D, xc, ZB); t = (yin(X, D, xc, ZB + 1.5) - yin(X, D, xc, ZB - 1.5)) / 3.0; mt = math.sqrt(1.0 + t * t)
        nw = (0.0, 1.0 / mt, -t / mt); tw = (0.0, t / mt, 1.0 / mt)
        nt = (0.0, (nw[1] + tw[1]) / math.sqrt(2.0), (nw[2] + tw[2]) / math.sqrt(2.0))
        c = (xc, yb + nt[1] * 6.0, ZB + nt[2] * 6.0)
        X.dif(strip, c3_obox(X, c, (1.0, 0.0, 0.0), (0.0, nt[2], -nt[1]), 6.0, 40.0, 12.0))
        v0 = X.vol(b); X.uni(b, strip)
        out.append((xc, round(math.degrees(math.atan(dydz)), 2), round(math.degrees(math.atan(dydx)), 2), round(s, 3), round(X.vol(b) - v0, 3)))
    G['HOUSING_F_door'] = b
    return out


def c3_obox(X, c, u, v, L, Wd, Ht):
    return sys.modules['c3'].obox_w(X, c, u, v, L, Wd, Ht)


# ---------- FDM10: the base plate's two noses 0.9 -> 1.2, grown upward ----------
def build_base(X):
    b = X.cp(X.body('FLOOR_PLATE')); out = []
    for sx in (1.0, -1.0):
        xa, xb = sorted((sx * 24.5, sx * 35.5))
        v0 = X.vol(b); X.uni(b, X.wbox(xa, xb, -0.9, 2.35, 5.2, 5.55)); out.append(round(X.vol(b) - v0, 3))
    G['FLOOR_PLATE'] = b
    return out


# ---------- FDM9, FDM12, FDM13: speaker boxes; touch clips ----------
YP = -7.05                                              # the touch clip's screw line: 0.1 further back, so that the 2.7 pilot keeps 2.0 on both sides
YB = -10.4                                              # the block and the clip's lug end here
RP = 1.35                                               # pilot 2.7


def build_box(X, sx):
    name = 'SPKBOX_L' if sx > 0 else 'SPKBOX_R'
    b0 = X.body(name); b = X.cp(b0); out = {}
    v0 = X.vol(b)
    X.uni(b, X.cyl((sx * 43.5, -6.95, 38.0), (sx * 49.0, -6.95, 38.0), 1.3))                 # the 2.5 pilot at y -6.95 filled
    xa, xb = sorted((sx * 43.5, sx * 50.5))
    X.uni(b, X.wbox(xa, xb, YB, -10.1, 30.0, 46.0))                                          # block 0.2 longer to the rear
    X.dif(b, X.cyl((sx * 43.4, YP, 38.0), (sx * 49.0, YP, 38.0), RP))                        # pilot 2.7 x 5.5 at y -7.05
    out['FDM9 pilot and block'] = round(X.vol(b) - v0, 3)
    v0 = X.vol(b)                                                                            # FDM12: the outer driver column joined to the side wall at its rear end
    xa, xb = sorted((sx * 91.9, sx * 93.4))
    X.uni(b, X.wbox(xa, xb, -11.5, -8.45, 43.75, 47.75))
    out['FDM12 column to wall'] = round(X.vol(b) - v0, 3)
    if sx < 0:
        v0 = X.vol(b)                                                                        # FDM12: the 0.44 slot between the staircase's top tread and the clip block
        X.uni(b, X.wbox(-48.06, -47.45, YB, -7.6, 29.5, 30.05))
        out['FDM12 stair to block'] = round(X.vol(b) - v0, 3)
        v0 = X.vol(b)                                                                        # FDM13: the lower inner cylinder carried up to z 79.0: no knife edge, no V-groove
        f48 = b0.faces.item(48).geometry; f75 = b0.faces.item(75).geometry
        o48 = k.W(f48.origin); o75 = k.W(f75.origin); a = k.unit(k.wv(f48.axis))
        out['FDM13 cylinders'] = (k.r2(o48), k.r2(o75), k.r2(a, 4), round(f48.radius * 10.0, 3), round(f75.radius * 10.0, 3))

        def at(o, y):
            s = (y - o[1]) / a[1]
            return (o[0] + a[0] * s, y, o[2])
        lens = X.cyl(at(o48, -50.68), at(o48, -23.32), f48.radius * 10.0)
        X.dif(lens, X.cyl(at(o75, -51.5), at(o75, -22.5), f75.radius * 10.0))
        X.sec(lens, X.wbox(-70.0, -57.0, -50.68, -23.32, 75.5, 79.0))
        out['FDM13 lens'] = round(X.vol(lens), 3)
        X.uni(b, lens)
        out['FDM13 added'] = round(X.vol(b) - v0, 3)
    G[name] = b
    return out


def build_clip(X, sx):
    name = 'TOUCH_CLIP_L' if sx > 0 else 'TOUCH_CLIP_R'
    b = X.cp(X.body(name)); v0 = X.vol(b)
    xa, xb = sorted((sx * 40.5, sx * 43.5))
    X.uni(b, X.wbox(xa, xb, YB, -10.1, 30.0, 46.0))                                          # lug 0.2 longer to the rear
    X.uni(b, X.cyl((sx * 40.5, -6.95, 38.0), (sx * 43.5, -6.95, 38.0), 1.75))               # the 3.4 hole at y -6.95 filled
    X.dif(b, X.cyl((sx * 40.4, YP, 38.0), (sx * 43.6, YP, 38.0), 1.7))                       # 3.4 hole at y -7.05
    G[name] = b
    return round(X.vol(b) - v0, 3)


# ---------- FDM12: the cap's eight corner slots closed (each corner pin joined to its two pocket walls) ----------
POCK = ((-37.7, -8.3), (8.3, 37.7))                     # the microphone pockets in x; y -29.7 .. -23.3
PY = (-29.7, -23.3)


def build_cap(X, pin=1.6, gap=0.4):
    b = X.cp(X.body('HOUSING_F_cap')); out = []
    for (x0, x1) in POCK:
        for cx, sx in ((x0, 1.0), (x1, -1.0)):
            for cy, sy in ((PY[0], 1.0), (PY[1], -1.0)):
                v0 = X.vol(b)
                X.uni(b, X.wbox(cx - 0.1 * sx, cx + gap * sx, cy - 0.1 * sy, cy + pin * sy, 177.5, 178.35))      # between the pin and the end wall
                X.uni(b, X.wbox(cx + gap * sx - 0.05 * sx, cx + pin * sx, cy - 0.1 * sy, cy + gap * sy, 177.5, 178.35))   # between the pin and the long wall
                out.append(round(X.vol(b) - v0, 3))
    G['HOUSING_F_cap'] = b
    return out


# ---------- FDM8: the cradle's rear bezel 0.80 -> 0.85 (its rear face 0.05 further out) ----------
def build_cradle(X):
    b0 = X.body('CRADLE_5807'); b = X.cp(b0); v0 = X.vol(b)
    lay = X.cp(b0); X.sec(lay, X.wbox(-12.0, 12.0, -84.6, -84.5, 10.0, 30.0))               # the rear 0.1 of the cradle: its rear face with the opening
    X.move(lay, 0.0, -0.05, 0.0)
    X.uni(b, lay)
    G['CRADLE_5807'] = b
    return round(X.vol(b) - v0, 3)
