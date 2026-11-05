# rev F cap block c2a (2026-11-05), read-only: key lanes for cap screws driven from inside (Daniel 15:26: "the fasteners will
#   be visible from the outside. The lid should have the screw bosses with the threaded inserts and the screws should come
#   up from the shell into the lid").
#   Screw axis on the cap's lip ring: plan point 11.3 inside REF_F_outer's outline at z 170 (≈ 10.5 normal: a Ø8 cap boss
#   just inside the lip, which ends 7.3 in), head socket at z 166.5 (pad z 169.5–172.5, DIN912 head 3.0).
#   Candidates: plan rays from (x_rel 0, y −30) at z 170 to REF, θ = −90 (straight back) … 0 (side), plus rays along +x
#   at y −27 / −24 (front corners); +x half (the unit is symmetric to ±0.1).
#   Lanes: Ø5 cylinders (2.5 mm ball-end key, 2.9 across corners, + 1 mm) from the head down to targets on a plane behind
#   the unit (y −100, x_rel −40…40, z 30…130), i.e. out through the back opening with the door off. Obstacles: every
#   current solid part (B6m filter) with the pre-cap front shell HOUSING_F_front_c0 instead of the new one (no posts /
#   flange), door + grommet removed, keep-outs (KO_*) ignored (empty space), leads (LEAD_*) reported separately; all cropped
#   to x ±90, y −100…−12, z 40…172 (lanes pass the door plane above z 60) and unioned once. Per candidate: the clear lanes with the smallest angle from vertical.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'KO_', 'PROBE_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3', '_fail1',
               '_fail3', '_fail3b', '_c0', '_c1v1', '_v1', '_fail')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V', 'GROMMET_usbc_F')
THETA = (-90, -75, -60, -45, -30, -15, 0)
FRONT = (-27.0, -24.0)          # extra candidates: rays along +x from (0, y) – the front corners (old FL at y −27)
XT = (-40.0, -20.0, 0.0, 20.0, 40.0)
ZT = (30.0, 50.0, 70.0, 90.0, 110.0, 130.0)
Z_HEAD, INSET, R_LANE = 166.5, 11.3, 2.5


def solids(X):
    out = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        out.append(b)
    return out


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        region = X.wbox(-90.0 + XC, 90.0 + XC, -100.0, -12.0, 40.0, 172.0)
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
        cands = {}
        rays = [('th%d' % th, (XC, -30.0, 170.0), (math.cos(math.radians(th)), math.sin(math.radians(th)), 0.0)) for th in THETA]
        rays += [('y%d' % yy, (XC, yy, 170.0), (1.0, 0.0, 0.0)) for yy in FRONT]
        for (k, o, d) in rays:
            hs = [h for h in ray_hits(X, o, d, ('REF_F_outer',)) if h[0] > 1.0]
            if not hs:
                continue
            h = hs[0]; n = h[5]; nh = math.hypot(n[0], n[1]) or 1.0
            cx, cy = h[2] - n[0] / nh * INSET, h[3] - n[1] / nh * INSET
            cands[k] = {'ref': [round(h[2], 2), round(h[3], 2)], 'n_h': [round(n[0] / nh, 3), round(n[1] / nh, 3)],
                        'axis': [round(cx, 2), round(cy, 2)]}
        res = {}
        for k, c in cands.items():
            cx, cy = c['axis']; hd = (cx, cy, Z_HEAD - 0.3)
            lanes = []
            for xt in XT:
                for zt in ZT:
                    dx, dy, dz = xt - cx, -100.0 - cy, zt - hd[2]
                    ang = math.degrees(math.atan2(math.hypot(dx, dy), -dz))
                    if ang > 50.0:
                        continue
                    cyl = X.tbm.createCylinderOrCone(Dw(XC + cx, cy, hd[2]), R_LANE / 10, Dw(XC + xt, -100.0, zt), R_LANE / 10)
                    v = vol_x(X, cyl, U)
                    vl = vol_x(X, cyl, L) if L is not None else 0.0
                    lanes.append([round(ang, 1), xt, zt, v, vl])
            lanes.sort(key=lambda r: r[0])
            clear = [r for r in lanes if r[3] == 0.0]
            res[k] = {'axis': c['axis'], 'n': len(lanes), 'clear_best5': clear[:5],
                      'clear_no_leads_best3': [r for r in clear if r[4] == 0.0][:3],
                      'all_best5': lanes[:5]}
            log('v5f_c2a_key_lanes', 'progress', {k: res[k], 't_s': round(time.time() - t0, 1)})
        out['cands'] = cands; out['lanes'] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2a_key_lanes', 'lanes', out)
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'n_obst': len(out.get('obstacles', []))}))
