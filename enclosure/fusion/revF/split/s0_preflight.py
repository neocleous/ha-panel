# Front shell split pass (2026-11-14), block 0: preflight, read-only. Loads the fix pass's libraries fresh by git blob hash.
import adsk.core, adsk.fusion, sys, types, hashlib, urllib.request, time, math
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
F = 'enclosure/fusion/revF/floor_plate/fusion/'
A = 'aa9abe4bd453711f8471052a6cd8861cd4cb6e17'


def blob(src): return hashlib.sha1(b'blob %d\0' % len(src) + src).hexdigest()


def load_mod(name, sha, path, want, repl=()):
    src = urllib.request.urlopen(RAW % (sha, path), timeout=20).read()
    if blob(src) != want:
        raise RuntimeError('blob of %s is %s' % (path, blob(src)))
    txt = src.decode('utf-8')
    for a, b in repl:
        if a not in txt:
            raise RuntimeError('not found in %s: %s' % (path, a))
        txt = txt.replace(a, b)
    mod = types.ModuleType(name); sys.modules[name] = mod
    exec(compile(txt, path.split('/')[-1], 'exec'), mod.__dict__)


def run(_context):
    t0 = time.time()
    load_mod('v5f_k', A, F + 'v5f_k_lib.py', 'ba8588482cd63f378ce5b98547aa702716f4855c')
    load_mod('v5f_m', A, F + 'v5f_m_lib.py', '62790f5aece862608eec414bfd419b2aa47ca04a')
    k = sys.modules['v5f_k']; k.budget(45)
    X = k.K()
    print('state', X.state())
    cur = k.current(X, leads=True)
    print('unit', len(cur), 'leads', sum(1 for q in cur if q.name.startswith('LEAD_')), 'KO', sum(1 for q in cur if q.name.startswith('KO_')))
    vis = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
    print('visible', len(vis), vis)
    for n in ('HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'FLOOR_PLATE', 'CRADLE_5807', 'HOUSING_F_door', 'HOUSING_F_cap', 'SLAB_frame'):
        b = X.body(n)
        print('vol', n, round(b.volume * 1000.0, 2), 'lumps', b.lumps.count, 'faces', b.faces.count)
    fr = X.body('HOUSING_F_front')
    rows = []; tot = 0.0
    for f in fr.faces:
        g = f.geometry
        if g.surfaceType != k.PLN:
            continue
        nw = k.wv(g.normal)
        p = k.W(f.pointOnFace)
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        nw = k.wv(nv)
        if nw[1] < 0.99 or p[1] < 6.0 or p[2] > 48.5:
            continue
        ws = [k.W(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)]
        ar = f.area * 100.0; tot += ar
        rows.append([round(ar, 1), [round(q, 4) for q in nw], ext, f.loops.count])
    rows.sort(key=lambda r: -r[0])
    print('chin +y faces', len(rows), 'total mm2', round(tot, 1))
    for r in rows[:12]:
        print('  ', r)
    print('t', round(time.time() - t0, 1))
