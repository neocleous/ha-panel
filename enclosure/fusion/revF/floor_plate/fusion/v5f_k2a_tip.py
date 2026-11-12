# rev F k2a (2026-11-12): fix pass, fix 2 - read-only: masses, centre of gravity and the tip figures, as v5f_j5d_tip.py (close of the
#   enclosure work), on the model as it stands. The front feet are read from the model, or given for a what-if.
#   Run through k.step(); the library is the global k. main(X, front=None, ballast=None, quiet=False) prints and returns the figures.
#     front   = {'FOOT_FL': (x, y), 'FOOT_FR': (x, y)}: front feet centres to assume instead of the model's
#     ballast = (grams, y, z): an extra mass, for the question "how much weight low at the back would reach the aim"
#   Printed parts: volume x 1.05 g/cm3 at the body's centroid. Components: the masses of j5d (sheet values or the flagged estimates)
#   at the volume-weighted centroid of the bodies named. Forward pivot: the front feet; backward pivot: the rear feet.
import math
RHO = 1.05
LEADS = ['LEAD_PIGTAIL_20V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_RADAR', 'LEAD_TOUCH', 'LEAD_BME680', 'LEAD_VEML', 'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B',
         'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_PI_POWER', 'LEAD_USB_RESP']
COMP = [('speaker driver left', 68.0, ['SPK_L']), ('speaker driver right', 68.0, ['SPK_R']),
        ('main board with supply module', 58.0, ['MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'MAIN_tall', 'MAIN_low']),
        ('inlet board', 2.2, ['PD_5807_env']), ('touch board', 11.0, ['TOUCH_PCB']), ('BME680 board', 2.0, ['BME680_env']),
        ('VEML6030 board', 2.0, ['VEML_env']), ('microphone strips x 2', 2.0, ['MIC_strip_L_env', 'MIC_strip_R_env']),
        ('feet x 4', 4.0, ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']), ('Pi 5 with cooler', 75.0, ['PI5_F', 'PI5_F_cooler']),
        ('ReSpeaker', 12.0, ['RESP_pcb']), ('radar board', 2.0, ['LD2410C_env_F']),
        ('display module with glass', 254.0, ['LCD_panel_body', 'LCD_glass', 'LCD_pcb_76x110']), ('magnets x 20', 11.3, None),
        ('leads, screws, inserts', 40.0, LEADS), ('cloth and spline', 25.0, ['TOOL_outer_skin_0p7'])]
MAGS = [(72.59, -60.47, 24.92), (67.74, -60.2, 59.85), (58.87, -59.66, 94.7), (39.89, -58.68, 131.11), (16.04, -58.15, 148.35)]
GLASS_TOP = (-6.67, 174.67)          # y, z of the glass's top front edge
DOOR_FOOT_Y = -84.0


def cen(b): return k.W(b.physicalProperties.centerOfMass)


def mass(X):                          # total g, centre of gravity (world), printed g
    m = 0.0; s = [0.0, 0.0, 0.0]; mp = 0.0
    for n in k.PRINTED:
        b = X.body(n); g = b.volume * RHO; q = cen(b)
        mp += g; m += g
        for i in range(3):
            s[i] += q[i] * g
    for lab, g, names in COMP:
        if names is None:
            q = [0.0, sum(w[1] for w in MAGS) / len(MAGS), sum(w[2] for w in MAGS) / len(MAGS)]
        else:
            v = 0.0; t = [0.0, 0.0, 0.0]
            for n in names:
                b = X.body(n)
                if b is None:
                    raise RuntimeError('no body ' + n)
                w = cen(b)
                for i in range(3):
                    t[i] += w[i] * b.volume
                v += b.volume
            q = [t[i] / v for i in range(3)]
        m += g
        for i in range(3):
            s[i] += q[i] * g
    return m, [s[i] / m for i in range(3)], mp


def feet(X):                          # name -> [centre x, centre y, radius, z0, z1], from the cylinder face (lesson 132)
    out = {}
    for n in ('FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'):
        b = X.body(n); best = None
        for fc in b.faces:
            g = fc.geometry
            if g.surfaceType == k.CYL and (best is None or g.radius > best.radius):
                best = g
        q = k.W(best.origin); e = k.wbb(X, b)
        out[n] = [round(q[0], 2), round(q[1], 2), round(best.radius * 10.0, 2), e[4], e[5]]
    return out


def figures(m, cog, ft):
    Wn = m / 1000.0 * 9.81
    yr = [ft[n] for n in ('FOOT_RL', 'FOOT_RR')]; yf = [ft[n] for n in ('FOOT_FL', 'FOOT_FR')]
    y_rc = sum(f[1] for f in yr) / 2.0; y_re = min(f[1] - f[2] for f in yr)
    y_fc = sum(f[1] for f in yf) / 2.0; y_fe = max(f[1] + f[2] for f in yf)
    zp = min(f[3] for f in yr + yf)
    res = {'mass g': round(m, 1), 'cog': [round(v, 2) for v in cog], 'front feet centre y / front edge y': [round(y_fc, 2), round(y_fe, 2)],
           'rear feet centre y / rear edge y': [round(y_rc, 2), round(y_re, 2)], 'feet underside z': round(zp, 2),
           'rear feet share %': round(100.0 * (y_fc - cog[1]) / (y_fc - y_rc), 1)}
    for lab, yp in (('forward about the front feet centres', y_fc), ('forward about their front edges', y_fe)):
        M = Wn * (yp - cog[1]) / 1000.0
        res[lab] = {'tips at deg': round(math.degrees(math.atan2(yp - cog[1], cog[2] - zp)), 1), 'moment Nm': round(M, 4),
                    'pull at the top edge N': round(M / ((GLASS_TOP[1] - zp) / 1000.0), 2),
                    'push up at the door foot N': round(M / ((yp - DOOR_FOOT_Y) / 1000.0), 2)}
    for lab, yp in (('backward about the rear feet centres', y_rc), ('backward about their rear edges', y_re)):
        M = Wn * (cog[1] - yp) / 1000.0
        res[lab] = {'tips at deg': round(math.degrees(math.atan2(cog[1] - yp, cog[2] - zp)), 1), 'moment Nm': round(M, 4),
                    'push at the top edge N': round(M / ((GLASS_TOP[1] - zp) / 1000.0), 2)}
    return res


def ballast_for(m, cog, ft, aim, yb, zb):   # grams at (yb, zb) so that the unit tips forward about the front feet centres at 'aim' degrees
    yf = [ft[n] for n in ('FOOT_FL', 'FOOT_FR')]; y_fc = sum(f[1] for f in yf) / 2.0
    zp = min(f[3] for f in ft.values()); t = math.tan(math.radians(aim))
    # (y_fc - (m y + g yb)/(m + g)) = t ((m z + g zb)/(m + g) - zp)  ->  g
    num = m * (t * (cog[2] - zp) - (y_fc - cog[1]))
    den = (y_fc - yb) - t * (zb - zp)
    return num / den if den > 0 else None


def main(X, front=None, ballast=None, quiet=False):
    key = ('k2a_mass', X.doc.dataFile.versionNumber, X.doc.isModified, round(X.body('FLOOR_PLATE').volume, 6))
    if key not in k.c:
        k.c[key] = mass(X)
    m, cog, mp = k.c[key]
    ft = feet(X)
    if front:
        for n, (x, y) in front.items():
            ft[n] = [x, y] + ft[n][2:]
    if ballast:
        g, yb, zb = ballast
        cog = [cog[0] * m / (m + g), (cog[1] * m + yb * g) / (m + g), (cog[2] * m + zb * g) / (m + g)]; m = m + g
    res = figures(m, cog, ft); res['printed g'] = round(mp, 1); res['feet'] = ft
    if not quiet:
        for q, v in res.items():
            print(q, v)
    return res, m, cog, ft
