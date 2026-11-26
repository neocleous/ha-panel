# Block 9: inspection for the radar's holder. READ-ONLY (temporary bodies only).
#   bodies named for the radar; the radar's envelope's faces; the screws of SCREWS_M2x6_env near it (each lump's box and
#   volume); the radar's lead (faces, ends, length from volume); the left box near the clip block (needles); J5's plug.
# Run: runpy.run_path(D + 'p75_b9_inspect.py')['main']()  -> p75_b9_inspect.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    for b in X.root.bRepBodies:
        n = b.name
        if any(s in n.lower() for s in ('ld2410', 'radar', 'j5')):
            print('%-28s vis %-5s vol %10.3f lumps %d world box %s' % (n, b.isLightBulbOn, b.volume * 1000, b.lumps.count, [round(v, 2) for v in k.wbb(X, b)]))
    R = X.body('LD2410C_env_F')
    for f in R.faces:
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        print('  radar face %.1f mm2 n %s c %s' % (f.area * 100, k.r2(k.wv(nv)), k.r2(k.W(f.centroid))))
    S = X.body('SCREWS_M2x6_env')
    print('SCREWS_M2x6_env: %d lumps, %.3f' % (S.lumps.count, S.volume * 1000))
    rb = k.wbb(X, R)
    for i, lb in enumerate(S.lumps):
        t = X.tbm.copy(S)
        # each lump's world box from its own faces' points
        pts = []
        for sh in lb.shells:
            for f in sh.faces:
                pts.append(k.W(f.pointOnFace))
                for v in f.vertices:
                    pts.append(k.W(v.geometry))
        if not pts:
            continue
        lo = [min(p[j] for p in pts) for j in range(3)]; hi = [max(p[j] for p in pts) for j in range(3)]
        near = all(lo[j] < rb[2 * j + 1] + 6 and hi[j] > rb[2 * j] - 6 for j in range(3))
        if near:
            print('  lump %d near the radar: %.3f mm3, points box %s..%s' % (i, lb.volume * 1000, k.r2(lo), k.r2(hi)))
    ld = X.body('LEAD_RADAR')
    print('LEAD_RADAR: %.3f, faces %d, lumps %d' % (ld.volume * 1000, ld.faces.count, ld.lumps.count))
    for f in ld.faces:
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        print('  lead face %s %.2f mm2 n %s c %s' % (f.geometry.surfaceType, f.area * 100, k.r2(k.wv(nv)), k.r2(k.W(f.centroid))))
    B = X.tbm.copy(X.body('SPKBOX_L'))
    for z in (44.0, 46.0, 48.0, 50.0, 52.0, 55.0, 58.0, 61.0):
        print('left box at z %.1f, y -7.0, along x 38..56: %s' % (z, [(round(38 + a, 2), round(38 + q, 2)) for a, q in k.needle_t(X, [B], (38.0, -7.0, z), (56.0, -7.0, z), 0.02)]))
    for x in (44.0, 45.5, 46.5):
        print('left box at x %.1f, y -7.0, along z 20..80: %s' % (x, [(round(20 + a, 2), round(20 + q, 2)) for a, q in k.needle_t(X, [B], (x, -7.0, 20.0), (x, -7.0, 80.0), 0.02)]))
    for z in (50.0, 55.0, 60.0):
        print('left box at x 45.5, z %.1f, along y -20..2: %s' % (z, [(round(-20 + a, 2), round(-20 + q, 2)) for a, q in k.needle_t(X, [B], (45.5, -20.0, z), (45.5, 2.0, z), 0.02)]))
    for nm in ('MAIN_conn', 'MAIN_plug_env', 'MAIN_J2_plug_env', 'MAIN_pcb', 'LEAD_PI_POWER', 'LEAD_TOUCH', 'LEAD_GPIO_B', 'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_LCD_5V', 'LEAD_DSI', 'PI5_F', 'PI5_F_cooler', 'HOUSING_F_plate'):
        b = X.body(nm)
        if b is not None:
            print('%-18s world box %s' % (nm, [round(v, 2) for v in k.wbb(X, b)]))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p75_b9_inspect.txt', _main)
