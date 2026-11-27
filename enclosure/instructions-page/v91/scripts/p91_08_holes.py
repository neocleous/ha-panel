# Read-only: the round holes and bosses of the 17 printed parts, for placing
# the marks in the pictures. Every cylindrical face of radius 0.7 to 4.3 mm,
# with its radius, axis, and the centre and size of its box (mm, world frame).
# Writes out/p91_08_holes.json.
import adsk.core, adsk.fusion, os, json, time

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")
PRINTED = ["HOUSING_F_front", "HOUSING_F_plate", "SLAB_frame", "HOUSING_F_door",
           "FLOOR_PLATE", "SPKBOX_R", "SPKBOX_L", "RESP_CARRIER", "HOUSING_F_cap",
           "CRADLE_5807", "RADAR_HOLDER", "BME_HOOD", "GROMMET_usbc_F",
           "MIC_CLAMP_L", "MIC_CLAMP_R", "TOUCH_CLIP_L", "TOUCH_CLIP_R"]

def run(_context: str):
    t0 = time.time()
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    bodies = {b.name: b for b in root.bRepBodies}
    out = {}
    for n in PRINTED:
        rows = []
        for f in bodies[n].faces:
            g = f.geometry
            if g.objectType != adsk.core.Cylinder.classType():
                continue
            r = g.radius * 10
            if r < 0.7 or r > 4.3:
                continue
            bb = f.boundingBox
            c = [(bb.minPoint.x + bb.maxPoint.x) * 5, (bb.minPoint.y + bb.maxPoint.y) * 5,
                 (bb.minPoint.z + bb.maxPoint.z) * 5]
            s = [(bb.maxPoint.x - bb.minPoint.x) * 10, (bb.maxPoint.y - bb.minPoint.y) * 10,
                 (bb.maxPoint.z - bb.minPoint.z) * 10]
            ax = [g.axis.x, g.axis.y, g.axis.z]
            rows.append([round(r, 3), [round(v, 2) for v in c], [round(v, 3) for v in ax],
                         [round(v, 2) for v in s], round(f.area * 100, 2)])
        out[n] = rows
    out["seconds"] = round(time.time() - t0, 1)
    open(os.path.join(OUT, "p91_08_holes.json"), "w").write(json.dumps(out))
