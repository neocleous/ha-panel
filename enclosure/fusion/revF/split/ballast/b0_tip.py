"""Ballast pass, block 0: version 65's tipping figures reproduced on the D9 base (D156), read-only.
The k2a mass model (v5f_k2a_tip.py, blob 388dfb5) is run on version 65 and on the hidden _v64 bodies; the difference is
put on the split's D9 base. Results are kept in k.c['bal_tip'] (a call that runs late can be repeated: centroids are cached).
The same formulas are in analysis/geo.py (figs), which reproduces every row to the third decimal."""
import adsk.core, adsk.fusion, sys, time, math, types, hashlib, urllib.request
SHA = '83774786c2eb30f11679e1710c70a61f7552067f'
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
TSRC = r'''
import math, time, sys
k = sys.modules['cp2k']
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0))
GT = (-6.67, 174.67); SC = (5.70, 116.47); DOORY = -84.0
SW = ('SPKBOX_L', 'SPKBOX_R', 'HOUSING_F_front', 'HOUSING_F_plate', 'FLOOR_PLATE', 'FOOT_RL', 'FOOT_RR')
P36 = (-1.704, -5.231, 116.333)
CEN = {}

def cen(X, b, t0, lim):
    q = (b.name, round(b.volume, 6))
    if q not in CEN:
        if time.time() - t0 > lim:
            raise RuntimeError('late')
        CEN[q] = (b.volume, k.W(b.physicalProperties.centerOfMass))
    return CEN[q]

def mass(X, T, ver, t0, lim, extra=()):
    body = lambda n: X.body(n + '_v64') if (ver == 'v64' and n in SW) else X.body(n)
    m = 0.0; s = [0.0, 0.0, 0.0]
    for n in list(k.PRINTED) + ['HOUSING_F_plate']:
        v, q = cen(X, body(n), t0, lim); g = v * T['RHO']
        m += g
        for i in range(3): s[i] += q[i] * g
    for lab, g, names in T['COMP']:
        if names is None:
            q = [0.0, sum(w[1] for w in T['MAGS']) / len(T['MAGS']), sum(w[2] for w in T['MAGS']) / len(T['MAGS'])]
        else:
            vv = 0.0; t = [0.0, 0.0, 0.0]
            for n in names:
                v, w = cen(X, body(n), t0, lim)
                for i in range(3): t[i] += w[i] * v
                vv += v
            q = [t[i] / vv for i in range(3)]
        m += g
        for i in range(3): s[i] += q[i] * g
    for g, q in extra:
        m += g
        for i in range(3): s[i] += q[i] * g
    return m, [s[i] / m for i in range(3)]

def d9():
    m = 1080.5; s = [1080.5 * c for c in (-0.83, -17.57, 80.34)]
    for g, q in ((-210.4, (-2.681, -15.669, 97.632)), (71.7, P36), (109.7, (-3.590, -24.923, 82.360)), (3.6, P36)):
        m += g
        for i in range(3): s[i] += g * q[i]
    return m, [v / m for v in s]

def on_d9(ref, now):
    m9, c9 = d9(); (mr, cr), (mn, cn) = ref, now
    m = m9 + mn - mr
    return m, [(m9 * c9[i] + mn * cn[i] - mr * cr[i]) / m for i in range(3)]

def feet(X):
    out = {}
    for n in ('FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'):
        b = X.body(n); best = None
        for fc in b.faces:
            g = fc.geometry
            if g.surfaceType == k.CYL and (best is None or g.radius > best.radius):
                best = g
        q = k.W(best.origin); e = k.wbb(X, b)
        out[n] = (q[0], q[1], best.radius * 10.0, e[4])
    return out

def figs(m, cog, ft):
    yr = (ft['FOOT_RL'][1] + ft['FOOT_RR'][1]) / 2.0; yf = (ft['FOOT_FL'][1] + ft['FOOT_FR'][1]) / 2.0
    r = ft['FOOT_RL'][2]; zp = min(f[3] for f in ft.values())
    Wn = m / 1000.0 * 9.81; out = {}
    for lab, yp in (('rear centres', yr), ('rear edges', yr - r)):
        M = Wn * (cog[1] - yp) / 1000.0
        out['backward, ' + lab] = {'top edge horizontal N': round(M / ((GT[1] - zp) / 1000.0), 3),
                                   'top edge normal N': round(M / (((GT[1] - zp) * C - (GT[0] - yp) * S) / 1000.0), 3),
                                   'screen centre normal N': round(M / (((SC[1] - zp) * C - (SC[0] - yp) * S) / 1000.0), 3),
                                   'tips at deg': round(math.degrees(math.atan2(cog[1] - yp, cog[2] - zp)), 2)}
    for lab, yp in (('front centres', yf), ('front edges', yf + r)):
        M = Wn * (yp - cog[1]) / 1000.0
        out['forward, ' + lab] = {'tips at deg': round(math.degrees(math.atan2(yp - cog[1], cog[2] - zp)), 2), 'pull at the top edge N': round(M / ((GT[1] - zp) / 1000.0), 3),
                                  'lift at the door foot N': round(M / ((yp - DOORY) / 1000.0), 3)}
    out['rear feet share %'] = round(100.0 * (yf - cog[1]) / (yf - yr), 2)
    return out
'''

def run(_context):
    t0 = time.time()
    k = sys.modules['cp2k']; X = k.K()
    t = sys.modules.get('cp2t')
    if t is None:
        path = 'enclosure/fusion/revF/floor_plate/fusion/v5f_k2a_tip.py'
        src = urllib.request.urlopen(RAW % (SHA, path), timeout=25).read()
        if hashlib.sha1(b'blob %d\x00' % len(src) + src).hexdigest() != '388dfb577f3ed1178d26e57369f9625073cf8a02':
            raise RuntimeError('k2a blob')
        T = {'__name__': 'cp2_k2a', 'k': k}; exec(compile(src.decode('utf-8'), path, 'exec'), T)
        t = types.ModuleType('cp2t'); exec(compile(TSRC, 'cp2t', 'exec'), t.__dict__); t.T = T; sys.modules['cp2t'] = t
    res = k.c.setdefault('bal_tip', {})
    for ver in ('g20', 'v64'):
        if ver in res:
            continue
        try:
            res[ver] = t.mass(X, t.T, ver, t0, 55.0)
        except RuntimeError as e:
            print('resume:', ver, e, 'centroids cached', len(t.CEN)); break
    print({v: (round(m, 3), [round(c, 3) for c in cg]) for v, (m, cg) in res.items()}, 't', round(time.time() - t0, 1))
    if 'g20' in res and 'v64' in res:
        m, cg = t.on_d9(res['v64'], res['g20'])
        ft = t.feet(X)
        print('D9 base, version 65: %.3f g at %s' % (m, [round(c, 3) for c in cg]), 'feet', {n: [round(v, 2) for v in f] for n, f in ft.items()})
        for q, v in t.figs(m, cg, ft).items():
            print('   ', q, v)
