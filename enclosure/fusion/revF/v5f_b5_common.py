# rev F block 5 helpers (2026-11-05). exec() after ~/Documents/v5f_common.py; saved on the Mac as ~/Documents/v5f_b5_common.py.
#   World mm (x_rel = x - XC), design frame per v5f_common. Tools are the hidden TOOL_* bodies made by v5f_b5c1 / b5c2.
B = adsk.fusion.BooleanTypes
TOP_Z = 175.3            # top groove lower edge = top of the fabric zone (groove 175.3...176.8, hard band 3.2)
GROOVE_Z = (175.3, 176.8)
YJ_F, YJ_D = -55.0, -55.3  # R1 joint planes (front end face, door end face)
LD_F = (-72.5, -22.1, 127.5)  # LD2410C antenna face centre (x_rel, y, z), B3i
LD_A = 59.0                    # antenna normal angle from +y toward -x
# magnets (z, y on the lap) for D1 = 0.7: z 25 / 60 moved back so the thicker pads clear the boxes' insertion pose (rear
# face y -53.0), z 150 moved back so the door pocket (now from s 0.2) stays 0.86 inside the door's end face (y -55.3)
MAG_D1 = [(25.0, -59.7), (60.0, -59.5), (95.0, -59.0), (132.0, -58.0), (150.0, -57.5)]
MAG_R1 = {(1, 25.0): (74.16, (0.692, -0.719, 0.067)), (1, 60.0): (69.18, (0.637, -0.761, 0.124)),
          (1, 95.0): (59.82, (0.526, -0.829, 0.190)), (1, 132.0): (41.07, (0.316, -0.906, 0.281)),
          (1, 150.0): (23.58, (0.162, -0.930, 0.331)), (-1, 25.0): (-74.16, (-0.692, -0.719, 0.067)),
          (-1, 60.0): (-69.18, (-0.637, -0.761, 0.123)), (-1, 95.0): (-59.77, (-0.528, -0.828, 0.188)),
          (-1, 132.0): (-41.10, (-0.316, -0.906, 0.282)), (-1, 150.0): (-23.58, (-0.162, -0.930, 0.331))}
MAG_R1_Y = {25.0: -59.0, 60.0: -59.0, 95.0: -59.0, 132.0: -58.0, 150.0: -56.5}
LANES_UP = [((47.5, -17.80, 146.23), (47.5, -65.72, 110.12)), ((-47.5, -17.80, 146.23), (-47.5, -65.72, 110.12))]  # world x
LANES_LO = [((47.5, -3.66, 79.72), (47.5, -101.1, 102.21)), ((-47.5, -3.66, 79.72), (-47.5, -101.1, 102.21))]


def tb_copy(X, name):
    b = X.body(name)
    if b is None:
        raise RuntimeError('missing body %s' % name)
    return X.tbm.copy(b)


def inter(X, a, b):
    X.tbm.booleanOperation(a, b, B.IntersectionBooleanType); return a


def vol_x(X, a, b):
    q = X.tbm.copy(a); X.tbm.booleanOperation(q, X.tbm.copy(b), B.IntersectionBooleanType); return round(q.volume * 1000, 2)


def wv(v):                                   # world direction -> design Vector3D
    return V3(v[0], v[1] * C + v[2] * S, -v[1] * S + v[2] * C)


def nw_of(n):                                # design Vector3D -> world tuple
    return (n.x, n.y * C - n.z * S, n.y * S + n.z * C)


def lbox(X, c, a1, a2, l1, l2, l3):         # box centred at (x_rel, y, z), axes a1, a2 (world), lengths (mm)
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(XC + c[0], c[1], c[2]), wv(a1), wv(a2), l1 / 10, l2 / 10, l3 / 10))


def dbox(X, x0, x1, y0, y1, z0, z1):        # DESIGN-frame box: x absolute, Y = -d, Z along the ramp (mm)
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
        P3((x0 + x1) / 20, (y0 + y1) / 20, (z0 + z1) / 20), V3(1, 0, 0), V3(0, 1, 0), abs(x1 - x0) / 10, abs(y1 - y0) / 10, abs(z1 - z0) / 10))


def mvw(X, t, dx, dy, dz):                   # translate a TemporaryBRep body by a WORLD vector (mm)
    m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
    X.tbm.transform(t, m); return t


def wbb(X, body_or_tb):                      # tight world bbox [x_rel0, x_rel1, y0, y1, z0, z1]
    t = X.tbm.copy(body_or_tb)
    M = adsk.core.Matrix3D.create()
    M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)
    X.tbm.transform(t, M); bb = t.boundingBox
    return [bb.minPoint.x * 10 - XC, bb.maxPoint.x * 10 - XC, bb.minPoint.y * 10, bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10]


def wbox_rel(X, bb, m=0.0):                  # world box from a [x_rel0, x_rel1, y0, y1, z0, z1] list, grown by m
    return X.wbox(XC + bb[0] - m, XC + bb[1] + m, bb[2] - m, bb[3] + m, bb[4] - m, bb[5] + m)


def ray_hits(X, o_w, d_w, names):            # [(t_mm, body, x_rel, y, z, n_world, face)] sorted by distance
    o = Dw(*o_w); d = wv(d_w); d.normalize()
    hp = adsk.core.ObjectCollection.create()
    fs = X.comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
    res = []
    for i in range(fs.count):
        f = fs.item(i)
        if f.body.name in names:
            p = hp.item(i); t = math.sqrt((p.x - o.x) ** 2 + (p.y - o.y) ** 2 + (p.z - o.z) ** 2) * 10
            ok, n = f.evaluator.getNormalAtPoint(p)
            res.append((t, f.body.name, p.x * 10 - XC, wy(p), wz(p), nw_of(n), f, p))
    return sorted(res, key=lambda r: r[0])


def solid_runs(X, o_w, d_w, name, tmax=60.0):  # entry/exit distances of a body along a ray (pairs), from its face hits
    b = X.body(name)
    hs = [r for r in ray_hits(X, o_w, d_w, (name,)) if r[0] <= tmax]
    ts = sorted(set(round(r[0], 3) for r in hs))
    dn = math.sqrt(sum(c * c for c in d_w)); u = [c / dn for c in d_w]
    runs = []
    for i in range(len(ts) - 1):
        tm = (ts[i] + ts[i + 1]) / 2
        p = (o_w[0] + u[0] * tm, o_w[1] + u[1] * tm, o_w[2] + u[2] * tm)
        if b.pointContainment(Dw(*p)) in INS:
            runs.append([round(ts[i], 2), round(ts[i + 1], 2), round(ts[i + 1] - ts[i], 2)])
    return runs


def magnet_point(X, s, z, y):                # INNER_E surface point on the lap at (z, y), side s: ray from the centre plane
    hs = [r for r in ray_hits(X, (XC, y, z), (s, 0, 0), ('INNER_E',))]
    if not hs:
        raise RuntimeError('no INNER_E hit at %s' % ((s, z, y),))
    r = hs[0]
    p = r[7]; ok, n = r[6].evaluator.getNormalAtPoint(p); n.normalize()
    return p, n, r[2], tuple(round(c, 3) for c in nw_of(n))


def qpt(p, n, k):                            # point p + k * n (k in mm)
    return P3(p.x + n.x * k / 10, p.y + n.y * k / 10, p.z + n.z * k / 10)


def cyl_pn(X, p, n, k0, k1, r):              # cylinder along n from p + k0 n to p + k1 n, radius r (mm)
    return X.tbm.createCylinderOrCone(qpt(p, n, k0), r / 10, qpt(p, n, k1), r / 10)


def slot_in(X):                              # no D1 layer behind the slot face / boss (d < 15.6 above design Z -94.3)
    return dbox(X, -250, 250, -15.6, 60.0, -94.3, 260.0)


def slot_out(X):                             # no recess on the slot face / boss (d < 13.0 above the under-slab groove)
    return dbox(X, -250, 250, -13.0, 60.0, -93.43, 260.0)


def ld_excl(X):                              # LD2410C window (B5d: the layer stays > 4.0 from the antenna face, so unused)
    a = math.radians(LD_A); n = (-math.sin(a), math.cos(a), 0.0); t = (math.cos(a), math.sin(a), 0.0)
    c = (LD_F[0] + n[0] * 6.5, LD_F[1] + n[1] * 6.5, LD_F[2])
    return lbox(X, c, n, t, 15.0, 20.3, 26.3)


def veml_excl(X, m=0.5):
    cands = [b for b in X.comp.bRepBodies if b.name == 'VEML_env']
    if not cands:
        raise RuntimeError('VEML_env missing')
    return wbox_rel(X, wbb(X, cands[0]), m)


def build_layer(X, part, excl_ld=False, excl_veml=True):
    """D1 inner layer as a TemporaryBRep body for 'front' or 'door' (not added)."""
    L = tb_copy(X, 'TOOL_inner_skin_0p7'); inter(X, L, X.wbox(-250, 250, -250, 250, 2.5, TOP_Z))
    Lc = tb_copy(X, 'TOOL_outer_skin_3p2'); inter(X, Lc, X.wbox(-250, 250, -250, 250, 2.5, 6.2))
    X.diff(Lc, tb_copy(X, 'TOOL_floor_off6'))
    X.union(L, Lc)
    X.diff(L, slot_in(X))
    if excl_ld:
        X.diff(L, ld_excl(X))
    if excl_veml:
        X.diff(L, veml_excl(X))
    if part == 'front':
        inter(X, L, X.wbox(-250, 250, YJ_F, 250, 2.5, 260))
    else:
        inter(X, L, X.wbox(-250, 250, -250, YJ_D, 2.8, 260))
    return L
