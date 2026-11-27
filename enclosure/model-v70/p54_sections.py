# Block 5: sections by needles and face lists at the shell's remaining places. READ-ONLY (temporary bodies only).
#   'frame'  faces of the shell square to y near y -53.5 (any z): the door frame's lower ends
#   'div'    the shell's faces square to x beside the two touch clips (x 44.5..47.5 either side, z 25..70)
#   'fins'   needles along y (0 to 6) at x +46.15 / -46.05, z 62.5 to 66.7: solid stretches
#   'band'   needles along y (-56 to -46) at x 0, 3, 12, z 164 to 171: the back band's bar
#   'bme'    the shell's and the hood's faces at the hood's top plate, and needles along x there
# Run: runpy.run_path(D + 'p54_sections.py')['main'](stage)  -> p54_<stage>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def needles(k, X, name, box, lines):
    c = X.wbox(*box); X.sec(c, X.tbm.copy(X.body(name)))
    for (a, b, lab) in lines:
        s = k.needle_t(X, [c], a, b, 0.02)
        print('   %-22s %s' % (lab, s))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    if stage == 'frame':
        for r in k.faces(X, X.body('HOUSING_F_front'), (-100, 100, -53.65, -53.35, 0, 180), ('p',), 0.05):
            print('   ', r)
        S = X.body('HOUSING_F_front')
        for f in S.faces:
            if f.geometry.surfaceType != 0:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            n = k.wv(nv)
            ws = [k.W(v.geometry) for v in f.vertices]
            if n[1] > 0.999 and ws and abs(sum(w[1] for w in ws) / len(ws) + 53.5) < 0.15:
                print('   face +y near -53.5: area %.1f, vertices y %.3f..%.3f, x %.2f..%.2f, z %.2f..%.2f' % (
                    f.area * 100, min(w[1] for w in ws), max(w[1] for w in ws), min(w[0] for w in ws), max(w[0] for w in ws),
                    min(w[2] for w in ws), max(w[2] for w in ws)))
    elif stage == 'div':
        for sx in (1, -1):
            box = sorted((sx * 44.5, sx * 47.5)) + [-12.0, 5.0, 20.0, 72.0]
            for r in k.faces(X, X.body('HOUSING_F_front'), box, ('p',), 0.5):
                if abs(r[1][0]) > 0.99:
                    print('   ', r)
    elif stage == 'fins':
        for x in (46.15, -46.05):
            lines = [((x, -0.5, z), (x, 6.0, z), 'x %.2f z %.2f' % (x, z)) for z in [62.5 + 0.2 * i for i in range(22)]]
            needles(k, X, 'HOUSING_F_front', (x - 1, x + 1, -1, 7, 61, 68), lines)
    elif stage == 'band':
        for x in (0.0, 3.0, 12.0):
            lines = [((x, -57.0, z), (x, -45.0, z), 'x %.1f z %.2f' % (x, z)) for z in [164.0 + 0.25 * i for i in range(29)]]
            needles(k, X, 'HOUSING_F_front', (x - 1, x + 1, -58, -44, 163, 172), lines)
    elif stage == 'bme':
        for n in ('HOUSING_F_front', 'BME_HOOD'):
            print(n)
            for r in k.faces(X, X.body(n), (-86, -76, -53, -26, 105, 112), ('p',), 0.3):
                print('   ', r)
        for n in ('HOUSING_F_front', 'BME_HOOD', 'FOAM_bme_top_env'):
            print(n, 'needles along x at z 108.0..110.6, y -40:')
            lines = [((-90.0, -40.0, z), (-74.0, -40.0, z), 'z %.2f' % z) for z in [108.0 + 0.2 * i for i in range(14)]]
            needles(k, X, n, (-92, -72, -42, -38, 106, 112), lines)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p54_%s.txt' % stage, _main, stage)
