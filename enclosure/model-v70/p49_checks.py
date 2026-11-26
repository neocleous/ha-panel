# Block 4, checks on the model after p47 (READ-ONLY for the model: temporary bodies 'TMP_*' only, deleted again).
# Slab frame: x = world x, d = depth behind the glass's front, Zd = design z.
#   'slab'   bounded distances: the slab's upper rim, lower rim and two side rims to the screen plate; the slab's rebate to the
#            glass on four sides and at its back (LCD_glass); the slab to the shell
#   'move'   the slab moved along the screen's normal (out, 0.5 to 60, the ride-in's steps) and 0.05 to 0.30 along Zd both ways:
#            its overlap with the screen plate at each step
#   'holes'  the screen plate's four screw holes: diameter read off the faces; needles along d on rings r 2.15 to 2.85 round each
#            axis on the plate's front face (d 9.0): where the plate begins (the head's seat)
#   'lip'    where the slab begins along d near both x ends (p45's grid)
#   'ride'   the display module's ride-in (k4a's ride_in) for the slab alone, against the shell and the parts in it
# Run: runpy.run_path(D + 'p49_checks.py')['main']('slab')  -> p49_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
k_ = None


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 4), [round(v, 3) for v in k_.Sf(r.positionOne)], [round(v, 3) for v in k_.Sf(r.positionTwo)]


def tcrop(X, name, box):
    t = X.dbox(*box); X.sec(t, X.tbm.copy(X.body(name))); return X.add(t, 'TMP_c', show=False)


def slab(k, X):
    P = X.body('HOUSING_F_plate'); G = X.body('LCD_glass')
    # the rims from d 9.05 (the slab's back face at d 9.0 lies on the plate's front face: contact, by design)
    for nm, box in (('upper rim', (-100, 100, 9.05, 12.1, 33.0, 38.0)), ('lower rim', (-100, 100, 9.05, 12.1, -93.0, -88.0)),
                    ('+x side rim', (98.0, 106, 9.05, 12.1, -80, 25)), ('-x side rim', (-106, -98.0, 9.05, 12.1, -80, 25))):
        t = tcrop(X, 'SLAB_frame', box)
        print('slab %-12s to the screen plate %s' % (nm, dist(X, t, P)))
        t.deleteMe()
    for nm, box in (('rebate top', (-90, 90, -0.1, 1.25, 31.0, 34.0)), ('rebate bottom', (-90, 90, -0.1, 1.25, -89.0, -86.0)),
                    ('rebate +x', (99.0, 102.5, -0.1, 1.25, -80, 25)), ('rebate -x', (-97.0, -94.0, -0.1, 1.25, -80, 25)),
                    ('rebate floor', (-90, 90, 1.15, 2.0, -80, 25))):
        t = tcrop(X, 'SLAB_frame', box)
        print('slab %-12s to LCD_glass %s' % (nm, dist(X, t, G)))
        t.deleteMe()
    print('slab to the shell %s' % (dist(X, X.body('SLAB_frame'), X.body('HOUSING_F_front')),))
    print('slab to LCD_panel_body %s' % (dist(X, X.body('SLAB_frame'), X.body('LCD_panel_body')),))


def move(k, X):
    s = X.tbm.copy(X.body('SLAB_frame')); p = X.tbm.copy(X.body('HOUSING_F_plate'))
    out = []
    for st in (0.0, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 30, 40, 60):
        t = X.move_n(X.tbm.copy(s), st)
        out.append((st, round(X.xv(t, p), 4)))
    print('slab moved out along the normal: overlap with the screen plate (mm3): %s' % out)
    out = []
    for dz in (-0.10, -0.05, -0.01, 0.0, 0.05, 0.10, 0.15, 0.19, 0.20, 0.21, 0.25, 0.30):
        t = X.tbm.copy(s)
        m = adsk.core.Matrix3D.create(); m.translation = k.V3(0, 0, dz / 10.0); X.tbm.transform(t, m)
        out.append((dz, round(X.xv(t, p), 4)))
    print('slab moved along Zd (+ = up the screen): overlap with the screen plate (mm3): %s' % out)
    g = X.tbm.copy(X.body('LCD_glass'))
    out = []
    for dz in (-0.35, -0.30, -0.25, -0.21, -0.20, -0.15, 0.15, 0.20, 0.25, 0.30, 0.35):
        t = X.tbm.copy(s)
        m = adsk.core.Matrix3D.create(); m.translation = k.V3(0, 0, dz / 10.0); X.tbm.transform(t, m)
        out.append((dz, round(X.xv(t, g), 4)))
    print('slab moved along Zd: overlap with the glass (mm3): %s' % out)


def holes(k, X):
    P = X.body('HOUSING_F_plate')
    for h in k.holes_of(P, 1.5, 2.5):
        A = k.Sf(k.Wp(*h['A'])); B = k.Sf(k.Wp(*h['B']))
        if abs(h['a'][1] - 0.978) > 0.01:
            continue
        x, zd = A[0], A[2]
        print('hole at (%+.2f, Zd %.3f): r %.3f, d %.2f..%.2f, cov %.2f' % (x, zd, h['r'], min(A[1], B[1]), max(A[1], B[1]), h['cov']))
        crop = X.dbox(x - 4, x + 4, 7.0, 13.0, zd - 4, zd + 4); X.sec(crop, X.tbm.copy(P))
        rows = []
        for r in (h['r'] + 0.05, 2.4, 2.7, 2.85):
            ds = []
            for j in range(24):
                a = 2 * math.pi * j / 24
                px, pz = x + r * math.cos(a), zd + r * math.sin(a)
                s = k.needle_t(X, [crop], k.W(k.Dp(px, 7.5, pz)), k.W(k.Dp(px, 12.0, pz)), 0.02)
                ds.append(round(7.5 + s[0][0], 3) if s else None)
            rows.append((r, min(v for v in ds if v is not None) if any(ds) else None, max(v for v in ds if v is not None) if any(ds) else None,
                         sum(1 for v in ds if v is None)))
        print('   ring r, plate begins at d (least, most), rays with no plate: %s' % rows)


def lip(k, X):
    S = X.body('SLAB_frame')
    for side, xs in (('+x', [99.5, 99.75, 99.9, 100.1, 100.35, 100.6, 101.0, 101.5, 101.75, 102.0]), ('-x', [-102.0, -101.0, -100.0, -99.5, -99.0, -98.0])):
        zr = [-88.5, -87.5, -86.5, -85.5, -84.5, -60.0, -27.0, 0.0, 29.0, 30.5, 31.5, 32.5, 33.5]
        crop = X.dbox(min(xs) - 0.5, max(xs) + 0.5, -0.5, 3.0, -90, 35); X.sec(crop, X.tbm.copy(S))
        print('%s end, d where the slab begins:' % side)
        print('   Zd \\ x ' + ' '.join('%7.2f' % x for x in xs))
        for z in zr:
            row = []
            for x in xs:
                s = k.needle_t(X, [crop], k.W(k.Dp(x, -0.5, z)), k.W(k.Dp(x, 3.0, z)), 0.02)
                row.append('%7.3f' % (s[0][0] - 0.5) if s else '      -')
            print('   %7.2f ' % z + ' '.join(row))


def ride(k, X):
    k.budget(70)
    # the library's groups name a few bodies the model no longer has (USBA_cable_env): for this call, only those it has
    keep = {}
    for g in ('SHELL', 'PLATE', 'PI', 'PIPWR', 'CRADLE', 'INLET', 'BOXES', 'USBA', 'TOUCH', 'RADAR', 'BME', 'DISP', 'RESP', 'MAIN', 'UNIT', 'MODULE'):
        keep[g] = list(k.ST[g])
        k.ST[g] = [n for n in k.ST[g] if n.endswith('*') or X.body(n) is not None]
        if k.ST[g] != keep[g]:
            print('group %s: left out %s' % (g, sorted(set(keep[g]) - set(k.ST[g]))))
    try:
        skip = [n for n in [b.name for b in k.st(X, 'MODULE')] if n != 'SLAB_frame']
        res, left = k.K4NS['ride_in'](X, 'b4slab', leads=False, skip=skip)
    finally:
        for g, v in keep.items():
            k.ST[g] = v
    hits = {key: v for key, v in res.items() if v}
    print('ride-in, the slab alone: %d positions, left %d; positions with an overlap: %s' % (len(res), left, hits if hits else 'none'))


def _main(stage):
    global k_
    k = L['load'](); X = k.K(); k_ = k
    print(L['stamp'](), 'before', X.state())
    {'slab': slab, 'move': move, 'holes': holes, 'lip': lip, 'ride': ride}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p49_%s.txt' % stage, _main, stage)
