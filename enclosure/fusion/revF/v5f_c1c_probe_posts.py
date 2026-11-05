# rev F cap block c1c (2026-11-05), read-only: numbers for the cap posts, chins / ribs and the new exhaust row.
#   Candidate post axes (x_rel, y): F0 (0, −27), FL/FR (±62, −27) behind the front bar; BL/BR (±28, −38.6) on the back wall.
#   Per axis: plate underside z (ray up from z 170), top surface z at the axis and on r 3.6 (head Ø7.2) in 8 directions,
#   post cylinder r 4.0 z 170.5…177.5 ∩ bodies nearby (mm³), notch cylinder r 4.2 z 175.3…177.5 ∩ TOOL_cap_off4p7 (must be 0:
#   the cap's bottom face keeps covering the groove), bar back face y (front posts, rays +y at z 163…177) or back-wall
#   inner y (back posts, rays −y at z 156…176).
#   Exhaust: front-shell faces along rays −y at x_rel 0 / 20 / 40 for z 158…171 (new row 162.5…165.5).
#   Joint: front-shell material between y −22.5 and −22.6 above z 175.3 (bbox of the sliver).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
POSTS = {'F0': (0.0, -27.0), 'FL': (62.0, -27.0), 'FR': (-62.0, -27.0), 'BL': (28.0, -38.6), 'BR': (-28.0, -38.6)}
NEAR = ['MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env', 'LEAD_MIC_L', 'LEAD_MIC_R',
        'LEAD_VEML', 'SLAB_frame', 'LCD_panel_body', 'LCD_glass', 'HOUSING_F_door', 'RESP_pcb', 'RESP_CARRIER',
        'TOOL_exhaust_slots', 'KO_K5_UL', 'KO_K5_UR']


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        P = {}
        for k, (xr, y) in POSTS.items():
            r = {}
            hu = ray_hits(X, (XC + xr, y, 170.0), (0, 0, 1), ('HOUSING_F_front',))
            r['plate_under_z'] = round(hu[0][4], 2) if hu else None
            tops = []
            for a in [None] + list(range(0, 360, 45)):
                px = xr if a is None else xr + 3.6 * math.cos(math.radians(a))
                py = y if a is None else y + 3.6 * math.sin(math.radians(a))
                hd = ray_hits(X, (XC + px, py, 190.0), (0, 0, -1), ('HOUSING_F_front',))
                tops.append(round(hd[0][4], 2) if hd else None)
            r['top_z_axis_then_r3.6_0..315'] = tops
            cyl = X.wcyl_z(XC + xr, y, 4.0, 170.5, 177.5)
            hit = {}
            for n in NEAR:
                b = X.body(n)
                if b is None:
                    continue
                v = vol_x(X, cyl, X.tbm.copy(b))
                if v > 0:
                    hit[n] = v
            r['post_r4_x_bodies_mm3'] = hit
            r['post_r4_x_front_mm3'] = vol_x(X, cyl, tb_copy(X, 'HOUSING_F_front'))
            notch = X.wcyl_z(XC + xr, y, 4.2, 175.3, 177.5)
            r['notch_r4.2_x_off4p7_mm3'] = vol_x(X, notch, tb_copy(X, 'TOOL_cap_off4p7'))
            r['notch_r4.2_x_off5p9_mm3'] = vol_x(X, notch, tb_copy(X, 'TOOL_cap_off5p9'))
            if k.startswith('F'):
                rows = []
                for z in range(163, 178, 2):
                    hs = ray_hits(X, (XC + xr, y, float(z)), (0, 1, 0), ('HOUSING_F_front',))
                    rows.append([z, round(hs[0][3], 2) if hs else None])
                r['bar_back_y_by_z'] = rows
                rows = []
                for dx in (-4.0, 4.0):
                    hs = ray_hits(X, (XC + xr + dx, y, 170.0), (0, 1, 0), ('HOUSING_F_front',))
                    rows.append([dx, round(hs[0][3], 2) if hs else None])
                r['bar_back_y_z170_at_dx'] = rows
                if k != 'F0':
                    sx = 1 if xr > 0 else -1
                    rows = []
                    for z in range(163, 178, 2):
                        hs = ray_hits(X, (XC + xr, y, float(z)), (sx, 0, 0), ('HOUSING_F_front',))
                        rows.append([z, round(hs[0][2], 2) if hs else None])
                    r['side_inner_x_by_z'] = rows
            else:
                rows = []
                for z in range(156, 177, 2):
                    hs = ray_hits(X, (XC + xr, y, float(z)), (0, -1, 0), ('HOUSING_F_front', 'HOUSING_F_door'))
                    rows.append([z] + [[h[1][10:11], round(h[3], 2)] for h in hs[:3]])
                r['back_y_by_z'] = rows
            P[k] = r
        out['posts'] = P
        E = {}
        for xr in (0.0, 20.0, 40.0):
            rows = []
            for z10 in range(1580, 1712, 10):
                z = z10 / 10.0
                hs = ray_hits(X, (XC + xr, -30.0, z), (0, -1, 0), ('HOUSING_F_front', 'HOUSING_F_door'))
                rows.append([z] + [[h[1][10:11], round(h[3], 2)] for h in hs[:4]])
            E['x%g' % xr] = rows
        out['exhaust_rays'] = E
        sl = tb_copy(X, 'HOUSING_F_front'); inter(X, sl, X.wbox(-250, 250, -22.6, -22.5, 175.3, 190.0))
        out['joint_sliver'] = {'mm3': round(sl.volume * 1000, 3), 'bbox': [round(v, 2) for v in wbb(X, sl)] if sl.volume > 0 else None}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1c_probe_posts', 'probe', out)
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
