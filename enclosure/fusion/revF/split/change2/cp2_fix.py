# change2/cp2_fix.py - block 2 of the posts / shadow gap / FDM strength pass (2026-11-17): every new body, built on temporary copies.
# Exec'd into sys.modules['cp2'] after cp2_lib*.py, cp2_posts.py and cp2_vents.py. k = cp2k (v5f_k_lib.py).
# World mm: x + = viewer's left, y + toward the screen, z up. Slab frame (x, d, up). Nothing here changes the document: commit() does (cp2_calls.py).
import adsk.core, adsk.fusion, sys, math
k = sys.modules['cp2k']
G = k.c.setdefault('g21', {})                           # name -> the new temporary body


def W3(a, b):                                           # design vector from world point a to world point b
    return k.Wp(*a).vectorTo(k.Wp(*b))


def obox_w(X, c, u, v, L, Wd, Ht):                      # box centred at world c: L along u, Wd along v, Ht along u x v (world unit vectors)
    U = W3(c, [c[i] + u[i] for i in range(3)]); V = W3(c, [c[i] + v[i] for i in range(3)]); U.normalize(); V.normalize()
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(k.Wp(*c), U, V, L / 10.0, Wd / 10.0, Ht / 10.0))


def cone_w(X, p0, r0, p1, r1):
    return X.tbm.createCylinderOrCone(k.Wp(*p0), r0 / 10.0, k.Wp(*p1), r1 / 10.0)


def cone_d(X, x, up, d0, r0, d1, r1):
    return X.tbm.createCylinderOrCone(k.Dp(x, d0, up), r0 / 10.0, k.Dp(x, d1, up), r1 / 10.0)


def ref_w(X, v):                                        # the cloth reference moved by a world vector (mm)
    t = X.tbm.copy(k.c['skin_ref']); X.move(t, v[0], v[1], v[2]); return t


def tube(X, p0, p1, r_out, r_in):
    t = X.cyl(p0, p1, r_out)
    e = [(p1[i] - p0[i]) for i in range(3)]; n = math.sqrt(sum(q * q for q in e)); e = [q / n for q in e]
    X.dif(t, X.cyl([p0[i] - e[i] for i in range(3)], [p1[i] + e[i] for i in range(3)], r_in))
    return t


# ---------- shell: fins removed (question 3 a), gussets under the cap's seat 2.0 -> 2.6 (D209) ----------
def shell_fins(X, b):                                   # the two triangular fins beside the top posts: 215.22 mm3 each
    out = {}
    for sx in (1.0, -1.0):
        xa, xb = sorted((sx * 38.0, sx * 40.0))
        a1 = X.wbox(xa, xb, -28.5, -15.0, 152.5, 170.6)
        a2 = X.wbox(xa, xb, -33.2, -28.5, 152.5, 169.5)
        a3 = X.wbox(xa, xb, -29.6, -28.5, 169.5, 170.6)
        X.dif(a3, X.cyl((sx * 43.36, -32.85, 169.0), (sx * 43.36, -32.85, 173.0), 5.5))      # the cap's side pad stays whole
        X.uni(a1, a2); X.uni(a1, a3)
        v = X.vol(b); X.dif(b, a1); out[sx] = round(v - X.vol(b), 3)
    return out


# left side: (point on the face that moves out (x, y), its outward unit normal, unit vector along the gusset from the wall inward, centre, length)
GUS = (((19.970, -42.175), (-0.9955, 0.0946), (0.0946, 0.9955), -0.2, 22.5),      # x 21, away from the cap key's lane
       ((31.013, -42.237), (0.9955, -0.0946), (0.0946, 0.9955), 0.2, 21.0),       # x 30
       ((49.733, -34.097), (0.9333, 0.3591), (-0.3591, 0.9333), 0.0, 19.0))       # the oblique one beside the side pad
GT = 0.6


def shell_gussets(X, b, sides=(1.0, -1.0)):
    out = []
    for sx in sides:
        for i, (q, n, v, sc, ln) in enumerate(GUS):
            q = (sx * q[0], q[1]); n = (sx * n[0], n[1], 0.0); v = (sx * v[0], v[1], 0.0)
            c = (q[0] + n[0] * GT / 2 + v[0] * sc, q[1] + n[1] * GT / 2 + v[1] * sc, 164.75)
            xs = [c[0] + a * n[0] + e * v[0] for a in (-3.4, 1.2) for e in (-ln / 2 - 1.5, ln / 2 + 1.5)]
            ys = [c[1] + a * n[1] + e * v[1] for a in (-3.4, 1.2) for e in (-ln / 2 - 1.5, ln / 2 + 1.5)]
            crop = None                                 # the gusset and what it meets, under the shelf: from version 65's shell
            for p in k.region(X, 'HOUSING_F_front', 'gus%+d%d' % (sx, i), (min(xs), max(xs), min(ys), max(ys), 160.0, 169.5), 'W'):
                t = X.cp(p)
                if crop is None:
                    crop = t
                else:
                    X.uni(crop, t)
            X.sec(crop, obox_w(X, (c[0] - n[0] * 1.3, c[1] - n[1] * 1.3, 164.75), n, v, 3.4, ln + 1.0, 9.5))
            X.move(crop, n[0] * GT, n[1] * GT, 0.0)
            X.sec(crop, obox_w(X, c, n, v, GT, ln, 9.5))                                                       # only the 0.6 beside the old face
            X.sec(crop, ref_w(X, (v[0] * 1.7, v[1] * 1.7, 0.0)))                                               # ends inside the wall
            v0 = X.vol(b); X.uni(b, crop); out.append(round(X.vol(b) - v0, 3))
    return out


def build_shell(X, stage):                              # three calls: 'fins', 'left', 'right'
    cp2 = sys.modules['cp2']
    if stage == 'fins':
        if 'shell_new' not in k.c:
            k.c['shell_new'], k.c['shell_rep'] = cp2.new_shell(X)                            # the four posts (cp2_posts.py)
        b = X.tbm.copy(k.c['shell_new']); r = shell_fins(X, b); k.c['shell_wip'] = b
        return r
    b = k.c['shell_wip']; r = shell_gussets(X, b, (1.0,) if stage == 'left' else (-1.0,))
    if stage == 'right':
        G['HOUSING_F_front'] = b
    return r


# ---------- door: vents (question 2 a = cp2.VENTS['b']) and the four bosses' buttresses ----------
DOOR = ((50.0, -67.0, 0.34, -0.94, 8.2), (-50.0, -67.0, -0.34, -0.94, 8.2), (19.0, -74.5, 0.0, -1.0, 7.9), (-19.0, -77.0, 0.0, -1.0, 5.4))


def build_door(X):
    cp2 = sys.modules['cp2']
    b = X.tbm.copy(k.c['door_b']) if 'door_b' in k.c else cp2.new_door(X, 'b')[0]             # the vents alone (cp2_vents.py): 47,034.26 mm3
    out = []
    for (bx, by, ux, uy, ln) in DOOR:
        m = math.hypot(ux, uy); ux /= m; uy /= m
        bt = obox_w(X, (bx + ux * ln / 2, by + uy * ln / 2, 6.65), (ux, uy, 0.0), (-uy, ux, 0.0), ln, 8.0, 7.7)   # as wide as the boss, z 2.8 .. 10.5
        v0 = X.vol(b); X.uni(b, bt)
        X.dif(b, X.cyl((bx, by, 2.7), (bx, by, 9.5), 2.0))                                                       # the insert hole as before
        out.append(round(X.vol(b) - v0, 3))
    G['HOUSING_F_door'] = b
    return out


# ---------- cap: 45 degree root flare 1.0 on its four bosses ----------
def build_cap(X):
    b = X.cp(X.body('HOUSING_F_cap')); v0 = X.vol(b)
    for (x, y) in ((43.36, -32.85), (-43.36, -32.85), (25.91, -37.80), (-25.91, -37.80)):
        X.uni(b, cone_w(X, (x, y, 176.5), 4.0, (x, y, 177.5), 5.0))
        X.dif(b, X.cyl((x, y, 172.5), (x, y, 178.5), 2.0))
    G['HOUSING_F_cap'] = b
    return round(X.vol(b) - v0, 3)


# ---------- base plate: Pi posts' root cones; the two posts under the inlet board's cradle joined, with cone roots ----------
def build_base(X):
    b = X.cp(X.body('FLOOR_PLATE')); out = []
    for (x, y) in ((-39.65, -54.5), (-39.65, -5.5), (18.35, -54.5), (18.35, -5.5)):
        v0 = X.vol(b); X.uni(b, cone_w(X, (x, y, 2.5), 4.8, (x, y, 3.5), 3.8))                # 45 degree flare 1.0 (5.3 came 0.05 from the Pi's power plug)
        X.dif(b, X.cyl((x, y, 1.5), (x, y, 8.1), 2.0)); out.append(round(X.vol(b) - v0, 3))
    v0 = X.vol(b)
    X.uni(b, X.wbox(-1.5, 6.5, -76.5, -72.5, 2.5, 12.5))                                    # joined behind their axes; the Pi's power lead lies 0.2 in front, as before
    for x in (-1.5, 6.5):
        c = cone_w(X, (x, -72.5, 2.5), 5.5, (x, -72.5, 8.5), 4.0)                            # 6.0 came 0.51 from the door
        X.sec(c, X.wbox(x - 4.0, x + 4.0, -90.0, -70.7, 0.0, 20.0))                          # growth to the rear only: the Pi's power lead's space lies in front and beside (0.2, as before)
        X.uni(b, c)
    for x in (-1.5, 6.5):
        X.dif(b, X.cyl((x, -72.5, 6.3), (x, -72.5, 13.1), 2.0))
    out.append(round(X.vol(b) - v0, 3))
    G['FLOOR_PLATE'] = b
    return out


# ---------- speaker boxes and touch clips ----------
YP = -6.95                                              # the touch clip's screw line: 0.85 back, 2.0 from the box's front face
YB = -10.2                                              # the block and the clip's lug end here: 2.0 behind the hole


def build_box(X, sx):
    name = 'SPKBOX_L' if sx > 0 else 'SPKBOX_R'
    b = X.cp(X.body(name)); out = {}
    v0 = X.vol(b); X.uni(b, X.cyl((sx * 52.75, -10.55, 10.25), (sx * 52.75, -9.7, 10.25), 1.3)); out['pilot tip filled'] = round(X.vol(b) - v0, 3)
    v0 = X.vol(b)
    X.uni(b, tube(X, (sx * 88.25, -11.5, 10.25), (sx * 88.25, -5.7, 10.25), 4.0, 3.74))       # the outer pair of driver columns 7.5 -> 8.0
    X.uni(b, tube(X, (sx * 88.25, -11.5, 45.75), (sx * 88.25, -3.0, 45.75), 4.0, 3.74))
    for (x, z) in ((52.75, 10.25), (52.75, 45.75), (88.25, 10.25)):                          # the bosses the driver's frame sits on, 0.7 proud of the face: 8.0 too
        X.uni(b, tube(X, (sx * x, -3.7, z), (sx * x, -3.0, z), 4.0, 3.74))
    out['driver columns 8.0'] = round(X.vol(b) - v0, 3)
    v0 = X.vol(b)
    xa, xb = sorted((sx * 43.5, sx * 50.5))
    X.uni(b, X.wbox(xa, xb, YB, -8.5, 30.0, 46.0))
    X.uni(b, X.cyl((sx * 43.5, -6.1, 38.0), (sx * 49.0, -6.1, 38.0), 1.3))
    X.dif(b, X.cyl((sx * 43.4, YP, 38.0), (sx * 49.0, YP, 38.0), 1.25))
    out['clip block'] = round(X.vol(b) - v0, 3)
    G[name] = b
    return out


def build_clip(X, sx):
    name = 'TOUCH_CLIP_L' if sx > 0 else 'TOUCH_CLIP_R'
    b = X.cp(X.body(name)); v0 = X.vol(b)
    xa, xb = sorted((sx * 40.5, sx * 43.5))
    X.uni(b, X.wbox(xa, xb, YB, -8.5, 30.0, 46.0))
    X.uni(b, X.cyl((sx * 40.5, -6.1, 38.0), (sx * 43.5, -6.1, 38.0), 1.75))
    X.dif(b, X.cyl((sx * 40.4, YP, 38.0), (sx * 43.6, YP, 38.0), 1.7))
    G[name] = b
    return round(X.vol(b) - v0, 3)


# ---------- carrier ----------
def axes_d(body, r):                                    # cylinders of radius r (mm) along the screen's normal: [(x, up)] in the slab frame
    out = set()
    for f in body.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and abs(g.radius * 10.0 - r) < 0.005 and abs(abs(g.axis.y) - 1.0) < 1e-4:
            out.add((round(g.origin.x * 10.0 - k.XC, 3), round(g.origin.z * 10.0, 3)))
    return sorted(out)


def build_carrier(X):
    b = X.cp(X.body('RESP_CARRIER')); out = {}
    posts = axes_d(b, 4.0); bosses = axes_d(b, 3.0); out['posts'] = posts; out['bosses'] = bosses
    slab = X.tbm.copy(b); X.sec(slab, X.dbox(-60.0, 60.0, 15.2, 17.2, -80.0, 20.0))
    prism = X.tbm.copy(slab)
    for i in range(1, 9):                               # the slab's outline as a prism to d 32.4
        t = X.tbm.copy(slab); X.move_n(t, -1.9 * i); X.uni(prism, t)
    v0 = X.vol(b)
    for (x, up) in posts:
        c = cone_d(X, x, up, 17.2, 6.0, 31.1, 4.0); X.sec(c, X.tbm.copy(prism))
        if up > -40.0 and x < -30.0:                    # the right microphone's lead passes 0.89 beside this post: no growth toward it
            X.sec(c, X.dbox(-80.0, x + 4.0, 17.0, 31.3, -80.0, 20.0))
        if up < -40.0:                                  # the two lower posts
            X.sec(c, X.dbox(x - 9.0, x + 9.0, 17.0, 31.3, -80.0, up + 4.0))    # 0.7 from the ReSpeaker's edge: no growth toward it
            X.uni(c, X.cyld(x, up, 4.0, 15.2, 31.1))    # whole again where the slab's bottom edge cut them (wall 1.70 -> 2.0), from the bed up
        X.uni(b, c)
        X.dif(b, X.cyld(x, up, 2.0, 24.4, 31.2))        # the insert hole as before
    out['posts added'] = round(X.vol(b) - v0, 3); v0 = X.vol(b)
    for (x, up) in bosses:
        X.uni(b, cone_d(X, x, up, 17.2, 4.0, 18.2, 3.0))
        X.dif(b, X.cyld(x, up, 0.8, 17.7, 22.3))
    out['bosses added'] = round(X.vol(b) - v0, 3)
    G['RESP_CARRIER'] = b
    return out


# ---------- cradle ----------
def build_cradle(X):
    b = X.cp(X.body('CRADLE_5807')); v0 = X.vol(b)
    X.uni(b, X.wbox(10.4, 10.55, -83.0, -79.3, 14.5, 17.0))                                 # wall round the right screw hole 1.95 -> 2.0; 0.35 to the grommet
    G['CRADLE_5807'] = b
    return round(X.vol(b) - v0, 3)


# ---------- what a new body adds and removes, and what the added plastic meets ----------
def delta(X, name, near=1.5, skip=()):
    new = G[name]; old = k.tcopy(X, name)
    add = X.tbm.copy(new); X.dif(add, old); rem = X.tbm.copy(old); X.dif(rem, new)
    va = X.vol(add) if add.faces.count else 0.0; vr = X.vol(rem) if rem.faces.count else 0.0
    res = {'old': round(X.vol(old), 2), 'new': round(X.vol(new), 2), 'added': round(va, 3), 'removed': round(vr, 3), 'lumps': new.lumps.count, 'faces': new.faces.count}
    hits = {}; close = {}
    if va > 1e-4:
        q = add.boundingBox; e = near / 10.0
        box = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e), k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
        for o in k.current(X, leads=True):
            if o.name == name or o.name in skip or not box.intersects(o.boundingBox):
                continue
            t = k.tcopy(X, o.name)
            d = X.mm.measureMinimumDistance(add, t).value * 10.0
            if d < 0.0005:
                hits[o.name] = round(X.xv(add, t), 3)
            elif d < near:
                close[o.name] = round(d, 2)
    return res, hits, close


def outside(X, name):                                   # what of a new body lies outside the cloth reference
    t = X.tbm.copy(G[name]); X.dif(t, X.tbm.copy(k.c['skin_ref']))
    return (round(X.vol(t), 3), [round(l.volume * 1000.0, 3) for l in t.lumps]) if t.faces.count else (0.0, [])
