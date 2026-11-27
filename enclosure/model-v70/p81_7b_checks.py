# Part A (block 7b): checks on the model after the put. READ-ONLY but for TMP_ bodies, deleted again.
# Run: runpy.run_path(D + 'p81_7b_checks.py')['main']()  -> p81_7b_checks.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def dist(k, X, a, b):
    A = X.add(X.tbm.copy(a), 'TMP_a', show=False) if not hasattr(a, 'parentComponent') else a
    B = X.add(X.tbm.copy(b), 'TMP_b', show=False) if not hasattr(b, 'parentComponent') else b
    r = X.mm.measureMinimumDistance(A, B); out = (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
    if A is not a: A.deleteMe()
    if B is not b: B.deleteMe()
    return out


def lev(k, X, b, bed, step, box=None):
    rows = []
    for f in b.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(n[2]) < 0.99:
            continue
        c = k.W(f.centroid)
        if box and not all(box[2 * i] <= c[i] <= box[2 * i + 1] for i in range(3)):
            continue
        h = bed(c[2]); off = h - round(h / step) * step
        rows.append((round(c[2], 3), round(h, 4), round(off, 4), round(f.area * 100, 2), k.r2(c)))
    for r in sorted(rows):
        print('   z %.3f bed %.4f off %+.4f  %7.2f mm2 at %s' % r)


def _main():
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    cap = X.tbm.copy(X.body('HOUSING_F_cap')); cl = X.tbm.copy(X.body('MIC_CLAMP_L'))
    # squeeze: the pad's face, the ceiling, the toe, the ledge, the seat, along z
    for x, y, what in ((9.1, -28.9, 'pad'), (20.0, -26.5, 'ceiling'), (10.8, -26.5, 'toe'), (10.8, -29.2, 'ledge'), (18.6, -33.0, 'seat/roof')):
        c = [(round(170 + a, 3), round(170 + b, 3)) for a, b in k.needle_t(X, [cap], (x, y, 170.0), (x, y, 181.0), 0.005)]
        m = [(round(170 + a, 3), round(170 + b, 3)) for a, b in k.needle_t(X, [cl], (x, y, 170.0), (x, y, 181.0), 0.005)]
        print('%-9s at (%.1f, %.1f): cap %s | clamp L %s' % (what, x, y, c, m))
    for xp in (11.5, 30.0):
        print('pin at x %.1f: cap along z %s' % (xp, [(round(170 + a, 3), round(170 + b, 3)) for a, b in k.needle_t(X, [cap], (xp, -26.5, 170.0), (xp, -26.5, 181.0), 0.005)]))
    print('strip env L box', k.wbb(X, X.body('MIC_strip_L_env')), '; KO L box', k.wbb(X, X.body('KO_mic_L_back')))
    for s in ('L', 'R'):
        print('%s clamp to strip env: %s; shared %.4f' % (s, dist(k, X, X.body('MIC_CLAMP_' + s), X.body('MIC_strip_%s_env' % s)), X.xv(X.tbm.copy(X.body('MIC_CLAMP_' + s)), X.tbm.copy(X.body('MIC_strip_%s_env' % s)))))
        print('%s cap to strip env shared %.4f' % (s, X.xv(X.tbm.copy(X.body('MIC_strip_%s_env' % s)), X.tbm.copy(X.body('HOUSING_F_cap')))))
        print('%s clamp to LEAD_MIC_%s: %s' % (s, s, dist(k, X, X.body('MIC_CLAMP_' + s), X.body('LEAD_MIC_' + s))))
        print('%s clamp to the shell: %s; to VEML_env shared %.4f' % (s, dist(k, X, X.body('MIC_CLAMP_' + s), X.body('HOUSING_F_front')), X.xv(X.tbm.copy(X.body('MIC_CLAMP_' + s)), X.tbm.copy(X.body('VEML_env')))))
    # the lip over the shelf
    cc = X.wbox(-62, 62, -23.6, -22.2, 176.0, 179.0); X.sec(cc, X.tbm.copy(X.body('HOUSING_F_cap')))
    ss = X.wbox(-62, 62, -23.6, -22.2, 176.0, 179.0); X.sec(ss, X.tbm.copy(X.body('HOUSING_F_front')))
    print('cap over the shelf (x -62..62, y -23.6..-22.2): %s' % (dist(k, X, cc, ss),))
    print('cap to the shell (whole): %s' % (dist(k, X, X.body('HOUSING_F_cap'), X.body('HOUSING_F_front')),))
    # the clips: to the box's front face; moved back 0.4 and 0.45
    for s, bxn in (('L', 'SPKBOX_L'), ('R', 'SPKBOX_R')):
        c = X.body('TOUCH_CLIP_' + s)
        print('clip %s to its box: %s; to the board: %s; to the shell: %s' % (s, dist(k, X, c, X.body(bxn)), dist(k, X, c, X.body('TOUCH_PCB')), dist(k, X, c, X.body('HOUSING_F_front'))))
        for back in (0.4, 0.45):
            t = X.move(X.tbm.copy(c), 0, -back, 0)
            print('   moved %.2f back: shares %.4f with its box, %.4f with the shell' % (back, X.xv(t, X.tbm.copy(X.body(bxn))), X.xv(t, X.tbm.copy(X.body('HOUSING_F_front')))))
    print('grid, cap (top face down, 0.10; bed = 180 - z), the strip pockets and the front band:')
    lev(k, X, X.body('HOUSING_F_cap'), lambda z: 180.0 - z, 0.1, (-40, 40, -31, -22, 176.5, 178.6))
    print('grid, clamp L (as fitted, 0.20; bed = z - 172.7):')
    lev(k, X, X.body('MIC_CLAMP_L'), lambda z: z - 172.7, 0.2)
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p81_7b_checks.txt', _main)
