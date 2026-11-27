# Read-only: plane sections of the shell (temporary bodies, nothing added).
# YZ sections at x = 0, 12, -12 and XY sections at z = 30, 36, 42.
# Each section's edges are written as sampled points (mm, world frame) so
# the profile at the cap's middle bay and the door opening can be drawn.
# Writes out/p91_04_sections.json.
import adsk.core, adsk.fusion, os, json, time

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")

def find(root, name):
    for b in root.bRepBodies:
        if b.name == name:
            return b
    raise Exception("no body " + name)

def edges_pts(wire):
    res = []
    for body in [wire]:
        for e in body.edges:
            ev = e.evaluator
            ok, p0, p1 = ev.getParameterExtents()
            ok2, strokes = ev.getStrokes(p0, p1, 0.005)
            res.append([[round(p.x * 10, 2), round(p.y * 10, 2), round(p.z * 10, 2)] for p in strokes])
    return res

def run(_context: str):
    t0 = time.time()
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    tm = adsk.fusion.TemporaryBRepManager.get()
    names = ["HOUSING_F_front", "HOUSING_F_plate", "HOUSING_F_cap"]
    out = {}
    planes = []
    for x in (0.0, 12.0, -12.0):
        planes.append(("x%.0f" % x, adsk.core.Plane.create(adsk.core.Point3D.create(x / 10, 0, 0),
                                                            adsk.core.Vector3D.create(1, 0, 0))))
    for z in (30.0, 36.0, 42.0):
        planes.append(("z%.0f" % z, adsk.core.Plane.create(adsk.core.Point3D.create(0, 0, z / 10),
                                                            adsk.core.Vector3D.create(0, 0, 1))))
    for nm in names:
        b = find(root, nm)
        for key, pl in planes:
            try:
                w = tm.planeIntersection(b, pl)
            except RuntimeError as ex:
                out["%s|%s" % (nm, key)] = "no section: " + str(ex)[:60]
                continue
            out["%s|%s" % (nm, key)] = edges_pts(w) if w else []
    out["seconds"] = round(time.time() - t0, 1)
    open(os.path.join(OUT, "p91_04_sections.json"), "w").write(json.dumps(out))
