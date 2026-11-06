# rev F audit-response d5a (2026-11-06), read-only: front-shell package probe (audit findings 1, 3, 4, 6, 10, 14, 37, 40).
#   Writes ~/Documents/HA_panel_renders/d_data/data/d5a_probe.json (+ section loops for plotting).
#   1. void shells of the front (design boxes); 2. the 10 magnet pockets (Ø8.3): axis, floor end, skin along the axis;
#   3. Pi bosses: cylinders and the Pi's clearance below the PCB round each hole; 4. bodies named BME / LD2410 / VEML;
#   5. sections: shelf + exhaust rows, BME680 corner, LD2410C corner, lip end.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d5a_probe.json')
GUARD = {'HOUSING_F_front': 236.2249}
PI_HOLES = ((18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5))
F = 'HOUSING_F_front'
PLANES5 = {
    'S_x0_top': ('x', 0.0, (-42.0, -14.0, 150.0, 182.0), [F, 'HOUSING_F_cap']),
    'S_x40_top': ('x', 40.0, (-42.0, -14.0, 150.0, 182.0), [F, 'HOUSING_F_cap']),
    'S_z164': ('z', 164.0, (-52.0, 52.0, -42.0, -14.0), [F]),
    'S_z168.5': ('z', 168.5, (-52.0, 52.0, -42.0, -14.0), [F]),
    'B_z91': ('z', 91.0, (-95.0, -50.0, -62.0, -22.0), [F, 'HOUSING_F_door', 'BME680_env', 'MAIN_front_env', 'MAIN_pcb', 'MAIN_BRACKET']),
    'B_x-73': ('x', -73.0, (-62.0, -22.0, 70.0, 110.0), [F, 'HOUSING_F_door', 'BME680_env']),
    'L_z127.5': ('z', 127.5, (-95.0, -50.0, -45.0, -5.0), [F, 'LD2410C_env_F', 'SLAB_frame', 'LCD_panel_body']),
    'P_y-63.4': ('y', -63.4, (-85.0, 85.0, 0.0, 170.0), [F, 'HOUSING_F_door']),
    'P_x30': ('x', 30.0, (-70.0, -48.0, 90.0, 150.0), [F, 'HOUSING_F_door']),
}


def cyl_rows(b, rad, tol=0.02):
    rows = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType() or abs(g.radius * 10 - rad) > tol:
            continue
        ax = g.axis; ax.normalize(); o = g.origin
        ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices] or [0.0]
        rows.append((f, ax, o, min(ts), max(ts)))
    return rows


def pt(o, ax, t):
    return P3(o.x + ax.x * t / 10, o.y + ax.y * t / 10, o.z + ax.z * t / 10)


def wpt(p):
    return [round(p.x * 10 - XC, 3), round(wy(p), 3), round(wz(p), 3)]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        fb = X.body(F)
        if abs(fb.volume - GUARD[F]) > 0.0005:
            raise RuntimeError('guard: front %s' % round(fb.volume, 4))
        # 1. shells
        sh = []
        for li in range(fb.lumps.count):
            L = fb.lumps.item(li)
            for si in range(L.shells.count):
                s = L.shells.item(si)
                if s.isVoid:
                    bb = s.boundingBox
                    sh.append({'lump': li, 'design_min_cm': [round(bb.minPoint.x, 4), round(bb.minPoint.y, 4), round(bb.minPoint.z, 4)],
                               'design_max_cm': [round(bb.maxPoint.x, 4), round(bb.maxPoint.y, 4), round(bb.maxPoint.z, 4)],
                               'centre_world': wpt(P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2,
                                                      (bb.minPoint.z + bb.maxPoint.z) / 2)), 'faces': s.faces.count})
        out['front_lumps'] = fb.lumps.count; out['void_shells'] = sh
        # 2. magnet pockets
        mp = []
        for f, ax, o, t_lo, t_hi in cyl_rows(fb, 4.15):
            ends = {}
            for k, t in (('lo', t_lo), ('hi', t_hi)):
                d = -0.05 if k == 'lo' else 0.05
                ends[k] = fb.pointContainment(pt(o, ax, t + d)) in INS
            # floor end = the end with solid beyond it; skin = solid run beyond the floor along the axis
            fe = 'lo' if ends['lo'] and not ends['hi'] else ('hi' if ends['hi'] and not ends['lo'] else '?')
            skin = None
            if fe != '?':
                t_f = t_lo if fe == 'lo' else t_hi; sg = -1.0 if fe == 'lo' else 1.0
                k = 0.0
                while k < 3.0 and fb.pointContainment(pt(o, ax, t_f + sg * (k + 0.01))) in INS:
                    k += 0.01
                skin = round(k, 2)
            c = pt(o, ax, (t_lo + t_hi) / 2)
            axw = nw_of(ax)
            mp.append({'centre': wpt(c), 'axis_w': [round(v, 4) for v in axw], 'len': round(t_hi - t_lo, 3), 'floor_end': fe,
                       'floor_pt': wpt(pt(o, ax, t_lo if fe == 'lo' else t_hi)) if fe != '?' else None,
                       'open_pt': wpt(pt(o, ax, t_hi if fe == 'lo' else t_lo)) if fe != '?' else None, 'skin_axis': skin})
        out['magnet_pockets'] = mp
        out['t2'] = round(time.time() - t0, 1)
        # 3. Pi bosses
        pb = {}
        for (x, y) in PI_HOLES:
            rows = []
            for rad in (3.8, 3.0, 2.0):
                for f, ax, o, t_lo, t_hi in cyl_rows(fb, rad):
                    c = wpt(pt(o, ax, (t_lo + t_hi) / 2))
                    if abs(c[0] - x) < 0.3 and abs(c[1] - y) < 0.3:
                        zs = [wz(v.geometry) for v in f.vertices]
                        rows.append([2 * rad, [round(min(zs), 3), round(max(zs), 3)]])
            clr = {}
            for r in (3.4, 3.8):
                clr['r%g_z7-8' % r] = vol_x(X, X.wcyl_z(XC + x, y, r, 7.0, 8.0), tb_copy(X, 'PI5_F'))
                clr['r%g_z7.9-8.1' % r] = vol_x(X, X.wcyl_z(XC + x, y, r, 7.9, 8.1), tb_copy(X, 'PI5_F'))
            pb['%g,%g' % (x, y)] = {'cyl': rows, 'pi_x': clr}
        out['pi_bosses'] = pb
        out['pi_box'] = [round(v, 3) for v in wbb(X, X.body('PI5_F'))]
        # 4. named bodies
        nb = {}
        for b in X.comp.bRepBodies:
            if any(k in b.name for k in ('BME', 'LD2410', 'VEML', 'LEAD_BME', 'LEAD_LD', 'LEAD_VEML')):
                nb[b.name] = {'vis': b.isLightBulbOn, 'box': [round(v, 2) for v in wbb(X, b)], 'cm3': round(b.volume, 4)}
        out['named'] = nb
        out['t4'] = round(time.time() - t0, 1)
        out['sec'] = sections(X, PLANES5)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: v for k, v in out.items() if k not in ('sec', 'magnet_pockets', 'named', 'pi_bosses', 'void_shells')}
    log('v5f_d5a_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
