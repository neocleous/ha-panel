"""Slice check: a feature's cross-section as sliced against the same section as modelled.
The extruded lines of one layer inside a window are taken as area (length x line width); area and the
principal second moments are compared with the solid section of the model in the same window."""
import numpy as np
from s2_gcode import *

def sliced_props(tag, h, win):
    a = load(tag); zs = np.unique(a[:, 0]); z = zs[np.argmin(np.abs(zs - h))]; b = a[a[:, 0] == z]
    u0, u1, v0, v1 = win
    # split segments into short pieces so that clipping by the window is fair
    P0 = b[:, 4:6]; P1 = b[:, 6:8]; L = np.hypot(*(P1 - P0).T)
    n = np.maximum(1, np.ceil(L / 0.1).astype(int))
    idx = np.repeat(np.arange(len(b)), n)
    k = np.concatenate([np.arange(m) for m in n]); f = (k + 0.5) / n[idx]
    C = P0[idx] + (P1[idx] - P0[idx]) * f[:, None]
    dA = (L[idx] / n[idx]) * b[idx, 3]
    typ = b[idx, 2].astype(int)
    m = (C[:, 0] >= u0) & (C[:, 0] <= u1) & (C[:, 1] >= v0) & (C[:, 1] <= v1)
    C, dA, typ = C[m], dA[m], typ[m]
    A = dA.sum()
    if A <= 0:
        return dict(A=0, I1=0, I2=0, z=float(z), mix={})
    c = (C * dA[:, None]).sum(0) / A
    d = C - c
    Ixx = (dA * d[:, 1] ** 2).sum(); Iyy = (dA * d[:, 0] ** 2).sum(); Ixy = (dA * d[:, 0] * d[:, 1]).sum()
    ev = np.linalg.eigvalsh(np.array([[Ixx, -Ixy], [-Ixy, Iyy]]))
    mix = {TYPES[t]: float(dA[typ == t].sum()) for t in np.unique(typ)}
    return dict(A=float(A), I1=float(ev[0]), I2=float(ev[1]), z=float(z), mix=mix)

def solid_props(part, h, win):
    L = part.slice(); hs = np.array([x[0] for x in L]); i = int(np.argmin(np.abs(hs - (h - part.lh / 2))))
    g = L[i][1].intersection(box(win[0], win[2], win[1], win[3]))
    if g.is_empty:
        return dict(A=0, I1=0, I2=0)
    # second moments by sampling
    xs = np.arange(win[0], win[1], 0.05) + 0.025; ys = np.arange(win[2], win[3], 0.05) + 0.025
    X, Y = np.meshgrid(xs, ys); pts = shapely.points(X.ravel(), Y.ravel())
    inside = shapely.contains(g, pts)
    C = np.c_[X.ravel()[inside], Y.ravel()[inside]]; dA = 0.05 * 0.05
    A = len(C) * dA; c = C.mean(0); d = C - c
    Ixx = (d[:, 1] ** 2).sum() * dA; Iyy = (d[:, 0] ** 2).sum() * dA; Ixy = (d[:, 0] * d[:, 1]).sum() * dA
    ev = np.linalg.eigvalsh(np.array([[Ixx, -Ixy], [-Ixy, Iyy]]))
    return dict(A=float(A), I1=float(ev[0]), I2=float(ev[1]))

def compare(tag, body, cases, parts={}):
    if body not in parts: parts[body] = Part(body)
    p = parts[body]
    for name, h, win in cases:
        s = sliced_props(tag, h, win); m = solid_props(p, h, win)
        mix = ', '.join('%s %.0f%%' % (k.replace(' infill', '').replace('Internal ', ''), 100 * v / s['A']) for k, v in sorted(s['mix'].items(), key=lambda kv: -kv[1])[:4]) if s['A'] else ''
        print('%-34s layer %.1f | model A %.1f I %.1f/%.1f | sliced A %.1f (%.0f%%) I %.1f/%.1f (%.0f%% / %.0f%%) | %s' % (
            name, s['z'], m['A'], m['I1'], m['I2'], s['A'], 100 * s['A'] / m['A'] if m['A'] else 0, s['I1'], s['I2'],
            100 * s['I1'] / m['I1'] if m['I1'] else 0, 100 * s['I2'] / m['I2'] if m['I2'] else 0, mix))

if __name__ == '__main__':
    T = (67.45, 23.7); B = (82.45, -82.9)
    w = lambda c, ru, rv=None: (c[0] - ru, c[0] + ru, c[1] - (rv or ru), c[1] + (rv or ru))
    compare('shell', 'HOUSING_F_front', [
        ('top post at the insert', 27.0, w(T, 5.0)), ('top post at the insert end', 31.0, w(T, 6.3)),
        ('top post cone', 33.0, w(T, 6.6)), ('bottom post at the insert', 4.0, w(B, 5.6)),
        ('bottom post at the insert end', 7.0, w(B, 6.0)),
        ('rear lip between pockets (20 wide)', 66.0, (-10, 10, 0, 14))])
    compare('door', 'HOUSING_F_door', [
        ('door vent bar', 87.2, (-1.2, 2.1, -76.3, -73.3)), ('door boss block', 5.0, (12.0, 21.0, -84.5, -70.0)),
        ('door wall 20 wide at mid height', 60.0, (40, 60, -86, -60))])
    compare('base', 'FLOOR_PLATE', [('Pi post', 5.0, (11.5, 20.5, -9.5, -1.0)), ('cradle posts', 6.0, (-8, 8, -78, -68)),
                                    ('nose', 4.8, (21.5, 33.5, -1.2, 2.6))])
