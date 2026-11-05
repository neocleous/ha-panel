# rev F cap block c2i (2026-11-05): front shell rebuilt from HOUSING_F_front_c0 as in c2c, with one change: SL/SR get ONE
#   rib, along the wall normal on the outer side, instead of two ribs along the key lane.
#   Why: the c2e plan section at z 165 showed SL/SR's inner lane-aligned rib ending ≈ 0.7 short of the back wall below
#   z ≈ 167 (the wall leans back going down), i.e. hanging free with a flat bottom at z 160 – unprintable without support.
#   Reaching the wall would make it cross both exhaust rows at x ≈ ±31…34. The outer rib along the wall normal n_h
#   (SL (0.359, −0.933), SR (−0.359, −0.933)) at 4.5 outboard of the axis roots in the rear-corner wall at |x| > 45, outside
#   the exhaust slots, and stays on the far side from the key lane (the lane leaves inboard). BL/BR unchanged (two ribs
#   along the lane, rooted in the back wall). Pads, holes, shelf, groove-last, everything else as c2c.
#   Gates: 1 lump; front ∩ cap / door 0; insertion sweep of the cap (h 0.1…4.0) 0; KO_capkey_* ∩ front 0; every rib's
#   bottom rooted (rib part below z 166 ∩ the c0 wall below z 166 > 0, reported per rib).
#   Commit: HOUSING_F_front → HOUSING_F_front_c2a (hidden), new HOUSING_F_front (no fillets – c2d re-run follows).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
MODE = 'commit'
Y_T, Y_TC = -22.5, -22.6
Z_L, Z_C, Z_G, Z_F, Z_IN = 175.3, 175.8, 172.8, 171.8, 174.0
STEPS = [(5.0, 170.95, 171.8), (4.1, 170.1, 170.95)]
Z_PAD_B, Z_BOSS_B, Z_PLATE = 169.5, 172.5, 177.5
R_BOSS, R_INS, H_INS, R_PAD, R_CLR = 4.0, 2.0, 6.0, 5.5, 1.7
RIB_T, RIB_OFF, RIB_K = 2.0, 4.5, 0.700
SCREWS = {'BL': ((25.91, -37.80), (20.0, 30.0)), 'BR': ((-25.91, -37.80), (-20.0, 30.0)),
          'SL': ((43.36, -32.85), (20.0, 30.0)), 'SR': ((-43.36, -32.85), (-20.0, 30.0))}
# rib specs per screw: (direction, lateral offsets); 'lane' = plan direction of the key lane, else a wall normal
RIBS = {'BL': ('lane', (-RIB_OFF, RIB_OFF)), 'BR': ('lane', (-RIB_OFF, RIB_OFF)),
        'SL': ((0.359, -0.933), (RIB_OFF,)), 'SR': ((-0.359, -0.933), (-RIB_OFF,))}
Z_LANE0, R_LANE = 166.2, 2.5
V_C0, V_DOOR, V_FRONT, V_CAP = 240.8876, 51.101, 237.2748, 9.9147
HS = (0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 4.0)


def tool(t):
    return 'TOOL_cap_off%s' % (('%.2f' % t).rstrip('0').rstrip('.')).replace('.', 'p')


def band(X, t_out, t_in, z0, z1, y1):        # d in [t_out, t_in], z0…z1, y < y1
    b = tb_copy(X, tool(t_in)); inter(X, b, X.wbox(-250, 250, -250, y1, z0, z1))
    if t_out > 0:
        X.diff(b, tb_copy(X, tool(t_out)))
    return b


def refcrop(X):
    r = tb_copy(X, 'REF_F_outer'); inter(X, r, X.wbox(-250, 250, -250, 250, 160.0, 177.2))
    inter(X, r, dbox(X, -250, 250, -250, -13.9, -250, 250)); return r


def core(X, t):                              # inside d t, z 160…177.2, design Y ≤ −13.9
    c = refcrop(X); X.diff(c, tb_copy(X, tool(t))); return c


def split_region(X, y1):
    r = X.wbox(-250, 250, -250, y1, Z_L, 260.0)
    i = X.wbox(-250, 250, -250, y1, Z_IN, Z_L + 0.01); X.diff(i, tb_copy(X, tool(7.3)))
    X.union(r, i); return r


def unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def hs_box(X, p, n, L=80.0):                 # box filling {q : (q − p)·n ≥ 0} near p (p = (x_rel, y, z))
    n = unit(n); ref = (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)
    a1 = unit(cross(n, ref)); a2 = cross(n, a1)
    c = (p[0] + n[0] * L / 2, p[1] + n[1] * L / 2, p[2] + n[2] * L / 2)
    return lbox(X, c, a1, a2, L, L, L)


def lane_dir(k):                             # plan unit vector from the axis toward the lane target
    (cx, cy), (xt, zt) = SCREWS[k]
    return unit((xt - cx, -100.0 - cy, 0.0))[:2]


def lane_cyl(X, k):
    (cx, cy), (xt, zt) = SCREWS[k]
    return X.tbm.createCylinderOrCone(Dw(XC + cx, cy, Z_LANE0), R_LANE / 10, Dw(XC + xt, -100.0, zt), R_LANE / 10)


def pad_body(X, k, c41):
    (cx, cy), _t = SCREWS[k]; vx, vy = lane_dir(k); wx, wy_ = -vy, vx
    p = X.wcyl_z(XC + cx, cy, R_PAD, Z_PAD_B, Z_BOSS_B)
    X.union(p, lbox(X, (cx + vx * 8.0, cy + vy * 8.0, (Z_PAD_B + Z_BOSS_B) / 2), (vx, vy, 0.0), (wx, wy_, 0.0), 16.0,
                    2 * R_PAD, Z_BOSS_B - Z_PAD_B))
    inter(X, p, X.tbm.copy(c41))
    return p


def ribs_for(X, k, c19):
    (cx, cy), _t = SCREWS[k]; spec, offs = RIBS[k]
    vx, vy = lane_dir(k) if spec == 'lane' else unit((spec[0], spec[1], 0.0))[:2]
    wx, wy_ = -vy, vx
    smin, smax = -R_PAD, 16.0
    zb = Z_PAD_B - RIB_K * (smax - smin) - 1.0
    out = []
    for o in offs:
        sm = (smin + smax) / 2
        r = lbox(X, (cx + vx * sm + wx * o, cy + vy * sm + wy_ * o, (Z_PAD_B + 0.5 + zb) / 2), (vx, vy, 0.0), (wx, wy_, 0.0),
                 smax - smin, RIB_T, Z_PAD_B + 0.5 - zb)
        X.diff(r, hs_box(X, (cx + vx * smin, cy + vy * smin, Z_PAD_B), (-RIB_K * vx, -RIB_K * vy, -1.0)))
        inter(X, r, X.tbm.copy(c19))
        out.append(r)
    return out


def run(_context):
    X = Ctx(); out = {'MODE': MODE}
    t0 = time.time()
    try:
        g0 = {n: round(X.body(n).volume, 4) for n in ('HOUSING_F_front_c0', 'HOUSING_F_door', 'HOUSING_F_front', 'HOUSING_F_cap')}
        out['guard'] = g0
        if abs(g0['HOUSING_F_front_c0'] - V_C0) > 0.001 or abs(g0['HOUSING_F_door'] - V_DOOR) > 0.001 or \
                abs(g0['HOUSING_F_front'] - V_FRONT) > 0.001 or abs(g0['HOUSING_F_cap'] - V_CAP) > 0.001:
            raise RuntimeError('volume guard %s' % g0)
        if X.body('HOUSING_F_front_c2a') is not None:
            raise RuntimeError('HOUSING_F_front_c2a exists')
        c41 = core(X, 4.1); c19 = core(X, 1.9)
        wall = tb_copy(X, 'HOUSING_F_front_c0'); inter(X, wall, X.wbox(-250, 250, -250, 250, 150.0, 166.0))   # existing wall below z 166
        F = tb_copy(X, 'HOUSING_F_front_c0'); X.diff(F, split_region(X, Y_T))
        FL = band(X, 0.72, 5.9, Z_F, Z_L, 0.0)
        for (t, z0, z1) in STEPS:
            X.union(FL, band(X, 0.72, t, z0, z1, 0.0))
        X.union(F, FL)
        EX = X.wbox(XC - 45.0, XC + 45.0, -62.0, -40.0, 162.5, 165.5)
        X.diff(F, X.tbm.copy(EX))
        PR = None; HO = None; pv = {}; rooted = {}
        for k, ((cx, cy), _t) in SCREWS.items():
            p = pad_body(X, k, c41); rbs = ribs_for(X, k, c19)
            pv[k] = {'pad_mm3': round(p.volume * 1000, 1), 'ribs_mm3': [round(r.volume * 1000, 1) for r in rbs]}
            for i, r in enumerate(rbs):
                lo = X.tbm.copy(r); inter(X, lo, X.wbox(-250, 250, -250, 250, 150.0, 166.0))
                rooted['%s_%d' % (k, i)] = vol_x(X, lo, wall) if lo.volume > 0 else 0.0
                X.union(p, r)
            PR = p if PR is None else X.union(PR, p)
            h = X.wcyl_z(XC + cx, cy, R_CLR, Z_PAD_B - 0.5, Z_BOSS_B + 0.5)
            HO = h if HO is None else X.union(HO, h)
        out['pads'] = pv; out['rib_bottom_in_wall_mm3'] = rooted
        X.union(F, PR); X.diff(F, HO)
        SH = X.wbox(XC - 60.0, XC + 60.0, -23.3, -21.6, 176.0, 177.4)
        inter(X, SH, hs_box(X, (0.0, -23.3, 177.4), (0.0, 0.7071, 0.7071), 160.0))
        X.union(F, SH)
        G = band(X, 1.9, 4.7, Z_G, Z_L + 0.2, Y_T)              # groove last
        X.diff(F, G)
        out['front'] = {'cm3': round(F.volume, 4), 'lumps': F.lumps.count, 'faces': F.faces.count}
        log('v5f_c2i_front_ribs', 'progress', {'front': out['front'], 'pads': pv, 'rooted': rooted, 't_s': round(time.time() - t0, 1)})
        g = {}
        FT = X.tbm.copy(F); inter(X, FT, X.wbox(-250, 250, -250, 250, 150.0, 260.0))
        CAP = tb_copy(X, 'HOUSING_F_cap')
        DT = tb_copy(X, 'HOUSING_F_door'); inter(X, DT, X.wbox(-250, 250, -250, 250, 150.0, 260.0))
        g['front_x_cap_mm3'] = vol_x(X, FT, CAP)
        g['front_x_door_mm3'] = vol_x(X, FT, DT)
        sw = {}
        for hh in HS:
            c = X.tbm.copy(CAP); mvw(X, c, 0.0, 0.0, hh); sw['%.2f' % hh] = vol_x(X, c, FT)
        g['sweep_mm3'] = sw
        g['lanes_mm3'] = {k: vol_x(X, lane_cyl(X, k), F) for k in SCREWS}
        out['gates'] = g
        ok = (F.lumps.count == 1 and g['front_x_cap_mm3'] < 0.01 and g['front_x_door_mm3'] < 0.01
              and all(v < 0.01 for v in sw.values()) and all(v < 0.01 for v in g['lanes_mm3'].values())
              and all(v > 0.0 for v in rooted.values()))
        out['gates_ok'] = ok
        if MODE == 'commit' and ok:
            old = X.body('HOUSING_F_front'); app_, mat_ = old.appearance, old.material
            old.name = 'HOUSING_F_front_c2a'; old.isLightBulbOn = False
            try:
                nf = X.add(F, 'HOUSING_F_front'); nf.material = mat_; nf.appearance = app_
            except Exception:
                old.name = 'HOUSING_F_front'; old.isLightBulbOn = True
                raise
            out['committed'] = round(nf.volume, 4)
            out['dupes'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F_front (')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2i_front_ribs', MODE, out)
    print(json.dumps(out, separators=(',', ':'))[:5000])
