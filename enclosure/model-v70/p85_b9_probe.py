# Block 9, for the three conditions of claude/architect-log-2026-11-26.md section 4.B. READ-ONLY (temporary bodies only).
#   'names'   every body of the unit as it stands (leads and keep-outs included) with its world box, volume and lump count
#   'lumps'   the lumps of named bodies with their world boxes and volumes
#   'near'    every body of the unit against a world box: shared volume and smallest distance (to find what stands in a place)
#   'leadseg' the laid lead (k.c['b9_lead'] pieces rebuilt from the points) piece by piece against named bodies' lumps
# Run: runpy.run_path(D + 'p85_b9_probe.py')['main'](stage, tag, **kw)  -> p85_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def names(k, X, **kw):
    rows = []
    for b in k.current(X, leads=True):
        rows.append((b.name, k.wbb(X, b), round(b.volume * 1000.0, 3), b.lumps.count, b.isLightBulbOn))
    for r in sorted(rows):
        print('%-28s %-52s %12.3f lumps %2d %s' % (r[0], r[1], r[2], r[3], 'shown' if r[4] else 'hidden'))
    print('%d bodies' % len(rows))


def lumpbox(k, X, l):
    t = X.tbm.copy(l)
    return k.wbb(X, t)


def lumps(k, X, bodies=(), **kw):
    for nm in bodies:
        b = k.c[nm[2:]] if nm.startswith('c:') else X.body(nm)
        print('%s: %d lumps' % (nm, b.lumps.count))
        rows = []
        for l in b.lumps:
            rows.append((lumpbox(k, X, l), round(l.volume * 1000.0, 3), l.faces.count))
        for i, r in enumerate(sorted(rows)):
            print('   %2d box %-52s %10.3f mm3 faces %d' % (i, r[0], r[1], r[2]))


def dist(k, X, a, b):
    A = X.add(X.tbm.copy(a), 'TMP_a', show=False); B = X.add(X.tbm.copy(b), 'TMP_b', show=False)
    r = X.mm.measureMinimumDistance(A, B); out = (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
    A.deleteMe(); B.deleteMe(); return out


def near(k, X, box=None, margin=3.0, extra=(), **kw):
    t = X.wbox(*box)
    grown = X.wbox(box[0] - margin, box[1] + margin, box[2] - margin, box[3] + margin, box[4] - margin, box[5] + margin)
    print('box %s, bodies within %.1f:' % (list(box), margin))
    src = [(b.name, b) for b in k.current(X, leads=True)] + [(e, k.c[e[2:]]) for e in extra]
    rows = []
    for nm, b in src:
        if k.late():
            print('time'); break
        if not grown.boundingBox.intersects(b.boundingBox):
            continue
        tb = X.tbm.copy(b)
        sh = X.xv(t, tb)
        d = dist(k, X, t, tb) if sh < 0.0005 else (0.0, '', '')
        if sh >= 0.0005 or d[0] <= margin:
            rows.append((d[0], -sh, nm, d[1], d[2]))
    for r in sorted(rows):
        print('   %-28s shared %9.3f  dist %6.3f  %s %s' % (r[2], -r[1], r[0], r[3], r[4]))


def leadseg(k, X, pts=None, bodies=(), r=1.3, **kw):
    for nm in bodies:
        b = X.body(nm)
        ls = [(lumpbox(k, X, l), X.tbm.copy(l)) for l in b.lumps]
        print('%s: %d lumps' % (nm, len(ls)))
        s0 = 0.0
        for a, e in zip(pts[:-1], pts[1:]):
            n = math.sqrt(sum((a[i] - e[i]) ** 2 for i in range(3)))
            c = X.cyl(a, e, r)
            for bx, l in ls:
                v = X.xv(c, l)
                if v > 0.0005:
                    # the stretch of this piece's axis inside the lump
                    st = k.needle_t(X, [l], a, e, 0.02)
                    print('   piece %s -> %s (%.1f long, from %.1f along the lead): %.3f mm3 in lump %s; axis inside over %s' % (
                        k.r2(a, 1), k.r2(e, 1), n, s0, v, bx, st))
            s0 += n


def _main(stage, kw):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'names': names, 'lumps': lumps, 'near': near, 'leadseg': leadseg}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag, **kw):
    L['out']('p85_%s.txt' % tag, _main, stage, kw)
