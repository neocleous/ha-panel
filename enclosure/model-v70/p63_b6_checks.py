# Block 6 checks on the temporary bodies of p62 (k.c['b6_*']) before they go in. Adds 'TMP_*' bodies for distances and deletes
# them again; nothing else in the document changes.
#   'grid'   level faces of the new clamp L and cap (left half) with their bed heights (clamp: underside z 172.7, 0.20 layers;
#            cap: top face z 180.0, 0.10 layers)
#   'fits'   bounded distances: the lug to the peg's flare, the slot to the peg, the clamp floor to the boss end, the seat to the roof,
#            the toes to the strip, the pins to the strip's holes (drawn), the clamp to the shell, to the microphone lead and to the VEML
#            board; the cap's front edge over the shell's shelf
#   'lug'    the lug and the rail's end to the peg and its flare only (the roof left out), new and as at version 74
#   'pairs'  shared volume of each new body with every body of the unit (the model's, the old ones taken out)
# Run: runpy.run_path(D + 'p63_b6_checks.py')['main'](stage)  -> p63_<stage>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
NEW = {'HOUSING_F_cap': 'b6_cap', 'MIC_CLAMP_L': 'b6_clampL', 'MIC_CLAMP_R': 'b6_clampR', 'MIC_strip_L_env': 'b6_stripL',
       'MIC_strip_R_env': 'b6_stripR', 'KO_mic_L_back': 'b6_koL', 'KO_mic_R_back': 'b6_koR'}


def tmp(X, tb, nm):
    return X.add(X.tbm.copy(tb), 'TMP_' + nm, show=False)


def crop(X, tb, box, nm):
    t = X.wbox(*box); X.sec(t, X.tbm.copy(tb)); return X.add(t, 'TMP_' + nm, show=False)


def d(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))


def grid(k, X):
    for key, z0, lay, box in (('b6_clampL', 172.7, 0.2, (-200, 200, -200, 200, 0, 400)), ('b6_cap', 180.0, 0.1, (0, 60, -45, -15, 170, 181))):
        t = k.c[key]; zs = {}
        for f in t.faces:
            if f.geometry.surfaceType != k.PLN:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv); p = k.W(f.pointOnFace)
            if abs(abs(n[2]) - 1) < 1e-4 and box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]:
                q = (round(p[2], 4), int(round(n[2]))); zs.setdefault(q, 0.0); zs[q] += f.area * 100
        print('%s level faces (z, normal z, mm2, bed height, off the %.2f grid):' % (key, lay))
        for (z, s), a in sorted(zs.items()):
            bed = abs(z - z0); off = round(bed / lay - round(bed / lay), 4) * lay
            print('   z %9.4f n %+d %8.2f mm2  bed %.4f  off %+.4f' % (z, s, a, bed, off))


def fits(k, X):
    cap = tmp(X, k.c['b6_cap'], 'cap'); sh = X.body('HOUSING_F_front')
    for sx, s in ((1, 'L'), (-1, 'R')):
        cl = tmp(X, k.c['b6_clamp' + s], 'cl' + s); st = tmp(X, k.c['b6_strip' + s], 'st' + s)
        xa, xb = sorted((sx * 28.0, sx * 37.5))
        lug = crop(X, k.c['b6_clamp' + s], (xa, xb, -38, -29, 176.0, 177.6), 'lug' + s)
        peg = crop(X, k.c['b6_cap'], (sx * 32.75 - 3.0, sx * 32.75 + 3.0, -36.5, -30.0, 174.0, 177.6), 'peg' + s)
        print('%s lug (z 176..177.6) to the cap round the peg (flare and peg): %s' % (s, d(k, X, lug, peg)))
        slot = crop(X, k.c['b6_clamp' + s], (xa, xb, -38, -29, 175.0, 176.6), 'slot' + s)
        pg = crop(X, k.c['b6_cap'], (sx * 32.75 - 1.6, sx * 32.75 + 1.6, -34.9, -31.6, 175.2, 176.49), 'pg' + s)
        print('%s slot walls (z 175..176.6) to the peg Ø3.0: %s' % (s, d(k, X, slot, pg)))
        fl = crop(X, k.c['b6_clamp' + s], (sx * 15.5 - 3.5, sx * 15.5 + 3.5, -38.8, -31.6, 174.3, 174.55), 'fl' + s)
        be = crop(X, k.c['b6_cap'], (sx * 15.5 - 3.1, sx * 15.5 + 3.1, -38.4, -32.0, 174.6, 175.0), 'be' + s)
        print('%s clamp floor to the boss end: %s' % (s, d(k, X, fl, be)))
        print('%s clamp to the cap (whole): %s' % (s, d(k, X, cl, cap)))
        print('%s clamp to the strip envelope: %s' % (s, d(k, X, cl, st)))
        print('%s clamp to the shell: %s' % (s, d(k, X, cl, sh)))
        print('%s clamp to LEAD_MIC_%s: %s' % (s, s, d(k, X, cl, X.body('LEAD_MIC_' + s))))
        print('%s clamp to VEML_env: %s, shared %.4f mm3' % (s, d(k, X, cl, X.body('VEML_env')), X.xv(k.c['b6_clamp' + s], X.tbm.copy(X.body('VEML_env')))))
        print('%s strip envelope to the cap: %s, shared %.4f mm3' % (s, d(k, X, st, cap), X.xv(k.c['b6_strip' + s], k.c['b6_cap'])))
        for xp in (11.5, 30.0):
            pn = crop(X, k.c['b6_cap'], (sx * xp - 1, sx * xp + 1, -27.5, -25.5, 177.3, 178.2), 'pin')
            wall = crop(X, k.c['b6_cap'], (sx * 8.0 if sx > 0 else sx * 38, sx * 38.0 if sx > 0 else sx * 8, -30.0, -29.69, 177.5, 178.3), 'wall')
            print('%s pin at x %.1f: tip z %s; to the pocket wall y -29.7: %s' % (s, sx * xp, round(k.wbb(X, pn)[4], 3), d(k, X, pn, wall)))
            pn.deleteMe(); wall.deleteMe()
    # the cap's front edge over the shell's shelf (record: shelf z 177.4, cap 177.5, at x 0, y -23.0)
    ce = crop(X, k.c['b6_cap'], (-60, 60, -23.4, -22.5, 177.3, 177.7), 'ce')
    se = crop(X, sh, (-60, 60, -23.4, -22.5, 176.5, 177.45), 'se')
    print('cap front edge over the shelf: %s' % (d(k, X, ce, se),))
    for x in (-50.0, 0.0, 50.0):
        print('   at x %+.0f: cap underside z %s, shelf top z %s' % (x, [round(176.5 + b, 3) for a, b in k.needle_t(X, [X.tbm.copy(k.c['b6_cap'])], (x, -23.0, 176.5), (x, -23.0, 178.0), 0.02)][:1],
              [round(176.0 + b, 3) for a, b in k.needle_t(X, [X.tbm.copy(sh)], (x, -23.0, 176.0), (x, -23.0, 177.49), 0.02)][-1:]))


def pairs(k, X):
    cur = k.current(X, leads=True)
    names = [b.name for b in cur]
    for nm, key in NEW.items():
        t = k.c[key]; row = []
        for b in cur:
            if b.name == nm:
                continue
            other = k.c[NEW[b.name]] if b.name in NEW else X.tbm.copy(b)
            v = X.xv(t, other)
            if abs(v) > 0.0005:
                row.append((b.name, round(v, 3)))
        print('%-16s shares with: %s' % (nm, row))


def lug(k, X):
    for sx, s in ((1, 'L'), (-1, 'R')):
        for key, nm, z0 in (('b6_clamp' + s, 'new', 175.0), ('b6_clamp' + s, 'new, above the peg', 176.55), (None, 'v74', 175.0), (None, 'v74, above the peg', 176.55)):
            src = k.c[key] if key else X.tbm.copy(X.body('MIC_CLAMP_' + s))
            capsrc = k.c['b6_cap'] if key else X.tbm.copy(X.body('HOUSING_F_cap'))
            xa, xb = sorted((sx * 27.0, sx * 37.5))
            cl = crop(X, src, (xa, xb, -38, -29, z0, 177.45), 'lug')
            cone = X.cyl((sx * 32.75, -33.25, 175.0), (sx * 32.75, -33.25, 177.45), 2.6); X.sec(cone, X.tbm.copy(capsrc))
            cn = X.add(cone, 'TMP_cone', show=False)
            print(('%s %s: the lug and rail end (z %.2f..177.45) to the peg and its flare (r <= 2.6, z 175..177.45): %s') % (s, nm, z0, d(k, X, cl, cn)))
            for z in (177.0, 177.2, 177.4):
                print('     at z %.1f the flare radius is %.2f' % (z, 1.5 + (z - 176.5)))
            cl.deleteMe(); cn.deleteMe()


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'grid': grid, 'fits': fits, 'pairs': pairs, 'lug': lug}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p63_%s.txt' % stage, _main, stage)
