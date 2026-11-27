# Block 4, the close: read on the saved version. READ-ONLY (temporary bodies only). Outputs go to THIS pass's folder; the earlier
# passes' scripts are called by their own functions (each checked by its sha256) and their folders are only read.
#   matrix   the interference table by the method of the last passes (c3k.K4NS['matrix']): call again until FINISHED, then the
#            pairs new, gone and changed by more than 0.001 mm3 against version 88's (../box_margins_v85/m20_matrix_bm.json)
#   total    each changed body against its hidden copy _v88: what came and went (lumps, volume, world box), flat faces under
#            0.3 mm2 at new places, level faces (square to the print's upright) that differ with their height and the grid
#   table    every M3 x 8 and M2.5 x 6 into a printed part (the holes of ../model-v85/m11_holes.py): the hole as the part has it
#            now (radius, depth, both ends), what stands outside its mouth under the head (needles at the record's offset, two
#            sides), the head's seat, the tip, the room to the floor, the thread; the floor's height and landing in the print
#   walk     the shell's way down (../model-v80/d27_fits.st_walk): case, side, behind, to the side
#   walkadd  the same walk for what this pass added to each box (the box less its _v88 copy)
#   old70    one function of an earlier pass's script (s00_lib.OLD), with the helpers that added bodies to the document replaced
#            by ones that measure on temporary bodies (as ../model-v80/d60_close._old); compared line by line with a file of an
#            earlier close when ref is given
#   capway   the cap set lifted straight up (../model-v70/p64_b6_ways.capway, in parts: the lifts are given)
#   clampkey the precision driver straight out of each clamp screw's head (p64's clampkeys, with the head's height given)
#   plate    the screen plate onto the shell: the plate moved out along its screws' line (the slab's normal) by steps, what it
#            shares with the shell; at home its distance to the shell and the gap at the two lower bosses
#   cmp      compare a file of this folder with a file of an earlier close, line by line
# Run: L.checked('s50_close.py', sha)['main'](stage, tag, **kw)  -> s50_<stage>_<tag>.txt
import runpy, time, json, math, os
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
D85 = L['D85']; D80 = L['D80']; D70 = L['D70']
THRESH = 0.0005
ST = adsk.core.SurfaceTypes
CHANGED = ('SPKBOX_L', 'SPKBOX_R', 'HOUSING_F_front', 'HOUSING_F_door', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'SCREWS_M2x6_env')
CAPSET = ['HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env']
MODULE = ('SLAB_frame', 'LCD_', 'RESP_', 'MAIN_')


# ---------- the interference table ----------
def _norm(d):
    o = {}
    for p, v in d.items():
        a, b = [s.strip() for s in p.split('|')]
        o[tuple(sorted((a, b)))] = v
    return o


def st_matrix(k, X, tag='sr', sec=50, fresh=True, ref=D85 + 'm20_matrix_bm.json'):
    q = ('k4m', tag)
    if fresh and q not in k.c:
        h = k.hc(); n = 0
        for key in list(h.keys()):
            if isinstance(key, tuple) and key and key[0] in ('tc', 'tile'):
                del h[key]; n += 1
        print('dropped %d cached copies and slabs before a fresh table' % n)
    t0 = time.time(); k.budget(sec)
    res, left, nb = k.K4NS['matrix'](X, tag)
    print('%s  tag %s: bodies %d, pairs done %d, left this call %d, %.1f s' % (L['stamp'](), tag, nb, len(res), left, time.time() - t0))
    if left:
        return
    nz = {'%s | %s' % p: v for p, v in res.items() if abs(v) > THRESH}
    print('FINISHED: %d pairs, %d not zero (above %.4f mm3)' % (len(res), len(nz), THRESH))
    L['jdump']('s50_matrix_%s.json' % tag, {'tag': tag, 'read': L['stamp'](), 'bodies': nb, 'pairs': len(res), 'state': X.state(), 'not_zero': dict(sorted(nz.items()))})
    A = _norm(json.load(open(ref))['not_zero']); B = _norm(nz)
    print('version 88 (%s): %d pairs not zero; this table: %d' % (ref.split('/')[-1], len(A), len(B)))
    for p in sorted(set(B) - set(A)):
        print('NEW      %-58s %12.4f' % (' | '.join(p), B[p]))
    for p in sorted(set(A) - set(B)):
        print('GONE     %-58s %12.4f' % (' | '.join(p), A[p]))
    for p in sorted(set(A) & set(B)):
        if abs(A[p] - B[p]) > 0.001:
            print('CHANGED  %-58s %12.4f -> %12.4f' % (' | '.join(p), A[p], B[p]))
    print('same pairs, same volumes within 0.001: %d' % sum(1 for p in set(A) & set(B) if abs(A[p] - B[p]) <= 0.001))
    for n in CHANGED:
        rows = sorted((' | '.join(p), v) for p, v in B.items() if n in p)
        print('   pairs with %-16s %s' % (n + ':', rows if rows else 'none'))


# ---------- what changed, body by body ----------
def st_total(k, X, names=CHANGED, suf='_v88'):
    M10 = L['old']('m10')
    for n in names:
        b = X.body(n); o = X.body(n + suf)
        if o is None:
            print('%s: no copy %s' % (n, n + suf)); continue
        add = X.tbm.copy(b); X.dif(add, X.tbm.copy(o)); rem = X.tbm.copy(o); X.dif(rem, X.tbm.copy(b))
        la = X.lumps(add, maxv=1e9) if add.faces.count else []; lr = X.lumps(rem, maxv=1e9) if rem.faces.count else []
        print('%-16s now %.3f / %.3f (preflight / very high), the copy %.3f / %.3f; lumps %d, faces %d (copy %d)' % (
            n, b.volume * 1000.0, L['vhi'](b), o.volume * 1000.0, L['vhi'](o), b.lumps.count, b.faces.count, o.faces.count))
        print('   came %.4f mm3 in %d lumps: %s' % (sum(q[0] or 0 for q in la), len(la), la[:12]))
        print('   went %.4f mm3 in %d lumps: %s' % (sum(q[0] or 0 for q in lr), len(lr), lr[:12]))
        res = []
        for body in (b, o):
            res.append([(round(f.area * 100.0, 4), tuple(k.r2(k.W(f.pointOnFace), 1))) for f in body.faces if f.area * 100.0 < 0.3])
        was = set(q[1] for q in res[1])
        print('   faces under 0.3 mm2: now %d, the copy %d; not at a place of the copy: %s' % (len(res[0]), len(res[1]), [q for q in res[0] if q[1] not in was][:20]))
        if n not in M10['PRINT']:
            continue
        up = M10['up_dir'](k, n); lh = M10['PRINT'][n][3]; lv = []
        for body in (b, o):
            d = {}
            for f in body.faces:
                if f.geometry.surfaceType != ST.PlaneSurfaceType:
                    continue
                ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); nn = k.wv(nv); c = sum(nn[i] * up[i] for i in range(3))
                if abs(abs(c) - 1) > 1e-4:
                    continue
                h = round(M10['height'](k, n, k.W(f.pointOnFace)), 3); q = (h, 'up' if c > 0 else 'down'); d[q] = d.get(q, 0.0) + f.area * 100.0
            lv.append(d)
        rows = [(q, lv[0].get(q, 0.0), lv[1].get(q, 0.0)) for q in sorted(set(lv[0]) | set(lv[1])) if abs(lv[0].get(q, 0.0) - lv[1].get(q, 0.0)) > 0.005]
        print('   level faces that differ (prints %s, layers %.2f): %s' % (M10['PRINT'][n][0], lh, 'none' if not rows else ''))
        for q, a, c in rows:
            off = q[0] - round(q[0] / lh) * lh
            print('      height %8.3f %-4s off the grid %+.3f   %9.3f mm2 now / %9.3f the copy%s' % (q[0], q[1], off, a, c, '   OFF' if abs(off) > 0.002 and a > 0 else ''))


# ---------- the table of screws ----------
def holes_now(k, X):
    """m11's list with each hole read off its part as it stands: (part, mouth, far end, closed, offset, radius, depth)."""
    M11 = L['old']('m11'); out = {}; cache = {}
    for nm, (part, M, F, closed, off) in M11['H'].items():
        if part not in cache:
            cache[part] = [h for h in k.holes_of(X.body(part), 0.7, 2.15) if h['k'] == 'h']
        o = k.unit(tuple(F[i] - M[i] for i in range(3))); best = None
        for h in cache[part]:
            if abs(abs(sum(h['a'][i] * o[i] for i in range(3))) - 1.0) > 2e-3:
                continue
            for P, Q in ((h['A'], h['B']), (h['B'], h['A'])):
                dm = math.sqrt(sum((P[i] - M[i]) ** 2 for i in range(3)))
                if dm < 0.35 and (best is None or dm < best[0] or (abs(dm - best[0]) < 1e-6 and h['L'] > best[1]['L'])):
                    best = (dm, h, P, Q)
        if best is None:
            out[nm] = (part, M, F, closed, off, None, None); continue
        out[nm] = (part, tuple(best[2]), tuple(best[3]), closed, off, best[1]['r'], best[1]['L'])
    return out


def st_table(k, X, names=None, sec=55, reach=12.0):
    k.budget(sec)
    M10 = L['old']('m10')
    k.c.pop('m10_bodies', None)
    H = k.c.get('s50_holes')
    if H is None or k.c.get('s50_holes_v') != X.state()['version']:
        H = holes_now(k, X); k.c['s50_holes'] = H; k.c['s50_holes_v'] = X.state()['version']
    for nm in (names or sorted(H)):
        part, M, F, closed, off, r, depth = H[nm]
        if r is None:
            print('%-7s %s: NO HOLE FOUND on the axis from %s' % (nm, part, M)); continue
        Ls = 6.0 if nm.startswith('pi_') else 8.0
        o = k.unit(tuple(M[i] - F[i] for i in range(3))); u, v = M10['perp'](o)
        E = tuple(M[i] + o[i] * reach for i in range(3))
        near = M10['near_bodies'](k, X, M, E, off + 0.5); stack = []
        for n in near:
            if n == part:
                continue
            pl = k.parts(X, n); seg = []
            for w in (u, tuple(-q for q in u)):
                p0 = tuple(M[i] - o[i] * 1.0 + w[i] * off for i in range(3)); p1 = tuple(E[i] + w[i] * off for i in range(3))
                seg += [(round(a - 1.0, 2), round(c - 1.0, 2)) for a, c in k.needle_t(X, pl, p0, p1, 0.02)]
            if seg:
                stack.append((min(s[0] for s in seg), max(s[1] for s in seg if s[0] <= min(q[0] for q in seg) + 0.01), n, sorted(set(seg))))
        stack.sort()
        seat = None; chain = []
        for a, c, n, seg in stack:
            if a < -0.05:
                continue
            if seat is None:
                if a <= 0.5:
                    seat = c; chain.append((n, a, c))
            elif a <= seat + 0.45:
                if c > seat:
                    seat = c
                chain.append((n, a, c))
        pt = k.Wp(*F); row = ''
        up = M10['up_dir'](k, part); lh = M10['PRINT'][part][3]; dd = sum(-o[i] * up[i] for i in range(3)); ht = M10['height'](k, part, F)
        lean = math.degrees(math.acos(min(1.0, abs(dd))))
        if closed:
            if abs(dd) < 0.02:
                row = 'lies in the layers'
            else:
                looks = 'down' if dd > 0 else 'up'
                row = 'floor height %.3f looks %s, lands %s%s' % (ht, looks, M10['land'](ht, lh, looks)[0], '' if lean < 0.5 else ' (leans %.1f deg)' % lean)
        G = tuple(F[i] - o[i] * 10.0 for i in range(3))
        beh = k.needle_t(X, k.parts(X, part), F, G, 0.02) if closed else None
        if seat is None:
            print('%-7s %-16s r %.3f, %.3f deep %s | nothing under the head within 0.5 of the mouth; stack %s' % (nm, part, r, depth, 'closed' if closed else 'open', [(n, a, c) for a, c, n, s in stack]))
        else:
            tip = Ls - seat
            print('%-7s %-16s r %.3f, %.3f deep %s | under the head %s -> seat %.2f out, tip %.2f in, %s%s | %s | behind the floor %s' % (
                nm, part, r, depth, 'closed' if closed else 'open', [(n.replace('HOUSING_F_', ''), a, c) for n, a, c in chain], seat, tip,
                ('ROOM %.2f' % (depth - tip)) if closed else 'through',
                '; with the gap of %.2f drawn up %.2f' % (chain[0][1], depth - tip - chain[0][1]) if closed and chain[0][1] > 0.05 else '',
                row, beh))
        if k.late():
            print('time: run again from the next'); return


# ---------- the shell's way down ----------
def st_walk(k, X, case='boxes', side='L', bs=(0.95, 1.6), s=0.0, sec=60, step=0):
    L['old']('d27')['st_walk'](k, X, case=case, side=side, bs=bs, s=s, sec=sec, step=step)


def st_walkadd(k, X, cases=('frame', 'boxes'), sides=('L', 'R'), offs=(0.0, 0.25, -0.25), bs=(0.95, 1.3, 1.6), sec=60, suf='_v88'):
    k.budget(sec)
    F27 = L['old']('d27')
    for side in sides:
        sx = 1 if side == 'L' else -1
        add = X.tbm.copy(X.body('SPKBOX_' + side)); X.dif(add, X.tbm.copy(X.body('SPKBOX_%s%s' % (side, suf))))
        print('SPKBOX_%s: added against %s %.3f mm3 in %d lumps, world box %s' % (side, suf, X.vol(add), add.lumps.count, k.wbb(X, add)))
        for case in cases:
            names, boxes, near, hs = F27['CASES'][case]
            crops = [L['crop'](X, 'HOUSING_F_front', bx) for bx in boxes(sx)]
            m = X.tbm.copy(add)
            if case == 'frame':
                X.sec(m, X.wbox(-110, 110, -53.0, -47.0, -1, 85))
            if case == 'boxes':
                X.sec(m, X.wbox(-110, 110, -16.0, 8.0, -1, 90))
            if not m.faces.count:
                print('   %-6s: nothing added inside the walk\'s crop' % case); continue
            print('   %-6s: added inside the walk\'s crop %.3f mm3' % (case, X.vol(m)))
            for so in offs:
                for b in bs:
                    hit = []
                    for h in hs:
                        t = X.move(X.tbm.copy(m), so, -b, -h)
                        vv = sum(X.xv(t, cr) for cr in crops)
                        if vv > 0.0005:
                            hit.append((h, round(vv, 4)))
                    print('      %+.2f to the side, %.2f behind: %s' % (so, b, ('meets at %s' % hit[:6]) if hit else 'clear at every lift (%d to %.1f)' % (len(hs), hs[-1])))
                    if k.late():
                        print('time'); return


# ---------- earlier passes' functions ----------
def dist_t(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))


def mind_t(k, X, t, fixed):
    best = None
    for nm, f in fixed:
        d = X.mm.measureMinimumDistance(t, f).value * 10.0
        if best is None or d < best[0]:
            best = (round(d, 2), nm)
    return best


def st_old70(k, X, key, fun, kw=None, setg=None, sec=60):
    k.budget(sec)
    m = L['old'](key); func = fun
    g = m[func].__globals__
    if 'dist' in g and g['dist'].__code__.co_argcount == 4:
        g['dist'] = dist_t
    if 'mind' in g:
        g['mind'] = mind_t
    for name, val in (setg or {}).items():
        g[name] = val
    if 'k_' in g:
        g['k_'] = k
    if 'ctmp' in g:
        g['ctmp'] = lambda X_, name, box: L['crop'](X_, name, box)
    print('%s.%s(%s)' % (key, func, kw or ''))
    m[func](k, X, **(kw or {}))


def lines(text):
    return [l.rstrip() for l in text.splitlines() if l.strip() and not l.startswith('20') and not l.lstrip().startswith(('time', '%', '[')) and '.st_' not in l[:12]
            and not l.startswith(('p64.', 'p95.', 'p37.', 'p71.', 'p97.', 'd52.', 'd27.', 'm17.', 'm12.'))]


def compare(new_text, ref, maxd=14, width=230):
    out = []
    if not os.path.exists(ref):
        return ['no file %s' % ref]
    a = lines(open(ref).read()); b = lines(new_text)
    if len(a) == len(b):
        df = [(x, y) for x, y in zip(a, b) if x != y]
        out.append('against %s: %d lines, %d differ' % (ref.replace(os.path.dirname(os.path.dirname(ref.rstrip('/'))), '..'), len(b), len(df)))
        for x, y in df[:maxd]:
            out.append('   was: ' + x.strip()[:width]); out.append('   now: ' + y.strip()[:width])
        if len(df) > maxd:
            out.append('   ... %d more' % (len(df) - maxd))
    else:
        sa = set(a); sb = set(b)
        gone = [x for x in a if x not in sb]; new = [y for y in b if y not in sa]
        out.append('against %s: %d lines then, %d now; %d only then, %d only now' % (ref.replace(os.path.dirname(os.path.dirname(ref.rstrip('/'))), '..'), len(a), len(b), len(gone), len(new)))
        for x in gone[:maxd]:
            out.append('   then: ' + x.strip()[:width])
        for y in new[:maxd]:
            out.append('   now:  ' + y.strip()[:width])
    return out


# ---------- the cap ----------
def capfixed(k, X):
    q = ('s50_capfix', X.state()['version'])
    if q in k.c:
        return k.c[q]
    fx = []
    for b in k.current(X, leads=False, kos=False):
        n = b.name
        if n in CAPSET or n.startswith(MODULE) or n == 'SCREWS_M2x6_env' or n.startswith('LEAD_'):
            continue
        fx.append(b)
    zone = X.wbox(-110, 110, -70, 10, 150, 215); fixc = []
    for b in fx:
        t = X.tbm.copy(b)
        if not t.boundingBox.intersects(zone.boundingBox):
            continue
        X.sec(t, X.tbm.copy(zone))
        if t.faces.count:
            fixc.append((b.name, t))
    k.c[q] = (sorted(b.name for b in fx), fixc)
    return k.c[q]


def st_capway(k, X, lifts=(0.0, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0), sec=55, head=True):
    """p64_b6_ways.capway, its lines, with the lifts given so that it runs in parts. The fixed bodies' crops are kept between calls."""
    k.budget(sec)
    names, fixc = capfixed(k, X)
    if head:
        print('fixed bodies (%d): %s' % (len(names), names))
    movers = [X.tbm.copy(X.body(n)) for n in CAPSET]
    for sx in (1, -1):
        c = X.cyl((sx * 15.5, -35.2, 171.5), (sx * 15.5, -35.2, 180.0), 2.6); X.sec(c, X.tbm.copy(X.body('SCREWS_M2x6_env'))); movers.append(c)
        if head:
            print('   the clamp screw at x %+.1f rides with the cap: world box %s' % (sx * 15.5, k.wbb(X, c)))
    if head:
        print('within reach of the cap (z 150..215): %s' % [n for n, t in fixc])
    for h in lifts:
        hit = {}
        for m in movers:
            mv = X.move(X.tbm.copy(m), 0, 0, h)
            for n, t in fixc:
                vv = X.xv(mv, t)
                if abs(vv) > 0.0005:
                    hit[n] = round(hit.get(n, 0.0) + vv, 4)
        print('lift %5.2f: %s' % (h, hit if hit else 'clear'))
        if k.late():
            print('time: run again from the next lift'); return


def st_clampkey(k, X, z=172.0):
    bench = [X.body(n) for n in CAPSET + ['LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_VEML']]
    for sx in (1, -1):
        o = (sx * 15.5, -35.2, z)
        print('clamp screw at x %+.1f, head at z %.1f, driver along -z:' % (sx * 15.5, z))
        print('   MICRO ', k.fm(k.line(X, o, (0, 0, -1), k.MICRO, bench, st0=0.5, step=1.0)))
    for sx in (1, -1):
        s = 'L' if sx > 0 else 'R'
        c = X.cyl((sx * 15.5, -35.2, 171.5), (sx * 15.5, -35.2, 180.0), 2.6); X.sec(c, X.tbm.copy(X.body('SCREWS_M2x6_env')))
        near = []
        for b in k.current(X, leads=True, kos=True):
            if b.name in ('SCREWS_M2x6_env', 'MIC_CLAMP_' + s, 'HOUSING_F_cap'):
                continue
            if not c.boundingBox.intersects(b.boundingBox):
                bb = k.wbb(X, b); cb = k.wbb(X, c)
                if bb[0] > cb[1] + 8 or bb[1] < cb[0] - 8 or bb[2] > cb[3] + 8 or bb[3] < cb[2] - 8 or bb[4] > cb[5] + 8 or bb[5] < cb[4] - 8:
                    continue
            r = X.mm.measureMinimumDistance(c, b)
            if r.value * 10.0 < 8.0:
                near.append((round(r.value * 10.0, 3), b.name, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)))
        print('the %s clamp\'s screw at home, every body of the unit within 8 (clamp and cap left out): %s' % (s, sorted(near)))


# ---------- the screen plate onto the shell ----------
def st_plate(k, X, steps=(0.0, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0), sec=55, home=True):
    k.budget(sec)
    P = X.body('HOUSING_F_plate'); S = X.body('HOUSING_F_front')
    if home:
        r = X.mm.measureMinimumDistance(P, S)
        print('the screen plate to the shell at home: %.4f at %s / %s' % (r.value * 10.0, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)))
        n = k.wv(adsk.core.Vector3D.create(0, 1, 0))                    # design +y = out of the slab toward the viewer
        print('   the way: along the slab\'s normal toward the viewer, world %s (the two lower screws\' line)' % (k.r2(n, 4),))
        for sx in (1, -1):
            M = (sx * 85.0, 5.7, 60.68); o = (0.0, 0.9781, 0.2079)
            a = tuple(M[i] - o[i] * 8.0 for i in range(3)); c = tuple(M[i] + o[i] * 6.0 for i in range(3))
            for off, lab in ((0.0, 'on the axis'), (2.3, '2.3 off the axis')):
                a2 = (a[0] + off, a[1], a[2]); c2 = (c[0] + off, c[1], c[2])
                sp = [(round(p - 8.0, 2), round(q - 8.0, 2)) for p, q in k.needle_t(X, [k.tcopy(X, 'HOUSING_F_plate')], a2, c2, 0.02)]
                ss = [(round(p - 8.0, 2), round(q - 8.0, 2)) for p, q in k.needle(X, 'HOUSING_F_front', a2, c2, 0.02)]
                print('   lower screw at x %+.0f, %s, mm outward from the boss\'s face: the shell solid %s, the screen plate solid %s' % (sx * 85, lab, ss, sp))
    parts = k.parts(X, 'HOUSING_F_front'); pc = k.tcopy(X, 'HOUSING_F_plate')
    for d in steps:
        t = X.tbm.copy(pc); k.K.move_n(X, t, d)
        vv = sum(X.xv(t, p) for p in parts)
        print('the screen plate %5.1f out: shares %.4f mm3 with the shell' % (d, vv))
        if k.late():
            print('time: run again from the next step'); return


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'matrix': st_matrix, 'total': st_total, 'table': st_table, 'walk': st_walk, 'walkadd': st_walkadd, 'old70': st_old70, 'capway': st_capway,
     'clampkey': st_clampkey, 'plate': st_plate}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', ref=None, **kw):
    fn = 's50_%s%s.txt' % (stage, ('_' + tag) if tag else '')
    if stage == 'cmp':
        res = compare(open(D + kw['mine']).read(), ref); open(D + fn, 'w').write('\n'.join(res) + '\n'); return
    L['out'](fn, _main, stage, **kw)
    if ref:
        res = compare(open(D + fn).read(), ref)
        open(D + fn.replace('.txt', '_cmp.txt'), 'w').write('\n'.join(res) + '\n')
# END
