# change1/c0_calls.py - change pass after the split's audit (2026-11-15), block 0: preflight. Every call read-only.
# Each function is the body of one connector call's run(_context). Model "HA Panel v5 - tapered" version 64 (g19).
import adsk.core, adsk.fusion, sys, time, types, hashlib, urllib.request
SHA = '83774786c2eb30f11679e1710c70a61f7552067f'
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
LIBS = [('cp1k', 'enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py', 'ba8588482cd63f378ce5b98547aa702716f4855c', [("'v5f_h_cache'", "'cp1_cache'")]),
        ('cp1m', 'enclosure/fusion/revF/floor_plate/fusion/v5f_m_lib.py', '62790f5aece862608eec414bfd419b2aa47ca04a', [("sys.modules['v5f_k']", "sys.modules['cp1k']")]),
        ('cp1a', 'enclosure/fusion/audit-asm/followup/aud4_lib.py', '181243c7068e2715b299f519df4a7ac8948c95eb',
         [("sys.modules['aud4k']", "sys.modules['cp1k']"), ("sys.modules['aud4m']", "sys.modules['cp1m']")]),
        ('cp1x', 'enclosure/fusion/audit-asm/split/aud5x_lib.py', 'cdec604d3e54f1484a7d4c0d9675d7af76ea7f09',
         [("sys.modules['aud5k']", "sys.modules['cp1k']"), ("sys.modules['aud5']", "sys.modules['cp1a']")])]


def load():                                           # each library by its git blob hash, under a fresh name, text substitutions checked
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


GUARD = {'HOUSING_F_plate': 68255.48, 'HOUSING_F_front': 104428.62, 'SPKBOX_L': 26086.63, 'SPKBOX_R': 26807.97, 'FLOOR_PLATE': 32450.57,
         'RESP_CARRIER': 12404.26, 'CRADLE_5807': 1770.95, 'HOUSING_F_door': 47019.77, 'HOUSING_F_cap': 9944.06}


def preflight(_context):
    load()
    k = sys.modules['cp1k']; X = k.K()
    print('state', X.state())                        # version 64 of 64, not modified, 397 bodies, 37 visible, no templates
    cur = k.current(X, leads=True)                   # 96 in the unit: 16 leads, 13 keep-outs
    vols = {n: round(X.body(n).volume * 1000.0, 2) for n in list(k.PRINTED) + ['HOUSING_F_plate']}
    print({n: round(vols[n] - v, 2) for n, v in GUARD.items()})      # all 0.00
    # this pass's cache: a copy of the version 64 copies and slabs made by earlier sessions (keys carry name and volume)
    m = types.ModuleType('cp1_cache'); m.c = dict(sys.modules['v5f_h_cache'].c); sys.modules['cp1_cache'] = m


def f44_reproduce(_context):                          # the audit's F44 numbers, both sides
    k = sys.modules['cp1k']; x = sys.modules['cp1x']; X = k.K(); k.budget(70)
    P = k.tcopy(X, 'HOUSING_F_plate')
    for side, box in (('left', 'SPKBOX_L'), ('right', 'SPKBOX_R')):
        g, p0, u, sb = x.bt_line(side)
        e1 = (u[1], -u[0], 0.0)
        B = k.tcopy(X, box)

        def needles(body, r, s0, s1):                # four needles parallel to the line, r off it; plane faces: their mean is the centre-line value
            res = {}
            for lab, dv in (('+e1', e1), ('-e1', tuple(-c for c in e1)), ('+z', (0.0, 0.0, 1.0)), ('-z', (0.0, 0.0, -1.0))):
                a = tuple(x.bt_point(side, s0)[i] + dv[i] * r for i in range(3))
                b = tuple(x.bt_point(side, s1)[i] + dv[i] * r for i in range(3))
                res[lab] = [[round(q[0] + s0, 3), round(q[1] + s0, 3)] for q in k.needle_t(X, [body], a, b)]
            return res
        pl = needles(P, 2.5, -20.0, 20.0); lug = needles(B, 2.2, -12.0, 4.0)
        s_front = sum(v[-1][1] for v in pl.values()) / 4.0; s_floor = sum(v[-1][1] for v in lug.values()) / 4.0
        ins = x.insert_body(X, side, s_front)
        first = None
        for i in range(30):                          # the audit's way: 0.02 steps, first step with volume
            t = 0.30 + 0.02 * i
            m = X.tbm.copy(ins); X.move(m, -u[0] * t, -u[1] * t, 0.0)
            if X.xv(m, B) > 0.0005:
                first = round(t, 2); break
        lugc = X.cp(B); X.sec(lugc, X.wbox(g * 50.0, g * 66.0, -6.0, 1.0, 72.0, 86.0))
        top = X.mm.measureMinimumDistance(lugc, P).value * 10.0
        print(side, round(s_front, 3), round(s_floor, 3), round(s_front - 5.7 - s_floor, 3), first, round(top, 3))
    # left: front 5.11, floor -1.0, gap 0.41 (0.405), first contact 0.42; right: 4.76, -1.35, 0.41, 0.42; lug top to plate 0.292 both
    # pull until the top edge touches: 0.305 continuous, 0.32 at 0.02 steps (both sides)


def window_reproduce(_context):                       # step 20's window: the unit moved back b and down h against the shell
    k = sys.modules['cp1k']; a = sys.modules['cp1a']; m = sys.modules['cp1m']; X = k.K(); k.budget(65)
    R = a.R
    if 'win_fix' not in R:
        fx = []
        for key, box in (('w_chin', (-42.0, 42.0, -8.0, 10.0, -1.0, 14.0)), ('w_cornerL', (68.0, 106.0, -8.0, 10.0, -1.0, 62.0)),
                         ('w_cornerR', (-106.0, -68.0, -8.0, 10.0, -1.0, 62.0)), ('w_frameL', (38.0, 78.0, -72.0, -50.0, -1.0, 45.0)),
                         ('w_frameR', (-78.0, -38.0, -72.0, -50.0, -1.0, 45.0))):
            for p in a.crop(X, 'HOUSING_F_front', key, box):
                fx.append((key, p, m.bb6(p)))
        R['win_fix'] = fx
        mv = [('tongues', p) for p in a.crop(X, 'FLOOR_PLATE', 'u_tongue', (-40.0, 40.0, -6.0, 8.0, -1.0, 8.0))]
        mv += [('box L back', p) for p in a.crop(X, 'SPKBOX_L', 'u_boxL', (30.0, 106.0, -72.0, -45.0, -1.0, 45.0))]
        mv += [('box R back', p) for p in a.crop(X, 'SPKBOX_R', 'u_boxR', (-106.0, -30.0, -72.0, -45.0, -1.0, 45.0))]
        mv.append(('heads', k.tcopy(X, 'DRV_screw_heads_env')))
        R['win_mov'] = mv
    res = R.setdefault('win', {})
    jobs = [('tongues', b, h) for b in (1.05, 1.10, 1.15) for h in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0)]
    jobs += [('heads', 1.15, h) for h in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 42.0,
                                          43.0, 44.0, 45.0, 46.0, 47.0, 48.0, 50.0, 55.0)]
    jobs += [(lab, 1.50, h) for lab in ('box L back', 'box R back') for h in (0.0, 2.0, 5.0, 10.0, 15.0, 18.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 28.0, 30.0)]
    for lab, b, h in jobs:
        if (lab, b, h) in res:
            continue
        best = None
        for ml, p in R['win_mov']:
            if ml != lab:
                continue
            t = a.mv(X, p, (0.0, -b, -h)); q = m.bb6(t)
            for fl, fp, fq in R['win_fix']:
                if m.bgap(q, fq) <= 3.0:
                    d = X.mm.measureMinimumDistance(t, fp).value * 10.0
                    if best is None or d < best[0]:
                        best = (round(d, 3), fl)
        res[(lab, b, h)] = best
    # tongues, least over h > 0: 0.000 at 1.05, 0.050 at 1.10, 0.100 at 1.15. Boxes' backs at 1.50: 0.000 to h 22, 0.039 at 23, 0.185 at 25.
    # Heads at 1.15: 0.366 at h 5 (the audit's 0.37) but 0.000 at h 7-8 and 42-43: they touch at exactly 1.15 (volume 0; 0.0005-0.0039 mm3
    # at 1.10-1.14; 0.01 at 1.16) - the window's lower stop as the instructions give it.
