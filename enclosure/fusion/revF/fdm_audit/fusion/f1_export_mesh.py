# Design-for-FDM audit of version 66 -- the audit's own measurement meshes. READ-ONLY on the design.
# Writes raw number files (float32 x,y,z in mm, model coordinates; int32 triangle indices) -- not print files -- to
# ~/Documents/HA_panel_renders/fdm_audit/mesh/. Surface tolerance 0.005 mm.
import adsk.core, adsk.fusion, os, array, time
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fdm_audit/mesh')
NAMES = ['HOUSING_F_plate', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'RESP_CARRIER', 'CRADLE_5807',
         'HOUSING_F_door', 'HOUSING_F_cap', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SLAB_frame', 'GROMMET_usbc_F', 'BME_HOOD']

def run(_context: str):
    app = adsk.core.Application.get(); root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    os.makedirs(OUT, exist_ok=True)
    for nm in NAMES:
        b = root.bRepBodies.itemByName(nm)
        calc = b.meshManager.createMeshCalculator(); calc.surfaceTolerance = 0.0005     # cm
        m = calc.calculate()
        with open(os.path.join(OUT, nm + '.v.f32'), 'wb') as f:
            f.write(array.array('f', [c * 10.0 for c in m.nodeCoordinatesAsFloat]).tobytes())
        with open(os.path.join(OUT, nm + '.t.i32'), 'wb') as f:
            f.write(array.array('i', m.nodeIndices).tobytes())
        print(nm, m.nodeCount, m.triangleCount)
    print('modified', app.activeDocument.isModified)
