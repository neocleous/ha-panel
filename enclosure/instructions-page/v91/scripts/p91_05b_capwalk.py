# Read-only walk of the cap's way up with the display module out.
# Temporary copies only; nothing is added to the design.
#
# The cap, with its two clamps, is stood on end: its long axis along a line
# leaning BETA degrees from the unit's up (world z) toward the door (-y), its
# depth across the unit (world x). It is pushed up along that line through the
# roof's middle bay. The line passes through (XB, YB, 36.0). S is the travel of
# the cap's centre along the line from that point.
# For each pose: the least distance to every obstacle with the module out
# (shell, screen plate, boxes and drivers, clips, holder, touch board, base
# plate, Pi, cradle, hood, ...). Negative = the two share volume.
# Writes out/p91_05_capwalk_<tag>.txt.
import adsk.core, adsk.fusion, os, math, time, datetime

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")
BETAS = [20.0, 25.0]
YBS = [-26.0]
XB = -2.55
SS = [-82.0, 0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 90.0]
TAG = "b20b25"
MOVING = ["HOUSING_F_cap", "MIC_CLAMP_L", "MIC_CLAMP_R"]
OBST = ["HOUSING_F_front", "HOUSING_F_plate", "SPKBOX_L", "SPKBOX_R", "SPK_L", "SPK_R",
        "TOUCH_CLIP_L", "TOUCH_CLIP_R", "RADAR_HOLDER", "TOUCH_PCB", "FLOOR_PLATE",
        "PI5_F", "PI5_F_cooler", "CRADLE_5807", "BME_HOOD", "GPIO_plugA_env",
        "GPIO_plugB_env", "DRV_screw_heads_env", "PD_5807_env", "GROMMET_usbc_F"]

def find(root, name):
    for b in root.bRepBodies:
        if b.name == name:
            return b
    raise Exception("no body " + name)

def boxes_near(a, b, margin):
    return not (a.maxPoint.x + margin < b.minPoint.x or b.maxPoint.x + margin < a.minPoint.x or
                a.maxPoint.y + margin < b.minPoint.y or b.maxPoint.y + margin < a.minPoint.y or
                a.maxPoint.z + margin < b.minPoint.z or b.maxPoint.z + margin < a.minPoint.z)

def run(_context: str):
    t0 = time.time()
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    tm = adsk.fusion.TemporaryBRepManager.get()
    mm = app.measureManager
    L = ["clock " + datetime.datetime.now().isoformat()]
    mov = [find(root, n) for n in MOVING]
    obs = [(n, find(root, n)) for n in OBST]
    bb = mov[0].boundingBox
    c0 = adsk.core.Point3D.create((bb.minPoint.x + bb.maxPoint.x) / 2,
                                  (bb.minPoint.y + bb.maxPoint.y) / 2,
                                  (bb.minPoint.z + bb.maxPoint.z) / 2)
    L.append("cap centre %.2f %.2f %.2f" % (c0.x * 10, c0.y * 10, c0.z * 10))
    for beta in BETAS:
        b = math.radians(beta)
        dup = adsk.core.Vector3D.create(0, math.sin(b), math.cos(b))
        e2 = adsk.core.Vector3D.create(1, 0, 0)
        e3 = dup.crossProduct(e2)
        for yb in YBS:
            for s in SS:
                # rotation: cap x -> dup, cap y -> world x, cap z -> e3, about c0;
                # then the centre to (XB, YB, 36) + s * dup
                m = adsk.core.Matrix3D.create()
                tgt = adsk.core.Point3D.create(XB / 10 + dup.x * s / 10,
                                               yb / 10 + dup.y * s / 10,
                                               3.6 + dup.z * s / 10)
                m.setToAlignCoordinateSystems(
                    c0, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                    adsk.core.Vector3D.create(0, 0, 1),
                    tgt, dup, e2, e3)
                parts = []
                for mb in mov:
                    t = tm.copy(mb)
                    tm.transform(t, m)
                    parts.append(t)
                worst = []
                for n, ob in obs:
                    dmin = None
                    for t in parts:
                        if not boxes_near(t.boundingBox, ob.boundingBox, 0.3):
                            continue
                        d = mm.measureMinimumDistance(t, ob).value * 10
                        if d < 0.001:
                            tt = tm.copy(t)
                            tm.booleanOperation(tt, tm.copy(ob), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                            v = tt.volume * 1000 if tt else 0.0
                            d = -v
                        dmin = d if dmin is None else min(dmin, d)
                    if dmin is not None and dmin < 3.0:
                        worst.append("%s %.2f" % (n, dmin))
                top = max(t.boundingBox.maxPoint.z for t in parts) * 10
                low = min(t.boundingBox.minPoint.z for t in parts) * 10
                L.append("beta %.0f yb %.1f s %.0f cap z %.1f..%.1f | %s" % (
                    beta, yb, s, low, top, "; ".join(worst) if worst else "clear (3.0+)"))
                if time.time() - t0 > 75:
                    L.append("STOPPED for time")
                    open(os.path.join(OUT, "p91_05_capwalk_%s.txt" % TAG), "w").write("\n".join(L) + "\n")
                    return
    L.append("seconds %.1f" % (time.time() - t0))
    open(os.path.join(OUT, "p91_05_capwalk_%s.txt" % TAG), "w").write("\n".join(L) + "\n")
