import numpy as np, bz
from matplotlib.path import Path
R = dict(np.load('plane_cur.npz'))
from plane import NAMES, LNAMES
X, Z = np.meshgrid(bz.XS, bz.ZS)
A = bz.H**2
HOLES = [(41.5, 37.5), (-41.5, 37.5), (41.5, 80.5), (-41.5, 80.5)]
def mask(poly):
    p = Path(poly)
    return p.contains_points(np.c_[X.ravel(), Z.ravel()]).reshape(X.shape)
def evaluate(poly, name, R=R, verbose=True):
    m = mask(poly)
    ins = R['inside']; hf = R['hf'] - 0.5; hb = np.minimum(R['hb_door'], R['hb_fixed'])
    boss = np.zeros_like(m)
    for hx, hz in HOLES:
        boss |= (X - hx)**2 + (Z - hz)**2 <= 4.0**2
    out = m & ~ins
    usable = m & ~boss
    r = dict(name=name, gross=m.sum()*A, outside=out.sum()*A, usable=usable.sum()*A)
    for t in (1, 3, 6, 10, 16, 28):
        r['hf>=%d' % t] = (usable & (hf >= t)).sum()*A
    r['hb_min'] = float(np.min(np.where(m, hb, np.inf)))
    r['hb<1'] = (m & (hb < 1.0)).sum()*A; r['hb<2.9'] = (m & (hb < 2.9)).sum()*A; r['hb<3.5'] = (m & (hb < 3.5)).sum()*A
    r['bracket_front'] = (m & ~boss & (R['hbr'] < 30)).sum()*A
    leads = {}
    for k, nm in enumerate(LNAMES):
        lm = m & (R['lwho'] == k) & (R['hl'] < 30)
        if lm.any():
            leads[nm] = (round(lm.sum()*A), round(float(R['hl'][lm].min()), 1))
    r['leads<30'] = leads
    if verbose:
        print('%-28s gross %6.0f  usable %6.0f  outside-free %5.0f | front>=1 %5.0f >=3 %5.0f >=6 %5.0f >=10 %5.0f >=16 %5.0f >=28 %5.0f | hb min %.1f  hb<1 %4.0f  hb<2.9 %5.0f  hb<3.5 %5.0f | bracket-front %4.0f' % (
            name, r['gross'], r['usable'], r['outside'], r['hf>=1'], r['hf>=3'], r['hf>=6'], r['hf>=10'], r['hf>=16'], r['hf>=28'], r['hb_min'], r['hb<1'], r['hb<2.9'], r['hb<3.5'], r['bracket_front']))
        print('     leads within 30 mm in front (area mm2, min mm):', leads)
        if out.any():
            xs, zs = X[out], Z[out]
            print('     OUTSIDE free region: x %.1f..%.1f z %.1f..%.1f' % (xs.min(), xs.max(), zs.min(), zs.max()))
    return r, m
