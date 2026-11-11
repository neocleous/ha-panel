# rev F i4g (2026-11-11): step 3 repeated, block 4 - read-only: the checks on the leads that h3c and h3f do not make.
#   A  lead against lead: the smallest distance of every pair of the 16 leads whose boxes come within 6, with the point on the first
#      lead (board frame u, v, w); where it is 0, the shared volume in mm3
#   B  named pairs with both points: the VEML6030 lead over the supply module at the top of its tolerance, the BME680 lead and the
#      cap screws' key paths, the display's power lead and the microphone leads against the carrier with its fourth post
#   C  the height at which a lead crosses a column over another connector's plug or over the supply module (w range of the lead inside
#      the column u0..u1, v0..v1)
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
PAIRS = [('LEAD_VEML', 'MAIN_PS1_tol'), ('LEAD_VEML', 'MAIN_PS1'), ('LEAD_VEML', 'KO_capkey_BL'), ('LEAD_VEML', 'KO_capkey_BR'), ('LEAD_VEML', 'RESP_CARRIER'),
         ('LEAD_VEML', 'HOUSING_F_door'), ('LEAD_BME680', 'MAIN_PS1_tol'), ('LEAD_BME680', 'KO_capkey_SR'), ('LEAD_BME680', 'KO_capkey_BR'), ('LEAD_BME680', 'MAIN_low'),
         ('LEAD_BME680', 'MAIN_tall'), ('LEAD_BME680', 'MAIN_conn'), ('LEAD_BME680', 'HOUSING_F_door'), ('LEAD_BME680', 'KO_K5_LR'), ('LEAD_LCD_5V', 'RESP_CARRIER'),
         ('LEAD_MIC_L', 'RESP_CARRIER'), ('LEAD_MIC_R', 'RESP_CARRIER'), ('LEAD_LCD_5V', 'KO_K5_LR'), ('LEAD_LCD_5V', 'RESP_top_env'), ('LEAD_LCD_5V', 'MAIN_pcb')]
COLS = [('LEAD_BME680', 'radar plug J5', (-43.20, -36.36, -20.60, -7.11)), ('LEAD_BME680', 'right speaker plug J9', (-43.24, -34.76, -28.95, -22.11)),
        ('LEAD_BME680', 'radar fuse F3', (-35.64, -32.84, -14.30, -8.10)), ('LEAD_VEML', 'supply module', (-37.11, 13.79, -4.35, 7.75)),
        ('LEAD_VEML', 'C5', (-8.3, 2.3, 8.6, 19.2)), ('LEAD_RADAR', 'BME680 plug J10', (-32.22, -28.59, -19.74, -8.49))]


def near(a, b, r):
    p, q = a.boundingBox, b.boundingBox
    r = r / 10.0
    return not (p.minPoint.x - r > q.maxPoint.x or q.minPoint.x - r > p.maxPoint.x or p.minPoint.y - r > q.maxPoint.y or q.minPoint.y - r > p.maxPoint.y
                or p.minPoint.z - r > q.maxPoint.z or q.minPoint.z - r > p.maxPoint.z)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        mm = X.app.measureManager
        leads = [b for b in current(X, leads=True) if b.name.startswith('LEAD_')]
        st['n'] = len(leads)
        A = {}
        for i, a in enumerate(leads):
            for b in leads[i + 1:]:
                if not near(a, b, 6.0):
                    continue
                m = mm.measureMinimumDistance(a, b)
                d = m.value * 10.0
                if d > 6.0:
                    continue
                e = [round(d, 2), [round(v, 1) for v in Bf(m.positionOne)]]
                if d < 0.005:
                    e = [0.0, round(xvol(X, X.cp(a), X.cp(b)), 1)]
                A[a.name[5:] + '~' + b.name[5:]] = e
        st['A'] = dict(sorted(A.items(), key=lambda kv: kv[1][0]))
        B = {}
        for a, b in PAIRS:
            m = mm.measureMinimumDistance(X.body(a), X.body(b))
            B[a[5:] + '~' + b] = [round(m.value * 10.0, 2), [round(v, 1) for v in Bf(m.positionOne)], [round(v, 1) for v in Bf(m.positionTwo)]]
        st['B'] = B
        Cc = {}
        for ln, what, (u0, u1, v0, v1) in COLS:
            t = X.cp(X.body(ln)); X.sec(t, bbox_b(X, u0, u1, v0, v1, -20.0, 80.0))
            q = bbb(t) if X.vol(t) > 0.001 else None
            Cc[ln[5:] + ' over ' + what] = None if q is None else [q[4], q[5]]
        st['C'] = Cc
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('i4g', st)


run(None)
