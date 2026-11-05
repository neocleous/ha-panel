# rev F block 6 / seam (b) probe (2026-11-05), read-only. Daniel 09:16 chose (b): both joint faces re-cut normal to the wall,
#   cloth (0.7) wrapped round them → plastic faces 1.7 apart for a 0.3 cloth-to-cloth gap.
#   Stations: rays in the old joint plane y −55.0 from (XC, −55.0, 2.9) at 1° steps; on each ray the hits on INNER_E (P, s 0,
#   normal n), TOOL_inner_skin_0p7 (A, s −0.7: old inner edge), TOOL_outer_skin_0p7 (Q, s 1.8: old plastic outer edge) and
#   REF_F_outer (B, s 2.5: old cloth edge); resampled to ≈ 4 mm along the arch; t from the neighbours, u = t × n (in the
#   surface, ⟂ the joint, toward the door). lean = asin|n_y| (old door edge angle = 90° − lean).
#   Old gap centre G = B + 0.15/|u_y| · u (y −55.15). New faces contain n; front face F, door face D = F + 1.7 u; gap centre
#   F + 0.85 u on the cloth level. Options for where F sits:
#     I  inner edge kept   F_in = A               → the visible seam moves (along u / in y / in z)
#     O  seam kept         F(s 2.5) = G − 0.85 u   → the inner edge moves forward; root band (s −0.7…−2.1, 1.5 in front of
#                                                    F_in) against the speaker boxes (rear face y −52.0, z 3–76)
#     M  mid-wall pivot    F through (A + Q) / 2
#   Door magnet pockets (Ø8.3, plastic s 0.2…1.8, at MAG_D1): smallest distance from the rim to D (old: to y −55.3).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
Y0 = -55.0
NAMES = ('INNER_E', 'TOOL_inner_skin_0p7', 'TOOL_outer_skin_0p7', 'REF_F_outer')


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def unit(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)
def r2(v): return [round(c, 2) for c in v]


def stations(X):
    raw = []
    for i in range(180):
        ph = math.radians(0.5 + i)
        d = (math.cos(ph), 0.0, math.sin(ph))
        hs = ray_hits(X, (XC, Y0, 2.9), d, NAMES)
        first = {}
        for h in hs:
            if h[1] not in first:
                first[h[1]] = h
        if len(first) < 4:
            continue
        pt = lambda nm: (first[nm][2], first[nm][3], first[nm][4])
        raw.append({'P': pt('INNER_E'), 'n': unit(first['INNER_E'][5]), 'A': pt('TOOL_inner_skin_0p7'),
                    'Q': pt('TOOL_outer_skin_0p7'), 'B': pt('REF_F_outer')})
    st = [raw[0]]; acc = 0.0
    for k in range(1, len(raw)):
        dd = vsub(raw[k]['P'], raw[k - 1]['P']); acc += math.sqrt(dot(dd, dd))
        if acc >= 4.0 or k == len(raw) - 1:
            st.append(raw[k]); acc = 0.0
    for k, s in enumerate(st):
        a = st[max(k - 1, 0)]['P']; b = st[min(k + 1, len(st) - 1)]['P']
        s['t'] = unit(vsub(b, a))
        u = unit(cross(s['t'], s['n']))
        s['u'] = vmul(u, -1.0) if u[1] > 0 else u
    return st


def faces(s):
    n, u, A, Q, B = s['n'], s['u'], s['A'], s['Q'], s['B']
    G = vadd(B, vmul(u, 0.15 / abs(u[1])))
    FI = A
    FO = vsub(vsub(G, vmul(u, 0.85)), vmul(n, 3.2))
    M = vmul(vadd(A, Q), 0.5); FM = vsub(M, vmul(n, 1.25))
    return G, {'I': FI, 'O': FO, 'M': FM}


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        st = stations(X)
        out['n_stations'] = len(st)
        rows = []; agg = {k: {'seam_u': [], 'seam_y': [], 'seam_z': [], 'inner_u': [], 'inner_y': [], 'rb_y_box': []} for k in 'IOM'}
        leans = []
        for k, s in enumerate(st):
            n, u, A = s['n'], s['u'], s['A']
            lean = math.degrees(math.asin(min(1.0, abs(n[1])))); leans.append(lean)
            G, F = faces(s)
            row = [round(s['P'][0], 1), round(s['P'][2], 1), round(lean, 1)]
            for key in 'IOM':
                Fi = F[key]
                Gn = vadd(vadd(Fi, vmul(n, 3.2)), vmul(u, 0.85))
                su = dot(vsub(Gn, G), u)
                iu = dot(vsub(A, Fi), u)                       # > 0: new inner edge in front of the old one
                rb = vsub(vsub(Fi, vmul(u, 1.5)), vmul(n, 1.4))  # root band front at s −2.1
                agg[key]['seam_u'].append(su); agg[key]['seam_y'].append(Gn[1] - G[1]); agg[key]['seam_z'].append(Gn[2] - G[2])
                agg[key]['inner_u'].append(iu); agg[key]['inner_y'].append(Fi[1] - A[1])
                if 3.0 <= s['P'][2] <= 76.0:
                    agg[key]['rb_y_box'].append(rb[1])
                row += [round(su, 2), round(iu, 2), round(rb[1], 2)]
            if k % 4 == 0 or k == len(st) - 1:
                rows.append(row)
        out['rows_xrel_z_lean__I_seam_inner_rbY__O_seam_inner_rbY__M_seam_inner_rbY'] = rows
        out['lean_deg'] = [round(min(leans), 1), round(max(leans), 1)]
        out['summary'] = {k: {m: ([round(min(v), 2), round(max(v), 2)] if v else None) for m, v in d.items()} for k, d in agg.items()}
        # door magnet pockets
        mags = {}
        for sx in (1, -1):
            for (zm, ym) in MAG_D1:
                p, nn, xr, nw = magnet_point(X, sx, zm, ym)
                pw = (xr, wy(p), wz(p)); nm = unit(nw)
                k = min(range(len(st)), key=lambda i: dot(vsub(st[i]['P'], pw), vsub(st[i]['P'], pw)))
                s = st[k]; u = s['u']
                G, F = faces(s)
                w = unit(vadd(vmul(u, -1.0), vmul(nm, dot(u, nm))))
                cl = {'old': 9e9, 'I': 9e9, 'O': 9e9, 'M': 9e9}
                for sd in (0.2, 1.0, 1.8):
                    rim = vadd(vadd(pw, vmul(nm, sd)), vmul(w, 4.15))
                    cl['old'] = min(cl['old'], -55.3 - rim[1])
                    for key in 'IOM':
                        D = vadd(F[key], vmul(u, 1.7))
                        cl[key] = min(cl[key], dot(vsub(rim, D), u))
                mags['%+d,z%g' % (sx, zm)] = {kk: round(v, 2) for kk, v in cl.items()}
                mags['%+d,z%g' % (sx, zm)]['xr_y_z'] = r2(pw)
        out['door_pocket_rim_to_D_mm'] = mags
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6s1_seam_probe', 'probe', out)
    print(json.dumps(out, separators=(',', ':')))
