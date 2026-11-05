# rev F cap block c1d (2026-11-05): split the front shell into HOUSING_F_front + HOUSING_F_cap and build the fabric clamp
#   (Daniel 13:31 / 13:51: 1 A spline groove in the ledge, 2 A countersunk M3 from the top, 3 a joint ≈ 3 mm behind the
#   display's top-back edge). All TemporaryBRep; the bodies are added only if every gate passes (MODE 'commit').
#   d = normal distance inside REF_F_outer (offset tools TOOL_cap_off*, c1b2 / c1b5). World mm, x as x_rel.
#   Joint: front shell keeps y ≥ −22.5 above z 175.3 (the old groove's front end, 3.0 behind the slab's back face y −19.5);
#     cap front face y −22.6 (0.1 gap). Split at z 175.3 near the walls (d < 7.3) and at z 174.0 inside (the four mic
#     heat-stake pins reach z 174.8 and stay on the cap).
#   Front shell: ledge top z 175.3 from the cloth surface (d 0.7) to d 5.9; flange d 0.72…5.9 z 171.8…175.3 with two 0.9
#     steps under it (d 5.0 z 170.95…171.8, d 4.1 z 170.1…170.95, ≈ 45° in two steps; the lower exhaust row ends at z 170.0);
#     spline groove d 1.9…4.7 (1.2…4.0 from the cloth surface, 2.8 wide), floor z 172.8 (2.5 deep), y < −22.5;
#     the upper exhaust row (z 171.5…174.5) is filled by the flange, a new row z 162.5…165.5 (x ±45, 270 mm²) replaces it,
#     lower row z 167.0…170.0 unchanged → 540 mm² as before (minus the two rib widths).
#   Cap: old top region; within d 7.3 below z 177.2 rebuilt from REF (no near-coincident faces with the old hard band):
#     bottom face z 175.8 from the outer surface to d 7.3 (0.5 over the ledge: 0.7 cloth squeezed 0.2), the old groove
#     filled; z 177.2…177.5 closed by the 0.72…7.3 band moved up 0.4 (stays 0.5 inside the outer surface);
#     lip d 6.1…7.3 (0.2 off the flange, 1.2 thick) z 173.3…175.8.
#   Posts (front shell, Ruthex M3 Ø4.0 × 6.0 from the top, plate underside z 177.5 measured at all four): FL/FR (±60, −27)
#     behind the front bar, BL/BR (±28, −38.1) on the back wall; Ø8 z 170.5…177.5, 45° cone to Ø2 at z 167.5, rib 2.0
#     with a 55° lower edge to the bar (FL/FR, ends z ≈ 162.8) or the back wall (BL/BR, z ≈ 157.3); web to the bar
#     (z 170.5…173.1) / flange (z 171.8…173.1), under the cap's lip; ribs / webs stop 1.0 inside the bar's back face or at
#     the back wall's mid-plane (the slots they cross stay open on the outer half). Cap: notch r 4.2 round each post, Ø3.4 hole,
#     90° countersink Ø6.9 (ISO 10642 M3 head dk ≤ 6.72, flush on the flat top z 180), M3 × 8: 5.3 thread engagement.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
MODE = 'commit'           # gates decide; a dry run is the same script with MODE 'dry'
Y_T, Y_TC = -22.5, -22.6
Z_L, Z_C, Z_G, Z_F, Z_IN = 175.3, 175.8, 172.8, 171.8, 174.0
STEPS = [(5.0, 170.95, 171.8), (4.1, 170.1, 170.95)]
LIP = (173.3, 175.85)
Z_TOP, Z_B, H_INS = 177.5, 170.5, 6.0
POSTS = {'FL': (60.0, -27.0, (0.0, 1.0)), 'FR': (-60.0, -27.0, (0.0, 1.0)),
         'BL': (28.0, -38.1, (0.0, -1.0)), 'BR': (-28.0, -38.1, (0.0, -1.0))}
RIB_K = 0.700                     # 55° overhang (from vertical): 0.70 down per mm along the rib
V_FRONT, V_DOOR = 240.8876, 51.101
NEAR = ['MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env', 'LEAD_MIC_L', 'LEAD_MIC_R',
        'LEAD_VEML', 'SLAB_frame', 'LCD_glass', 'HOUSING_F_door']


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


def post_body(X, k):
    xr, y0, u = POSTS[k]; ux, uy = u
    b = X.wcyl_z(XC + xr, y0, 4.0, Z_B, Z_TOP)
    X.union(b, X.tbm.createCylinderOrCone(Dw(XC + xr, y0, Z_B), 0.4, Dw(XC + xr, y0, Z_B - 3.0), 0.1))
    smax = 16.0; zb = Z_B - 3.0 - RIB_K * (smax - 1.0) - 1.0
    rib = lbox(X, (xr + ux * (smax - 1.0) / 2, y0 + uy * (smax - 1.0) / 2, (Z_B + zb) / 2), (ux, uy, 0.0), (-uy, ux, 0.0),
               smax + 1.0, 2.0, Z_B - zb)
    p0 = (xr + ux * 1.0, y0 + uy * 1.0, Z_B - 3.0)
    X.diff(rib, hs_box(X, p0, (-RIB_K * ux, -RIB_K * uy, -1.0)))
    if k.startswith('F'):          # into the front bar: stop 1.0 inside its back face (plane y -19.32 at z 163, 12° tilt)
        web = lbox(X, (xr + ux * 4.0, y0 + uy * 4.0, (Z_B + 173.1) / 2), (ux, uy, 0.0), (-uy, ux, 0.0), 8.0, 8.0, 173.1 - Z_B)
        lim = hs_box(X, (xr, -18.30, 163.0), (0.0, 1.0, 0.213))
    else:                          # into the back wall: stop at its mid-plane (x 28: y -53.1 at z 158, 0.39 / mm forward)
        web = lbox(X, (xr + ux * 4.5, y0 + uy * 4.5, (Z_F + 173.1) / 2), (ux, uy, 0.0), (-uy, ux, 0.0), 9.0, 8.0, 173.1 - Z_F)
        lim = hs_box(X, (xr, -53.1, 158.0), (0.0, -1.0, 0.39))
    X.diff(rib, X.tbm.copy(lim)); X.diff(web, X.tbm.copy(lim))
    X.union(b, rib); X.union(b, web)
    inter(X, b, X.wbox(-250, 250, -250, 250, 156.5, Z_TOP))
    return b


def lumps_tb(t):
    return t.lumps.count if hasattr(t, 'lumps') else -1


def run(_context):
    X = Ctx(); out = {'MODE': MODE}
    t0 = time.time()
    try:
        fb, db = X.body('HOUSING_F_front'), X.body('HOUSING_F_door')
        out['guard'] = [round(fb.volume, 4), round(db.volume, 4)]
        if abs(fb.volume - V_FRONT) > 0.001 or abs(db.volume - V_DOOR) > 0.001:
            raise RuntimeError('volume guard: front %.4f door %.4f' % (fb.volume, db.volume))
        c73 = core(X, 7.3)
        # ---- cap ----
        CAP = tb_copy(X, 'HOUSING_F_front'); inter(X, CAP, split_region(X, Y_TC))
        v_cap_old = CAP.volume * 1000
        rm = X.wbox(-250, 250, -250, Y_TC, Z_L - 0.01, 177.2); X.diff(rm, X.tbm.copy(c73))
        X.diff(CAP, rm)
        X.union(CAP, band(X, 0, 7.3, Z_C, 177.2, Y_TC))
        r2 = band(X, 0.72, 7.3, 176.75, 177.2, Y_TC + 5.0); mvw(X, r2, 0.0, 0.0, 0.4)
        inter(X, r2, X.wbox(-250, 250, -250, Y_TC, 177.15, 177.6)); X.union(CAP, r2)
        X.union(CAP, band(X, 6.1, 7.3, LIP[0], LIP[1], Y_TC))
        for k, (xr, y0, u) in POSTS.items():
            X.diff(CAP, X.wcyl_z(XC + xr, y0, 4.2, 170.0, Z_TOP))
            X.diff(CAP, X.wcyl_z(XC + xr, y0, 1.7, 177.0, 181.0))
            X.diff(CAP, X.tbm.createCylinderOrCone(Dw(XC + xr, y0, 180.5), 0.395, Dw(XC + xr, y0, 178.25), 0.17))
        out['cap'] = {'cm3': round(CAP.volume, 4), 'lumps': lumps_tb(CAP), 'faces': CAP.faces.count,
                      'old_region_cm3': round(v_cap_old / 1000, 4)}
        # ---- front shell ----
        F = tb_copy(X, 'HOUSING_F_front'); X.diff(F, split_region(X, Y_T))
        v_cut = F.volume
        FL = band(X, 0.72, 5.9, Z_F, Z_L, 0.0)
        for (t, z0, z1) in STEPS:
            X.union(FL, band(X, 0.72, t, z0, z1, 0.0))
        out['flange_cm3'] = round(FL.volume, 4)
        X.union(F, FL)
        G = band(X, 1.9, 4.7, Z_G, Z_L + 0.2, Y_T)
        out['groove_cm3'] = round(G.volume, 4)
        X.diff(F, G)
        EX = X.wbox(XC - 45.0, XC + 45.0, -62.0, -40.0, 162.5, 165.5)
        X.diff(F, X.tbm.copy(EX))
        pv = {}; PB = None; HO = None
        for k, (xr, y0, u) in POSTS.items():
            pb = post_body(X, k); pv[k] = round(pb.volume * 1000, 1)
            PB = pb if PB is None else X.union(PB, pb)
            h = X.wcyl_z(XC + xr, y0, 2.0, Z_TOP - H_INS, Z_TOP + 0.5)
            HO = h if HO is None else X.union(HO, h)
        out['posts_mm3'] = pv
        X.union(F, PB); X.diff(F, HO)
        out['front'] = {'cm3': round(F.volume, 4), 'lumps': lumps_tb(F), 'faces': F.faces.count, 'after_split_cm3': round(v_cut, 4)}
        # ---- gates ----
        g = {}
        top = lambda: X.wbox(-250, 250, -250, 250, 150.0, 260.0)
        FT = X.tbm.copy(F); inter(X, FT, top())                 # changes are all above z 156.5: check the top part only
        OT = tb_copy(X, 'HOUSING_F_front'); inter(X, OT, top())
        DT = tb_copy(X, 'HOUSING_F_door'); inter(X, DT, top())
        RT = tb_copy(X, 'REF_F_outer'); inter(X, RT, top())
        g['front_x_cap_mm3'] = vol_x(X, FT, CAP)
        g['front_x_door_mm3'] = vol_x(X, FT, DT)
        g['cap_x_door_mm3'] = vol_x(X, CAP, DT)
        g['cap_outside_REF_mm3'] = round(CAP.volume * 1000 - vol_x(X, CAP, RT), 3)
        g['front_top_outside_REF_mm3'] = round(FT.volume * 1000 - vol_x(X, FT, RT), 3)
        g['old_top_outside_REF_mm3'] = round(OT.volume * 1000 - vol_x(X, OT, RT), 3)
        nb = {}
        for n in NEAR:
            b = X.body(n)
            if b is None or n == 'HOUSING_F_door':
                continue
            a = vol_x(X, CAP, X.tbm.copy(b)); c = vol_x(X, FT, X.tbm.copy(b))
            if a or c:
                nb[n] = {'cap': a, 'front': c, 'old_front': vol_x(X, OT, X.tbm.copy(b))}
        g['vs_bodies_mm3'] = nb
        out['gates'] = g
        ok = (lumps_tb(F) == 1 and lumps_tb(CAP) == 1 and g['front_x_cap_mm3'] < 0.01 and g['front_x_door_mm3'] < 0.01
              and g['cap_x_door_mm3'] < 0.01)
        out['gates_ok'] = ok
        if MODE == 'commit' and ok:
            old = X.body('HOUSING_F_front'); app_, mat_ = old.appearance, old.material   # old body kept hidden as _c0
            if X.body('HOUSING_F_front_c0') is not None:
                raise RuntimeError('HOUSING_F_front_c0 exists')
            old.name = 'HOUSING_F_front_c0'; old.isLightBulbOn = False
            try:
                nf = X.add(F, 'HOUSING_F_front'); nf.material = mat_; nf.appearance = app_
            except Exception:
                old.name = 'HOUSING_F_front'; old.isLightBulbOn = True
                raise
            nc = X.add(CAP, 'HOUSING_F_cap'); nc.material = mat_; nc.appearance = app_
            te = X.add(EX, 'TOOL_exhaust_row_c1'); te.isLightBulbOn = False
            out['committed'] = {'front': round(nf.volume, 4), 'cap': round(nc.volume, 4),
                                'dupes': [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_front (', 'HOUSING_F_cap ('))]}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1d_cap_build', MODE, out)
    print(json.dumps(out, separators=(',', ':'))[:6000])
