# Read-only: list the visible bodies with their world boxes (mm), and the
# screen plate's and shell's face counts. Writes out/p91_01_bodies.txt.
import adsk.core, adsk.fusion, os, datetime

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")

def bb(b):
    x = b.boundingBox
    return "%.2f %.2f %.2f | %.2f %.2f %.2f" % (
        x.minPoint.x * 10, x.minPoint.y * 10, x.minPoint.z * 10,
        x.maxPoint.x * 10, x.maxPoint.y * 10, x.maxPoint.z * 10)

def run(_context: str):
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeProduct)
    root = des.rootComponent
    L = ["clock " + datetime.datetime.now().isoformat()]
    vis = [b for b in root.bRepBodies if b.isVisible]
    L.append("visible %d" % len(vis))
    for b in vis:
        L.append("V %s | faces %d | %s" % (b.name, b.faces.count, bb(b)))
    keys = ("LEAD", "SCREW", "MIC", "VEML", "LCD", "DISP", "MAIN", "TOUCH", "DRIVER",
            "DMA", "PI", "USB", "RIBBON", "KEEP", "ENV", "RESP", "LD2410", "BME", "INLET", "5807")
    for b in root.bRepBodies:
        if b.isVisible:
            continue
        n = b.name.upper()
        if "_V" in n and n.split("_V")[-1].isdigit():
            continue
        if any(k in n for k in keys):
            L.append("H %s | %s" % (b.name, bb(b)))
    open(os.path.join(OUT, "p91_01_bodies.txt"), "w").write("\n".join(L) + "\n")
