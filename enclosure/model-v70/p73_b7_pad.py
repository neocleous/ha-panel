# Block 7, the hood's pad taken to the side plate: shared volume of the hood with every body near it, new (k.c['b7_hood'])
# and version 75's (BME_HOOD_v69); and the shell's nearest approach to the pad's level (bed 1.1..1.5). Read-only apart from
# TMP_ bodies, deleted again.
# Run: runpy.run_path(D + 'p73_b7_pad.py')['main']()  -> p73_pad.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
HN = (0.11394, 0.09756, 0.98869); HP0 = (-69.8829, -39.0603, 110.0342)
NEAR = ('HOUSING_F_front', 'FOAM_bme_env', 'FOAM_bme_top_env', 'BME680_env', 'LEAD_BME', 'SCREWS_hood_env', 'BME_pcb')


def near(a, b, m=0.05):
    return all(a.minPoint.asArray()[i] - m <= b.maxPoint.asArray()[i] and b.minPoint.asArray()[i] - m <= a.maxPoint.asArray()[i] for i in range(3))


def shared(X, a, b):
    t = X.tbm.copy(a); X.sec(t, X.tbm.copy(b))
    return round(X.vol(t), 3) if t.faces.count else 0.0


def _main(full=True):
    k = L['load'](); X = k.K(); k.budget(70)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'before', X.state())
    new = k.c['b7_hood']; old = X.tbm.copy(X.body('BME_HOOD_v69'))
    foam_new = k.c['b7_foamtop']; foam_old = X.tbm.copy(X.body('FOAM_bme_top_env_v69'))
    hb = new.boundingBox
    names = [b.name for b in X.root.bRepBodies if not b.name.endswith('_v69') and not b.name.startswith('TMP_')]
    for nm in (names if full else []):
        if nm in ('BME_HOOD',):
            continue
        b = X.body(nm)
        if b is None or not near(hb, b.boundingBox):
            continue
        o = X.tbm.copy(b) if nm != 'FOAM_bme_top_env' else None
        a1 = shared(X, old, o if o else foam_old); a2 = shared(X, new, o if o else foam_new)
        if a1 or a2:
            print('BME_HOOD | %-28s v75 %8.3f  new %8.3f' % (nm, a1, a2))
    # the shell within the pad's level band, nearest to the new hood
    n = k.unit(HN)
    sh = k.c.get('b7_shell') or X.tbm.copy(X.body('HOUSING_F_front'))
    for tag, hb_ in (('new', new), ('v75', old)):
        band(k, X, n, sh, hb_, tag)
    # what the new hood adds to version 75's (the pad and the offset slivers), each lump to the shell
    g = X.tbm.copy(new); X.dif(g, X.tbm.copy(old))
    G = X.add(g, 'TMP_g', show=False); S = X.add(X.tbm.copy(sh), 'TMP_sh', show=False)
    for lb in G.lumps:
        bb = lb.boundingBox
        best = None
        for sh_ in lb.shells:
            for f in sh_.faces:
                r = X.mm.measureMinimumDistance(f, S)
                if best is None or r.value < best.value:
                    best = r
        print('added lump %.3f mm3, box %s..%s: to the shell %.3f at %s' % (lb.volume * 1000, k.r2(k.W(bb.minPoint)), k.r2(k.W(bb.maxPoint)), best.value * 10, k.r2(k.W(best.positionOne))))
    G.deleteMe(); S.deleteMe()
    print(L['stamp'](), 'after', X.state())


def band(k, X, n, sh, hb_, tag):
    H = X.add(X.tbm.copy(hb_), 'TMP_h', show=False)
    for b0, b1 in ((1.0, 1.6), (0.0, 1.0)):
        # slab between bed b0 and b1, as a big oriented box
        u = k.unit((0.7593, 0.6497, -0.1517)); dd = sum(u[i] * n[i] for i in range(3)); u = k.unit(tuple(u[i] - dd * n[i] for i in range(3)))
        vv = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
        c = tuple(HP0[i] - 0.5 * (b0 + b1) * n[i] for i in range(3))
        slab = X.obox(c, u, vv, 40.0, 40.0, b1 - b0); X.sec(slab, X.tbm.copy(sh))
        if slab.faces.count:
            s = X.add(slab, 'TMP_s', show=False)
            r = X.mm.measureMinimumDistance(H, s)
            print('shell in bed %.1f..%.1f to the %s hood: %.3f at %s / %s' % (b0, b1, tag, r.value * 10, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))))
            s.deleteMe()
    H.deleteMe()


def main(full=True):
    L['out']('p73_pad%s.txt' % ('' if full else '_band'), _main, full)
