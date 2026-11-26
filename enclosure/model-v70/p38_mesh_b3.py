# Block 3: triangle meshes of the bodies block 3 changed, as p11_mesh.py does, written to mesh_b3/ (block 1's mesh/ of version
# 70 stays as it is, for the pictures of today). READ-ONLY.
# Run: runpy.run_path(D + 'p38_mesh_b3.py')['main']()  -> mesh_b3/<name>.f32 / .i32, mesh_b3/index.json
import runpy, os, json, array

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
M = D + 'mesh_b3/'
NAMES = ['GROMMET_usbc_F', 'HOUSING_F_door', 'FLOOR_PLATE', 'SCREWS_M2x6_env']


def main(tol_cm=0.01):
    k = L['load'](); X = k.K()
    if not os.path.isdir(M):
        os.mkdir(M)
    idx = {}
    for n in NAMES:
        b = X.body(n)
        mc = b.meshManager.createMeshCalculator()
        mc.surfaceTolerance = tol_cm
        tm = mc.calculate()
        xyz = array.array('f', tm.nodeCoordinatesAsFloat)
        ids = array.array('i', tm.nodeIndices)
        with open(M + n + '.f32', 'wb') as f:
            xyz.tofile(f)
        with open(M + n + '.i32', 'wb') as f:
            ids.tofile(f)
        idx[n] = {'nodes': len(xyz) // 3, 'tris': len(ids) // 3, 'tol': tol_cm, 'visible': b.isLightBulbOn}
    json.dump(idx, open(M + 'index.json', 'w'), indent=0)
    print(L['stamp'](), idx)
