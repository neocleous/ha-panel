# rev F cap block c1b (2026-11-05): offset tools for the cap / clamp ledge (hidden, no part changed).
#   TOOL_cap_off<t> = REF_F_outer ∩ (z 160…177.2, y < −15) shelled inward by t with the z-160, z-177.2 and y-−15 faces removed:
#   the band within t of the outer surface on the sides, rear corners and back (below the R3 tangent, z 177.3 / 177.7, so the
#   offset never meets the R3 edges; the slot face is outside the crop).
#   t: 0.72 flange outer face (0.02 inside the recess surface, no coincident faces, lesson 48), 1.9 / 4.7 spline groove (1.2…4.0 from the cloth surface = REF − 0.7), 4.1 / 5.0 stepped 45° chamfer under the flange,
#   5.9 ledge inner edge (5.2 from the cloth surface), 6.1 / 7.3 cap lip (0.2 gap, 1.2 thick).
#   Check: front-shell material in the cap footprint just below the split (y < −23, z 173.5…175.3) outside the 5.9 band = what
#   hangs from the top wall below the split (heat-stake pins expected).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
TS = (0.72, 1.9, 4.1, 4.7, 5.0, 5.9, 6.1, 7.3)
Z0, Z1, YF = 160.0, 177.2, -15.0


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        made = {}
        for t in TS:
            name = 'TOOL_cap_off%s' % (('%.2f' % t).rstrip('0').rstrip('.')).replace('.', 'p')
            if X.body(name) is not None:
                made[name] = 'exists'; continue
            tb = tb_copy(X, 'REF_F_outer')
            inter(X, tb, X.wbox(-250, 250, -250, YF, Z0, Z1))
            b = X.add(tb, name)
            coll = adsk.core.ObjectCollection.create(); kinds = []
            for f in b.faces:
                if not f.geometry.objectType.endswith('Plane'):
                    continue
                p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
                nz = n.y * S + n.z * C; ny = n.y * C - n.z * S
                if abs(nz) > 0.99 and (abs(wz(p) - Z0) < 0.05 or abs(wz(p) - Z1) < 0.05):
                    coll.add(f); kinds.append('z%.1f' % wz(p))
                elif abs(ny) > 0.99 and abs(wy(p) - YF) < 0.05:
                    coll.add(f); kinds.append('y%.1f' % wy(p))
            si = X.feats.shellFeatures.createInput(coll, False)
            si.insideThickness = VI(t / 10)
            X.feats.shellFeatures.add(si)
            b = X.body(name); b.isLightBulbOn = False
            hs = ray_hits(X, (XC, -30.0, 170.0), (0, -1, 0), (name,))
            made[name] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 'faces': b.faces.count, 'open': kinds,
                          'x0_z170_y': [round(h[3], 2) for h in hs[:3]]}
        out['tools'] = made
        band = tb_copy(X, 'TOOL_cap_off5p9')
        hang = tb_copy(X, 'HOUSING_F_front'); inter(X, hang, X.wbox(-250, 250, -250, -23.0, 173.5, 175.3))
        X.diff(hang, band)
        rows = []
        for i in range(hang.lumps.count):
            lu = hang.lumps.item(i); bb = lu.boundingBox
            c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
            rows.append([round(lu.volume * 1000, 3), round(c.x * 10 - XC, 1), round(wy(c), 1), round(wz(c), 1)])
        out['hanging_below_split_[mm3, xr, y, z]'] = sorted(rows, key=lambda r: -r[0])[:20]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1b_cap_tools', 'tools', out)
    print(json.dumps(out, separators=(',', ':'))[:6000])
