# rev F block 6 / seam (b), option I (2026-11-05), read-only: stations + magnet moves → ~/Documents/v5f_seam_I.json
#   Option I (B6s-1): the new joint faces contain the wall normal n and keep the old inner edges – front face F through
#   A (s −0.7 on y −55.0), door face D = F + 1.7 u (0.7 cloth wrapped on each face + 0.3 gap). Lip, root band and speaker
#   boxes unchanged; the visible seam moves 2.6–3.1 back in y; the door pockets (rim 0.07–0.16 from D at z 25–95, open
#   at z 132 / 150) move back along u until the rim is ≥ 1.0 from D at s 0.2 / 1.0 / 1.8.
#   1. Rays in y −55.0 from (XC, −55.0, 2.9) at 1° (0.5…179.5°): P (INNER_E, n), A (TOOL_inner_skin_0p7), Q
#      (TOOL_outer_skin_0p7), B (REF_F_outer).
#   2. Magnets: from the MAG_D1 point, δ = 1.05 − clearance along u, projected back onto INNER_E by a ray along n; repeated
#      until the clearance is ≥ 1.0 (max 4 passes).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
Y0 = -55.0
NAMES = ('INNER_E', 'TOOL_inner_skin_0p7', 'TOOL_outer_skin_0p7', 'REF_F_outer')
OUT = os.path.expanduser('~/Documents/v5f_seam_I.json')


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def unit(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)
def r4(v): return [round(c, 4) for c in v]


def frames(st):
    for k, s in enumerate(st):
        a = st[max(k - 1, 0)]['P']; b = st[min(k + 1, len(st) - 1)]['P']
        t = unit(vsub(b, a)); n = s['n']
        u = unit(cross(t, n))
        if u[1] > 0:
            u = vmul(u, -1.0)
        s['t'] = unit(cross(n, u)); s['u'] = u
    return st


def clearance(pw, nm, s):
    u = s['u']; D = vadd(s['A'], vmul(u, 1.7))
    w = unit(vadd(vmul(u, -1.0), vmul(nm, dot(u, nm))))
    return min(dot(vsub(vadd(vadd(pw, vmul(nm, sd)), vmul(w, 4.15)), D), u) for sd in (0.2, 1.0, 1.8))


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        raw = []
        for i in range(180):
            ph = math.radians(0.5 + i)
            hs = ray_hits(X, (XC, Y0, 2.9), (math.cos(ph), 0.0, math.sin(ph)), NAMES)
            first = {}
            for h in hs:
                if h[1] not in first:
                    first[h[1]] = h
            if len(first) < 4:
                continue
            pt = lambda nm: (first[nm][2], first[nm][3], first[nm][4])
            raw.append({'ph': round(0.5 + i, 1), 'P': pt('INNER_E'), 'n': unit(first['INNER_E'][5]), 'A': pt('TOOL_inner_skin_0p7'),
                        'Q': pt('TOOL_outer_skin_0p7'), 'B': pt('REF_F_outer')})
        frames(raw)
        out['n_raw'] = len(raw); out['t_rays_s'] = round(time.time() - t0, 1)
        mags = {}
        for sx in (1, -1):
            for (zm, ym) in MAG_D1:
                p, nn, xr, nw = magnet_point(X, sx, zm, ym)
                pw = (xr, wy(p), wz(p)); nm = unit(nw)
                hist = []
                for it in range(5):
                    k = min(range(len(raw)), key=lambda i: dot(vsub(raw[i]['P'], pw), vsub(raw[i]['P'], pw)))
                    cl = clearance(pw, nm, raw[k]); hist.append(round(cl, 3))
                    if cl >= 1.0 or it == 4:
                        break
                    d = 1.05 - cl; u = raw[k]['u']
                    o = vsub(vadd(pw, vmul(u, d)), vmul(nm, 1.5))
                    hs = ray_hits(X, (XC + o[0], o[1], o[2]), nm, ('INNER_E',))
                    h = hs[0]
                    pw = (h[2], h[3], h[4]); nm = unit(h[5])
                mags['%+d,%g' % (sx, zm)] = {'old_xr_y_z': [round(xr, 3), ym, zm], 'new_xr_y_z': r4(pw), 'n': r4(nm), 'cl_hist': hist}
        json.dump({'raw': [{k: (r4(v) if isinstance(v, tuple) else v) for k, v in s.items()} for s in raw], 'mags': mags},
                  open(OUT, 'w'))
        out['mags'] = {k: {'new': [round(c, 2) for c in v['new_xr_y_z']], 'cl': v['cl_hist']} for k, v in mags.items()}
        out['file'] = OUT
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6s2_seam_stations', 'stations', out)
    print(json.dumps(out, separators=(',', ':')))
