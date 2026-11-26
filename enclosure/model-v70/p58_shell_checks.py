# Block 5: checks on the model after p57 (READ-ONLY for the model; temporary bodies 'TMP_*' added for distances, deleted again).
#   'fits'   bounded distances: the cap to the shell's bar (seam), the boxes' backs to the door frame, the clips to the dividers,
#            the dividers' tops to the screen plate; the frame stop on the way down (boxes b behind, lifted 0..25)
#   'walls'  the wall left behind the heads' relief (needles along +y to the outer skin); the band bar's section (needles along
#            y); the outer-skin check: what of the shell lies outside the cloth reference REF_F_outer, new and version 69
# Run: runpy.run_path(D + 'p58_shell_checks.py')['main'](stage)  -> p58_<stage>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
k_ = None


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), [round(v, 2) for v in k_.W(r.positionOne)], [round(v, 2) for v in k_.W(r.positionTwo)]


def ctmp(X, name, box):
    t = X.wbox(*box); X.sec(t, X.tbm.copy(X.body(name))); return X.add(t, 'TMP_c', show=False)


def fits(k, X):
    a = ctmp(X, 'HOUSING_F_cap', (-80, 80, -23.0, -22.5, 172, 180.5)); b = ctmp(X, 'HOUSING_F_front', (-80, 80, -22.5, -22.0, 172, 180.5))
    print('cap front face to the shell bar (seam): %s' % (dist(X, a, b),))
    sh = ctmp(X, 'HOUSING_F_front', (-100, 100, -55, -53.4, 0, 90))
    for n in ('SPKBOX_L', 'SPKBOX_R'):
        bb = ctmp(X, n, (-100, 100, -52.5, -51.5, 0, 90))
        print('%s back to the door frame: %s' % (n, dist(X, bb, sh)))
    for n in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
        print('%s to the shell: %s' % (n, dist(X, X.body(n), X.body('HOUSING_F_front'))))
    for sx in (1, -1):
        d = ctmp(X, 'HOUSING_F_front', sorted((sx * 45.0, sx * 47.2)) + [0.5, 4.5, 55, 67])
        print('divider top at x %+d to the screen plate: %s' % (sx * 46, dist(X, d, X.body('HOUSING_F_plate'))))
    # the frame stop on the way down
    crop = X.wbox(-100, 100, -58, -48, 0, 90); X.sec(crop, X.tbm.copy(X.body('HOUSING_F_front')))
    movers = []
    for n in ('SPKBOX_L', 'SPKBOX_R'):
        m = X.tbm.copy(X.body(n)); X.sec(m, X.wbox(-100, 100, -53, -47, -1, 90)); movers.append(m)
    for bb in (1.55, 1.6, 1.65):
        hit = []
        for h in [0, 1, 2, 4, 6, 8, 10, 15, 20, 25]:
            v = sum(X.xv(X.move(X.tbm.copy(m), 0, -bb, -h), crop) for m in movers)
            if v > 0.0005:
                hit.append((h, round(v, 3)))
        print('boxes %.2f behind: %s' % (bb, hit if hit else 'clear at lifts 0 to 25'))


def seam(k, X):
    for z0, z1 in ((178.5, 180.5), (177.6, 178.5)):
        a = ctmp(X, 'HOUSING_F_cap', (-80, 80, -23.0, -22.55, z0, z1)); b = ctmp(X, 'HOUSING_F_front', (-80, 80, -22.45, -22.0, z0, z1))
        print('cap front face to the shell bar, z %.1f..%.1f: %s' % (z0, z1, dist(X, a, b)))
    S = X.body('HOUSING_F_front')
    for f in S.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv); p = k.W(f.pointOnFace)
        if abs(abs(n[1]) - 1) < 1e-4 and any(abs(p[1] - y) < 0.002 for y in (-22.4, -53.6, 1.0)):
            print('   level in print: y %.4f (bed height %.4f), %.1f mm2, normal %+.0f, at %s' % (p[1], 6.7992 - p[1], f.area * 100, n[1], k.r2(p)))


def lip(k, X):
    S = X.body('HOUSING_F_front'); P = X.body('FLOOR_PLATE')
    cs = X.wbox(20, 40, -3, 8, 2, 6); X.sec(cs, X.tbm.copy(S))
    cp = X.wbox(20, 40, -3, 8, 2, 7); X.sec(cp, X.tbm.copy(P))
    for z in (3.4, 3.8, 4.0):
        print('   shell at x 30, z %.2f, along y: %s' % (z, [(round(-3 + a, 2), round(-3 + b, 2)) for a, b in k.needle_t(X, [cs], (30, -3, z), (30, 8, z), 0.02)]))
    for z in (4.4, 4.8, 5.2):
        print('   base plate at x 30, z %.2f, along y: %s' % (z, [(round(-3 + a, 2), round(-3 + b, 2)) for a, b in k.needle_t(X, [cp], (30, -3, z), (30, 8, z), 0.02)]))


def walls(k, X):
    S = X.body('HOUSING_F_front')
    c = X.wbox(85, 100, 0, 8, 2, 6); X.sec(c, X.tbm.copy(S))
    for x in (90.2, 90.6, 91.0):
        for z in (2.85, 3.0, 3.2):
            s = k.needle_t(X, [c], (x, 0.9, z), (x, 8.0, z), 0.02)
            print('   relief, x %.1f z %.2f, along +y from y 0.9: %s' % (x, z, s))
    c = X.wbox(-19, 19, -58, -44, 163.5, 171.5); X.sec(c, X.tbm.copy(S))
    for x in (0.0, 12.0, 17.5):
        rows = []
        for z in (165.5, 165.75, 166.0, 166.25, 166.5, 166.75, 166.95):
            s = k.needle_t(X, [c], (x, -57.0, z), (x, -45.0, z), 0.01)
            rows.append((z, [(round(-57 + a, 2), round(-57 + b, 2)) for a, b in s][:1]))
        print('   band bar at x %.1f (z, y from..to): %s' % (x, rows))
    ref = X.body('REF_F_outer')
    if ref is None:
        print('no REF_F_outer'); return
    for n in ('HOUSING_F_front', 'HOUSING_F_front_v69'):
        t = X.tbm.copy(X.body(n)); X.dif(t, X.tbm.copy(ref))
        print('%s outside the cloth reference: %.4f mm3, %d lump(s)' % (n, X.vol(t) if t.faces.count else 0.0, t.lumps.count if t.faces.count else 0))


def _main(stage):
    global k_
    k = L['load'](); X = k.K(); k_ = k; k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'fits': fits, 'walls': walls, 'seam': seam, 'lip': lip}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p58_%s.txt' % stage, _main, stage)
