# rev F enclosure fix pass (2026-11-12) - library for the k scripts (brief claude/brief-enclosure-fix-pass-2026-11-12.md).
# Loaded from the repo's raw URL into sys.modules['v5f_k'] inside Fusion (see the loader at the end). Nothing is read from or
# written to the Mac's disk by this library: results are printed, temporary bodies and tables live in the dict c between calls.
# It is the frames and helpers of v5f_fp_lib / v5f_h_lib / v5f_j_lib and of the audit's aud2_lib in one file, without file access.
# World mm: x = x_rel (+x = viewer's left), y + toward the screen, z up from the plate's underside.
# Slab frame (x_rel, d, Zd): d = depth behind the glass. Board frame (u, v, w) of the site document.
# Keep these names free in step scripts: C, S, H, XC, U0, V0, D0, P3, V3, BT, K, W, Wp, Dp, Bp, c.
import adsk.core, adsk.fusion, math, re, sys, time, json, hashlib, urllib.request
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
U0, V0, D0 = 2.5, -27.45, 32.7
P3 = adsk.core.Point3D.create; V3 = adsk.core.Vector3D.create
BT = adsk.fusion.BooleanTypes
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType; PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
DOC = 'HA Panel v5 - tapered'
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
FDIR = 'enclosure/fusion/revF/floor_plate/fusion/'
BACK = re.compile(r'(_v\d+|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
NOTPART = ('REF_', 'TOOL_', 'INNER', 'RENDER_', 'AUD_')
BIG = ('HOUSING_F_front', 'HOUSING_F_door', 'FLOOR_PLATE', 'SLAB_frame')
PRINTED = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'FLOOR_PLATE', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'CRADLE_5807',
           'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'GROMMET_usbc_F']
c = {}                                   # results and temporary bodies, kept between connector calls
DEAD = [0.0]

# tools: [(diameter, length), ...] from the working end (the audit's shapes)
IRON = [(6.0, 10.0), (10.0, 65.0), (16.8, 98.0)]; IRONG = [(6.0, 10.0), (10.0, 65.0), (40.0, 98.0)]
KEY20 = [(2.4, 101.0), (34.4, 4.0)]; KEY20G = [(2.4, 101.0), (55.0, 4.0)]; KEY20L = [(2.4, 101.0)]
KEY25 = [(3.0, 112.0), (39.0, 4.0)]; KEY25G = [(3.0, 112.0), (60.0, 4.0)]; KEY25L = [(3.0, 112.0)]
MICRO = [(3.0, 60.0), (13.0, 97.0)]; MICROG = [(3.0, 60.0), (40.0, 97.0)]

# bodies present, by group (the audit's lists)
ST = {'SHELL': ['HOUSING_F_front'], 'PLATE': ['FLOOR_PLATE'], 'PI': ['PI5_F', 'PI5_F_cooler'], 'PIPWR': ['PIPWR_a_env'], 'CRADLE': ['CRADLE_5807'],
      'INLET': ['PD_5807_env'], 'BOXES': ['SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'DRV_screw_heads_env'],
      'TOUCH': ['TOUCH_PCB', 'TOUCH_components_env', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R'], 'DISP': ['SLAB_frame', 'LCD_*'],
      'RESP': ['RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env'],
      'MAIN': ['MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_conn', 'MAIN_tall', 'MAIN_low'], 'USBA': ['USBA_plug_env', 'USBA_cable_env'],
      'CAP': ['HOUSING_F_cap', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env'], 'PLUGS_PI': ['GPIO_plugA_env', 'GPIO_plugB_env'],
      'PLUGS_MB': ['MAIN_plug_env', 'MAIN_J2_plug_env'], 'RADAR': ['LD2410C_env_F'],
      'BME': ['BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'BME_HOOD'], 'DOOR': ['HOUSING_F_door', 'GROMMET_usbc_F'], 'FEET': ['FOOT_*']}
ST['UNIT'] = ST['PLATE'] + ST['PI'] + ST['PIPWR'] + ST['CRADLE'] + ST['INLET'] + ST['BOXES']
ST['MODULE'] = ST['DISP'] + ['RESP_CARRIER'] + ST['RESP'] + ST['MAIN']


# ---------- frames ----------
def Wp(x, y, z): return P3((x + XC) / 10.0, (y * C + (z - H) * S) / 10.0, (-y * S + (z - H) * C) / 10.0)      # world -> design point (cm)
def Dp(x, d, zd): return P3((x + XC) / 10.0, -d / 10.0, zd / 10.0)                                           # slab frame -> design
def Bp(u, v, w): return Dp(U0 + u, D0 + w, V0 + v)                                                           # board frame -> design
def W(p): return (p.x * 10 - XC, (p.y * C - p.z * S) * 10, H + (p.y * S + p.z * C) * 10)                      # design -> world
def Sf(p): return (p.x * 10 - XC, -p.y * 10, p.z * 10)                                                       # design -> slab frame
def Bf(p): return (p.x * 10 - XC - U0, p.z * 10 - V0, -p.y * 10 - D0)                                        # design -> board frame
def wv(v): return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)                                                # design vector -> world
def dv(w): return V3(w[0], w[1] * C + w[2] * S, -w[1] * S + w[2] * C)                                        # world direction -> design
def B2W(u, v, w): return W(Bp(u, v, w))
def W2B(x, y, z): return Bf(Wp(x, y, z))


def unit(u):
    n = math.sqrt(sum(q * q for q in u)); return tuple(q / n for q in u)


def tilt(d0, toward, deg):                                              # direction d0 turned by deg toward 'toward'
    d0 = unit(d0); t = unit(toward)
    k = sum(d0[i] * t[i] for i in range(3)); t = unit(tuple(t[i] - k * d0[i] for i in range(3)))
    ca = math.cos(math.radians(deg)); sa = math.sin(math.radians(deg))
    return tuple(d0[i] * ca + t[i] * sa for i in range(3))


def along(o, u, s): return (o[0] + u[0] * s, o[1] + u[1] * s, o[2] + u[2] * s)
def r2(q, n=2): return [round(v, n) for v in q]
def budget(sec): DEAD[0] = time.time() + sec
def late(): return bool(DEAD[0]) and time.time() > DEAD[0]


class K:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.doc = self.app.activeDocument
        if self.doc.name != DOC:
            raise RuntimeError('active document is %r' % self.doc.name)
        self.des = adsk.fusion.Design.cast(self.app.activeProduct)
        self.root = self.des.rootComponent
        self.tbm = adsk.fusion.TemporaryBRepManager.get()
        self.mm = self.app.measureManager

    def body(self, name): return self.root.bRepBodies.itemByName(name)
    def names(self): return [b.name for b in self.root.bRepBodies]

    def state(self):
        df = self.doc.dataFile; nm = self.names()
        return {'version': df.versionNumber, 'latest': df.latestVersionNumber, 'modified': self.doc.isModified, 'bodies': len(nm),
                'visible': sum(1 for b in self.root.bRepBodies if b.isLightBulbOn),
                'templates': [n for n in nm if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))], 'dups': self.dups()}

    # --- temporary solids (mm in, world unless said) ---
    def wbox(self, x0, x1, y0, y1, z0, z1):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        return self.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Wp((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), V3(1, 0, 0), V3(0, C, -S),
                                                                         (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0))

    def dbox(self, x0, x1, d0, d1, z0, z1):                               # slab frame
        x0, x1 = sorted((x0, x1)); d0, d1 = sorted((d0, d1)); z0, z1 = sorted((z0, z1))
        return self.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dp((x0 + x1) / 2.0, (d0 + d1) / 2.0, (z0 + z1) / 2.0), V3(1, 0, 0), V3(0, 1, 0),
                                                                         (x1 - x0) / 10.0, (d1 - d0) / 10.0, (z1 - z0) / 10.0))

    def bbox(self, u0, u1, v0, v1, w0, w1): return self.dbox(U0 + u0, U0 + u1, D0 + w0, D0 + w1, V0 + v0, V0 + v1)      # board frame

    def obox(self, cen, ax, ay, L, Wd, Ht):                               # world centre, world unit axes (length, width), sizes; height = ax x ay
        return self.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Wp(*cen), dv(unit(ax)), dv(unit(ay)), L / 10.0, Wd / 10.0, Ht / 10.0))

    def cyl(self, a, b, r, r1=None):                                      # between two world points
        return self.tbm.createCylinderOrCone(Wp(*a), r / 10.0, Wp(*b), (r if r1 is None else r1) / 10.0)

    def cylb(self, u, v, r, w0, w1):                                      # along the board normal
        return self.tbm.createCylinderOrCone(Bp(u, v, w0), r / 10.0, Bp(u, v, w1), r / 10.0)

    def cyld(self, x, zd, r, d0, d1):                                     # along the slab normal
        return self.tbm.createCylinderOrCone(Dp(x, d0, zd), r / 10.0, Dp(x, d1, zd), r / 10.0)

    def sph(self, a, r): return self.tbm.createSphere(Wp(*a), r / 10.0)
    def cp(self, b): return self.tbm.copy(b)

    def uni(self, a, b):
        self.tbm.booleanOperation(a, b, BT.UnionBooleanType); return a

    def dif(self, a, b):
        self.tbm.booleanOperation(a, b, BT.DifferenceBooleanType); return a

    def sec(self, a, b):
        self.tbm.booleanOperation(a, b, BT.IntersectionBooleanType); return a

    def move(self, tb, dx=0.0, dy=0.0, dz=0.0):                           # world translation
        m = adsk.core.Matrix3D.create()
        m.translation = V3(dx / 10.0, (dy * C + dz * S) / 10.0, (-dy * S + dz * C) / 10.0)
        self.tbm.transform(tb, m); return tb

    def move_n(self, tb, out):                                            # along the slab normal toward the viewer
        m = adsk.core.Matrix3D.create(); m.translation = V3(0, out / 10.0, 0)
        self.tbm.transform(tb, m); return tb

    def vol(self, tb):                                                    # mm3
        try:
            return tb.volume * 1000.0
        except Exception:
            return 0.0

    def xv(self, small, big):                                             # mm3 of small inside big; only a copy of small is changed
        if not small.boundingBox.intersects(big.boundingBox):
            return 0.0
        t = self.tbm.copy(small)
        try:
            self.tbm.booleanOperation(t, big, BT.IntersectionBooleanType)
        except Exception:
            return -1000.0
        return self.vol(t)

    def lumps(self, tb, maxv=600):                                        # [[mm3, world box from vertices], ...] largest first
        out = []
        for l in tb.lumps:
            ws = [W(v.geometry) for v in l.vertices] if l.vertices.count <= maxv else []
            bb = [round(f(w[i] for w in ws), 2) for i in range(3) for f in (min, max)] if ws else None
            try:
                v = round(l.volume * 1000.0, 3)
            except Exception:
                v = None
            out.append([v, bb])
        return sorted(out, key=lambda t: -(t[0] or 0))

    # --- model bodies ---
    def add(self, tb, name, like=None, show=True):
        b = self.root.bRepBodies.add(tb)
        b.name = name
        if like is not None:
            try:
                b.appearance = like.appearance
            except Exception:
                pass
            try:
                b.material = like.material
            except Exception:
                pass
        b.isLightBulbOn = show
        return b

    def retire(self, body, suffix):
        body.name = body.name + suffix
        body.isLightBulbOn = False
        return body

    def swap(self, name, tb, suffix, show=None):                          # old body -> name+suffix (hidden), temporary body -> name
        old = self.body(name)
        if self.body(name + suffix) is not None:
            raise RuntimeError('backup exists: ' + name + suffix)
        vis = old.isLightBulbOn if show is None else show
        self.retire(old, suffix)
        return self.add(tb, name, like=old, show=vis)

    def dups(self):
        return sorted(n for n in self.names() if n.endswith(')') and not n.startswith(('LCD_', 'SPK_driver', 'TOOL_cap')))

    def wipe(self, prefix='AUD_'):                                        # delete template bodies
        n = 0
        for b in [b for b in self.root.bRepBodies if b.name.startswith(prefix)]:
            b.deleteMe(); n += 1
        return n


def current(X, leads=False, kos=True):                                   # the bodies of the unit as it stands
    out = []
    for b in X.root.bRepBodies:
        n = b.name
        if n.startswith('LCD_'):
            if re.search(r'(_v\d+|_[a-e]\d+[a-z0-9]*)$', n):
                continue
            out.append(b); continue
        if BACK.search(n) or n in LEGACY or n.startswith(NOTPART):
            continue
        if n.startswith('LEAD_') and not leads:
            continue
        if n.startswith('KO_') and not kos:
            continue
        out.append(b)
    return out


def present(X, names):
    cur = {}
    for b in current(X, leads=True):
        cur.setdefault(b.name, b)
    out = []
    for n in names:
        if n.endswith('*'):
            out += [b for q, b in cur.items() if q.startswith(n[:-1])]
        elif n in cur:
            out.append(cur[n])
        elif X.body(n) is not None:
            out.append(X.body(n))
        else:
            raise RuntimeError('no body ' + n)
    return out


def st(X, *keys):
    names = []
    for q in keys:
        names += ST[q] if q in ST else [q]
    return present(X, names)


# ---------- cache of the enclosure chat (temporary copies, eight slabs per big body) ----------
def hc():
    m = sys.modules.get('v5f_h_cache')
    if m is None:
        m = type(sys)('v5f_h_cache'); m.c = {}; sys.modules['v5f_h_cache'] = m
    return m.c


def purge(prefixes):                                                    # drop cached copies, slabs and crops of bodies that changed or moved
    n = 0
    for d in (hc(), c):
        for q in list(d.keys()):
            if isinstance(q, tuple) and len(q) > 1 and str(q[1]).startswith(tuple(prefixes)):
                del d[q]; n += 1
    return n


def tcopy(X, name):                                                     # cached temporary copy, keyed by name and volume
    b = X.body(name)
    if b is None:
        raise RuntimeError('no body ' + name)
    q = ('tc', name, round(b.volume, 6)); h = hc()
    if q not in h:
        h[q] = X.tbm.copy(b)
    return h[q]


def tiles(X, name, n=8):                                                # a big body as eight slabs along its longest design axis; None if out of time
    b = X.body(name); v = round(b.volume, 6); h = hc()
    if not all(('tile', name, v, i) in h for i in range(n)):
        big = tcopy(X, name)
        bb = b.boundingBox; lo = [bb.minPoint.x, bb.minPoint.y, bb.minPoint.z]; hi = [bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z]
        ext = [hi[i] - lo[i] for i in range(3)]; ax = ext.index(max(ext))
        for i in range(n):
            q = ('tile', name, v, i)
            if q in h:
                continue
            if late():
                return None
            a = [w - 0.1 for w in lo]; e = [w + 0.1 for w in hi]
            if i > 0:
                a[ax] = lo[ax] + ext[ax] * i / n
            if i < n - 1:
                e[ax] = lo[ax] + ext[ax] * (i + 1) / n
            bx = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P3((a[0] + e[0]) / 2, (a[1] + e[1]) / 2, (a[2] + e[2]) / 2), V3(1, 0, 0), V3(0, 1, 0),
                                                                        e[0] - a[0], e[1] - a[1], e[2] - a[2]))
            X.tbm.booleanOperation(bx, big, BT.IntersectionBooleanType)
            h[q] = bx
    return [t for t in (h[('tile', name, v, i)] for i in range(n)) if t.faces.count > 0]


def parts(X, name):                                                     # a big body as its slabs, any other as one cached copy
    if name in BIG:
        t = tiles(X, name)
        if t is None:
            raise RuntimeError('slabs of %s not finished: call again' % name)
        return t
    return [tcopy(X, name)]


def region(X, name, key, box, frame='W'):                               # cached crop of a body to a world or slab-frame box: list of pieces
    q = ('region', name, key, round(X.body(name).volume, 6))
    if q in c:
        return c[q]
    bx = X.wbox(*box) if frame == 'W' else X.dbox(*box); out = []
    for p in parts(X, name):
        if not bx.boundingBox.intersects(p.boundingBox):
            continue
        t = X.tbm.copy(bx)
        X.tbm.booleanOperation(t, p, BT.IntersectionBooleanType)
        if X.vol(t) > 0.001:
            out.append(t)
    c[q] = out; return out


def xparts(X, tb, plist):                                               # mm3 of tb inside a list of temporary bodies
    return sum(X.xv(tb, p) for p in plist)


def xvol(X, tb, name): return xparts(X, tb, parts(X, name))


def clash(X, tb, names, eps=0.005):
    out = {}
    for n in names:
        v = xvol(X, tb, n)
        if abs(v) > eps:
            out[n] = round(v, 2)
    return out


def mcopy(X, name, d=(0.0, 0.0, 0.0)):                                  # a copy of a small model body moved by d (world)
    t = X.tbm.copy(tcopy(X, name))
    if d[0] or d[1] or d[2]:
        X.move(t, d[0], d[1], d[2])
    return t


def wbb(X, b):                                                          # world box of a body [x0, x1, y0, y1, z0, z1] from a copy turned into the world frame
    t = X.tbm.copy(b)
    m = adsk.core.Matrix3D.create()
    m.setWithArray([1, 0, 0, -XC / 10.0, 0, C, -S, 0, 0, S, C, H / 10.0, 0, 0, 0, 1])
    X.tbm.transform(t, m)
    q = t.boundingBox
    return [round(v * 10, 2) for v in (q.minPoint.x, q.maxPoint.x, q.minPoint.y, q.maxPoint.y, q.minPoint.z, q.maxPoint.z)]


def bbb(b):                                                             # board-frame box [u0, u1, v0, v1, w0, w1] (exact: the frame is parallel to the design's)
    q = b.boundingBox; a = Bf(q.minPoint); e = Bf(q.maxPoint)
    return [round(v, 2) for v in (a[0], e[0], a[1], e[1], e[2], a[2])]


def inside(b, p):                                                       # world point in or on a body
    return b.pointContainment(Wp(*p)) in (adsk.fusion.PointContainment.PointInsidePointContainment, adsk.fusion.PointContainment.PointOnPointContainment)


def dist(X, a, b): return X.mm.measureMinimumDistance(a, b).value * 10.0   # two model bodies, or a design point and a model body


def near(X, p, b):                                                      # distance from a world point to a model body, and the body's point
    r = X.mm.measureMinimumDistance(Wp(*p), b)
    a = W(r.positionOne); e = W(r.positionTwo)
    q = a if (abs(a[0] - p[0]) + abs(a[1] - p[1]) + abs(a[2] - p[2])) > (abs(e[0] - p[0]) + abs(e[1] - p[1]) + abs(e[2] - p[2])) else e
    return round(r.value * 10.0, 2), [round(v, 2) for v in q]


# ---------- sections ----------
def needle_t(X, plist, p0, p1, w=0.04):                                 # solid stretches (mm from p0) of a thin bar between two world points, in temporary bodies
    a = Wp(*p0); b = Wp(*p1)
    d = V3(b.x - a.x, b.y - a.y, b.z - a.z); L = d.length; d.normalize()
    ref = V3(0, 0, 1) if abs(d.z) < 0.9 else V3(1, 0, 0)
    wd = d.crossProduct(ref); wd.normalize()
    cen = P3((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0)
    out = []
    for prt in plist:
        nd = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(cen, d, wd, L, w / 10.0, w / 10.0))
        if not nd.boundingBox.intersects(prt.boundingBox):
            continue
        try:
            X.tbm.booleanOperation(nd, prt, BT.IntersectionBooleanType)
        except Exception:
            out.append([-1.0, -1.0]); continue
        for l in nd.lumps:
            ts = [((v.geometry.x - a.x) * d.x + (v.geometry.y - a.y) * d.y + (v.geometry.z - a.z) * d.z) * 10.0 for v in l.vertices]
            out.append([round(min(ts), 2), round(max(ts), 2)])
    out.sort(); mg = []
    for s in out:
        if mg and s[0] <= mg[-1][1] + 0.03:
            mg[-1][1] = max(mg[-1][1], s[1])
        else:
            mg.append(s)
    return mg


def needle(X, name, p0, p1, w=0.04): return needle_t(X, parts(X, name), p0, p1, w)


def ringfill(X, plist, a, b, r0, r1):                                   # share of a tube r0..r1 between two world points that is solid
    t = X.cyl(a, b, r1); X.dif(t, X.cyl(along(a, unit((a[0] - b[0], a[1] - b[1], a[2] - b[2])), 0.5), along(b, unit((b[0] - a[0], b[1] - a[1], b[2] - a[2])), 0.5), r0))
    v = X.vol(t)
    return xparts(X, t, plist) / v if v > 0 else 0.0


def faces(X, b, box, kinds=('p', 'c'), amin=0.5):                       # faces of a body with their sample point in a world box: planes and cylinders
    out = []
    for f in b.faces:
        g = f.geometry; t = g.surfaceType
        if t == PLN and 'p' not in kinds or t == CYL and 'c' not in kinds or t not in (PLN, CYL):
            continue
        p = W(f.pointOnFace)
        if not (box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]):
            continue
        ar = f.area * 100.0
        if ar < amin:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        ws = [W(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)] if ws else None
        if t == PLN:
            out.append(['p', r2(wv(nv), 3), r2(p), round(ar, 1), ext])
        else:
            out.append(['c', round(g.radius * 10.0, 3), r2(W(g.origin)), r2(unit(wv(g.axis)), 3), round(ar, 1), ext, 'pin' if sum((p[i] - W(g.origin)[i]) * wv(nv)[i] for i in range(3)) > 0 else 'hole'])
    return out


def holes_of(b, rmin=0.7, rmax=7.0):                                    # cylinder faces grouped per axis: k 'h' hole / 'p' pin, r, ends A and B (world), coverage
    groups = {}
    for f in b.faces:
        g = f.geometry
        if g.surfaceType != CYL:
            continue
        r = g.radius * 10.0
        if r < rmin or r > rmax:
            continue
        o = W(g.origin); a = unit(wv(g.axis))
        q = max(range(3), key=lambda i: abs(a[i]))
        if a[q] < 0:
            a = tuple(-w for w in a)
        p = f.pointOnFace
        ok, nv = f.evaluator.getNormalAtPoint(p)
        pw = W(p); nw = wv(nv)
        t = sum((pw[i] - o[i]) * a[i] for i in range(3))
        rad = tuple(pw[i] - (o[i] + t * a[i]) for i in range(3))
        kind = 'p' if sum(rad[i] * nw[i] for i in range(3)) > 0 else 'h'
        s = -o[q] / a[q]
        e = tuple(o[i] + s * a[i] for i in range(3))
        key = (kind, round(r, 2), tuple(round(w, 1) for w in e), tuple(round(w, 3) for w in a))
        ts = [sum((W(v.geometry)[i] - e[i]) * a[i] for i in range(3)) for v in f.vertices]
        gq = groups.setdefault(key, {'t': [], 'area': 0.0, 'q': e, 'a': a})
        gq['t'] += ts; gq['area'] += f.area * 100.0
    rows = []
    for (kind, r, qq, aa), gq in groups.items():
        if not gq['t']:
            continue
        t0, t1 = min(gq['t']), max(gq['t']); L = t1 - t0
        cov = gq['area'] / (2 * math.pi * r * L) if L > 0.05 else 0.0
        e = gq['q']; a = gq['a']
        rows.append({'k': kind, 'r': r, 'A': [round(e[i] + t0 * a[i], 2) for i in range(3)], 'B': [round(e[i] + t1 * a[i], 2) for i in range(3)],
                     'a': [round(w, 3) for w in a], 'L': round(L, 2), 'cov': round(cov, 2)})
    return rows


# ---------- a tool on its axis: stations, point-to-body distance less the tool's radius (model bodies only) ----------
def bbd(b):
    q = b.boundingBox; return (q.minPoint.x, q.minPoint.y, q.minPoint.z, q.maxPoint.x, q.maxPoint.y, q.maxPoint.z)


def pbox(p, q):
    dx = max(q[0] - p.x, 0.0, p.x - q[3]); dy = max(q[1] - p.y, 0.0, p.y - q[4]); dz = max(q[2] - p.z, 0.0, p.z - q[5])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def rad_at(secs, s):
    a = 0.0
    for dia, L in secs:
        if s <= a + L + 1e-6:
            return dia / 2.0
        a += L
    return secs[-1][0] / 2.0


def line(X, o, u, secs, bodies, st0=2.0, step=5.0, rng=12.0, head=7.0):
    u = unit(u); total = sum(L for d, L in secs)
    best = {}; hb = {}; free = None
    bx = [bbd(b) for b in bodies]
    s = st0
    while s <= total + 1e-6:
        if late():
            raise RuntimeError('time budget')
        r = rad_at(secs, s)
        p = Wp(o[0] + u[0] * s, o[1] + u[1] * s, o[2] + u[2] * s)
        for i, b in enumerate(bodies):
            if pbox(p, bx[i]) * 10.0 > r + rng:
                continue
            mg = X.mm.measureMinimumDistance(p, b).value * 10.0 - r
            tgt = hb if s <= head else best
            if b.name not in tgt or mg < tgt[b.name][0]:
                tgt[b.name] = (mg, s)
            if mg < 0 and free is None:
                free = s
        s += step
    rows = sorted([round(v[0], 2), round(v[1], 0), q] for q, v in best.items())
    hrows = sorted([round(v[0], 2), round(v[1], 0), q] for q, v in hb.items())
    return {'min': rows[0] if rows else None, 'rows': rows[:3], 'head': hrows[0] if hrows else None, 'free': 'free' if free is None else free}


def sn(n): return n.replace('HOUSING_F_', '').replace('_env', '')
def short(r): return '>12' if r['min'] is None else '%+.2f@%d %s' % (r['min'][0], r['min'][1], sn(r['min'][2]))
def fm(r): return 'head %s, beyond %s' % ('>12' if r['head'] is None else '%+.2f %s' % (r['head'][0], sn(r['head'][2])), short(r))


def probe(X, o, u, tool, hand, hard, leads=None, st0=2.0, step=5.0):
    out = 'tool: ' + fm(line(X, o, u, tool, hard, st0, step))
    if hand:
        out += ' | hand: ' + short(line(X, o, u, hand, hard, st0, step))
    if leads:
        out += ' | lead: ' + short(line(X, o, u, tool, leads, st0, step, head=0.0))
    return out


# ---------- pictures: the camera is set here, the picture is taken with the connector's screenshot query ----------
def show(X, names):                                                     # exactly these bodies visible; returns the names that were visible
    was = [b.name for b in X.root.bRepBodies if b.isLightBulbOn]
    want = set(names)
    for b in X.root.bRepBodies:
        on = b.name in want
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    return was


def cam(X, eye, tgt, ext=None, angle=None, up=(0, 0, 1)):               # world eye and target; ext = orthographic view extents, angle = perspective angle (rad)
    vp = X.app.activeViewport; q = vp.camera
    q.isSmoothTransition = False; q.isFitView = False
    q.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ext else adsk.core.CameraTypes.PerspectiveCameraType
    q.eye = Wp(*eye); q.target = Wp(*tgt); q.upVector = dv(unit(up))
    if angle:
        q.perspectiveAngle = angle
    vp.camera = q
    q = vp.camera; q.isSmoothTransition = False; q.isFitView = False
    if ext:
        q.viewExtents = ext
    vp.camera = q
    vp.refresh()


# ---------- step scripts from the repo ----------
def fetch(sha, name, h256=None):
    src = urllib.request.urlopen(RAW % (sha, FDIR + name), timeout=25).read()
    got = hashlib.sha256(src).hexdigest()
    if h256 and got != h256:
        raise RuntimeError('sha256 of %s is %s' % (name, got))
    return src.decode('utf-8')


def step(sha, name, h256=None, **G):                                    # exec a k script; it sees this module as k and the globals given
    ns = {'__name__': 'v5f_k_step', 'k': sys.modules['v5f_k']}; ns.update(G)
    exec(compile(fetch(sha, name, h256), name, 'exec'), ns)
    return ns


# loader, typed into every connector call (the connector runs run()):
#   import sys, types, urllib.request
#   def run(_context):
#       k = sys.modules.get('v5f_k')
#       if k is None:                      # first call of a session, or a new library version
#           src = urllib.request.urlopen(RAW % (sha, FDIR + 'v5f_k_lib.py')).read().decode('utf-8')
#           k = types.ModuleType('v5f_k'); exec(compile(src, 'v5f_k_lib.py', 'exec'), k.__dict__); sys.modules['v5f_k'] = k
#       X = k.K(); k.budget(50)
#       ...
