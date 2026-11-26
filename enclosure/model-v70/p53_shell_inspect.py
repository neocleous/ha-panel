# Block 5: the shell (HOUSING_F_front) at the places its items touch. READ-ONLY (temporary bodies only).
# The shell prints chin down: its bed is world y +6.80 (part C), print height = 6.80 - y, 0.20 layers.
# Run: runpy.run_path(D + 'p53_shell_inspect.py')['main'](stage)  -> p53_<stage>.txt
#   'corner' AA-A3: faces at the front corners beside the outer driver heads (axes x +-88.25, z 10.25 / 45.75, r 2.85, y 0..1.65)
#   'bar'    AA-A7: the bar's rear face (y -22.5) and the cap's front face; AA-C4: the back band's bar
#   'frame'  the door frame's lower ends (y -53.5) and the boxes' backs
#   'fins'   AA-C14: the chin dividers' fins
#   'clips'  AA-A18: the shell beside the two touch clips
#   'bme'    AA-B18: the BME680's top foam, the hood and the shell above it
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
k_ = None


def show(k, X, name, box, kinds=('p', 'c'), amin=0.05):
    rows = k.faces(X, X.body(name), box, kinds, amin)
    print('%s faces in %s: %d' % (name, box, len(rows)))
    for r in rows:
        print('   ', r)


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), [round(v, 2) for v in k_.W(r.positionOne)], [round(v, 2) for v in k_.W(r.positionTwo)]


def crop_tmp(X, name, box):
    t = X.wbox(*box); X.sec(t, X.tbm.copy(X.body(name))); return X.add(t, 'TMP_c', show=False)


def _main(stage):
    global k_
    k = L['load'](); X = k.K(); k_ = k; k.budget(70)
    print(L['stamp'](), 'before', X.state())
    if stage == 'corner':
        for sx in (1, -1):
            show(k, X, 'HOUSING_F_front', sorted((sx * 84.0, sx * 96.0)) + [-1.0, 3.0, 2.0, 6.0])
    elif stage == 'bar':
        show(k, X, 'HOUSING_F_front', (-80, 80, -22.8, -22.2, 176.0, 181.0))
        show(k, X, 'HOUSING_F_cap', (-80, 80, -22.8, -22.2, 176.0, 181.0))
        show(k, X, 'HOUSING_F_front', (-20.0, 20.0, -52.0, -49.5, 164.5, 170.5))
    elif stage == 'frame':
        show(k, X, 'HOUSING_F_front', (-100, 100, -54.6, -52.4, 0.0, 70.0))
        for n in ('SPKBOX_L', 'SPKBOX_R'):
            show(k, X, n, (-100, 100, -52.2, -51.8, 0.0, 60.0))
    elif stage == 'fins':
        for sx in (1, -1):
            show(k, X, 'HOUSING_F_front', sorted((sx * 44.0, sx * 48.0)) + [0.5, 4.5, 61.5, 67.5], amin=0.01)
    elif stage == 'clips':
        S = X.body('HOUSING_F_front')
        for n in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
            b = X.body(n)
            print('%s world box %s; to the shell %s' % (n, k.wbb(X, b), dist(X, b, S)))
    elif stage == 'bme':
        S = X.body('HOUSING_F_front')
        for n in ('FOAM_bme_top_env', 'FOAM_bme_env', 'BME_HOOD', 'BME680_env'):
            b = X.body(n)
            print('%s world box %s; to the shell %s; to the hood %s' % (n, k.wbb(X, b), dist(X, b, S), dist(X, b, X.body('BME_HOOD')) if n != 'BME_HOOD' else '-'))
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p53_%s.txt' % stage, _main, stage)
