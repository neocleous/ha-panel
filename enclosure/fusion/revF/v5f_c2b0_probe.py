# rev F cap block c2b0 (2026-11-05), read-only: inputs for the hidden-screw cap (Daniel 15:26 + answers: back screws from
#   below, front "hooks into the bar", VEML6030 to the centre).
#   1 inventory: VEML / LUX / MIC / LEAD / KO / PIN bodies above z 150 (world bbox, cm3, visible).
#   2 boss centres: Ø8 boss (r 4.0) kept at d >= 6.1 (lip outer face) for z 172.5…175.8 (pad top … cap ring bottom), found
#     by bisection along the plan normal from REF_F_outer at z 175.8; back pair at x_rel ±28 (ray −y), front-side pair on
#     the rays θ −15 / −165 from (0, −30) (c2a's th-15 candidate and its mirror).
#   3 key lanes from each centre (head bottom z 166.5, lane start 166.2, Ø5) to targets behind the unit (y −100,
#     x_rel −40…40, z 10…130): obstacles as c2a (B6m filter + HOUSING_F_front_c0) WITHOUT VEML_env (moves to the centre);
#     leads (LEAD_*) except LEAD_VEML (re-routed) reported separately.
#   4 bar back face near the joint: first HOUSING_F_front hit along +y from y −30 at x_rel 0, ±30, ±45, ±50, z 175.5…177.8.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'KO_', 'PROBE_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3', '_fail1',
               '_fail3', '_fail3b', '_c0', '_c1v1', '_v1', '_fail')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V', 'GROMMET_usbc_F')
MOVING = ('VEML_env', 'LEAD_VEML')
XT = (-40.0, -20.0, 0.0, 20.0, 40.0)
ZT = (10.0, 30.0, 50.0, 70.0, 90.0, 110.0, 130.0)
Z_HEAD, R_LANE, R_BOSS = 166.5, 2.5, 4.0


def solids(X):
    out = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n in MOVING \
                or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        out.append(b)
    return out


def boss_centre(X, o, d, t61):
    hs = [h for h in ray_hits(X, (XC + o[0], o[1], 175.8), (d[0], d[1], 0.0), ('REF_F_outer',)) if h[0] > 1.0]
    h = hs[0]; n = h[5]; nh = math.hypot(n[0], n[1]); ux, uy = n[0] / nh, n[1] / nh
    lo, hi = 6.0, 16.0
    for _ in range(9):
        m = (lo + hi) / 2
        cx, cy = h[2] - ux * m, h[3] - uy * m
        cyl = X.wcyl_z(XC + cx, cy, R_BOSS, 172.5, 175.8)
        if vol_x(X, cyl, t61) > 0.0:
            lo = m
        else:
            hi = m
    cx, cy = h[2] - ux * hi, h[3] - uy * hi
    return {'ref': [round(h[2], 2), round(h[3], 2)], 'n_h': [round(ux, 3), round(uy, 3)], 'inset': round(hi, 2),
            'axis': [round(cx, 2), round(cy, 2)]}


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        inv = {}
        for b in X.comp.bRepBodies:
            n = b.name
            if any(k in n.upper() for k in ('VEML', 'LUX', 'MIC', 'LEAD_', 'KO_', 'PIN')) and not n.endswith(SKIP_SUFFIX):
                bb = wbb(X, b)
                if bb[5] < 150.0:
                    continue
                inv[n] = {'bb': [round(v, 2) for v in bb], 'cm3': round(b.volume, 4), 'vis': b.isLightBulbOn}
        out['inventory'] = inv
        t61 = tb_copy(X, 'TOOL_cap_off6p1'); inter(X, t61, X.wbox(-250, 250, -250, 250, 172.4, 175.9))
        bosses = {'BL': boss_centre(X, (28.0, -30.0), (0.0, -1.0), t61), 'BR': boss_centre(X, (-28.0, -30.0), (0.0, -1.0), t61)}
        for k, th in (('SL', -15.0), ('SR', -165.0)):
            bosses[k] = boss_centre(X, (0.0, -30.0), (math.cos(math.radians(th)), math.sin(math.radians(th))), t61)
        out['bosses'] = bosses
        cap = X.body('HOUSING_F_cap')

        def runs(pts):                       # [(s, point)] -> s-ranges where the cap is NOT solid (pockets / holes)
            r = []; cur = None
            for s, p in pts:
                hole = cap.pointContainment(Dw(*p)) not in INS
                if hole and cur is None:
                    cur = [s, s]
                elif hole:
                    cur[1] = s
                elif cur is not None:
                    r.append([round(cur[0], 2), round(cur[1], 2)]); cur = None
            if cur is not None:
                r.append([round(cur[0], 2), round(cur[1], 2)])
            return r
        xs = [i * 0.1 for i in range(-620, 621)]
        ys = [-22.7 - i * 0.1 for i in range(0, 231)]
        pk = {}
        for (lab, y, z) in (('y-26.5_z177.9', -26.5, 177.9), ('y-31_z177.9', -31.0, 177.9), ('y-26.5_z179.5', -26.5, 179.5),
                            ('y-31_z179.5', -31.0, 179.5)):
            pk['x_' + lab] = runs([(x, (XC + x, y, z)) for x in xs])
        for (lab, x, z) in (('x22.5_z177.9', 22.5, 177.9), ('x-22.5_z177.9', -22.5, 177.9), ('x46_z177.9', 46.0, 177.9),
                            ('x46_z179.5', 46.0, 179.5), ('x35.5_z179.5', 35.5, 179.5), ('x0_z177.9', 0.0, 177.9)):
            pk['y_' + lab] = runs([(y, (XC + x, y, z)) for y in ys])
        pins = {}
        for xr in (11.5, 30.0, -11.5, -30.0):
            col = []
            for z10 in range(1740, 1781, 2):
                z = z10 / 10.0
                col.append(1 if cap.pointContainment(Dw(XC + xr, -26.5, z)) in INS else 0)
            pins['x%g' % xr] = {'z174.0..178.0_step0.2': ''.join(str(c) for c in col)}
        pk['pins_at_y-26.5'] = pins
        out['cap_pockets'] = pk
        log('v5f_c2b0_probe', 'bosses', {'inventory': inv, 'bosses': bosses, 'cap_pockets': pk, 't_s': round(time.time() - t0, 1)})
        bar = {}
        for xr in (0.0, 30.0, -30.0, 45.0, -45.0, 50.0, -50.0):
            row = []
            for z in (175.5, 176.0, 176.5, 177.0, 177.4, 177.8):
                hs = ray_hits(X, (XC + xr, -30.0, z), (0, 1, 0), ('HOUSING_F_front',))
                row.append([z, round(hs[0][3], 2) if hs else None])
            bar['x%g' % xr] = row
        out['bar_back_face'] = bar
        region = X.wbox(-90.0 + XC, 90.0 + XC, -100.0, -12.0, 0.0, 172.0)
        U = tb_copy(X, 'HOUSING_F_front_c0'); inter(X, U, X.tbm.copy(region))
        L = None; used = []; leads = []
        rb = wbb(X, region)
        for b in solids(X):
            bb = wbb(X, b)
            if bb[1] < rb[0] or bb[0] > rb[1] or bb[3] < rb[2] or bb[2] > rb[3] or bb[5] < rb[4] or bb[4] > rb[5]:
                continue
            t = X.tbm.copy(b); inter(X, t, X.tbm.copy(region))
            if t.volume <= 0:
                continue
            if b.name.startswith('LEAD_'):
                L = t if L is None else X.union(L, t); leads.append(b.name)
            else:
                X.union(U, t); used.append(b.name)
        out['obstacles'] = used; out['leads'] = leads
        out['t_union_s'] = round(time.time() - t0, 1)
        res = {}
        for k, c in bosses.items():
            cx, cy = c['axis']; hz = Z_HEAD - 0.3
            lanes = []
            for xt in XT:
                for zt in ZT:
                    ang = math.degrees(math.atan2(math.hypot(xt - cx, -100.0 - cy), hz - zt))
                    if ang > 40.0:
                        continue
                    cyl = X.tbm.createCylinderOrCone(Dw(XC + cx, cy, hz), R_LANE / 10, Dw(XC + xt, -100.0, zt), R_LANE / 10)
                    v = vol_x(X, cyl, U)
                    vl = vol_x(X, cyl, L) if L is not None else 0.0
                    lanes.append([round(ang, 1), xt, zt, v, vl])
            lanes.sort(key=lambda r: r[0])
            clear = [r for r in lanes if r[3] == 0.0]
            res[k] = {'axis': c['axis'], 'n': len(lanes), 'clear_best5': clear[:5],
                      'clear_no_leads_best5': [r for r in clear if r[4] == 0.0][:5], 'all_best5': lanes[:5]}
            log('v5f_c2b0_probe', 'progress', {k: res[k], 't_s': round(time.time() - t0, 1)})
        out['lanes'] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2b0_probe', 'probe', out)
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'bosses': out.get('bosses')}))
