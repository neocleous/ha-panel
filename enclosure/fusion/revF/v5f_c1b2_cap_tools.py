# rev F cap block c1b2 (2026-11-05): c1b's offset tools rebuilt without the front band.
#   c1b found no face at y −15: between z 160 and 177.2 REF_F_outer's front face (the slot-face plane, design Y −12.4,
#   world y −16.1 at z 160 … −19.8 at z 177.2) lies behind y −15, so c1b shelled that face too and every TOOL_cap_off* has a
#   band behind the slot face as well (it would have put a flange / groove along the front bar). c1b's tools are renamed
#   TOOL_cap_off*_v1 and stay hidden.
#   First attempt (front plane passed as a removed face): SHELL_GENERIC_FAILURE – the front plane is tangent to the two
#   front-corner blend faces (c1b3 / c1b4: NURBS, y −18.7…−24.6, x ±73…±84 at z 160–177.2); the un-shelled body was renamed
#   TOOL_cap_off0p72_fail (c1b3).
#   Now: REF_F_outer ∩ z 160…177.2 ∩ design Y ≤ −13.9 (1.5 behind the front plane, cuts the blends ≈ 45° to their surface,
#   world y −17.8 at z 160 … −21.2 at z 177.2, in front of the cap joint y −22.5) shelled with the two z faces and the Y crop
#   face removed: bands along the sides, front-corner blends, rear corners and back only. Same names / t list as c1b.
#   Run 1 of this version made all but 1.9: the first attempt had shelled 0.72 (front plane removed) and failed at 1.9,
#   leaving TOOL_cap_off1p9 un-shelled and visible; c1b3 had renamed that attempt's 0.72 band to TOOL_cap_off0p72_fail.
#   Run 2 renamed the leftover TOOL_cap_off1p9_fail (hidden); its 1.9 shell failed as well (body hidden, 'TOOL_cap_off1p9_fail (1)').
#   Run 3: t 1.95 instead (groove outer wall 1.25 from the cloth surface).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
TS = (0.72, 1.95, 4.1, 4.7, 5.0, 5.9, 6.1, 7.3)   # 1.9 fails in run 2 (SHELL_GENERIC_FAILURE), 1.95 in run 3
Z0, Z1, YD = 160.0, 177.2, -13.9


def tname(t):
    return 'TOOL_cap_off%s' % (('%.2f' % t).rstrip('0').rstrip('.')).replace('.', 'p')


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        ren = []
        for t in TS:
            b = X.body(tname(t))
            if b is not None and X.body(tname(t) + '_v1') is None:
                b.name = tname(t) + '_v1'; b.isLightBulbOn = False; ren.append(b.name)
        out['renamed'] = ren
        lo = X.body('TOOL_cap_off1p9')   # leftover of the first attempt: un-shelled crop (74.5 cm3, 6 faces, left visible)
        if lo is not None and lo.faces.count == 6 and lo.volume > 50:
            lo.name = 'TOOL_cap_off1p9_fail'; lo.isLightBulbOn = False; out['leftover'] = [lo.name, round(lo.volume, 3)]
        made = {}
        for t in TS:
            name = tname(t)
            if X.body(name) is not None:
                made[name] = 'exists'; continue
            tb = tb_copy(X, 'REF_F_outer')
            inter(X, tb, X.wbox(-250, 250, -250, 250, Z0, Z1))
            inter(X, tb, dbox(X, -250, 250, -250, YD, -250, 250))
            b = X.add(tb, name)
            coll = adsk.core.ObjectCollection.create(); kinds = []
            for f in b.faces:
                if not f.geometry.objectType.endswith('Plane'):
                    continue
                p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
                nz = n.y * S + n.z * C
                if abs(nz) > 0.99 and (abs(wz(p) - Z0) < 0.05 or abs(wz(p) - Z1) < 0.05):
                    coll.add(f); kinds.append('z%.1f' % wz(p))
                elif abs(n.y) > 0.99 and abs(p.y * 10 - YD) < 0.05:
                    coll.add(f); kinds.append('Y%.1f (y%.2f z%.1f)' % (p.y * 10, wy(p), wz(p)))
            si = X.feats.shellFeatures.createInput(coll, False)
            si.insideThickness = VI(t / 10)
            try:
                X.feats.shellFeatures.add(si)
            except Exception:
                b.name = name + '_fail'; b.isLightBulbOn = False
                raise
            b = X.body(name); b.isLightBulbOn = False
            hb = ray_hits(X, (XC, -30.0, 170.0), (0, -1, 0), (name,))
            hs = ray_hits(X, (XC, -25.0, 175.0), (1, 0, 0), (name,))
            hc = ray_hits(X, (XC + 60.0, -23.0, 175.0), (1, 0, 0), (name,))
            hf = ray_hits(X, (XC, -30.0, 175.0), (0, 1, 0), (name,))
            made[name] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 'faces': b.faces.count, 'open': kinds,
                          'x0_z170_back_y': [round(h[3], 2) for h in hb[:3]],
                          'y-25_z175_side_x': [round(h[2], 2) for h in hs[:3]],
                          'y-23_z175_side_x': [round(h[2], 2) for h in hc[:3]],
                          'x0_z175_front_y(none)': [round(h[3], 2) for h in hf[:3]]}
        out['tools'] = made
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1b2_cap_tools', 'tools', out)
    print(json.dumps(out, separators=(',', ':'))[:6000])
