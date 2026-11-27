# Read-only: the lumps of the screw and lead bodies the pictures use (mm).
import adsk.core, adsk.fusion, os

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")
NAMES = ["DRV_screw_heads_env", "SCREWS_M2x6_env", "SPK_L", "SPK_R", "FOAM_spk_L_env",
         "FOAM_spk_R_env", "LEAD_SPK_L", "LEAD_SPK_R", "HOUSING_F_door", "TOUCH_PCB"]

def run(_context: str):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    L = []
    for b in root.bRepBodies:
        if b.name not in NAMES and not b.name.startswith("SCREWS"):
            continue
        L.append("== %s lumps %d visible %s" % (b.name, b.lumps.count, b.isVisible))
        for i in range(b.lumps.count):
            bb = b.lumps.item(i).boundingBox
            L.append("  %d  %.2f %.2f %.2f | %.2f %.2f %.2f" % (
                i, bb.minPoint.x * 10, bb.minPoint.y * 10, bb.minPoint.z * 10,
                bb.maxPoint.x * 10, bb.maxPoint.y * 10, bb.maxPoint.z * 10))
    open(os.path.join(OUT, "p91_07_lumps.txt"), "w").write("\n".join(L) + "\n")
