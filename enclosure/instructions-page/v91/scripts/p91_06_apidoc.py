# Read-only: write the API doc strings this session needs to a file.
import adsk.core, adsk.fusion, os

OUT = os.path.expanduser("~/Documents/HA_panel_renders/instructions_page_v91/out")

def run(_context: str):
    items = [
        ("Camera.viewExtents", adsk.core.Camera.viewExtents),
        ("Camera.perspectiveAngle", adsk.core.Camera.perspectiveAngle),
        ("Viewport.modelToViewSpace", adsk.core.Viewport.modelToViewSpace),
        ("Viewport.saveAsImageFileWithOptions", adsk.core.Viewport.saveAsImageFileWithOptions),
        ("SaveImageFileOptions", adsk.core.SaveImageFileOptions),
        ("CustomGraphicsGroup.addBRepBody", adsk.fusion.CustomGraphicsGroup.addBRepBody),
        ("CustomGraphicsBasicMaterialColorEffect.create", adsk.fusion.CustomGraphicsBasicMaterialColorEffect.create),
        ("CustomGraphicsSolidColorEffect.create", adsk.fusion.CustomGraphicsSolidColorEffect.create),
        ("Viewport.visualStyle", adsk.core.Viewport.visualStyle),
        ("VisualStyles", adsk.core.VisualStyles),
    ]
    L = []
    for n, o in items:
        L.append("== " + n)
        L.append(str(getattr(o, "__doc__", "")))
    L.append("== SaveImageFileOptions members")
    L.append(", ".join(m for m in dir(adsk.core.SaveImageFileOptions) if not m.startswith("_")))
    L.append("== VisualStyles members")
    L.append(", ".join(m for m in dir(adsk.core.VisualStyles) if not m.startswith("_")))
    open(os.path.join(OUT, "p91_06_apidoc.txt"), "w").write("\n".join(L) + "\n")
