# rev F cap block c2e (2026-11-05), read-only: section loops for the c2 checkpoint pictures (plotted off-line), written to
#   ~/Documents/HA_panel_renders/c2_sections.json.
#   S1 x_rel 0 (VEML pocket, lux port, shelf, back lip), S2 x_rel 25.91 (BL axis: boss, insert, pad, clearance hole, key lane),
#   S3 x_rel 43.36 (SL axis), S4 world z 165.0 (plan just under the screw heads: ribs either side of the key lanes;
#   run 1 at z 168 missed the lanes, which start at the head bottom z 166.2),
#   S5 world z 177.9 (plan through the cap's pockets: mic strips, VEML, insert holes).
#   Loops per body in plane coordinates (x planes: (y, z); z planes: (x_rel, y)), clipped to the window, RDP 0.01 mm.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/c2_sections.json')
SIDE = ['HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'SLAB_frame', 'REF_F_outer', 'TOOL_outer_skin_0p7', 'VEML_env',
        'MIC_strip_L_env', 'MIC_strip_R_env', 'LEAD_VEML', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR']
PLAN4 = ['HOUSING_F_front', 'REF_F_outer', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR', 'LEAD_VEML',
         'LEAD_MIC_L', 'LEAD_MIC_R', 'KO_mic_L_back', 'KO_mic_R_back']
PLAN5 = ['HOUSING_F_cap', 'HOUSING_F_front', 'REF_F_outer', 'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env']
PLANES = {'S1_x0': ('x', 0.0, (-60.0, -14.0, 150.0, 183.0), SIDE),
          'S2_x25.91': ('x', 25.91, (-58.0, -18.0, 150.0, 183.0), SIDE),
          'S3_x43.36': ('x', 43.36, (-50.0, -15.0, 150.0, 183.0), SIDE),
          'S4_z165': ('z', 165.0, (-75.0, 75.0, -60.0, -14.0), PLAN4),
          'S5_z177.9': ('z', 177.9, (-75.0, 75.0, -56.0, -18.0), PLAN5)}


def clip(P, W):
    S0, S1, Z0, Z1 = W

    def cut(P, inside, inter_):
        o = []
        for i in range(len(P)):
            a = P[i - 1]; b = P[i]; ia, ib = inside(a), inside(b)
            if ib:
                if not ia: o.append(inter_(a, b))
                o.append(b)
            elif ia:
                o.append(inter_(a, b))
        return o
    ix = lambda v: (lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / ((b[0] - a[0]) or 1e-12)))
    iz = lambda v: (lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / ((b[1] - a[1]) or 1e-12), v))
    for f in [(lambda p: p[0] >= S0, ix(S0)), (lambda p: p[0] <= S1, ix(S1)), (lambda p: p[1] >= Z0, iz(Z0)), (lambda p: p[1] <= Z1, iz(Z1))]:
        if not P: break
        P = cut(P, f[0], f[1])
    return P


def rdp(P, eps):
    if len(P) < 3: return P
    a, b = P[0], P[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(P) - 1):
        d = abs(dy * (P[i][0] - a[0]) - dx * (P[i][1] - a[1])) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return rdp(P[:idx + 1], eps)[:-1] + rdp(P[idx:], eps)
    return [a, b]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for pk, (kind, val, W, bodies) in PLANES.items():
            if kind == 'x':
                pl = adsk.core.Plane.create(P3((XC + val) / 10, 0, 0), V3(1, 0, 0))
                uv = lambda p: (wy(p), wz(p))
            else:
                pl = adsk.core.Plane.create(Dw(0.0, 0.0, val), UP)
                uv = lambda p: (p.x * 10 - XC, wy(p))
            res = {}
            for n in bodies:
                b = X.body(n)
                if b is None:
                    continue
                try:
                    wb = X.tbm.planeIntersection(b, pl)
                except Exception as e:
                    res[n + '_FAIL'] = str(e)[:60]; continue
                if wb is None:
                    continue
                segs = []
                for e in wb.edges:
                    ev = e.evaluator; ok, t0e, t1e = ev.getParameterExtents(); ok, pts = ev.getStrokes(t0e, t1e, 0.0005)
                    segs.append([uv(p) for p in pts])
                loops = []
                while segs:
                    cur = segs.pop(0); grown = True
                    while grown:
                        grown = False
                        for i, s in enumerate(segs):
                            if math.dist(s[0], cur[-1]) < 0.005: cur += s[1:]; segs.pop(i); grown = True; break
                            if math.dist(s[-1], cur[-1]) < 0.005: cur += s[::-1][1:]; segs.pop(i); grown = True; break
                    loops.append(cur)
                keep = []
                for L in loops:
                    Cc = clip(L, W)
                    if len(Cc) < 3: continue
                    k = max(range(len(Cc)), key=lambda i: math.dist(Cc[0], Cc[i]))
                    Cc = rdp(Cc[:k + 1], 0.01)[:-1] + rdp(Cc[k:] + [Cc[0]], 0.01)
                    keep.append([[round(a, 3), round(c, 3)] for (a, c) in Cc])
                res[n] = keep
            out[pk] = {'kind': kind, 'val': val, 'win': W, 'loops': res}
        out['t_s'] = round(time.time() - t0, 1)
        json.dump(out, open(OUT, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2e_sections', 'sections', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'),
                                         'n': {k: {n: (len(v) if isinstance(v, list) else v) for n, v in out[k]['loops'].items()}
                                               for k in PLANES if k in out}})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
