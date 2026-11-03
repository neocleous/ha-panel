# rev F common header (2026-11-03). Pasted at the top of every v5f_b* script (the Fusion MCP runs single files).
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
