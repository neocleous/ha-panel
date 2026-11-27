# Read-only: what the screen plate rests on. For every face of the screen
# plate, the least distance to the shell and to the slab, with the face's
# type, area, a point on it and its normal at that point (mm, world frame).
# Writes out/p91_02_plate_rest.txt.
import adsk.core, adsk.fusion, os, datetime, time

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")

def find(root, name):
    for b in root.bRepBodies:
        if b.name == name:
            return b
    raise Exception("no body " + name)

def run(_context: str):
    t0 = time.time()
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    mm = app.measureManager
    plate = find(root, "HOUSING_F_plate")
    shell = find(root, "HOUSING_F_front")
    L = ["clock " + datetime.datetime.now().isoformat()]
    r = mm.measureMinimumDistance(plate, shell)
    L.append("plate-shell min %.4f at %s / %s" % (
        r.value * 10, tuple(round(v * 10, 2) for v in r.positionOne.asArray()),
        tuple(round(v * 10, 2) for v in r.positionTwo.asArray())))
    rows = []
    for i in range(plate.faces.count):
        f = plate.faces.item(i)
        d = mm.measureMinimumDistance(f, shell)
        p = f.pointOnFace
        ok, n = f.evaluator.getNormalAtPoint(p)
        rows.append((d.value * 10, i, f.geometry.objectType.split("::")[-1], f.area * 100,
                     tuple(round(v * 10, 2) for v in p.asArray()),
                     tuple(round(v, 3) for v in n.asArray()),
                     tuple(round(v * 10, 2) for v in d.positionTwo.asArray())))
        if time.time() - t0 > 60:
            L.append("STOPPED at face %d for time" % i)
            break
    rows.sort()
    for row in rows:
        L.append("d %.3f face %d %s area %.2f pt %s n %s shellpt %s" % row)
    L.append("seconds %.1f" % (time.time() - t0))
    open(os.path.join(OUT, "p91_02_plate_rest.txt"), "w").write("\n".join(L) + "\n")
