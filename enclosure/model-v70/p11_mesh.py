# Block 1: triangle meshes of the unit's bodies, written to mesh/ in this folder, so that rays and pictures can be worked
# out outside Fusion. READ-ONLY: the mesh calculator reads the bodies; nothing is created in the document.
# Each body: mesh/<name>.f32 (node coordinates, design frame, cm, x y z per node) and mesh/<name>.i32 (three node indices per
# triangle); mesh/index.json lists every body done with its counts. The design frame is turned 12 deg about x from the world
# (v5f_k_lib: W()), so the reader turns the nodes into world mm.
# Run: runpy.run_path(D + 'p11_mesh.py')['main'](tol_cm) until it prints 'all done'.
import runpy, os, json, time, array
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
M = D + 'mesh/'


def main(tol_cm=0.01, budget=55.0, names=None):
    k = L['load']()
    X = k.K()
    t0 = time.time()
    if not os.path.isdir(M):
        os.mkdir(M)
    idx = json.load(open(M + 'index.json')) if os.path.exists(M + 'index.json') else {}
    todo = names or [b.name for b in k.current(X, leads=True)]
    for n in todo:
        if n in idx and idx[n].get('tol') == tol_cm:
            continue
        if time.time() - t0 > budget:
            break
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
    left = [n for n in todo if n not in idx or idx[n].get('tol') != tol_cm]
    print('%s: %d bodies meshed, %d left, %.1f s' % (L['stamp'](), len(todo) - len(left), len(left), time.time() - t0))
    if not left:
        print('all done: %d triangles' % sum(v['tris'] for q, v in idx.items() if q in todo))
