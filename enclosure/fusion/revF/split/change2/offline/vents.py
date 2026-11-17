# change2/offline/vents.py - the door's vent field: the usable zone (inside the shell's door opening, 6 clear of its edge),
# today's slots, and the symmetric layouts; areas, distance to the BME680's two slits, what lies behind.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import model as M, numpy as np
from scipy import ndimage
STEP = 0.25
xs = np.arange(-70, 70.001, STEP); zs = np.arange(40, 136.001, STEP)
X, Z = np.meshgrid(xs, zs)
CACHE = os.path.join(M.D, 'vent_zone.npz')


def zone():
    if os.path.exists(CACHE):
        d = np.load(CACHE); return d['opening'], d['dl']
    org = np.c_[X.ravel(), np.full(X.size, -120.0), Z.ravel()]; dr = np.tile([0, 1.0, 0], (len(org), 1))
    def hits(name, mode, after=None):
        m = M.mesh(name, 'w'); loc, ray, tri = m.ray.intersects_location(org, dr, multiple_hits=True)
        f = np.full(len(org), np.nan)
        for l, r in zip(loc[:, 1], ray):
            if after is not None and not (l > after[r] + 0.05):
                continue
            if np.isnan(f[r]) or (l < f[r] if mode == 'first' else l > f[r]):
                f[r] = l
        return f
    dl = hits('HOUSING_F_door', 'last'); sh = hits('HOUSING_F_front', 'first', after=dl - 5.0)
    opening = (np.isnan(sh) | (sh - dl > 6.0)).reshape(X.shape) & (Z > 53.5)
    lab, n = ndimage.label(opening); c = lab[np.argmin(abs(zs - 90)), np.argmin(abs(xs))]
    opening = lab == c
    np.savez(CACHE, opening=opening, dl=dl.reshape(X.shape)); return opening, dl.reshape(X.shape)


def eroded(opening, margin):
    dist = ndimage.distance_transform_edt(opening) * STEP
    return dist >= margin, dist


SLITS = np.array([[-78.1, -37.3, 99.0], [-69.7, -47.9, 99.0], [-78.1, -37.3, 104.9], [-69.7, -47.9, 104.9]])   # ends of the two slits (world)


def slot_mask(cx, w, z0, z1):                          # a slot with round ends: stadium
    r = w / 2.0
    core = (abs(X - cx) <= r) & (Z >= z0 + r) & (Z <= z1 - r)
    caps = ((X - cx) ** 2 + (Z - (z0 + r)) ** 2 <= r * r) | ((X - cx) ** 2 + (Z - (z1 - r)) ** 2 <= r * r)
    return core | caps


def slot_area(w, z0, z1):
    r = w / 2.0; return w * (z1 - z0) - (4 - np.pi) * r * r


def layout(centres, w, z0, z1, ok, dl):                # each slot cut to what the usable zone allows; returns rows
    rows = []
    for cx in centres:
        col = (abs(X - cx) <= w / 2.0)
        good = ok & col
        # the usable z range for the whole slot width
        j = np.all(ok[:, (abs(xs - cx) <= w / 2.0 + 1e-9)], axis=1)
        zz = zs[j & (zs >= z0) & (zs <= z1)]
        if len(zz) == 0:
            continue
        a, b = zz.min(), zz.max()
        yy = np.nanmean(dl[(abs(Z - (a + b) / 2) < 1.0) & (abs(X - cx) < 4.4)])
        rows.append((cx, w, round(float(a), 2), round(float(b), 2), round(slot_area(w, a, b), 1), round(float(yy), 1)))
    return rows


def dist_slits(rows, dl):
    best = 1e9
    for cx, w, a, b, ar, yy in rows:
        for ex in (cx - w / 2.0, cx + w / 2.0):
            for z in np.arange(a, b + 0.01, 1.0):
                p = np.array([ex, yy - 2.3, z])        # the slot's edge on the door's outer face (door about 2.3 thick)
                for i in (0, 2):
                    s0, s1 = SLITS[i], SLITS[i + 1]; ab = s1 - s0; t = np.clip((p - s0) @ ab / (ab @ ab), 0, 1)
                    best = min(best, np.linalg.norm(p - (s0 + t * ab)))
    return best


if __name__ == '__main__':
    opening, dl = zone(); ok, dist = eroded(opening, 6.0)
    for z in (60, 66, 80, 96, 104, 110, 116, 120, 124):
        j = np.argmin(abs(zs - z)); o = xs[opening[j]]; e = xs[ok[j]]
        print('z %d opening x %.1f..%.1f | 6 inside: %s' % (z, o.min(), o.max(), ('%.1f..%.1f' % (e.min(), e.max())) if len(e) else 'none'))
    today = [(c, 3.0, 66.5, {36: 103.5, 42: 96.5}.get(c, 109.5)) for c in range(-24, 43, 6)]
    for cx, w, a, b in today:
        m = slot_mask(cx, w, a, b); print('today slot x %d: min distance to the opening edge %.2f' % (cx, dist[m].min()))
    print('today area', round(sum(slot_area(w, a, b) for cx, w, a, b in today), 1))
