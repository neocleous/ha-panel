# rev F common header (2026-11-03). Pasted at the top of the v5f_b0/b1 scripts; the v5f_b1r scripts exec() a copy saved as
# ~/Documents/v5f_common.py instead (the Fusion MCP runs single files).
# Frames per enclosure/fusion/revE/README.md: design = Fusion native (Z up the 12 deg ramp, +Y toward the viewer, d = -Y);
# world: y_w = Y*C - Z*S, z_w = H + Y*S + Z*C. XC = -2.55. +x = viewer's LEFT. Units: mm in this code, cm in the API.
import adsk.core, adsk.fusion, json, math, os, time
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); T = math.tan(math.radians(12.0)); H = 143.3; XC = -2.55
LOG = os.path.expanduser('~/Documents/v5f_log.json')
P3 = adsk.core.Point3D.create
V3 = adsk.core.Vector3D.create
VI = adsk.core.ValueInput.createByReal
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
INS = (adsk.fusion.PointContainment.PointInsidePointContainment,)
UP = V3(0.0, S, C)                      # world +z in design coordinates
WY = V3(0.0, C, -S)                     # world +y in design coordinates


def log(script, step, data):
    arr = json.load(open(LOG)) if os.path.exists(LOG) else []
    arr.append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'script': script, 'step': step, 'data': data})
    json.dump(arr, open(LOG, 'w'), indent=1)


def Dw(x, y, z):                        # world mm -> design Point3D (cm)
    return P3(x / 10, (y * C + (z - H) * S) / 10, (-y * S + (z - H) * C) / 10)


def wz(p): return H + p.y * 10 * S + p.z * 10 * C
def wy(p): return p.y * 10 * C - p.z * 10 * S
def yfront(d, z): return -d / C - (z - H) * T


class Ctx:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.doc = self.app.activeDocument
        if self.doc.name != 'HA Panel v5 - tapered':
            raise RuntimeError('active document is %r' % self.doc.name)
        self.des = adsk.fusion.Design.cast(self.app.activeProduct)
        self.comp = self.des.rootComponent
        self.feats = self.comp.features
        self.tbm = adsk.fusion.TemporaryBRepManager.get()

    def body(self, name):
        for b in self.comp.bRepBodies:
            if b.name == name:
                return b

    def plane(self, name):
        for i in range(self.comp.constructionPlanes.count):
            p = self.comp.constructionPlanes.item(i)
            if p.name == name:
                return p

    def inside(self, b, x, y, z):
        return b.pointContainment(Dw(x, y, z)) in INS

    def interference(self, a, others):
        res = {}
        for o in others:
            if o is None:
                continue
            coll = adsk.core.ObjectCollection.create(); coll.add(a); coll.add(o)
            r = self.des.analyzeInterference(self.des.createInterferenceInput(coll))
            res[o.name] = round(sum(r.item(i).interferenceBody.volume for i in range(r.count)) * 1000, 2) if r else 0.0
        return res

    # --- TemporaryBRep solids in WORLD coordinates (mm) ---
    def wbox(self, x0, x1, y0, y1, z0, z1):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        c = Dw((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        obb = adsk.core.OrientedBoundingBox3D.create(c, V3(1, 0, 0), WY, (x1 - x0) / 10, (y1 - y0) / 10, (z1 - z0) / 10)
        return self.tbm.createBox(obb)

    def wcyl_z(self, x, y, r, z0, z1):     # vertical (world z) cylinder
        return self.tbm.createCylinderOrCone(Dw(x, y, z0), r / 10, Dw(x, y, z1), r / 10)

    def union(self, a, b):
        self.tbm.booleanOperation(a, b, adsk.fusion.BooleanTypes.UnionBooleanType); return a

    def diff(self, a, b):
        self.tbm.booleanOperation(a, b, adsk.fusion.BooleanTypes.DifferenceBooleanType); return a

    def add(self, tb, name):
        b = self.comp.bRepBodies.add(tb); b.name = name; return b

    def combine(self, target, tools, op=JOIN, keep=False):
        coll = adsk.core.ObjectCollection.create()
        for t in tools:
            coll.add(t)
        ci = self.feats.combineFeatures.createInput(target, coll); ci.operation = op; ci.isKeepToolBodies = keep
        return self.feats.combineFeatures.add(ci)


# --- door / ring outlines (added 2026-11-03 for the b1r scripts; same code as v5f_b1a_door.py, rev E p18 section_pts) ---
def section_pts(hw, dep, n, rc, N=241):
    ai = hw - rc; bi = dep - 2 * rc
    th = [math.pi * i / (N - 1) for i in range(N)]
    def sp(t):
        c = math.cos(t); s = math.sin(t)
        return (ai * (1 if c >= 0 else -1) * abs(c) ** (2.0 / n), -rc - bi * abs(s) ** (2.0 / n))
    P = [sp(t) for t in th]; Q = []
    for i in range(N):
        a = P[max(i - 1, 0)]; b = P[min(i + 1, N - 1)]; tu = b[0] - a[0]; tv = b[1] - a[1]; L = math.hypot(tu, tv) or 1e-9
        Q.append((P[i][0] + rc * (-tv / L), P[i][1] + rc * (tu / L)))
    Q[0] = (hw, -rc); Q[-1] = (-hw, -rc)
    tot = sum(math.hypot(Q[i + 1][0] - Q[i][0], Q[i + 1][1] - Q[i][1]) for i in range(N - 1)); dmin = max(3.0, tot / 64.0)
    inner = []; last = Q[0]; acc = 0.0
    for i in range(1, N - 1):
        acc += math.hypot(Q[i][0] - last[0], Q[i][1] - last[1]); last = Q[i]
        if acc >= dmin and math.hypot(Q[i][0] - Q[-1][0], Q[i][1] - Q[-1][1]) >= dmin:
            inner.append(Q[i]); acc = 0.0
    return ai, inner


def outline_body(X, OFF, z0, z1, name):
    """NEW body: the rev E outer generator's floor section (hw 100, back y -85, n 2.6, corner R12) offset OFF inward,
    cut at the chin line y = YC - OFF, front vertical corners R(12 - OFF), world z z0..z1. Returns (body, YC, rc)."""
    comp = X.comp; feats = X.feats
    fl = X.plane('FLOOR_plane')
    sb = X.body('SLAB_frame').boundingBox
    YBK = wy(P3(0, sb.minPoint.y, sb.minPoint.z)); YC = YBK - 0.5; YF = -sb.minPoint.z * 10 * S
    ZT = 180.0; PW = 2.2; PWW = 1.7; DTOP = 28.0; YTOP = yfront(13.0, ZT) - DTOP; HWT = 90.0
    hwE = lambda z: 100 - (100 - HWT) * (z / ZT) ** PWW
    ybE = lambda z: -85 + (YTOP + 85) * (z / ZT) ** PW
    nE = lambda z: 2.6 - 0.6 * (z / ZT)

    def sign_toward(sk, vec):
        n = sk.xDirection.crossProduct(sk.yDirection); return 1.0 if n.dotProduct(vec) > 0 else -1.0

    sk = comp.sketches.add(fl); sk.name = 'sk_' + name; sk.isLightBulbOn = False
    hw = hwE(0) - OFF; dep = (YF - ybE(0)) - 2 * OFF; n = nE(0); rc = 12.0 - OFF; yf = YF - OFF
    cu, mid = section_pts(hw, dep, n, rc)
    Q = lambda x, y: sk.modelToSketchSpace(Dw(x, y, 0.0))
    L = sk.sketchCurves.sketchLines; A = sk.sketchCurves.sketchArcs; k = math.sqrt(0.5)
    ln = L.addByTwoPoints(Q(XC - cu, yf), Q(XC + cu, yf)); ln.isFixed = True
    aR = A.addByThreePoints(ln.endSketchPoint, Q(XC + cu + rc * k, yf - rc + rc * k), Q(XC + hw, yf - rc)); aR.isFixed = True
    aL = A.addByThreePoints(Q(XC - hw, yf - rc), Q(XC - cu - rc * k, yf - rc + rc * k), ln.startSketchPoint); aL.isFixed = True
    cps = [aR.endSketchPoint, Q(XC + hw, yf - rc - 2.0)] + [Q(XC + u, yf + v) for (u, v) in mid] + [Q(XC - hw, yf - rc - 2.0), aL.startSketchPoint]
    sk.sketchCurves.sketchControlPointSplines.add(cps, adsk.fusion.SplineDegrees.SplineDegreeThree)
    pr = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda p: p.areaProperties().area)
    inp = feats.extrudeFeatures.createInput(pr, NEW); s = sign_toward(sk, UP)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s * z0 / 10)); inp.setDistanceExtent(False, VI(s * (z1 - z0) / 10))
    f = feats.extrudeFeatures.add(inp); body = f.bodies.item(0); body.name = name
    sk2 = comp.sketches.add(fl); sk2.name = 'sk_' + name + '_chin'; sk2.isLightBulbOn = False
    Q2 = lambda x, y: sk2.modelToSketchSpace(Dw(x, y, 0.0))
    sk2.sketchCurves.sketchLines.addTwoPointRectangle(Q2(-130.0, YC - OFF), Q2(130.0, 60.0))
    coll = adsk.core.ObjectCollection.create()
    for i in range(sk2.profiles.count):
        coll.add(sk2.profiles.item(i))
    ci = feats.extrudeFeatures.createInput(coll, CUT); s2 = sign_toward(sk2, UP)
    ci.startExtent = adsk.fusion.OffsetStartDefinition.create(VI(s2 * (z0 - 5.0) / 10)); ci.setDistanceExtent(False, VI(s2 * (z1 - z0 + 10.0) / 10))
    ci.participantBodies = [body]; feats.extrudeFeatures.add(ci)
    body = X.body(name)
    front = None
    for fc in body.faces:
        if fc.geometry.objectType.endswith('Plane') and abs(wy(fc.centroid) - (YC - OFF)) < 0.5:
            front = fc
    if front is None:
        raise RuntimeError('%s: chin face not found' % name)
    ec = adsk.core.ObjectCollection.create()
    for e in front.edges:
        if abs(wz(e.startVertex.geometry) - wz(e.endVertex.geometry)) > 0.5:
            ec.add(e)
    fi = feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(ec, VI(rc / 10), True)
    feats.filletFeatures.add(fi)
    return X.body(name), YC, rc
