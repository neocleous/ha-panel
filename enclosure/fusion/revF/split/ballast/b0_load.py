"""Ballast pass, block 0 (run as its own connector call, read-only).
Loads the libraries by git blob hash under fresh names (cp2k, cp2m, cp2a, cp2x; cache cp2_cache seeded from the
change pass's cp1_cache when that is still in Fusion), then reads state, counts and the nine guard volumes of version 65."""
import adsk.core, adsk.fusion, sys, time, types, hashlib, urllib.request
SHA = '83774786c2eb30f11679e1710c70a61f7552067f'
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
LIBS = [('cp2k', 'enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py', 'ba8588482cd63f378ce5b98547aa702716f4855c', [("'v5f_h_cache'", "'cp2_cache'")]),
        ('cp2m', 'enclosure/fusion/revF/floor_plate/fusion/v5f_m_lib.py', '62790f5aece862608eec414bfd419b2aa47ca04a', [("sys.modules['v5f_k']", "sys.modules['cp2k']")]),
        ('cp2a', 'enclosure/fusion/audit-asm/followup/aud4_lib.py', '181243c7068e2715b299f519df4a7ac8948c95eb', [("sys.modules['aud4k']", "sys.modules['cp2k']"), ("sys.modules['aud4m']", "sys.modules['cp2m']")]),
        ('cp2x', 'enclosure/fusion/audit-asm/split/aud5x_lib.py', 'cdec604d3e54f1484a7d4c0d9675d7af76ea7f09', [("sys.modules['aud5k']", "sys.modules['cp2k']"), ("sys.modules['aud5']", "sys.modules['cp2a']")])]

def load():
    for name, path, blob, subs in LIBS:
        m = sys.modules.get(name)
        if m is not None and getattr(m, '_blob', '') == blob:
            continue
        src = urllib.request.urlopen(RAW % (SHA, path), timeout=25).read()
        h = hashlib.sha1(b'blob %d\x00' % len(src) + src).hexdigest()
        if h != blob:
            raise RuntimeError('blob of %s is %s' % (path, h))
        txt = src.decode('utf-8')
        for a, b in subs:
            if a not in txt:
                raise RuntimeError('no %s in %s' % (a, path))
            txt = txt.replace(a, b)
        m = types.ModuleType(name); m._blob = blob; sys.modules[name] = m
        exec(compile(txt, path, 'exec'), m.__dict__)

GUARD = {'HOUSING_F_plate': 68247.71, 'HOUSING_F_front': 104433.98, 'SPKBOX_L': 26088.32, 'SPKBOX_R': 26809.82, 'FLOOR_PLATE': 32450.31,
         'RESP_CARRIER': 12404.26, 'CRADLE_5807': 1770.95, 'HOUSING_F_door': 47019.77, 'HOUSING_F_cap': 9944.06}

def run(_context):
    t0 = time.time()
    if 'cp2_cache' not in sys.modules:
        m = types.ModuleType('cp2_cache')
        m.c = dict(sys.modules['cp1_cache'].c) if 'cp1_cache' in sys.modules else {}
        sys.modules['cp2_cache'] = m
    load()
    k = sys.modules['cp2k']; X = k.K()
    st = X.state(); cur = k.current(X, leads=True); nm = [b.name for b in cur]
    print('state', st)
    print('unit', len(cur), 'leads', sum(1 for n in nm if n.startswith('LEAD_')), 'KO', sum(1 for n in nm if n.startswith('KO_')))
    allb = list(X.root.bRepBodies)
    print('backups', sorted(b.name for b in allb if b.name.endswith(('_v63', '_v64')) and not b.isLightBulbOn))
    vols = {n: round(X.body(n).volume * 1000.0, 2) for n in list(k.PRINTED) + ['HOUSING_F_plate']}
    print('printed', vols)
    print('guard diff', {n: round(vols[n] - v, 2) for n, v in GUARD.items()})
    print('t', round(time.time() - t0, 1))
