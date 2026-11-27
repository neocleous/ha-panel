# Read-only preflight: version, counts and the 17 printed parts' volumes.
import adsk.core, adsk.fusion, os, datetime
OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")
_lines = []
def print(*a):
    _lines.append(" ".join(str(x) for x in a))


PRINTED = ["HOUSING_F_front", "HOUSING_F_plate", "SLAB_frame", "HOUSING_F_door",
           "FLOOR_PLATE", "SPKBOX_R", "SPKBOX_L", "RESP_CARRIER", "HOUSING_F_cap",
           "CRADLE_5807", "RADAR_HOLDER", "BME_HOOD", "GROMMET_usbc_F",
           "MIC_CLAMP_L", "MIC_CLAMP_R", "TOUCH_CLIP_L", "TOUCH_CLIP_R"]

def run(_context: str):
    os.makedirs(OUT, exist_ok=True)
    _lines.append("clock " + datetime.datetime.now().isoformat())
    main()
    open(os.path.join(OUT, "p91_00_preflight.txt"), "w").write("\n".join(_lines) + "\n")

def main():
    app = adsk.core.Application.get()
    doc = app.activeDocument
    des = adsk.fusion.Design.cast(app.activeProduct)
    df = doc.dataFile
    print("doc", doc.name, "modified", doc.isModified)
    print("version", df.versionNumber, "latest", df.latestVersionNumber, "desc", df.description)
    bodies = []
    for comp in des.allComponents:
        for b in comp.bRepBodies:
            bodies.append(b)
    print("components", des.allComponents.count, "bodies", len(bodies),
          "visible", sum(1 for b in bodies if b.isVisible))
    byname = {}
    for b in bodies:
        byname.setdefault(b.name, []).append(b)
    vh = adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy
    for n in PRINTED:
        bs = byname.get(n, [])
        if len(bs) != 1:
            print(n, "COUNT", len(bs))
            continue
        b = bs[0]
        v1 = b.volume * 1000.0
        v2 = b.getPhysicalProperties(vh).volume * 1000.0
        print("%s %.3f / %.3f lumps %d" % (n, v1, v2, b.lumps.count))
