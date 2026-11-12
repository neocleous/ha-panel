# rev F j5d (2026-11-12): close, block 5.4 - read-only: masses, centre of gravity and the push that tips the unit backward, as b6n
#   (2026-11-05), on the model as it stands: base plate, boxes on the plate, main board behind the display, no bracket.
#   Printed parts: volume x 1.05 g/cm3, centroid from physicalProperties. Components: the masses of b6n (envelope sheet where it has
#   one, otherwise the flagged estimates), at the volume-weighted centroid of the bodies named.
#   Pivot: the rear feet (FOOT_RL / FOOT_RR), read from the model: their centre and the rear edge of their contact, at their lowest z.
#   Push at the glass's top front edge (y -6.67, z 174.67): horizontal, and normal to the glass; also normal at the screen's centre.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
RHO = 1.05
LEADS = ['LEAD_PIGTAIL_20V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_RADAR', 'LEAD_TOUCH', 'LEAD_BME680', 'LEAD_VEML', 'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B',
         'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_PI_POWER', 'LEAD_USB_RESP']
COMP = [('speaker driver left', 68.0, 'sheet', ['SPK_L']), ('speaker driver right', 68.0, 'sheet', ['SPK_R']),
        ('main board with supply module', 58.0, 'sheet (about 58, for rev 2.1)', ['MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'MAIN_tall', 'MAIN_low']),
        ('inlet board', 2.2, 'sheet', ['PD_5807_env']), ('touch board', 11.0, 'sheet (calculated)', ['TOUCH_PCB']),
        ('BME680 board', 2.0, 'sheet (< 2)', ['BME680_env']), ('VEML6030 board', 2.0, 'sheet (< 2)', ['VEML_env']),
        ('microphone strips x 2', 2.0, 'sheet (< 1 each)', ['MIC_strip_L_env', 'MIC_strip_R_env']),
        ('feet x 4', 4.0, 'sheet (< 1 each)', ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']),
        ('Pi 5 with cooler', 75.0, 'estimate (rev D)', ['PI5_F', 'PI5_F_cooler']), ('ReSpeaker', 12.0, 'estimate (calculated)', ['RESP_pcb']),
        ('radar board', 2.0, 'estimate', ['LD2410C_env_F']),
        ('display module with glass', 254.0, 'estimate (rev D)', ['LCD_panel_body', 'LCD_glass', 'LCD_pcb_76x110']),
        ('magnets x 20', 11.3, 'calculated', None), ('leads, screws, inserts', 40.0, 'estimate (rev D)', LEADS),
        ('cloth and spline', 25.0, 'estimate (rev D)', ['TOOL_outer_skin_0p7'])]
MAGS = [(72.59, -60.47, 24.92), (67.74, -60.2, 59.85), (58.87, -59.66, 94.7), (39.89, -58.68, 131.11), (16.04, -58.15, 148.35)]
GLASS_TOP = (-6.67, 174.67); SCREEN_C = (5.70, 116.47)


def cen(b):
    return W(b.physicalProperties.centerOfMass)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        pr = {}
        for n in PRINTED:
            b = X.body(n); q = cen(b)
            pr[n] = [round(b.volume, 3), round(b.volume * RHO, 1), [round(v, 1) for v in q]]
        st['printed (cm3, g, centroid)'] = pr
        comp = {}; missing = {}
        for lab, g, src, names in COMP:
            if names is None:
                q = [0.0, sum(m[1] for m in MAGS) / len(MAGS), sum(m[2] for m in MAGS) / len(MAGS)]
            else:
                v = 0.0; s = [0.0, 0.0, 0.0]
                for n in names:
                    b = X.body(n)
                    if b is None:
                        missing.setdefault(lab, []).append(n); continue
                    w = cen(b)
                    for i in range(3):
                        s[i] += w[i] * b.volume
                    v += b.volume
                q = [s[i] / v for i in range(3)] if v > 0 else None
            comp[lab] = [g, src, [round(v, 1) for v in q] if q else None]
        st['components (g, source, centroid)'] = comp; st['missing bodies'] = missing
        m = 0.0; s = [0.0, 0.0, 0.0]; mp = 0.0
        for n, (cm3, g, q) in pr.items():
            mp += g; m += g
            for i in range(3):
                s[i] += q[i] * g
        for lab, (g, src, q) in comp.items():
            if q is None:
                continue
            m += g
            for i in range(3):
                s[i] += q[i] * g
        cog = [s[i] / m for i in range(3)]
        Wn = m / 1000.0 * 9.81
        # the feet are round: wext() reads vertices only (the seam), so centre and radius come from the cylinder face (lesson 132)
        feet = {}
        for n in ('FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'):
            b = X.body(n); best = None
            for fc in b.faces:
                g = fc.geometry
                if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType and (best is None or g.radius > best.radius):
                    best = g
            q = W(best.origin); e = wext(b)
            feet[n] = [round(q[0], 2), round(q[1], 2), round(best.radius * 10.0, 2), e[4], e[5]]
        st['feet (centre x, centre y, radius, z0, z1)'] = feet
        yr = [feet[n] for n in ('FOOT_RL', 'FOOT_RR')]
        y_c = sum(f[1] for f in yr) / 2.0
        y_e = min(f[1] - f[2] for f in yr)
        zp = min(f[3] for f in yr)
        yf = [feet[n] for n in ('FOOT_FL', 'FOOT_FR')]
        y_fc = sum(f[1] for f in yf) / 2.0
        y_fe = max(f[1] + f[2] for f in yf)
        res = {'printed g': round(mp, 1), 'total g': round(m, 1), 'centre of gravity (x, y, z)': [round(v, 2) for v in cog], 'weight N': round(Wn, 3),
               'rear feet: centre y, rear edge y, lowest z': [round(y_c, 2), round(y_e, 2), round(zp, 2)],
               'front feet: centre y, front edge y': [round(y_fc, 2), round(y_fe, 2)],
               'load on the rear feet (share)': round((y_fc - cog[1]) / (y_fc - y_c), 3)}
        for lab, yp in (('forward, about the front feet centres', y_fc), ('forward, about the front edge of the front feet', y_fe)):
            M = Wn * (yp - cog[1]) / 1000.0
            res[lab] = {'restoring moment Nm': round(M, 4), 'pull at the glass top toward the viewer, horizontal N': round(M / ((GLASS_TOP[1] - zp) / 1000.0), 2),
                        'lift at the door\'s foot (y -84), upward N': round(M / ((yp + 84.0) / 1000.0), 2)}
        for lab, yp in (('about the rear feet centres', y_c), ('about the rear edge of the rear feet', y_e)):
            M = Wn * (cog[1] - yp) / 1000.0
            lh = (GLASS_TOP[1] - zp) / 1000.0
            ln = ((GLASS_TOP[1] - zp) * C - (GLASS_TOP[0] - yp) * S) / 1000.0
            lc = ((SCREEN_C[1] - zp) * C - (SCREEN_C[0] - yp) * S) / 1000.0
            res[lab] = {'restoring moment Nm': round(M, 4), 'push at the glass top, horizontal N': round(M / lh, 2), 'lever mm': round(lh * 1000, 1),
                        'push at the glass top, normal to the glass N': round(M / ln, 2), 'push at the screen centre, normal N': round(M / lc, 2)}
        st['result'] = res
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j5d', st)


run(None)
