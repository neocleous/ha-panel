# HA panel model audit (2026-11-05) block 5b: masses, CoG and tipping force on the c2 state (F.7), read-only.
#   Method and component table of v5f_b6n_mass_tip.py (B6n), re-typed here so the log goes to the audit log, plus
#   HOUSING_F_cap in the printed parts (B6n predates the cap). Densities as B6n: ASA 1.05, PETG 1.27 g/cm³; PETG_ALT 1.25
#   (Bambu PETG Basic TDS, E0 consumables §6a) as a third case. Rear feet contact z −3.0, pivots y −69.0 (foot centre) and
#   y −75.35 (patch rear edge); forces at the glass top edge (y −6.67, z 174.67) horizontal and normal to the glass, and
#   normal at the screen centre (y 5.70, z 116.47).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())
PRINTED_B = ['HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET',
             'RESP_CARRIER', 'CRADLE_5807', 'GROMMET_usbc_F']
COMP = [
    ('DMA45-4 L', 68.0, 'sheet', ['SPK_L']),
    ('DMA45-4 R', 68.0, 'sheet', ['SPK_R']),
    ('main board incl. NID100-5', 58.0, 'sheet (~58)', ['MAIN_pcb', 'MAIN_front_env']),
    ('5807 HUSB238', 2.2, 'sheet', ['PD_5807_env']),
    ('touch PCB', 11.0, 'sheet (~11 calc)', ['TOUCH_PCB']),
    ('BME680 board', 2.0, 'sheet (<2)', ['BME680_env']),
    ('VEML6030 board', 2.0, 'sheet (<2)', ['VEML_env']),
    ('mic strips x2', 2.0, 'sheet (<1 each)', ['MIC_strip_L_env', 'MIC_strip_R_env']),
    ('SJ5012 x4', 4.0, 'sheet (<1 each)', ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']),
    ('Pi 5 + Active Cooler', 75.0, 'EST rev D', ['PI5_F', 'PI5_F_cooler']),
    ('ReSpeaker Lite', 12.0, 'EST calc', ['RESP_pcb']),
    ('LD2410C', 2.0, 'EST', ['LD2410C_env_F']),
    ('LCD module + glass', 254.0, 'EST rev D', ['LCD_panel_body', 'LCD_glass', 'LCD_pcb_76x110']),
    ('magnets 20 x Ø8x1.5 NdFeB', 11.3, 'calc 75.4 mm³ x 7.5 g/cm³', None),
    ('harness, screws, inserts', 40.0, 'EST rev D', ['LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R',
                                                     'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_VEML', 'LEAD_BME680',
                                                     'LEAD_RADAR', 'LEAD_USB_RESP', 'LEAD_DSI', 'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER']),
    ('cloth + spline', 25.0, 'EST rev D', ['TOOL_outer_skin_0p7']),
]
MAGS = [(72.59, -60.47, 24.92), (67.74, -60.2, 59.85), (58.87, -59.66, 94.7), (39.89, -58.68, 131.11), (16.04, -58.15, 148.35)]
GLASS_TOP = (-6.67, 174.67); SCREEN_C = (5.70, 116.47)


def centroid(X, names):
    v = 0.0; s = [0.0, 0.0, 0.0]; miss = []
    for n in names:
        b = X.body(n)
        if b is None:
            miss.append(n); continue
        c = b.physicalProperties.centerOfMass; vol = b.volume
        w = (c.x * 10 - XC, wy(c), wz(c))
        for i in range(3):
            s[i] += w[i] * vol
        v += vol
    return ([s[i] / v for i in range(3)] if v > 0 else None), miss


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        pr = {}
        for n in PRINTED_B:
            b = X.body(n); c = b.physicalProperties.centerOfMass
            pr[n] = {'cm3': round(b.volume, 4), 'c': [round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2)]}
        comp = {}; missing = {}
        for (lab, g, src, names) in COMP:
            if names is None:
                c = [0.0, sum(m[1] for m in MAGS) / len(MAGS), sum(m[2] for m in MAGS) / len(MAGS)]
            else:
                c, miss = centroid(X, names)
                if miss:
                    missing[lab] = miss
            comp[lab] = {'g': g, 'src': src, 'c': [round(q, 2) for q in c] if c else None}
        out['printed'] = pr; out['components'] = comp; out['missing_bodies'] = missing
        res = {}
        for mat, rho in (('ASA', 1.05), ('PETG', 1.27), ('PETG_ALT', 1.25)):
            m = 0.0; s = [0.0, 0.0, 0.0]; mp = 0.0
            for n, d in pr.items():
                g = d['cm3'] * rho; mp += g; m += g
                for i in range(3):
                    s[i] += d['c'][i] * g
            for lab, d in comp.items():
                if d['c'] is None:
                    continue
                m += d['g']
                for i in range(3):
                    s[i] += d['c'][i] * d['g']
            cog = [s[i] / m for i in range(3)]
            W = m / 1000 * 9.81
            r = {'printed_g': round(mp, 1), 'total_g': round(m, 1), 'cog_xr_y_z': [round(q, 2) for q in cog], 'W_N': round(W, 3)}
            for pv, yp in (('foot_centre_y-69.0', -69.0), ('foot_rear_edge_y-75.35', -75.35)):
                zp = -3.0
                M = W * (cog[1] - yp) / 1000
                lh = (GLASS_TOP[1] - zp) / 1000
                ln = ((GLASS_TOP[1] - zp) * C - (GLASS_TOP[0] - yp) * S) / 1000
                lc = ((SCREEN_C[1] - zp) * C - (SCREEN_C[0] - yp) * S) / 1000
                r[pv] = {'M_Nm': round(M, 3), 'F_glass_top_horizontal_N': round(M / lh, 2), 'F_glass_top_normal_N': round(M / ln, 2),
                         'F_screen_centre_normal_N': round(M / lc, 2)}
            res[mat] = r
        out['result'] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a5b_mass_tip', 'mass', out)
    print(json.dumps(out, separators=(',', ':')))
