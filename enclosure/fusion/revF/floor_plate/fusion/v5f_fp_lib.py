# rev F floor plate pass - helpers for the modelling steps (block 2 on). exec()'d by the step scripts.
# World mm with x = x_rel (x_rel = design x - XC; +x = viewer's left), y + toward the viewer, z up from the floor.
# Slab frame: (x_rel, d, Zd) with d = -design Y (depth behind the glass front), Zd = design Z.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
FP = os.path.expanduser('~/Documents/HA_panel_renders/fp')
BT = adsk.fusion.BooleanTypes
P3 = adsk.core.Point3D.create
V3 = adsk.core.Vector3D.create


def Wp(xr, y, z):                       # world -> design point (cm)
    return P3((xr + XC) / 10.0, (y * C + (z - H) * S) / 10.0, (-y * S + (z - H) * C) / 10.0)


def Dp(xr, d, zd):                      # slab frame -> design point (cm)
    return P3((xr + XC) / 10.0, -d / 10.0, zd / 10.0)


def W(p):                               # design point -> world (x_rel, y, z)
    return (p.x * 10 - XC, (p.y * C - p.z * S) * 10, H + (p.y * S + p.z * C) * 10)


class K:
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.doc = [d for d in self.app.documents if d.name == 'HA Panel v5 - tapered'][0]
        self.des = adsk.fusion.Design.cast(self.doc.products.itemByProductType('DesignProductType'))
        self.root = self.des.rootComponent
        self.tbm = adsk.fusion.TemporaryBRepManager.get()

    def body(self, name):
        for b in self.root.bRepBodies:
            if b.name == name:
                return b
        return None

    def names(self):
        return [b.name for b in self.root.bRepBodies]

    # --- temporary solids ---
    def wbox(self, x0, x1, y0, y1, z0, z1):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        obb = adsk.core.OrientedBoundingBox3D.create(Wp((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0), V3(1, 0, 0), V3(0, C, -S),
                                                     (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
        return self.tbm.createBox(obb)

    def cylz(self, x, y, r, z0, z1, r1=None):                 # vertical; r1 = radius at z1 (cone)
        return self.tbm.createCylinderOrCone(Wp(x, y, z0), r / 10.0, Wp(x, y, z1), (r if r1 is None else r1) / 10.0)

    def cyly(self, x, z, r, y0, y1, r1=None):                 # along world y
        return self.tbm.createCylinderOrCone(Wp(x, y0, z), r / 10.0, Wp(x, y1, z), (r if r1 is None else r1) / 10.0)

    def dbox(self, x0, x1, d0, d1, z0, z1):                   # slab frame box
        x0, x1 = sorted((x0, x1)); d0, d1 = sorted((d0, d1)); z0, z1 = sorted((z0, z1))
        obb = adsk.core.OrientedBoundingBox3D.create(Dp((x0 + x1) / 2.0, (d0 + d1) / 2.0, (z0 + z1) / 2.0), V3(1, 0, 0), V3(0, 1, 0),
                                                     (x1 - x0) / 10.0, (d1 - d0) / 10.0, (z1 - z0) / 10.0)
        return self.tbm.createBox(obb)

    def cyld(self, x, zd, r, d0, d1, r1=None):                # along the slab normal
        return self.tbm.createCylinderOrCone(Dp(x, d0, zd), r / 10.0, Dp(x, d1, zd), (r if r1 is None else r1) / 10.0)

    def obz(self, x, y, r, travel, z0, z1):                   # vertical obround, travel along world y, centred on (x, y)
        t = self.cylz(x, y - travel / 2.0, r, z0, z1)
        self.uni(t, self.cylz(x, y + travel / 2.0, r, z0, z1))
        self.uni(t, self.wbox(x - r, x + r, y - travel / 2.0, y + travel / 2.0, z0, z1))
        return t

    def cp(self, b):
        return self.tbm.copy(b)

    def uni(self, a, b):
        self.tbm.booleanOperation(a, b, BT.UnionBooleanType); return a

    def dif(self, a, b):
        self.tbm.booleanOperation(a, b, BT.DifferenceBooleanType); return a

    def sec(self, a, b):
        self.tbm.booleanOperation(a, b, BT.IntersectionBooleanType); return a

    def move(self, tb, dx=0.0, dy=0.0, dz=0.0):               # world translation (mm)
        m = adsk.core.Matrix3D.create()
        m.translation = V3(dx / 10.0, (dy * C + dz * S) / 10.0, (-dy * S + dz * C) / 10.0)
        self.tbm.transform(tb, m); return tb

    def vol(self, tb):                                        # mm3
        try:
            return tb.volume * 1000.0
        except Exception:
            return 0.0

    def clash(self, a, b):                                    # mm3 of a copy of a intersected with a copy of b; -1 = boolean failed
        ba, bb = a.boundingBox, b.boundingBox
        if not ba.intersects(bb):
            return 0.0
        t = self.tbm.copy(a); u = self.tbm.copy(b)
        try:
            self.tbm.booleanOperation(t, u, BT.IntersectionBooleanType)
        except Exception:
            return -1.0
        return self.vol(t)

    def lumps(self, tb, maxv=400):                            # [[mm3, world bbox from vertices (None for big lumps: slow)], ...]
        out = []
        for l in tb.lumps:
            ws = [W(v.geometry) for v in l.vertices] if l.vertices.count <= maxv else []
            bb = [round(f(w[i] for w in ws), 1) for i in range(3) for f in (min, max)] if ws else None
            try:
                v = round(l.volume * 1000.0, 2)
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

    def retire(self, body, suffix='_v42'):
        body.name = body.name + suffix
        body.isLightBulbOn = False
        return body

    def dups(self):
        return sorted(n for n in self.names() if n.endswith(')') and not n.startswith(('LCD_', 'SPK_driver', 'TOOL_cap')))


def status(name, st):
    json.dump(st, open(os.path.join(FP, name + '_status.json'), 'w'), separators=(',', ':'))
