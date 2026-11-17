# change2/offline/survey.py - the FDM strength review (D211): every cylinder (boss, post, pin, insert and pilot hole) and every thin
# flat slab (fin, web, rib, lip) of the printed parts, from the B-rep face data sent by Fusion and the meshes.
import sys, os, json, math; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, model as M, geo
C, S = geo.C, geo.S
SV = json.load(open(os.path.join(M.D, 'survey.json')))
# print orientation: the direction that is up in the print, in world axes
UP = {'HOUSING_F_front': (0, -1, 0), 'HOUSING_F_plate': (0, C, S), 'HOUSING_F_door': (0, 0, 1), 'HOUSING_F_cap': (0, 0, -1), 'FLOOR_PLATE': (0, 0, 1),
      'SLAB_frame': (0, -C, -S), 'SPKBOX_L': (0, 1, 0), 'SPKBOX_R': (0, 1, 0), 'RESP_CARRIER': (0, -C, -S), 'CRADLE_5807': (0, 1, 0),
      'TOUCH_CLIP_L': (0, 0, 1), 'TOUCH_CLIP_R': (0, 0, 1), 'BME_HOOD': None, 'GROMMET_usbc_F': (0, 0, 1)}
_mesh = {}


def mesh(n):
    if n not in _mesh:
        _mesh[n] = M.mesh(n, 'w')
    return _mesh[n]


def ang_up(n, a):                                     # angle between an axis and the print's up direction (0 = layers square to the axis)
    u = UP.get(n)
    if u is None:
        return None
    c = abs(sum(a[i] * u[i] for i in range(3))); return round(math.degrees(math.acos(min(1.0, c))), 0)


def perp(a):
    a = np.array(a, float); r = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(a, r); e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1); return e1, e2


def wall(n, A, B, r, nang=24, nst=5):                 # least plastic round a hole: rays from its surface outward to the first exit
    m = mesh(n); A = np.array(A, float); B = np.array(B, float); a = (B - A); L = np.linalg.norm(a); a /= L
    e1, e2 = perp(a); org = []; dr = []
    for s in np.linspace(0.12, 0.88, nst):
        for t in np.linspace(0, 2 * np.pi, nang, endpoint=False):
            d = math.cos(t) * e1 + math.sin(t) * e2
            org.append(A + a * L * s + d * (r + 0.03)); dr.append(d)
    org = np.array(org); dr = np.array(dr)
    loc, ray, tri = m.ray.intersects_location(org, dr, multiple_hits=True)
    best = np.full(len(org), np.inf)
    for l, i in zip(loc, ray):
        t = float(np.dot(l - org[i], dr[i]))
        if t > 1e-4 and t < best[i]:
            best[i] = t
    inside = m.contains(org)
    v = best[inside]
    return (round(float(v.min()) + 0.03, 2), round(float(np.median(v)) + 0.03, 2), int(inside.sum())) if inside.any() else (None, None, 0)


def cyls(n):
    rows = SV[n]['cyl']; pins = [r for r in rows if r['k'] == 'p']; holes = [r for r in rows if r['k'] == 'h']
    return pins, holes


def coax(p, h, tol=0.25):
    a = np.array(p['a']); b = np.array(h['a'])
    if abs(abs(a @ b) - 1) > 0.002:
        return False
    d = np.array(h['A']) - np.array(p['A']); d = d - (d @ a) * a
    return np.linalg.norm(d) < tol


if __name__ == '__main__':
    for n in SV:
        pins, holes = cyls(n)
        hr = {}
        for h in holes:
            hr.setdefault(h['r'], 0); hr[h['r']] += 1
        pr = {}
        for p in pins:
            pr.setdefault(p['r'], 0); pr[p['r']] += 1
        print(n, 'holes by r:', dict(sorted(hr.items())), '| pins by r:', dict(sorted(pr.items())))


def boss_table(n, hole_r=(0.75, 0.8, 0.85, 1.2, 1.25, 1.45, 2.0), pin_min=1.4):
    pins, holes = cyls(n); out = []
    for h in holes:
        if h['r'] not in hole_r or h['L'] < 1.0:
            continue
        w = wall(n, h['A'], h['B'], h['r'])
        p = [q for q in pins if coax(q, h)]
        out.append(('hole', h['r'] * 2, h['L'], [round((h['A'][i] + h['B'][i]) / 2, 1) for i in range(3)], ang_up(n, h['a']), w[0], w[1],
                    ('boss dia %.1f' % (2 * max(q['r'] for q in p))) if p else 'in a wall or block'))
    for p in pins:
        if p['r'] < pin_min or p['L'] < 0.8:
            continue
        h = [q for q in holes if coax(q, p)]
        out.append(('pin', p['r'] * 2, p['L'], [round((p['A'][i] + p['B'][i]) / 2, 1) for i in range(3)], ang_up(n, p['a']), p['cov'],
                    None, ('hole dia %s' % sorted(set(round(2 * q['r'], 2) for q in h))) if h else 'solid'))
    return out


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'boss':
    for n in SV:
        rows = boss_table(n)
        print('##', n, 'print up', UP.get(n))
        for r in sorted(rows, key=lambda r: (r[0], r[1], r[3])):
            if r[0] == 'hole':
                print('  hole d%.2f L%.1f at %s axis-to-up %s deg  wall min %s med %s  %s' % (r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
            else:
                print('  pin  d%.2f L%.1f at %s axis-to-up %s deg  exposed %.2f  %s' % (r[1], r[2], r[3], r[4], r[5], r[7]))


def slabs(n, tmax=3.2, amin=6.0):                     # flat slabs: pairs of opposite plane faces with plastic between them
    P = np.array(SV[n]['pl'], float)
    if len(P) == 0:
        return []
    N = P[:, 0:3]; Q = P[:, 3:6]; A = P[:, 6]; B = P[:, 7:13]
    m = mesh(n); cand = {}
    for i in range(len(P)):
        if A[i] < amin:
            continue
        dots = N @ N[i]
        for j in np.where(dots < -0.9995)[0]:
            if j <= i or A[j] < amin:
                continue
            t = float((Q[i] - Q[j]) @ N[i])            # j lies behind i by t
            if not (0.25 <= t <= tmax):
                continue
            lo = np.maximum(B[i, 0::2], B[j, 0::2]) - 0.01; hi = np.minimum(B[i, 1::2], B[j, 1::2]) + 0.01
            # overlap of the two faces' boxes, ignoring the axis along the normal
            ext = hi - lo; ax = np.argsort(-abs(N[i]))  # ax[0] = the axis most along the normal
            e = [ext[a] for a in ax[1:]]
            if abs(N[i][ax[0]]) > 0.98:
                if min(e) <= 0.3:
                    continue
                area = e[0] * e[1]
            else:                                      # oblique slab: use the box centres
                if np.any(ext < -t - 0.5):
                    continue
                area = min(A[i], A[j])
            c = (np.maximum(lo, B[i, 0::2]) + np.minimum(hi, B[i, 1::2])) / 2.0
            c = c - ((c - Q[i]) @ N[i]) * N[i] - N[i] * (t / 2.0)      # onto face i's plane, then to mid-thickness
            key = (tuple(np.round(N[i] * np.sign(N[i][ax[0]]), 2)), round(float(Q[i] @ N[i]) * np.sign(N[i][ax[0]]), 1), round(t, 2))
            g = cand.setdefault(key, {'t': t, 'n': N[i] * np.sign(N[i][ax[0]]), 'area': 0.0, 'lo': lo.copy(), 'hi': hi.copy(), 'pts': []})
            g['area'] += min(area, A[i], A[j]); g['lo'] = np.minimum(g['lo'], lo); g['hi'] = np.maximum(g['hi'], hi); g['pts'].append(c)
    out = []
    for key, g in cand.items():
        pts = np.array(g['pts']); ins = m.contains(pts)
        if not ins.any():
            continue
        out.append({'t': round(g['t'], 2), 'n': [round(float(v), 2) for v in g['n']], 'area': round(g['area'], 1),
                    'box': [round(float(v), 1) for pair in zip(g['lo'], g['hi']) for v in pair], 'solid': int(ins.sum()), 'faces': len(pts)})
    return sorted(out, key=lambda r: (r['t'], -r['area']))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'slab':
    tot = 0
    for n in SV:
        rows = slabs(n)
        rows = [r for r in rows if r['area'] >= 10.0 and r['t'] <= 2.6]
        tot += len(rows)
        print('##', n, len(rows))
        for r in rows:
            print('  t %.2f  n %s  area %.0f  box x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (r['t'], r['n'], r['area'], *r['box']))
    print('total', tot)
