# change2/cp2_posts.py - the four screen-plate posts (D204, D207, D208) and the plate's border (D205), built on temporary copies.
# Exec'd into sys.modules['cp2'] (after cp2_lib.py). k = cp2k (v5f_k_lib.py). Slab frame (x, d, up); sx = +1 left-speaker side, -1 right.
TOP = (70.0, 27.0); BOT = (85.0, -82.0)               # post axes (|x|, up)
HA = 15.0                                              # the cones' half-angle, degrees
N_TOP = (0.582, 0.695, 0.423)                          # outward normal of the skin behind a top post (slab x, d, up), left side
N_BOT = (0.859, -0.507, -0.066)                        # outward normal of the side wall beside a bottom post, left side
Y_REAR = -2.6                                          # bottom posts end on this world-y plane: 1.1 in front of the boxes' front face (y -3.7)
Y_STRUT = 1.0                                          # the struts end here: 1.0 in front of the driver flanges
U_LOW = -88.2                                          # below this height the whole post keeps in front of Y_STRUT


def ref_in(X, n, s, sx):                               # the cloth reference moved s inward along a slab-frame normal (mirrored for sx = -1)
    t = X.tbm.copy(k.c['skin_ref'])
    m = adsk.core.Matrix3D.create(); m.translation = k.V3(-sx * n[0] * s / 10.0, n[1] * s / 10.0, -n[2] * s / 10.0)
    X.tbm.transform(t, m); return t


def cone(X, x, up, d0, r0, d1, ha):
    return X.tbm.createCylinderOrCone(k.Dp(x, d0, up), r0 / 10.0, k.Dp(x, d1, up), (r0 + (d1 - d0) * math.tan(math.radians(ha))) / 10.0)


def ybox(X, y0, y1):                                   # everything between two world-y planes
    return X.wbox(-150.0, 150.0, y0, y1, -50.0, 250.0)


def top_post(X, sx, fins=True):
    x0 = sx * TOP[0]; u0 = TOP[1]
    t = cone(X, x0, u0, 12.8, 4.5, 44.0, HA)
    if fins:
        w = cone(X, x0, u0, 13.8, 4.5, 44.0, 27.0)     # the gussets' free edges lie on this wider cone
        xa, xb = sorted((x0, x0 - sx * 30.0))
        fa = X.tbm.copy(w); X.sec(fa, X.dbox(xa, xb, 13.8, 44.0, u0 - 1.3, u0 + 1.3))       # toward the middle, 2.6 thick
        fb = X.tbm.copy(w); X.sec(fb, X.dbox(x0 - 1.3, x0 + 1.3, 13.8, 44.0, u0 - 30.0, u0))  # downward, 2.6 thick
        X.uni(t, fa); X.uni(t, fb)
    X.sec(t, ref_in(X, N_TOP, 1.7, sx))                # ends in the middle of the wall
    return t


def bot_post(X, sx):
    x0 = sx * BOT[0]; u0 = BOT[1]
    t = cone(X, x0, u0, 12.8, 5.5, 23.0, HA)
    xa, xb = sorted((x0, x0 + sx * 12.0))
    bt = X.dbox(xa, xb, 13.0, 23.0, u0 - 5.5, u0 + 5.5)                                   # buttress to the side wall, as tall as the land
    X.sec(bt, ref_in(X, N_BOT, 1.7, sx))                                                  # ends in the middle of the wall
    X.uni(t, bt)
    X.sec(t, ybox(X, Y_REAR, 60.0))
    low = X.dbox(x0 - 20.0, x0 + 20.0, 12.0, 30.0, -100.0, U_LOW); X.sec(low, ybox(X, -60.0, Y_STRUT)); X.dif(t, low)   # clear of the driver's flange
    s = X.dbox(x0 - 2.6, x0 + 2.6, 13.0, 23.0, -91.3, u0)                                 # strut down onto the chin block, 5.2 wide
    X.sec(s, ybox(X, Y_STRUT, 60.0))
    X.uni(t, s)
    X.uni(t, X.cyld(x0, u0, 4.0, 11.6, 12.8))                                             # peg 8.0 x 1.2
    return t


def new_shell(X, src='HOUSING_F_front', old='HOUSING_F_front_v63', fins=True):
    b = X.cp(X.body(src)); v63 = k.tcopy(X, old); rep = {}
    for sx in (1.0, -1.0):
        x0 = sx * TOP[0]
        xa, xb = sorted((x0 - sx * 8.0, x0 + sx * 9.0))
        B = X.dbox(xa, xb, 19.5, 31.0, 19.0, 34.0)     # the corner wall behind a top post as it was before the split (no column)
        o = X.tbm.copy(v63); X.sec(o, B)
        v0 = X.vol(b); X.dif(b, B); v1 = X.vol(b); X.uni(b, o); v2 = X.vol(b)
        rep[('top', sx)] = (round(v0 - v1, 3), round(v2 - v1, 3))
        X.uni(b, top_post(X, sx, fins))
        xb0 = sx * BOT[0]
        c = X.cyld(xb0, BOT[1], 4.6, 12.0, 21.0); X.sec(c, ybox(X, -60.0, Y_REAR)); X.dif(b, c)   # the old column behind the new rear plane
        X.uni(b, bot_post(X, sx))
    for sx in (1.0, -1.0):
        X.dif(b, X.cyld(sx * TOP[0], TOP[1], 2.0, 12.3, 12.8 + 6.35))
        X.dif(b, X.cyld(sx * BOT[0], BOT[1], 2.0, 11.1, 11.6 + 6.35))
    return b, rep


def island(X, d_sec=12.6):                             # a prism of the cloth reference's outline at depth d_sec, spanning d 11.9 .. 13.1
    sl = X.tbm.copy(k.c['skin_ref']); X.sec(sl, X.dbox(-120.0, 120.0, d_sec, d_sec + 0.02, -150.0, 60.0))
    mt = adsk.core.Matrix3D.create(); y0 = -d_sec / 10.0
    mt.setWithArray([1, 0, 0, 0, 0, 60.0, 0, y0 - 60.0 * y0, 0, 0, 1, 0, 0, 0, 0, 1])
    X.tbm.transform(sl, mt); X.move_n(sl, d_sec - 11.9)
    return sl


def new_plate(X, src='HOUSING_F_plate', step=True, d_sec=12.6):
    b = X.cp(X.body(src))
    if step:                                           # D205: the border's back at d 12.0 outside the island
        K = X.dbox(-120.0, 120.0, 12.0, 12.9, -150.0, 60.0); X.dif(K, island(X, d_sec)); X.dif(b, K)
    cut = X.cyld(BOT[0], BOT[1], 4.125, 11.4, 14.0)                                        # pocket 8.25 (left) and slot 8.25 x 9.75 (right)
    X.uni(cut, X.dbox(-BOT[0] - 4.875, -BOT[0] + 4.875, 11.4, 14.0, BOT[1] - 4.125, BOT[1] + 4.125))
    X.dif(b, cut)
    return b
