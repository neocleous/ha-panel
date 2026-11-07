import numpy as np, bz
from maps import *
from scipy import ndimage
F = load(FIXED); K = load(KEEPOUT); D = load(DOOR); L = load(LEADS); BR = load(BRACKET)
FK = {**F, **K}; NAMES = list(FK.keys()); LNAMES = list(L.keys())
X, Z = np.meshgrid(bz.XS, bz.ZS)
cx, cz = bz.cell_xz(np.arange(bz.NX * bz.NZ))
BOX = (np.abs(X) < 75) & (Z > 2) & (Z < 140)

def disk(r_mm):
    r = int(np.ceil(r_mm / bz.H)); yy, xx = np.mgrid[-r:r+1, -r:r+1]
    return (xx**2 + yy**2) * bz.H**2 <= r_mm**2 + 1e-9

def analyze(YF=-63.4, tilt_deg=0.0, z_pivot=34.0, lat=1.0, t=1.6):
    """Board front face y_f(z) = YF + (z - z_pivot) tan(tilt); slab [y_f - t, y_f]."""
    tn = np.tan(np.radians(tilt_deg))
    yf = YF + (cz - z_pivot) * tn; yb = yf - t / np.cos(np.radians(tilt_deg))
    def per_cell(B, fn):
        out = []
        for k, (nm, (c, y0, y1)) in enumerate(B.items()):
            out.append((k, c, y0, y1))
        return out
    hit = np.zeros(cx.size, bool); who = np.full(cx.size, -1)
    fin = np.full(cx.size, np.inf); fwho = np.full(cx.size, -1)
    beh = np.full(cx.size, -np.inf); bwho = np.full(cx.size, -1)
    for k, (nm, (c, y0, y1)) in enumerate(FK.items()):
        m = (y0 < yf[c]) & (y1 > yb[c]); hit[c[m]] = True; who[c[m]] = k
        m = y0 >= yf[c]; v = np.full(cx.size, np.inf); np.minimum.at(v, c[m], y0[m]); s = v < fin; fin[s] = v[s]; fwho[s] = k
        m = y1 <= yb[c]; v = np.full(cx.size, -np.inf); np.maximum.at(v, c[m], y1[m]); s = v > beh; beh[s] = v[s]; bwho[s] = k
    dmax = np.full(cx.size, -np.inf)
    for nm, (c, y0, y1) in D.items():
        np.maximum.at(dmax, c, y1)
    shadow = dmax > yb                       # door material in front of the back face: the door sweeps through
    lfin = np.full(cx.size, np.inf); lwho = np.full(cx.size, -1)
    for k, (nm, (c, y0, y1)) in enumerate(L.items()):
        m = y0 >= yf[c] - 1.0; v = np.full(cx.size, np.inf); np.minimum.at(v, c[m], y0[m]); s = v < lfin; lfin[s] = v[s]; lwho[s] = k
    bfin = np.full(cx.size, np.inf)
    for nm, (c, y0, y1) in BR.items():
        m = y0 >= yf[c] - 0.01; np.minimum.at(bfin, c[m], y0[m])
    G = lambda a: a.reshape(bz.NZ, bz.NX)
    blocked = G(hit) | G(shadow)
    blocked_d = ndimage.binary_dilation(blocked, structure=disk(lat))
    free = ~blocked_d & BOX
    lab, n = ndimage.label(free)
    inside = lab == lab[np.argmin(np.abs(bz.ZS - 60)), np.argmin(np.abs(bz.XS))]
    return dict(inside=inside, hf=G(fin - yf), fwho=G(fwho), hb_fixed=G(yb - beh), bwho=G(bwho),
                hb_door=G(np.where(np.isfinite(dmax), yb - dmax, np.inf)), hl=G(lfin - yf), lwho=G(lwho),
                hbr=G(bfin - yf), hit=G(hit), who=G(who), shadow=G(shadow), dmax=G(dmax), yf=G(yf), yb=G(yb))
