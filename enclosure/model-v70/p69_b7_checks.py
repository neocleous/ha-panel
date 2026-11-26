# Block 7 checks on the temporary bodies of p68 (k.c['b7_*']) against version 75's bodies. Adds 'TMP_*' bodies for distances and
# deletes them again; nothing else in the document changes.
#   'board'   the fits round the touch board, before (version 75) and after: seat, bottom and top edges, ends, clips, keep-out, lips
#   'grid'    level faces on their print grids: shell chin face (bed y), hood (top plate's outer face down), carrier (display side down)
#   'outer'   the outer-skin check: the shell outside REF_F_outer, new and version 69's copy
#   'hood'    the hood: top plate edge to the wall (needles along u), end piece to the wall's end, foot over the ledges, ear to boss,
#             pins' stand above the hood
#   'boxes'   right box to the shell; left box's pocket wall in section; the pilots and what stands beyond
#   'carrier' post tops to the main board; hole depth; the arrow
#   'pairs'   shared volume of each new body with every body of the unit (old ones taken out)
# Run: runpy.run_path(D + 'p69_b7_checks.py')['main'](stage)  -> p69_<stage>.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
NEW = {'HOUSING_F_front': 'b7_shell', 'TOUCH_PCB': 'b7_tpcb', 'TOUCH_components_env': 'b7_tcomp', 'KO_touch_back': 'b7_tko',
       'LEAD_TOUCH': 'b7_tlead', 'TOUCH_CLIP_L': 'b7_clipL', 'TOUCH_CLIP_R': 'b7_clipR', 'RESP_CARRIER': 'b7_carrier',
       'SPKBOX_L': 'b7_boxL', 'SPKBOX_R': 'b7_boxR', 'BME_HOOD': 'b7_hood', 'FOAM_bme_top_env': 'b7_foamtop', 'FOAM_bme_env': 'b7_foam'}
HN = (0.11394, 0.09756, 0.98869); HP0 = (-69.8829, -39.0603, 110.0342)


PUT = [False]   # True once the new bodies are in the model: 'before' then reads the hidden _v69 copies


def src(k, X, nm, new):
    if new and nm in NEW:
        return k.c[NEW[nm]]
    if PUT[0] and not new and X.body(nm + '_v69') is not None:
        return X.tbm.copy(X.body(nm + '_v69'))
    return X.tbm.copy(X.body(nm))


def crop(X, tb, box, nm):
    t = X.wbox(*box); X.sec(t, X.tbm.copy(tb))
    return X.add(t, 'TMP_' + nm, show=False) if t.faces.count else None


def d(k, X, a, b):
    if a is None or b is None:
        return None
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))


def board(k, X):
    for new in (False, True):
        tag = 'after' if new else 'v75'
        pcb = X.add(src(k, X, 'TOUCH_PCB', new), 'TMP_pcb', show=False)
        sh = src(k, X, 'HOUSING_F_front', new)
        rows = [('seat (chin face, x -40..40, z 10..45)', (-40, 40, 3.0, 6.0, 10, 45)),
                ('below the bottom edge (z 0..6)', (-48, 48, -3, 8, 0, 6.0)),
                ('above the top edge (z 50..56)', (-48, 48, -3, 8, 50.0, 56)),
                ('beside the left end (x 45..48)', (45.0, 48, -3, 8, 4, 52)),
                ('beside the right end (x -48..-45)', (-48, -45.0, -3, 8, 4, 52)),
                ('behind the back (y -3..2.75), the lips and ledges', (-48, 48, -3, 2.75, 4, 52))]
        for lab, bx in rows:
            c = crop(X, sh, bx, 'c')
            print('%s  board to the shell, %s: %s' % (tag, lab, d(k, X, pcb, c)))
            if c:
                c.deleteMe()
        for nm in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F'):
            o = X.add(src(k, X, nm, new), 'TMP_o', show=False)
            print('%s  board to %s: %s' % (tag, nm, d(k, X, pcb, o))); o.deleteMe()
        ko = X.add(src(k, X, 'KO_touch_back', new), 'TMP_ko', show=False)
        for nm in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'FLOOR_PLATE'):
            o = X.add(src(k, X, nm, new), 'TMP_o', show=False)
            print('%s  keep-out behind the board to %s: %s' % (tag, nm, d(k, X, ko, o))); o.deleteMe()
        for nm in ('TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
            o = X.add(src(k, X, nm, new), 'TMP_o', show=False)
            print('%s  %s to the shell: %s; to its box: %s' % (tag, nm, d(k, X, o, X.add(X.tbm.copy(sh), 'TMP_s', show=False)),
                  d(k, X, o, X.add(src(k, X, 'SPKBOX_L' if nm.endswith('L') else 'SPKBOX_R', new), 'TMP_b', show=False))))
            for t in [t for t in X.root.bRepBodies if t.name in ('TMP_o', 'TMP_s', 'TMP_b')]:
                t.deleteMe()
        for t in [t for t in X.root.bRepBodies if t.name.startswith('TMP_')]:
            t.deleteMe()


def grid(k, X):
    S = k.c['b7_shell']
    for f in S.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv); p = k.W(f.pointOnFace)
        if abs(abs(n[1]) - 1) < 1e-4 and 3.5 < p[1] < 5.5 and p[2] < 70 and f.area * 100 > 20:
            bed = 6.7992 - p[1]
            print('shell level face y %.4f (bed %.4f, %+.4f off the 0.2 grid) %.2f mm2' % (p[1], bed, bed - round(bed / 0.2) * 0.2, f.area * 100))
    n = k.unit(HN)
    for f in k.c['b7_hood'].faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); m = k.unit(k.wv(nv)); c = sum(m[i] * n[i] for i in range(3))
        if abs(abs(c) - 1) < 1e-3:
            p = k.W(f.pointOnFace); bed = sum((HP0[i] - p[i]) * n[i] for i in range(3))
            print('hood level face bed %.4f (%+.4f off) %s %.2f mm2 at %s' % (bed, bed - round(bed / 0.2) * 0.2, '+n' if c > 0 else '-n', f.area * 100, k.r2(p)))
    for f in k.c['b7_carrier'].faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); m = k.wv(nv)
        if abs(abs(m[1] * 0.978148 + m[2] * 0.207912) - 1) < 1e-4:
            q = k.Sf(f.pointOnFace); bed = q[1] - 15.2
            if f.area * 100 > 1.0:
                print('carrier level face d %.4f (bed %.4f, %+.4f off) %.2f mm2 at %s' % (q[1], bed, bed - round(bed / 0.2) * 0.2, f.area * 100, k.r2(k.W(f.pointOnFace))))


def outer(k, X):
    ref = X.body('REF_F_outer')
    for nm, t0 in (('new', k.c['b7_shell']), ('HOUSING_F_front_v69', X.tbm.copy(X.body('HOUSING_F_front_v69'))), ('v75', X.tbm.copy(X.body('HOUSING_F_front')))):
        t = X.tbm.copy(t0); X.dif(t, X.tbm.copy(ref))
        print('%s outside the cloth reference: %.4f mm3, %d lump(s)' % (nm, X.vol(t) if t.faces.count else 0.0, t.lumps.count if t.faces.count else 0))


def hood(k, X):
    n = k.unit(HN); u = (0.7593, 0.6497, -0.1517); dd = sum(u[i] * n[i] for i in range(3)); u = k.unit(tuple(u[i] - dd * n[i] for i in range(3)))
    v = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    for new in (False, True):
        tag = 'after' if new else 'v75'
        H = src(k, X, 'BME_HOOD', new); S = src(k, X, 'HOUSING_F_front', new)
        for bd in (0.3, 0.9, 1.3):
            o = tuple(HP0[i] - bd * n[i] for i in range(3))
            row = []
            for vq in (-10.5, -7.0, -3.5, 0.0, 3.5, 7.0, 10.5):
                a = tuple(o[i] - 9.0 * u[i] + vq * v[i] for i in range(3)); b = tuple(o[i] + 0.0 * u[i] + vq * v[i] for i in range(3))
                hs = k.needle_t(X, [H], a, b, 0.02); ss = k.needle_t(X, [S], a, b, 0.02)
                he = min(x for x, y in hs) if hs else None; se = max([y for x, y in ss if y < (he if he is not None else 99)], default=None)
                row.append((vq, round(he - se, 3) if he is not None and se is not None else None))
            print('%s  bed %.1f: top plate edge to the wall (gap along u) at v: %s' % (tag, bd, row))
        h = X.add(X.tbm.copy(H), 'TMP_h', show=False)
        sc = crop(X, S, (-62, -54, -55, -44, 96, 110), 's1')
        print('%s  hood to the shell at the end piece / boss (x -62..-54): %s' % (tag, d(k, X, h, sc)))
        sc2 = crop(X, S, (-85, -55, -60, -20, 85, 94), 's2')
        print('%s  hood to the shell at the foot / ledges (z 85..94): %s' % (tag, d(k, X, h, sc2)))
        ft = X.add(src(k, X, 'FOAM_bme_top_env', new), 'TMP_f', show=False)
        print('%s  top foam to the hood: %s; to the shell: shared %.3f mm3' % (tag, d(k, X, h, ft), X.xv(src(k, X, 'FOAM_bme_top_env', new), S)))
        for r in k.holes_of(X.body('BME_HOOD'), rmin=1.15, rmax=1.25):
            A = r['A']; a = r['a']
            if abs(a[2] - 0.989) > 0.01:
                continue
            st = k.needle_t(X, [S], A, tuple(A[i] + 5 * a[i] for i in range(3)), 0.02)
            print('%s  pin through the hole at %s: shell along its axis from the hood\'s plain underside: %s' % (tag, A, st))
        for t in [t for t in X.root.bRepBodies if t.name.startswith('TMP_')]:
            t.deleteMe()


def boxes(k, X):
    for new in (False, True):
        tag = 'after' if new else 'v75'
        S = X.add(src(k, X, 'HOUSING_F_front', new), 'TMP_s', show=False)
        for nm in ('SPKBOX_R', 'SPKBOX_L'):
            b = X.add(src(k, X, nm, new), 'TMP_b', show=False)
            print('%s  %s to the shell: %s' % (tag, nm, d(k, X, b, S))); b.deleteMe()
        L_ = src(k, X, 'SPKBOX_L', new)
        c = X.wbox(50, 62, -40, -31, 6, 22); X.sec(c, X.tbm.copy(L_))
        for z in (10.0, 12.0, 15.2, 19.0):
            print('%s  left box at z %.1f, along y at x 56.4: %s' % (tag, z, [(round(-40 + a, 2), round(-40 + q, 2)) for a, q in k.needle_t(X, [c], (56.4, -40.0, z), (56.4, -31.0, z), 0.02)]))
        u = X.add(X.tbm.copy(X.body('USBA_plug_env')), 'TMP_u', show=False); bl = X.add(X.tbm.copy(L_), 'TMP_bl', show=False)
        print('%s  USB-A plug to the left box: %s' % (tag, d(k, X, u, bl)))
        for nm, sx in (('SPKBOX_L', 1), ('SPKBOX_R', -1)):
            bb = src(k, X, nm, new)
            print('%s  %s along the pilot axis (x from %.1f): %s' % (tag, nm, sx * 43, k.needle_t(X, [bb], (sx * 43.0, -7.05, 38.0), (sx * 60.0, -7.05, 38.0), 0.02)))
        for t in [t for t in X.root.bRepBodies if t.name.startswith('TMP_')]:
            t.deleteMe()


def carrier(k, X):
    a = (0.0, 0.978148, 0.207912)
    for new in (False, True):
        tag = 'after' if new else 'v75'
        c = src(k, X, 'RESP_CARRIER', new)
        for r in k.holes_of(X.body('RESP_CARRIER'), rmin=1.9, rmax=2.1):
            A = r['A']
            p0 = tuple(A[i] - 1.0 * a[i] for i in range(3)); p1 = tuple(A[i] + 12.0 * a[i] for i in range(3))
            st = k.needle_t(X, [c], tuple(p0[i] + 2.5 * 0 for i in range(3)), p1, 0.02)
            q0 = tuple(A[i] + 3.0 * 1 for i in range(1)) 
            off = (A[0] + 3.0, A[1], A[2])
            st2 = k.needle_t(X, [c], tuple(off[i] - 1.0 * a[i] for i in range(3)), tuple(off[i] + 12.0 * a[i] for i in range(3)), 0.02)
            print('%s  post at %s: on its axis from 1.0 above the old mouth: %s; 3.0 off the axis: %s' % (tag, A, st, st2))
        cc = X.add(X.tbm.copy(c), 'TMP_c', show=False)
        print('%s  carrier to MAIN_pcb: %s, shared %.4f mm3' % (tag, d(k, X, cc, X.body('MAIN_pcb')), X.xv(X.tbm.copy(c), X.tbm.copy(X.body('MAIN_pcb')))))
        cc.deleteMe()


def pairs(k, X):
    cur = k.current(X, leads=True)
    for nm, key in NEW.items():
        t = k.c[key]; row = []
        for b in cur:
            if b.name == nm:
                continue
            other = k.c[NEW[b.name]] if b.name in NEW else X.tbm.copy(b)
            v = X.xv(t, other)
            if abs(v) > 0.0005:
                row.append((b.name, round(v, 3)))
        print('%-22s shares with: %s' % (nm, row))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'board': board, 'grid': grid, 'outer': outer, 'hood': hood, 'boxes': boxes, 'carrier': carrier, 'pairs': pairs}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, put=False):
    PUT[0] = put
    L['out']('p69_%s%s.txt' % (stage, '_put' if put else ''), _main, stage)
