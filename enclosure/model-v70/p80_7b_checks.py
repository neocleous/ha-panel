# Part A (block 7b): checks. READ-ONLY but for TMP_ bodies, deleted again.
#   'boxR'  the right box (k.c b7b_boxR, or the model's) to the shell, by bands of z and y; needles along x for gap and wall
# Run: runpy.run_path(D + 'p80_7b_checks.py')['main'](stage)  -> p80_<stage>.txt
import runpy, math
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def dist(k, X, a, b):
    A = X.add(X.tbm.copy(a), 'TMP_a', show=False); B = X.add(X.tbm.copy(b), 'TMP_b', show=False)
    r = X.mm.measureMinimumDistance(A, B); out = (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
    A.deleteMe(); B.deleteMe(); return out


def boxR(k, X, tag):
    src = {'new': k.c.get('b7b_boxR'), 'v77': X.tbm.copy(X.body('SPKBOX_R'))}[tag]
    sh = X.wbox(-100, -84, -56, 2.0, 55, 90); X.sec(sh, X.tbm.copy(X.body('HOUSING_F_front')))
    for z0, z1 in ((60, 70), (70, 76.5), (76.5, 80), (80, 84), (84, 87)):
        for y0, y1 in ((-53, -30), (-30, -15), (-15, -8), (-8, -3.0)):
            c = X.wbox(-97, -84, y0, y1, z0, z1); X.sec(c, X.tbm.copy(src))
            if not c.faces.count:
                continue
            print('%s box z %5.1f..%5.1f y %6.1f..%5.1f to the shell: %s' % (tag, z0, z1, y0, y1, dist(k, X, c, sh)))


def needles(k, X):
    for tag, b in (('v77', X.tbm.copy(X.body('SPKBOX_R'))), ('new', k.c.get('b7b_boxR'))):
        if b is None:
            continue
        sh = X.tbm.copy(X.body('HOUSING_F_front'))
        for z in (77.0, 79.0, 81.0, 83.0):
            for y in (-40.0, -20.0, -8.0, -4.0):
                bi = [(round(-100 + p, 2), round(-100 + q, 2)) for p, q in k.needle_t(X, [b], (-100.0, y, z), (-80.0, y, z), 0.01)]
                si = [(round(-100 + p, 2), round(-100 + q, 2)) for p, q in k.needle_t(X, [sh], (-100.0, y, z), (-80.0, y, z), 0.01)]
                print('%s z %.0f y %.0f along x -100..-80: box %s | shell %s' % (tag, z, y, bi[:2], si[-1:] if si else si))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    if stage == 'boxR':
        boxR(k, X, 'v77'); boxR(k, X, 'new')
    elif stage == 'needles':
        needles(k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p80_%s.txt' % stage, _main, stage)
