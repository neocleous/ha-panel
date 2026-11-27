# Block 5 (D471, PR44): the fill at the hood's boss, read on the model as it stands. READ-ONLY (temporary bodies only).
# The last pass's checks are run by their own functions (../model-v70/p71_b7_ways.py, p97_close_last.py, read from the last
# pass's folder on the Mac); their printed output is caught into this pass's folder, the last pass's files are not written.
#   fill       the shell against the shell as it stood before the put (k.c['b5_shell_before']): what was added and removed
#   pilot      p97's 'pilots' on the shell and on its hidden copy of version 79: the wall round every pilot 1.6 across
#   hood       p71's 'hood': the hood lifted along its pegs, then toward the middle: shared volume with the shell and the
#              neighbours; the end piece to the wall's end and the foot over the ledges at home (by temporary bodies)
#   hoodout    p97's 'hoodout' (part 'across' or 'back'): the hood lifted 3.5, across, then back out through the door opening
#   hoodscrew  p97's 'hoodscrew': the driver and a hand straight out of the hood's screw
#   seat       the hood at home against the shell round the boss: smallest distance of the hood to the added material's faces
#              (the planes z 97 and z 103 and the fill's end face) and the shared volume of hood and shell
# Run: runpy.run_path(D + 'd52_checks5.py')['main'](stage, tag='', **kw)  -> d52_<stage>[_<tag>].txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
D70 = L['D70']
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
HN = (0.11394, 0.09756, 0.98869); HU = (0.7593, 0.6497, 0.0)


def st_fill(k, X):
    new = X.body('HOUSING_F_front'); old = k.c.get('b5_shell_before')
    if old is None:
        print('the shell as it stood is not in this session any more'); return
    add = X.tbm.copy(new); X.dif(add, X.tbm.copy(old))
    rem = X.tbm.copy(old); X.dif(rem, X.tbm.copy(new))
    la = X.lumps(add) if add.faces.count else []; lr = X.lumps(rem) if rem.faces.count else []
    print('shell %.3f (very high %.3f), lumps %d, closed skins %d, faces %d; before the put %.3f' % (new.volume * 1000, L['vhi'](new), new.lumps.count, new.shells.count, new.faces.count, X.vol(old)))
    print('added %.4f in %d lump(s): %s' % (sum(q[0] or 0 for q in la), len(la), la[:4]))
    print('removed %.4f in %d lump(s): %s' % (sum(q[0] or 0 for q in lr), len(lr), lr[:4]))


def st_pilot(k, X):
    P97 = runpy.run_path(D70 + 'p97_close_last.py')
    P97['pilots'](k, X, names=('HOUSING_F_front',))
    print('--- the hidden copy of version 79:')
    P97['pilots'](k, X, names=('HOUSING_F_front_v79',))


def st_hood(k, X):
    P71 = runpy.run_path(D70 + 'p71_b7_ways.py')
    near = P71['near']; hits = P71['hits']
    n = k.unit(HN); u = k.unit(HU)
    hb = X.body('BME_HOOD'); S = X.body('HOUSING_F_front')
    H = X.tbm.copy(hb)
    fixed = near(k, X, (-95, -45, -62, -15, 85, 125), ('BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'SCREWS_M2x6_env'))
    print('fixed near the hood: %s' % [f[0] for f in fixed])
    for Lf in (0.0, 0.5, 1.0, 1.5, 1.9, 2.0, 2.1, 2.5, 3.0, 3.5, 3.7, 3.8, 4.0):
        print('lift %.1f along the pins: %s' % (Lf, hits(X, [H], fixed, Lf * n[0], Lf * n[1], Lf * n[2]) or 'clear'))
    for Lf in (2.1, 2.5, 3.0, 3.5):
        row = []
        for m in (0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0):
            hh = hits(X, [H], fixed, Lf * n[0] + m * u[0], Lf * n[1] + m * u[1], Lf * n[2] + m * u[2])
            row.append((m, hh or 'clear'))
        print('lift %.1f, then toward the middle: %s' % (Lf, row))
    for lab, hbx, sbx in (('end piece to the wall\'s end', (-59.6, -56.5, -50.2, -46.2, 103.8, 108.4), (-62, -54, -55, -44, 96, 110)),
                          ('foot (side plate\'s lower end) over the ledges', (-78, -59, -48, -26, 91.5, 92.6), (-85, -55, -60, -20, 85, 92.0))):
        a = X.wbox(*hbx); X.sec(a, X.tbm.copy(hb)); b = X.wbox(*sbx); X.sec(b, X.tbm.copy(S))
        if a.faces.count and b.faces.count:
            r = X.mm.measureMinimumDistance(a, b)
            print('%s: %.3f at %s / %s' % (lab, r.value * 10, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))))


def st_hoodout(k, X, part='across'):
    k.budget(70)
    runpy.run_path(D70 + 'p97_close_last.py')['hoodout'](k, X, part=part)


def st_hoodscrew(k, X):
    k.budget(70)
    runpy.run_path(D70 + 'p97_close_last.py')['hoodscrew'](k, X)


def st_seat(k, X):
    S = X.body('HOUSING_F_front'); hb = X.body('BME_HOOD')
    c = L['crop'](X, S, (-70.0, -52.0, -58.0, -42.0, 94.0, 106.0))
    print('hood and shell (cut to a box round the boss): shared %.4f mm3' % X.xv(X.tbm.copy(hb), c))
    rows = []
    for f in S.faces:
        if f.geometry.surfaceType != PLN:
            continue
        p = k.W(f.pointOnFace)
        if not (-68 < p[0] < -57 and -56 < p[1] < -48 and 96.9 < p[2] < 103.1):
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.r2(k.unit(k.wv(nv)), 3)
        if abs(abs(n[2]) - 1) < 1e-3 and (abs(p[2] - 97.0) < 1e-3 or abs(p[2] - 103.0) < 1e-3):
            lab = 'side plane z %.1f' % p[2]
        elif abs(n[0] - 0.927) < 2e-3 and abs(n[1] + 0.375) < 2e-3:
            lab = 'end face, square to the boss'
        else:
            continue
        r = X.mm.measureMinimumDistance(f, hb)
        rows.append('%-30s %8.3f mm2, normal %s: to the hood %.3f (on the face at %s)' % (lab, f.area * 100, n, r.value * 10, k.r2(k.W(r.positionOne), 2)))
    for r in rows:
        print('   ' + r)


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'fill': st_fill, 'pilot': st_pilot, 'hood': st_hood, 'hoodout': st_hoodout, 'hoodscrew': st_hoodscrew, 'seat': st_seat}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d52_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
