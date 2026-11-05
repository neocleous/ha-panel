# rev F cap block c2c (2026-11-05): cap held by four hidden M3 screws from inside (Daniel 15:26: "The lid should have the
#   screw bosses with the threaded inserts and the screws should come up from the shell into the lid"), VEML6030 moved to
#   the centre (Daniel: "Centre, as proposed"). Front hold: the swing-in hook can't be assembled (the cap's front face
#   z 177.5–180 sits 0.1 behind the bar, above the hook pivot), so option A as proposed at 15:57: two more screws at the rear
#   corners (their key lanes were blocked only by the old VEML lead) + a support shelf on the bar under the cap's front edge.
#   Rebuilt from HOUSING_F_front_c0 like c1d2 (same split, cap bands, flange, steps, exhaust row, groove last), without the
#   c1 posts, notches and countersinks. Numbers from c2b0:
#   - Boss axes (Ø8 boss tangent to the lip's outer face d 6.1 at z 175.8): BL/BR (±25.91, −37.80), SL/SR (±43.36, −32.85).
#   - Cap: boss r 4.0 from z 172.5 up into the plate (underside 177.5); Ruthex M3 hole Ø4.0 × 6.0 from below (z 172.5–178.5,
#     1.5 under the top z 180).
#   - Front shell: pad z 169.5–172.5 (r 5.5 + a strip along the key lane to the wall, d ≥ 4.1 so it joins the flange steps
#     and leaves the exhaust slots open), Ø3.4 through; two 2.0 ribs at ±4.5 either side of the key lane (lane plan
#     direction), lower edge 55° from vertical, merged into the wall at d ≥ 1.9. DIN912 M3 × 8: head z 166.5–169.5, tip
#     177.5 (5.0 in the insert). The boss bottom sits on the pad top (z 172.5) and sets the 0.5 clamp gap over the ledge.
#   - Key lanes (Ø5, from the head bottom z 166.2): BL → (20, −100, 30) 24.6°, BR → (−20, −100, 30), SL → (20, −100, 30)
#     27.6°, SR → (−20, −100, 30); clear of every part and lead in c2b0 (old VEML lead excluded). Kept as hidden KO_capkey_*.
#   - Shelf: 45° corbel on the bar's back face, top z 177.4 (0.1 under the cap), to y −23.3 (0.2 in front of the mic
#     strips), x ±60.
#   - VEML6030: VEML_env moved (−46.0, −2.7) to x −7.5…7.5, y −41.2…−26.2; pocket 15.4 × 15.4 × 0.8 (z 177.5–178.3), lux
#     port Ø2 at (0, −33.7); the old pocket (x 38.3–53.7, y −23.3…−38.7) and port (46, −31) filled. Run 1 had the proposed
#     y −42…−27 / port (0, −34.5): the cap ring's inner face leans forward to y −42.33 at z 177.2, 0.33 from the envelope;
#     run 2 (0.7 forward) still had 0.95 at z 177.4 (gate: the envelope grown 1.0 backward ∩ cap 0.1 mm³) – 0.8 forward
#     keeps the 1.0 to the ring / lip that was proposed (run 3: 0.01 mm³ left ≈ 0.997 at the top corner; gate < 0.05).
#   - Cap front edge: c0's inner corner fillet (bar back face / top wall underside) hangs below the plate underside at the
#     cap's front edge (to z ≈ 177.3, y −22.6…−22.8) and touched the shelf (run 1: front ∩ cap 1.04 mm³) – squared off
#     (|x| ≤ 61, y −23.2…−22.55, z 176.8–177.5).
#   - Mic strips 30 → 29 long (inner end x ±7.5 → ±8.5, ports ±35.5 and pins ±11.5 / ±30.0 unchanged, mic spacing 71.0
#     unchanged): with the 15 × 15 VEML envelope the strips would touch it over y −27…−29.5; pockets x ±(8.3…37.7) leave
#     0.6 between the pockets. MIC_strip_*_env and KO_mic_*_back cut at |x| 8.5.
#   - LEAD_VEML Ø3 re-routed from the board's back edge down the centre, joining the old route at (40, −35, 130).
#   Commit (gated): HOUSING_F_front / HOUSING_F_cap / VEML_env / LEAD_VEML / MIC_strip_*_env / KO_mic_*_back → *_c1 (hidden),
#   new bodies under the old names. Fillets (c1e4 method) follow in c2d.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
MODE = 'commit'
Y_T, Y_TC = -22.5, -22.6
Z_L, Z_C, Z_G, Z_F, Z_IN = 175.3, 175.8, 172.8, 171.8, 174.0
STEPS = [(5.0, 170.95, 171.8), (4.1, 170.1, 170.95)]
LIP = (173.3, 175.85)
Z_PAD_B, Z_BOSS_B, Z_PLATE = 169.5, 172.5, 177.5
R_BOSS, R_INS, H_INS, R_PAD, R_CLR = 4.0, 2.0, 6.0, 5.5, 1.7
RIB_T, RIB_OFF, RIB_K = 2.0, 4.5, 0.700
SCREWS = {'BL': ((25.91, -37.80), (20.0, 30.0)), 'BR': ((-25.91, -37.80), (-20.0, 30.0)),
          'SL': ((43.36, -32.85), (20.0, 30.0)), 'SR': ((-43.36, -32.85), (-20.0, 30.0))}
Z_LANE0, R_LANE = 166.2, 2.5
V_C0, V_DOOR, V_FRONT_C1, V_CAP_C1 = 240.8876, 51.101, 235.6548, 8.9419
VEML_MOVE = (-46.0, -2.7)
LEAD_PTS = [(0.0, -39.7, 174.5), (0.0, -39.7, 165.0), (14.0, -40.0, 150.0), (40.0, -35.0, 130.0), (40.0, -34.0, 95.0),
            (36.0, -15.0, 70.0), (36.0, 0.5, 52.0), (36.0, 2.0, 46.0)]
LEAD_EXCL = ('VEML_env', 'KO_touch_back', 'TOUCH_PCB')
OBST = ['SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
        'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER', 'RESP_pcb',
        'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'LD2410C_env_F', 'BME680_env', 'GPIO_plugA_env', 'GPIO_plugB_env',
        'USBA_plug_env', 'USBA_cable_env', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_LCD_5V', 'LEAD_DSI', 'LEAD_USB_RESP', 'LEAD_TOUCH',
        'LEAD_BME680', 'LEAD_RADAR', 'LEAD_GPIO_A', 'LEAD_GPIO_B']
RENAME = ['HOUSING_F_front', 'HOUSING_F_cap', 'VEML_env', 'LEAD_VEML', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back',
          'KO_mic_R_back']


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


def rib_pair(X, k, c19):
    (cx, cy), _t = SCREWS[k]; vx, vy = lane_dir(k); wx, wy_ = -vy, vx
    smin, smax = -R_PAD, 16.0
    zb = Z_PAD_B - RIB_K * (smax - smin) - 1.0
    ribs = None
    for side in (-1.0, 1.0):
        o = side * RIB_OFF; sm = (smin + smax) / 2
        r = lbox(X, (cx + vx * sm + wx * o, cy + vy * sm + wy_ * o, (Z_PAD_B + 0.5 + zb) / 2), (vx, vy, 0.0), (wx, wy_, 0.0),
                 smax - smin, RIB_T, Z_PAD_B + 0.5 - zb)
        X.diff(r, hs_box(X, (cx + vx * smin, cy + vy * smin, Z_PAD_B), (-RIB_K * vx, -RIB_K * vy, -1.0)))
        ribs = r if ribs is None else X.union(ribs, r)
    inter(X, ribs, X.tbm.copy(c19))
    return ribs


def tube(X, pts, dia):
    r = dia / 2.0; tb = None; L = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L += math.sqrt(sum((b[j] - a[j]) ** 2 for j in range(3)))
        c = X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), r / 10, Dw(XC + b[0], b[1], b[2]), r / 10)
        tb = c if tb is None else X.union(tb, c)
        if i > 0:
            X.union(tb, X.tbm.createSphere(Dw(XC + a[0], a[1], a[2]), r / 10))
    return tb, round(L, 1)


def lumps_tb(t):
    return t.lumps.count if hasattr(t, 'lumps') else -1


def run(_context):
    X = Ctx(); out = {'MODE': MODE}
    t0 = time.time()
    try:
        g0 = {n: round(X.body(n).volume, 4) for n in ('HOUSING_F_front_c0', 'HOUSING_F_door', 'HOUSING_F_front', 'HOUSING_F_cap')}
        out['guard'] = g0
        if abs(g0['HOUSING_F_front_c0'] - V_C0) > 0.001 or abs(g0['HOUSING_F_door'] - V_DOOR) > 0.001 or \
                abs(g0['HOUSING_F_front'] - V_FRONT_C1) > 0.001 or abs(g0['HOUSING_F_cap'] - V_CAP_C1) > 0.001:
            raise RuntimeError('volume guard %s' % g0)
        for n in RENAME:
            if X.body(n + '_c1') is not None:
                raise RuntimeError('%s_c1 exists' % n)
        c73 = core(X, 7.3); c41 = core(X, 4.1); c19 = core(X, 1.9)
        REF = tb_copy(X, 'REF_F_outer')
        # ---- cap (c1d2 without notches / countersinks) ----
        CAP = tb_copy(X, 'HOUSING_F_front_c0'); inter(X, CAP, split_region(X, Y_TC))
        rm = X.wbox(-250, 250, -250, Y_TC, Z_L - 0.01, 177.2); X.diff(rm, X.tbm.copy(c73))
        X.diff(CAP, rm)
        X.union(CAP, band(X, 0, 7.3, Z_C, 177.2, Y_TC))
        r2 = band(X, 0.72, 7.3, 176.75, 177.2, Y_TC + 5.0); mvw(X, r2, 0.0, 0.0, 0.4)
        inter(X, r2, X.wbox(-250, 250, -250, Y_TC, 177.15, 177.6)); X.union(CAP, r2)
        X.union(CAP, band(X, 6.1, 7.3, LIP[0], LIP[1], Y_TC))
        X.diff(CAP, X.wbox(XC - 61.0, XC + 61.0, -23.2, -22.55, 176.8, Z_PLATE))
        v_base = CAP.volume
        fv = X.wbox(XC + 38.2, XC + 53.8, -38.8, -23.2, Z_PLATE, 181.0); inter(X, fv, X.tbm.copy(REF)); X.union(CAP, fv)
        for s in (1.0, -1.0):
            fm = X.wbox(XC + s * 7.2, XC + s * 8.3, -29.8, -23.2, Z_PLATE, 178.4); inter(X, fm, X.tbm.copy(REF)); X.union(CAP, fm)
        v_fill = CAP.volume
        BO = None; HI = None
        for k, ((cx, cy), _t) in SCREWS.items():
            b = X.wcyl_z(XC + cx, cy, R_BOSS, Z_BOSS_B, Z_PLATE + 0.2)
            BO = b if BO is None else X.union(BO, b)
            h = X.wcyl_z(XC + cx, cy, R_INS, Z_BOSS_B - 0.1, Z_BOSS_B + H_INS)
            HI = h if HI is None else X.union(HI, h)
        inter(X, BO, X.tbm.copy(REF))
        X.union(CAP, BO)
        X.diff(CAP, X.wbox(XC - 7.7, XC + 7.7, -41.4, -26.0, Z_PLATE - 0.1, 178.3))
        X.diff(CAP, X.wcyl_z(XC, -33.7, 1.0, 178.0, 181.0))
        X.diff(CAP, HI)
        out['cap'] = {'cm3': round(CAP.volume, 4), 'lumps': lumps_tb(CAP), 'faces': CAP.faces.count,
                      'base_cm3': round(v_base, 4), 'fills_mm3': round((v_fill - v_base) * 1000, 2)}
        log('v5f_c2c_cap_hidden_screws', 'progress', {'cap': out['cap'], 't_s': round(time.time() - t0, 1)})
        # ---- front shell ----
        F = tb_copy(X, 'HOUSING_F_front_c0'); X.diff(F, split_region(X, Y_T))
        FL = band(X, 0.72, 5.9, Z_F, Z_L, 0.0)
        for (t, z0, z1) in STEPS:
            X.union(FL, band(X, 0.72, t, z0, z1, 0.0))
        X.union(F, FL)
        EX = X.wbox(XC - 45.0, XC + 45.0, -62.0, -40.0, 162.5, 165.5)
        X.diff(F, X.tbm.copy(EX))
        PR = None; HO = None; pv = {}
        for k, ((cx, cy), _t) in SCREWS.items():
            p = pad_body(X, k, c41); rb = rib_pair(X, k, c19)
            pv[k] = {'pad_mm3': round(p.volume * 1000, 1), 'ribs_mm3': round(rb.volume * 1000, 1)}
            X.union(p, rb)
            PR = p if PR is None else X.union(PR, p)
            h = X.wcyl_z(XC + cx, cy, R_CLR, Z_PAD_B - 0.5, Z_BOSS_B + 0.5)
            HO = h if HO is None else X.union(HO, h)
        out['pads'] = pv
        X.union(F, PR); X.diff(F, HO)
        SH = X.wbox(XC - 60.0, XC + 60.0, -23.3, -21.6, 176.0, 177.4)
        inter(X, SH, hs_box(X, (0.0, -23.3, 177.4), (0.0, 0.7071, 0.7071), 160.0))
        out['shelf_mm3'] = round(SH.volume * 1000, 1)
        X.union(F, SH)
        G = band(X, 1.9, 4.7, Z_G, Z_L + 0.2, Y_T)              # groove last
        out['groove_x_added_mm3'] = vol_x(X, G, PR)
        X.diff(F, G)
        out['front'] = {'cm3': round(F.volume, 4), 'lumps': lumps_tb(F), 'faces': F.faces.count}
        log('v5f_c2c_cap_hidden_screws', 'progress', {'front': out['front'], 'pads': pv, 't_s': round(time.time() - t0, 1)})
        # ---- moved / trimmed bodies ----
        VE = tb_copy(X, 'VEML_env'); mvw(X, VE, VEML_MOVE[0], VEML_MOVE[1], 0.0)
        NEW = {'VEML_env': VE}
        for n, s in (('MIC_strip_L_env', 1.0), ('KO_mic_L_back', 1.0), ('MIC_strip_R_env', -1.0), ('KO_mic_R_back', -1.0)):
            t = tb_copy(X, n)
            inter(X, t, X.wbox(XC + 8.5, XC + 200.0, -250, 250, 0, 260) if s > 0 else X.wbox(XC - 200.0, XC - 8.5, -250, 250, 0, 260))
            NEW[n] = t
        LV, lv_len = tube(X, LEAD_PTS, 3.0)
        NEW['LEAD_VEML'] = LV
        out['lead_veml_mm'] = lv_len
        out['new_bb'] = {n: [round(v, 2) for v in wbb(X, t)] for n, t in NEW.items()}
        # ---- gates ----
        g = {}
        top = lambda: X.wbox(-250, 250, -250, 250, 150.0, 260.0)
        FT = X.tbm.copy(F); inter(X, FT, top())
        OT = tb_copy(X, 'HOUSING_F_front_c0'); inter(X, OT, top())
        DT = tb_copy(X, 'HOUSING_F_door'); inter(X, DT, top())
        RT = tb_copy(X, 'REF_F_outer'); inter(X, RT, top())
        g['front_x_cap_mm3'] = vol_x(X, FT, CAP)
        g['front_x_door_mm3'] = vol_x(X, FT, DT)
        g['cap_x_door_mm3'] = vol_x(X, CAP, DT)
        g['cap_outside_REF_mm3'] = round(CAP.volume * 1000 - vol_x(X, CAP, RT), 3)
        g['front_top_outside_REF_mm3'] = round(FT.volume * 1000 - vol_x(X, FT, RT), 3)
        g['c0_top_outside_REF_mm3'] = round(OT.volume * 1000 - vol_x(X, OT, RT), 3)
        nb = {}
        for n in ('VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'LEAD_VEML'):
            nb[n] = {'cap': vol_x(X, CAP, NEW[n]), 'front': vol_x(X, FT, NEW[n])}
        for n in ('LEAD_MIC_L', 'LEAD_MIC_R', 'SLAB_frame', 'LCD_glass'):
            b = X.body(n)
            if b is not None:
                nb[n] = {'cap': vol_x(X, CAP, X.tbm.copy(b)), 'front_change': round(vol_x(X, FT, X.tbm.copy(b)) - vol_x(X, OT, X.tbm.copy(b)), 2)}
        grown = X.wbox(XC - 7.5, XC + 7.5, -42.2, -26.2, 172.3, Z_PLATE - 0.1)
        nb['VEML_env_1mm_back_x_cap'] = vol_x(X, grown, CAP)
        g['vs_bodies_mm3'] = nb
        ln = {}
        for k in SCREWS:
            lc = lane_cyl(X, k)
            ln[k] = {'front': vol_x(X, lc, F), 'cap': vol_x(X, lc, CAP), 'lead_veml': vol_x(X, lc, LV),
                     'ko_mic': vol_x(X, lc, NEW['KO_mic_L_back']) + vol_x(X, lc, NEW['KO_mic_R_back'])}
        g['lanes_mm3'] = ln
        log('v5f_c2c_cap_hidden_screws', 'progress', {'gates_so_far': g, 't_s': round(time.time() - t0, 1)})
        lb = wbb(X, LV); crop = wbox_rel(X, lb, 1.0); lh = {}
        for n in OBST + [b.name for b in X.comp.bRepBodies if b.name.startswith('LCD_')]:
            b = X.body(n)
            if b is None or n in LEAD_EXCL:
                continue
            bb = wbb(X, b)
            if bb[1] < lb[0] or bb[0] > lb[1] or bb[3] < lb[2] or bb[2] > lb[3] or bb[5] < lb[4] or bb[4] > lb[5]:
                continue
            q = X.tbm.copy(b); inter(X, q, X.tbm.copy(crop))
            v = vol_x(X, LV, q)
            if v > 0:
                lh[n] = v
        for n in ('MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back'):
            v = vol_x(X, LV, NEW[n])
            if v > 0:
                lh[n + '(new)'] = v
        FL2 = X.tbm.copy(F); inter(X, FL2, X.tbm.copy(crop))
        lh['front(new)'] = vol_x(X, LV, FL2)
        lh['cap(new)'] = vol_x(X, LV, CAP)
        g['lead_veml_hits_mm3'] = lh
        out['gates'] = g
        ok = (lumps_tb(F) == 1 and lumps_tb(CAP) == 1 and g['front_x_cap_mm3'] < 0.01 and g['front_x_door_mm3'] < 0.01
              and g['cap_x_door_mm3'] < 0.01 and nb['VEML_env']['cap'] < 0.01 and nb['VEML_env']['front'] < 0.01
              and nb['VEML_env_1mm_back_x_cap'] < 0.05
              and all(v['front'] < 0.01 and v['cap'] < 0.01 and v['lead_veml'] < 0.01 for v in ln.values()))
        out['gates_ok'] = ok
        if MODE == 'commit' and ok:
            olds = {}
            for n in RENAME:
                b = X.body(n); olds[n] = (b.appearance, b.material, b.isLightBulbOn)
                b.name = n + '_c1'; b.isLightBulbOn = False
            added = {}
            try:
                for n, t in (('HOUSING_F_front', F), ('HOUSING_F_cap', CAP)):
                    nb_ = X.add(t, n); nb_.material = olds[n][1]; nb_.appearance = olds[n][0]; nb_.isLightBulbOn = olds[n][2]
                    added[n] = round(nb_.volume, 4)
                for n, t in NEW.items():
                    nb_ = X.add(t, n); nb_.appearance = olds[n][0]; nb_.isLightBulbOn = olds[n][2]
                    added[n] = round(nb_.volume, 4)
                for k in SCREWS:
                    lc = lane_cyl(X, k); inter(X, lc, X.tbm.copy(REF))
                    kb = X.add(lc, 'KO_capkey_' + k); kb.isLightBulbOn = False
                    added['KO_capkey_' + k] = round(kb.volume, 4)
            except Exception:
                for n in added:
                    b = X.body(n)
                    if b is not None:
                        b.deleteMe()
                for n in RENAME:
                    b = X.body(n + '_c1'); b.name = n; b.isLightBulbOn = olds[n][2]
                raise
            out['committed'] = added
            out['dupes'] = [b.name for b in X.comp.bRepBodies if ' (' in b.name and b.name.split(' (')[0] in RENAME]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2c_cap_hidden_screws', MODE, out)
    print(json.dumps(out, separators=(',', ':'))[:6000])
