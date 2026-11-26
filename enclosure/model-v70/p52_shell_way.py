# Block 5, AA-A3: the shell's way down over the plate unit, as the last pass's k4a way_in walks it (the plate unit lifted in
# from below, b behind its place, against the shell, the radar board and the BME680's parts). READ-ONLY (temporary bodies only).
#   'heads'  the driver screw heads' envelope (DRV_screw_heads_env) as lumps with their world boxes
#   'way'    way_in at the given b values over the record's lifts; call again until nothing is left; then a summary per b:
#            which unit bodies meet what, and at which lifts
#   'where'  for one b, the overlap of each unit body with the shell at each lift where it meets it, as lumps with world boxes
# Run: runpy.run_path(D + 'p52_shell_way.py')['main']('way', tag='b4', bs=(...))  -> p52_<stage>_<tag>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
GROUPS = ('SHELL', 'PLATE', 'PI', 'PIPWR', 'CRADLE', 'INLET', 'BOXES', 'USBA', 'TOUCH', 'RADAR', 'BME', 'DISP', 'RESP', 'MAIN', 'UNIT', 'MODULE')


def present_only(k, X):
    keep = {}
    for g in GROUPS:
        keep[g] = list(k.ST[g])
        k.ST[g] = [n for n in k.ST[g] if n.endswith('*') or X.body(n) is not None]
    return keep


def restore(k, keep):
    for g, v in keep.items():
        k.ST[g] = v


def heads(k, X):
    b = X.body('DRV_screw_heads_env')
    print('DRV_screw_heads_env: %d lumps' % b.lumps.count)
    for r in X.lumps(X.tbm.copy(b)):
        print('   ', r)


def way(k, X, tag, bs):
    k.budget(66)
    keep = present_only(k, X)
    try:
        res, left = k.K4NS['way_in'](X, tag, behind=tuple(bs))
    finally:
        restore(k, keep)
    print('way_in %s: positions %d, left %d' % (tag, len(res), left))
    if left:
        return
    for b in bs:
        hits = {}
        for (n, i, bb, h), v in res.items():
            if bb != b or not v:
                continue
            for f, vol in v.items():
                hits.setdefault((n, i, f), []).append((h, vol))
        print('b %.2f: %s' % (b, 'clear at every lift' if not hits else ''))
        for key, hv in sorted(hits.items()):
            hv.sort()
            print('    %s piece %d ~ %s: lifts %s' % (key[0], key[1], key[2], hv))


def where(k, X, tag, b, lifts, names=('DRV_screw_heads_env', 'FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R')):
    S = X.tbm.copy(X.body('HOUSING_F_front'))
    for n in names:
        for h in lifts:
            t = X.move(X.tbm.copy(X.body(n)), 0.0, -b, -h)
            if not t.boundingBox.intersects(S.boundingBox):
                continue
            X.sec(t, X.tbm.copy(S))
            if X.vol(t) > 0.0005:
                print('b %.2f lift %5.1f: %s in the shell %.4f: %s' % (b, h, n, X.vol(t), X.lumps(t)[:6]))


def _main(stage, tag, bs, lifts):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    if stage == 'heads':
        heads(k, X)
    elif stage == 'way':
        way(k, X, tag, bs)
    else:
        where(k, X, tag, bs[0], lifts)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='b4', bs=(0.65, 1.0, 1.05, 1.1, 1.15, 1.3, 1.5, 1.55), lifts=(80, 60, 46, 44, 42, 40, 30, 20, 10, 8, 7, 5, 3, 2, 1, 0.5, 0)):
    L['out']('p52_%s_%s.txt' % (stage, tag), _main, stage, tag, bs, lifts)
