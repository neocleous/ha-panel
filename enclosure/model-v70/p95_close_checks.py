# The close (brief block 10; architect logs 2026-11-25-b section 4.C and 2026-11-26 section 4.C): checks read on the saved
# version. READ-ONLY but for TMP_ bodies, deleted again.
#   'door'        the door's stand on the base plate's two rear lands, read on both sides (D422): the plate's and the door's level
#                 faces round each land, the smallest distance door to plate there, and the area in contact (the door set 0.02
#                 lower shares that area times 0.02 with the plate)
#   'ride'        the display module's ride-in by the last pass's method (K4NS ride_in: every piece of the module at every step
#                 against the shell, the unit and what is fixed in them), leads left out; stops when its time is used up: call
#                 again until nothing is left
#   'rideholder'  the same steps for every body of the module against the radar's holder, the radar and its two screws, which the
#                 library's groups do not know at their new place
#   'grid17'      the layer grid over all 17 printed parts: every flat face square to the part's print height, with its height
#                 above the bed; per part the count on and off the grid, and each face off it (0.2 mm2 or more) with its place
#   'gridfit'     for each of those faces of 1.0 mm2 or more, on the parts whose print height is a world axis: which body of the unit
#                 stands in front of it within 0.6, and how near (in contact = a seat)
#   'main01'      D440: the main board's bodies (MAIN_*) as one, moved 0.1 out along the board's normal, away from the carrier:
#                 against every body within 3 of them, the smallest distance and the shared volume at home and 0.1 out; and the
#                 holder's key (p89's sweep) at 40 to 55 deg against the moved board, the Pi power plug's envelope left out
# Run: runpy.run_path(D + 'p95_close_checks.py')['main'](stage)  -> p95_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
HN = (0.11394, 0.09756, 0.98869); HP0 = (-69.8829, -39.0603, 110.0342)        # the hood's print: normal of its top plate, a point on its outer face (p69)
SN = (0.0, 0.978148, 0.207912)                                                 # the screen's normal in the world (p69)


def dist(k, X, a, b):
    A = X.add(X.tbm.copy(a), 'TMP_a', show=False); B = X.add(X.tbm.copy(b), 'TMP_b', show=False)
    r = X.mm.measureMinimumDistance(A, B); out = (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
    A.deleteMe(); B.deleteMe(); return out


def crop(X, body, box):
    c = X.wbox(*box); X.sec(c, X.tbm.copy(body)); return c


def door(k, X):
    Dr = X.body('HOUSING_F_door'); P = X.body('FLOOR_PLATE')
    for lab, box in (('right rear land, viewer\'s right (x -19, y -77)', (-29.0, -9.0, -86.0, -68.0, 1.8, 4.2)),
                     ('left rear land, viewer\'s left (x +19, y -74.5)', (9.0, 29.0, -86.0, -66.0, 1.8, 4.2))):
        d = crop(X, Dr, box); p = crop(X, P, box)
        print('%s; box %s' % (lab, box))
        for nm, b in (('plate', p), ('door', d)):
            rows = []
            for f in b.faces:
                if f.geometry.surfaceType != 0:
                    continue
                ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv); q = k.W(f.pointOnFace)
                if abs(abs(n[2]) - 1) < 1e-4 and 1.9 < q[2] < 4.1:
                    rows.append((round(q[2], 3), 'up' if n[2] > 0 else 'down', round(f.area * 100.0, 2), k.r2(q)))
            for r in sorted(rows):
                print('   %-5s level face z %.3f looks %-4s %8.2f mm2 at %s' % ((nm,) + r))
        print('   door to plate, smallest distance: %s' % (dist(k, X, d, p),))
        for dz in (0.02, 0.05):
            t = X.move(X.tbm.copy(d), 0, 0, -dz)
            v = X.xv(t, p)
            print('   door set %.2f lower: shares %.4f mm3 with the plate -> %.2f mm2 in contact' % (dz, v, v / dz))
        t = X.move(X.tbm.copy(d), 0, 0, 0.0)
        print('   door at home shares %.4f mm3 with the plate here' % X.xv(t, p))


def _groups(k, X):
    keep = {}
    for g in ('SHELL', 'PLATE', 'PI', 'PIPWR', 'CRADLE', 'INLET', 'BOXES', 'USBA', 'TOUCH', 'RADAR', 'BME', 'DISP', 'RESP', 'MAIN', 'UNIT', 'MODULE'):
        keep[g] = list(k.ST[g])
        k.ST[g] = [n for n in k.ST[g] if n.endswith('*') or X.body(n) is not None]
        if k.ST[g] != keep[g]:
            print('group %s: left out %s' % (g, sorted(set(keep[g]) - set(k.ST[g]))))
    return keep


def ride(k, X, leads=False):
    k.budget(68)
    keep = _groups(k, X)
    try:
        res, left = k.K4NS['ride_in'](X, 'close79', leads=leads)
    finally:
        for g, v in keep.items():
            k.ST[g] = v
    hits = {str(key): v for key, v in res.items() if v and 'no part in the box' not in v}
    print('ride-in, the whole module, %s: %d positions done, left %d; positions with an overlap: %s' % ('with the leads\' parts that ride with it' if leads else 'leads left out', len(res), left, hits if hits else 'none'))


def rideholder(k, X):
    k.budget(68)
    keep = _groups(k, X)
    try:
        mods = [b.name for b in k.st(X, 'MODULE')]
    finally:
        for g, v in keep.items():
            k.ST[g] = v
    fixed = [('RADAR_HOLDER', X.tbm.copy(X.body('RADAR_HOLDER'))), ('LD2410C_env_F', X.tbm.copy(X.body('LD2410C_env_F')))]
    s = X.wbox(18, 45, -8, 3, 27, 52); X.sec(s, X.tbm.copy(X.body('SCREWS_M2x6_env'))); fixed.append(('the radar\'s two screws', s))
    steps = k.K4NS['STEPS']
    done = k.c.setdefault('close_rideholder', {})
    n_hit = 0
    for nm in mods:
        if nm in done:
            continue
        if k.late():
            print('time: call again'); break
        b = X.body(nm)
        wb = k.wbb(X, b)
        # the holder's box, grown by the ride's length along the screen's normal and 2 all round
        if wb[1] < -4.0 or wb[0] > 46.5 or wb[5] < 25.6 - 13.0 or wb[4] > 64.0 or wb[3] < -12.7 - 60.0 or wb[2] > 5.4:
            done[nm] = 'far'; continue
        row = {}
        for st in steps:
            t = X.move_n(X.tbm.copy(b), st)
            for fn, fb in fixed:
                v = X.xv(t, fb)
                if abs(v) > 0.0005:
                    row[(st, fn)] = round(v, 3)
        done[nm] = row
    near = {n: r for n, r in done.items() if r != 'far'}
    print('module bodies %d; done %d; near the holder %d: %s' % (len(mods), len(done), len(near), sorted(near)))
    print('overlaps on the ride-in: %s' % ({n: r for n, r in near.items() if r} or 'none'))
    if len(done) == len(mods):
        near_d = {}
        H = X.body('RADAR_HOLDER')
        for n in sorted(near):
            if k.late():
                break
            near_d[n] = dist(k, X, X.body(n), H)[0]
        print('at home, to the holder: %s' % near_d)


def _off(h, lh, first=None):
    if first is not None:
        if abs(h) < 1e-6 or abs(h - first) < 1e-4:
            return 0.0
        q = (h - first) / lh
        return (q - round(q)) * lh
    q = h / lh
    return (q - round(q)) * lh


def grid17(k, X, only=None):
    spec = [('HOUSING_F_front', 'chin down, bed at y 6.7992', lambda p, q: 6.7992 - p[1], (0.0, 1.0, 0.0), 0.2, None),
            ('HOUSING_F_plate', 'back down, height 12.8 - d', lambda p, q: 12.8 - q[1], 'S', 0.2, None),
            ('SLAB_frame', 'glass side down, height d', lambda p, q: q[1], 'S', 0.1, None),
            ('RESP_CARRIER', 'plate down, height d - 15.2', lambda p, q: q[1] - 15.2, 'S', 0.2, None),
            ('HOUSING_F_door', 'standing, bed at z 2.8', lambda p, q: p[2] - 2.8, (0.0, 0.0, 1.0), 0.2, None),
            ('HOUSING_F_cap', 'top face down, height 180 - z', lambda p, q: 180.0 - p[2], (0.0, 0.0, 1.0), 0.1, None),
            ('FLOOR_PLATE', 'underside down, height z', lambda p, q: p[2], (0.0, 0.0, 1.0), 0.2, None),
            ('SPKBOX_L', 'rear face down, bed at its lowest y', None, (0.0, 1.0, 0.0), 0.2, None),
            ('SPKBOX_R', 'rear face down, bed at its lowest y', None, (0.0, 1.0, 0.0), 0.2, None),
            ('CRADLE_5807', 'rear face down, bed at its lowest y', None, (0.0, 1.0, 0.0), 0.2, None),
            ('TOUCH_CLIP_L', 'as fitted, bed at z 30.0', lambda p, q: p[2] - 30.0, (0.0, 0.0, 1.0), 0.2, None),
            ('TOUCH_CLIP_R', 'the left clip turned top for bottom: bed at z 46.0, height 46 - z', lambda p, q: 46.0 - p[2], (0.0, 0.0, 1.0), 0.2, None),
            ('GROMMET_usbc_F', 'on its side, bed at z 10.0, first layer 0.20 then 0.12', lambda p, q: p[2] - 10.0, (0.0, 0.0, 1.0), 0.12, 0.2),
            ('BME_HOOD', 'top plate\'s outer face down', lambda p, q: sum((HP0[i] - p[i]) * HN[i] for i in range(3)), HN, 0.2, None),
            ('MIC_CLAMP_L', 'as fitted, underside down, bed at z 172.7', lambda p, q: p[2] - 172.7, (0.0, 0.0, 1.0), 0.2, None),
            ('MIC_CLAMP_R', 'as fitted, underside down, bed at z 172.7', lambda p, q: p[2] - 172.7, (0.0, 0.0, 1.0), 0.2, None),
            ('RADAR_HOLDER', 'upright, bed at z 27.6', lambda p, q: p[2] - 27.6, (0.0, 0.0, 1.0), 0.2, None)]
    for name, how, hf, dr, lh, first in spec:
        if only and name not in only:
            continue
        if k.late():
            print('time: call again with only=...'); break
        b = X.body(name)
        if hf is None:
            y0 = k.wbb(X, b)[2]
            hf = (lambda y0: (lambda p, q: p[1] - y0))(y0)
            how += ' (y %.3f)' % y0
        rows = []
        for f in b.faces:
            if f.geometry.surfaceType != 0:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            if dr == 'S':
                if abs(abs(nv.y) - 1) > 1e-4:
                    continue
            else:
                n = k.unit(k.wv(nv)); d = k.unit(dr)
                if abs(abs(sum(n[i] * d[i] for i in range(3))) - 1) > (1e-3 if name == 'BME_HOOD' else 1e-4):
                    continue
            p = k.W(f.pointOnFace); q = k.Sf(f.pointOnFace)
            h = hf(p, q)
            rows.append((round(h, 4), round(_off(h, lh, first), 4), round(f.area * 100.0, 2), k.r2(p)))
        offg = [r for r in rows if abs(r[1]) > 0.004]
        big = [r for r in offg if r[2] >= 0.2]
        print('%s (%s, layers %.2f): %d level faces, %d on the grid, %d off it (%d of them 0.2 mm2 or more, %.2f mm2 in all)' % (
            name, how, lh, len(rows), len(rows) - len(offg), len(offg), len(big), sum(r[2] for r in offg)))
        for r in sorted(big, key=lambda r: -r[2])[:60]:
            print('   height %9.4f  off %+.4f  %9.2f mm2  at %s' % r)
        if len(big) > 60:
            print('   ... %d more' % (len(big) - 60))


def gridfit(k, X, only=None):
    # for each level face off its grid (1.0 mm2 or more) of the parts whose print height is a world axis: what stands in front of it.
    # A slab 0.3 thick behind the face (the part cropped to the face's own box) is moved out of the face by s; the first s at which it
    # shares volume with another body of the unit is that body's distance class: 0.02 = in contact (a seat), then 0.1, 0.2, 0.3, 0.45, 0.6.
    k.budget(66)
    spec = [('HOUSING_F_front', 1, lambda p: 6.7992 - p[1], 0.2), ('HOUSING_F_door', 2, lambda p: p[2] - 2.8, 0.2),
            ('HOUSING_F_cap', 2, lambda p: 180.0 - p[2], 0.1), ('FLOOR_PLATE', 2, lambda p: p[2], 0.2),
            ('SPKBOX_L', 1, lambda p: p[1] + 52.0, 0.2), ('SPKBOX_R', 1, lambda p: p[1] + 52.0, 0.2),
            ('CRADLE_5807', 1, lambda p: p[1] + 84.6, 0.2), ('TOUCH_CLIP_L', 2, lambda p: p[2] - 30.0, 0.2),
            ('TOUCH_CLIP_R', 2, lambda p: 46.0 - p[2], 0.2), ('RADAR_HOLDER', 2, lambda p: p[2] - 27.6, 0.2)]
    done = k.c.setdefault('close_gridfit', {})
    others_all = [b for b in k.current(X, leads=False, kos=False)]
    obox = {b.name: k.wbb(X, b) for b in others_all}
    for name, ax, hf, lh in spec:
        if only and name not in only:
            continue
        b = X.body(name)
        faces = []
        for i, f in enumerate(b.faces):
            if f.geometry.surfaceType != 0 or f.area * 100.0 < 1.0:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
            if abs(abs(n[ax]) - 1) > 1e-4:
                continue
            p = k.W(f.pointOnFace); h = hf(p); off = h - round(h / lh) * lh
            if abs(off) <= 0.004:
                continue
            faces.append((i, f, n, p, h, off))
        for i, f, n, p, h, off in faces:
            key = (name, i)
            if key in done:
                continue
            if k.late():
                break
            pts = [k.W(v.geometry) for v in f.vertices]
            for e in f.edges:
                ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, sp = ev.getStrokes(t0, t1, 0.01)
                pts += [k.W(q) for q in sp]
            bb = [min(q[0] for q in pts), max(q[0] for q in pts), min(q[1] for q in pts), max(q[1] for q in pts), min(q[2] for q in pts), max(q[2] for q in pts)]
            sgn = 1.0 if n[ax] > 0 else -1.0
            lo = p[ax] - 0.3 if sgn > 0 else p[ax]; hi = p[ax] if sgn > 0 else p[ax] + 0.3
            bx = list(bb); bx[2 * ax] = lo; bx[2 * ax + 1] = hi
            piece = X.wbox(*bx); X.sec(piece, X.tbm.copy(b))
            near = []
            if piece.faces.count:
                for ob in others_all:
                    if ob.name == name:
                        continue
                    w = obox[ob.name]
                    if w[1] < bb[0] - 0.1 or w[0] > bb[1] + 0.1 or w[3] < bb[2] - 0.1 or w[2] > bb[3] + 0.1 or w[5] < bb[4] - 0.1 or w[4] > bb[5] + 0.1:
                        # not over the face's box at all, unless it lies in front within 0.7
                        g = list(bb); g[2 * ax] -= 0.7; g[2 * ax + 1] += 0.7
                        if w[1] < g[0] or w[0] > g[1] or w[3] < g[2] or w[2] > g[3] or w[5] < g[4] or w[4] > g[5]:
                            continue
                    g = list(bb); g[2 * ax] -= 1.0; g[2 * ax + 1] += 1.0
                    c = X.wbox(*g); X.sec(c, X.tbm.copy(ob))
                    if not c.faces.count:
                        continue
                    for sft in (0.02, 0.1, 0.2, 0.3, 0.45, 0.6):
                        d = [0.0, 0.0, 0.0]; d[ax] = sgn * sft
                        t = X.move(X.tbm.copy(piece), d[0], d[1], d[2])
                        if X.xv(t, c) > 1e-4:
                            near.append((ob.name, sft)); break
            done[key] = (round(h, 3), round(off, 3), round(f.area * 100.0, 2), 'looks at the bed' if (hf((p[0] + n[0], p[1] + n[1], p[2] + n[2])) < h) else 'looks up', k.r2(p), sorted(near, key=lambda q: q[1]))
        rows = [done[(name, i)] for i, f, n, p, h, off in faces if (name, i) in done]
        print('%s: %d level faces of 1.0 mm2 or more off the grid; read %d' % (name, len(faces), len(rows)))
        for r in sorted(rows, key=lambda r: (r[0], r[4])):
            print('   height %8.3f off %+.3f %9.2f mm2 %-16s at %-24s in front: %s' % (r[0], r[1], r[2], r[3], r[4], r[5] or 'nothing within 0.6'))
        if k.late():
            print('time: call again'); break


def main01(k, X):
    k.budget(70)
    names = [b.name for b in X.root.bRepBodies if b.name.startswith('MAIN_') and not b.name.endswith(('_v67', '_v68', '_v69'))]
    cur = set(b.name for b in k.current(X, leads=True, kos=True))
    names = [n for n in names if n in cur]
    pcb = X.body('MAIN_pcb')
    big = sorted((f for f in pcb.faces if f.geometry.surfaceType == 0), key=lambda f: -f.area)[0]
    ok, nv = big.evaluator.getNormalAtPoint(big.pointOnFace); n = k.unit(k.wv(nv))
    wb = k.wbb(X, pcb); cb = k.wbb(X, X.body('RESP_CARRIER'))
    cm = [(wb[0] + wb[1]) / 2, (wb[2] + wb[3]) / 2, (wb[4] + wb[5]) / 2]; cc = [(cb[0] + cb[1]) / 2, (cb[2] + cb[3]) / 2, (cb[4] + cb[5]) / 2]
    if sum((cm[i] - cc[i]) * n[i] for i in range(3)) < 0:
        n = tuple(-w for w in n)
    print('the main board\'s bodies: %s' % names)
    print('out = the board\'s normal away from the carrier: %s' % (k.r2(n, 4),))
    U = None
    for nm in names:
        t = X.tbm.copy(X.body(nm)); U = t if U is None else X.uni(U, t)
    ub = k.wbb(X, U)
    M = X.move(X.tbm.copy(U), 0.1 * n[0], 0.1 * n[1], 0.1 * n[2])
    print('as one body: %.3f mm3, box %s' % (X.vol(U), ub))
    key = 'close_main01'
    done = k.c.setdefault(key, {})
    others = [b for b in k.current(X, leads=True, kos=True) if b.name not in names]
    for b in others:
        if b.name in done:
            continue
        if k.late():
            print('time: call again'); break
        bb = k.wbb(X, b)
        if bb[1] < ub[0] - 3 or bb[0] > ub[1] + 3 or bb[3] < ub[2] - 3 or bb[2] > ub[3] + 3 or bb[5] < ub[4] - 3 or bb[4] > ub[5] + 3:
            done[b.name] = None; continue
        c = crop(X, b, (ub[0] - 4, ub[1] + 4, ub[2] - 4, ub[3] + 4, ub[4] - 4, ub[5] + 4))
        if not c.faces.count:
            done[b.name] = None; continue
        v0 = X.xv(U, c); v1 = X.xv(M, c)
        d0 = 0.0 if abs(v0) > 0.0005 else dist(k, X, U, c)[0]
        d1 = 0.0 if abs(v1) > 0.0005 else dist(k, X, M, c)[0]
        done[b.name] = (round(v0, 3), round(v1, 3), d0, d1)
    rows = [(nm, r) for nm, r in done.items() if r is not None and (r[2] < 3.0 or r[3] < 3.0)]
    print('bodies done %d of %d; within 3 of the board: %d' % (len(done), len(others), len(rows)))
    print('%-28s %12s %12s %10s %10s' % ('body', 'shared home', 'shared 0.1', 'dist home', 'dist 0.1'))
    for nm, r in sorted(rows, key=lambda q: (min(q[1][2], q[1][3]), q[0])):
        flag = ''
        if abs(r[0]) <= 0.0005 and abs(r[1]) > 0.0005:
            flag = '  <- newly shared'
        elif r[3] < r[2] - 1e-6:
            flag = '  closer'
        print('%-28s %12.3f %12.3f %10.3f %10.3f%s' % (nm, r[0], r[1], r[2], r[3], flag))
    if len(done) == len(others) and not k.late():
        # the key works with the Pi power plug out (p89): its envelope on J2 is left out of the board here
        U = None
        for nm in names:
            if nm != 'MAIN_J2_plug_env':
                t = X.tbm.copy(X.body(nm)); U = t if U is None else X.uni(U, t)
        M = X.move(X.tbm.copy(U), 0.1 * n[0], 0.1 * n[1], 0.1 * n[2])
        M3 = (-7.35, 57.6); xe = 21.0
        for phi in (40, 45, 50, 55):
            r = math.radians(phi)
            arm = X.cyl((xe, M3[0], M3[1]), (xe, M3[0] - 101.0 * math.cos(r), M3[1] + 101.0 * math.sin(r)), 1.2)
            v0 = X.xv(arm, U); v1 = X.xv(arm, M)
            print('the holder\'s key at %d deg (Pi power plug out): shares %.3f with the board at home, %.3f with it 0.1 out; distance %s / %s' % (
                phi, v0, v1, 0.0 if v0 > 0.0005 else dist(k, X, arm, U)[0], 0.0 if v1 > 0.0005 else dist(k, X, arm, M)[0]))


def _main(stage, kw):
    k = L['load'](); X = k.K(); k.budget(72)
    print(L['stamp'](), 'before', X.state())
    try:
        {'door': door, 'ride': ride, 'rideholder': rideholder, 'grid17': grid17, 'gridfit': gridfit, 'main01': main01}[stage](k, X, **kw)
    finally:
        for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
            b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('p95_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, kw)
