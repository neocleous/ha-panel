# Read-only: the shell's faces at the two lower posts, and the screen plate's
# faces there, each with its box, type, area and least distance to the other
# part. Also the shell's faces at the two upper posts for comparison.
# Writes out/p91_03_lower_posts.txt.
import adsk.core, adsk.fusion, os, datetime, time

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")
CENTRES = {"lower_xpos": (82.45, -82.0), "lower_xneg": (-87.55, -82.0),
           "upper_xpos": (67.45, 27.0), "upper_xneg": (-72.55, 27.0)}

def find(root, name):
    for b in root.bRepBodies:
        if b.name == name:
            return b
    raise Exception("no body " + name)

def box(f):
    b = f.boundingBox
    return (b.minPoint.x * 10, b.minPoint.y * 10, b.minPoint.z * 10,
            b.maxPoint.x * 10, b.maxPoint.y * 10, b.maxPoint.z * 10)

def near(bx, c, r):
    cx = (bx[0] + bx[3]) / 2
    cz = (bx[2] + bx[5]) / 2
    return abs(cx - c[0]) < r and abs(cz - c[1]) < r and bx[1] > -16.0 and bx[4] < -8.0

def run(_context: str):
    t0 = time.time()
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    mm = app.measureManager
    plate = find(root, "HOUSING_F_plate")
    shell = find(root, "HOUSING_F_front")
    L = ["clock " + datetime.datetime.now().isoformat()]
    for key, c in CENTRES.items():
        L.append("== %s centre x %.2f z %.2f" % (key, c[0], c[1]))
        for name, body, other in (("shell", shell, plate), ("plate", plate, shell)):
            for i in range(body.faces.count):
                f = body.faces.item(i)
                bx = box(f)
                if not near(bx, c, 9.0):
                    continue
                d = mm.measureMinimumDistance(f, other).value * 10
                p = f.pointOnFace
                ok, n = f.evaluator.getNormalAtPoint(p)
                L.append("%s f%d %s area %.2f d %.3f box %s n %s" % (
                    name, i, f.geometry.objectType.split("::")[-1], f.area * 100, d,
                    tuple(round(v, 2) for v in bx), tuple(round(v, 2) for v in n.asArray())))
            if time.time() - t0 > 70:
                L.append("STOPPED for time")
                break
    L.append("seconds %.1f" % (time.time() - t0))
    open(os.path.join(OUT, "p91_03_lower_posts.txt"), "w").write("\n".join(L) + "\n")
