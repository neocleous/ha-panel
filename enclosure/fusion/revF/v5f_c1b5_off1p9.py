# rev F cap block c1b5 (2026-11-05): the groove's outer-wall tool. c1b2 made 0.72 and 4.1 … 7.3 but the shell failed at
#   1.9 and 1.95 (SHELL_GENERIC_FAILURE, failed copies hidden as TOOL_cap_off1p9_fail*). Try other front crops (design Y)
#   and thicknesses near 1.9 on one body per crop: the first success becomes TOOL_cap_off1p9 (actual t / crop logged);
#   a crop where every t fails is renamed TOOL_cap_off1p9_fail_Y<crop> and hidden.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
Z0, Z1 = 160.0, 177.2
TRY = [(-14.6, (1.9, 1.85, 2.0)), (-13.4, (1.9, 1.85, 2.0)), (-13.9, (1.85, 2.0, 1.8, 2.1))]


def run(_context):
    X = Ctx(); out = {'tries': []}
    t0 = time.time()
    try:
        done = None
        for (yd, ts) in TRY:
            if done:
                break
            tb = tb_copy(X, 'REF_F_outer')
            inter(X, tb, X.wbox(-250, 250, -250, 250, Z0, Z1))
            inter(X, tb, dbox(X, -250, 250, -250, yd, -250, 250))
            name = 'TOOL_cap_off1p9_tryY%s' % ('%.1f' % -yd).replace('.', 'p')
            b = X.add(tb, name); b.isLightBulbOn = False
            for t in ts:
                b = X.body(name)
                coll = adsk.core.ObjectCollection.create()
                for f in b.faces:
                    if not f.geometry.objectType.endswith('Plane'):
                        continue
                    p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
                    nz = n.y * S + n.z * C
                    if abs(nz) > 0.99 and (abs(wz(p) - Z0) < 0.05 or abs(wz(p) - Z1) < 0.05):
                        coll.add(f)
                    elif abs(n.y) > 0.99 and abs(p.y * 10 - yd) < 0.05:
                        coll.add(f)
                si = X.feats.shellFeatures.createInput(coll, False)
                si.insideThickness = VI(t / 10)
                try:
                    X.feats.shellFeatures.add(si)
                except Exception as e:
                    out['tries'].append([yd, t, 'fail', str(e)[:40]]); continue
                b = X.body(name); b.name = 'TOOL_cap_off1p9'; b.isLightBulbOn = False
                hb = ray_hits(X, (XC, -30.0, 170.0), (0, -1, 0), ('TOOL_cap_off1p9',))
                hs = ray_hits(X, (XC, -25.0, 175.0), (1, 0, 0), ('TOOL_cap_off1p9',))
                hc = ray_hits(X, (XC + 60.0, -23.0, 175.0), (1, 0, 0), ('TOOL_cap_off1p9',))
                out['tries'].append([yd, t, 'ok'])
                done = {'t': t, 'YD': yd, 'cm3': round(b.volume, 3), 'faces': b.faces.count, 'lumps': b.lumps.count,
                        'x0_z170_back_y': [round(h[3], 2) for h in hb[:3]],
                        'y-25_z175_side_x': [round(h[2], 2) for h in hs[:3]],
                        'y-23_z175_side_x': [round(h[2], 2) for h in hc[:3]]}
                break
            if not done:
                X.body(name).name = 'TOOL_cap_off1p9_fail_Y%s' % ('%.1f' % -yd).replace('.', 'p')
        out['result'] = done
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1b5_off1p9', 'tool', out)
    print(json.dumps(out, separators=(',', ':'))[:4000])
