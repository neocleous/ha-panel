# rev F audit-response d5d (2026-11-06), read-only: inputs for the vents, shelf land, BME680 pocket and LD2410C retention.
#   Writes ~/Documents/HA_panel_renders/d_data/data/d5d_probe.json.
#   1. underside section z 0.3 (recesses near the intake field); 2. shelf tip strip: x extent, lumps;
#   3. lip lower edge behind the door: for x in −50…50 the lowest z where the front has material 1.0–3.0 inside the door's
#      inner face (rays along the door normal are overkill: a vertical scan of the front at the door's inner surface offset);
#   4. BME680_env and LD2410C_env_F frames (planar faces: normal, centre, area) and what surrounds them.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d5d_probe.json')
F, D = 'HOUSING_F_front', 'HOUSING_F_door'
PL = {
    'U_z0.3': ('z', 0.3, (-95.0, 95.0, -90.0, 12.0), [F]),
    'BME_z87.5': ('z', 87.5, (-95.0, -50.0, -62.0, -22.0), [F, D, 'BME680_env', 'LEAD_BME680']),
    'BME_z95': ('z', 95.0, (-95.0, -50.0, -62.0, -22.0), [F, D, 'BME680_env', 'LEAD_BME680']),
    'LD_z120': ('z', 120.0, (-95.0, -50.0, -45.0, -5.0), [F, 'LD2410C_env_F', 'SLAB_frame']),
    'LD_z135': ('z', 135.0, (-95.0, -50.0, -45.0, -5.0), [F, 'LD2410C_env_F', 'SLAB_frame']),
}
for _x in range(-50, 51, 5):
    PL['LIP_x%d' % _x] = ('x', float(_x), (-72.0, -48.0, 60.0, 165.0), [F, D])


def faces_of(b):
    rows = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Plane.classType():
            continue
        ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
        bb = f.boundingBox
        c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
        rows.append({'n': [round(v, 4) for v in nw_of(n)], 'c': [round(c.x * 10 - XC, 3), round(wy(c), 3), round(wz(c), 3)],
                     'area': round(f.area * 100, 2)})
    return rows


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        fb = X.body(F); db = X.body(D)
        # 2. shelf tip strip
        st = tb_copy(X, F); inter(X, st, X.wbox(XC - 80, XC + 80, -23.31, -23.05, 177.2, 177.39))
        out['shelf_tip'] = {'mm3': round(st.volume * 1000, 3), 'box': [round(v, 3) for v in wbb(X, st)] if st.volume > 0 else None,
                            'lumps': st.lumps.count}
        lumps = []
        for i in range(st.lumps.count):
            bb = st.lumps.item(i).boundingBox
            lumps.append([round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2)])
        out['shelf_tip']['lump_x'] = sorted(lumps)
        out['t3'] = round(time.time() - t0, 1)
        # 4. envelopes
        for n in ('BME680_env', 'LD2410C_env_F'):
            b = X.body(n)
            out[n] = {'box': [round(v, 3) for v in wbb(X, b)], 'faces': faces_of(b), 'cm3': round(b.volume, 4)}
        # what is round the BME680 env (2 mm grown box) and the LD env
        for n, m in (('BME680_env', 6.0), ('LD2410C_env_F', 3.0)):
            bb = wbb(X, X.body(n)); reg = wbox_rel(X, bb, m)
            res = {}
            for b in X.comp.bRepBodies:
                if b.name in (n,) or b.name.startswith(('REF_', 'INNER_', 'TOOL_', 'RENDER_', 'HOUSING_E', 'sk_')) or b.name.endswith(('_tmp',)):
                    continue
                if not (b.isLightBulbOn or b.name.startswith(('LEAD_', 'KO_', 'MAIN_', 'LCD_', 'MIC_', 'VEML', 'BME', 'LD2410'))):
                    continue
                try:
                    v = vol_x(X, X.tbm.copy(reg), X.tbm.copy(b))
                except Exception:
                    continue
                if v > 0:
                    res[b.name] = v
            out[n + '_neighbours'] = res
        out['t4'] = round(time.time() - t0, 1)
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: v for k, v in out.items() if k not in ('sec', 'BME680_env', 'LD2410C_env_F')}
    log('v5f_d5d_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
