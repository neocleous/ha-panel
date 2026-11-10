# rev F f2c0 (2026-11-10): read-only probe before the speaker boxes are reworked.
#   A  face summary of SPKBOX_L (planes by world axis, cylinders by axis)   B  is SPKBOX_R the mirror of SPKBOX_L apart from the hump?
#   C  rays through the shell at the driver corners, the tab bosses and the key path   D  box pads against the plate's features
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())


def wv(v):                              # design vector -> world
    return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)


def faces(body):
    pl = {}; cy = []; other = [0, 0.0]
    for f in body.faces:
        g = f.geometry; a = f.area * 100.0
        if g.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType:
            ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
            n = wv(n); p = W(f.pointOnFace)
            for i, ax in enumerate('xyz'):
                if abs(n[i]) > 0.9995:
                    k = '%s%s%.2f' % (ax, '+' if n[i] > 0 else '-', p[i])
                    pl[k] = round(pl.get(k, 0.0) + a, 1)
                    break
            else:
                other[0] += 1; other[1] += a
        elif g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
            ax = wv(g.axis); o = W(g.origin)
            vs = [W(v.geometry) for v in f.vertices]
            for i, nm in enumerate('xyz'):
                if abs(ax[i]) > 0.9995 and vs:
                    j = [q for q in range(3) if q != i]
                    cy.append([nm, round(o[j[0]], 2), round(o[j[1]], 2), round(g.radius * 10, 2), round(min(v[i] for v in vs), 2),
                               round(max(v[i] for v in vs), 2)])
                    break
            else:
                other[0] += 1; other[1] += a
        else:
            other[0] += 1; other[1] += a
    cy = sorted(set(tuple(c) for c in cy))
    return {'planes': {k: v for k, v in sorted(pl.items()) if v >= 1.0}, 'cyl': cy, 'other': [other[0], round(other[1], 1)]}


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S')}
    t0 = time.time()
    try:
        X = K()
        L = X.body('SPKBOX_L'); R = X.body('SPKBOX_R')
        st['vol'] = [round(L.volume * 1000, 1), round(R.volume * 1000, 1), L.faces.count, R.faces.count, L.lumps.count, R.lumps.count]
        st['L'] = faces(L)
        status('f2c0', st)
        # B mirror about x_rel = 0
        m = adsk.core.Matrix3D.create()
        m.setCell(0, 0, -1.0); m.setCell(0, 3, 2.0 * XC / 10.0)
        ml = X.cp(L); ok = X.tbm.transform(ml, m)
        st['mirror'] = {'ok': ok, 'vol': round(X.vol(ml), 1)}
        a = X.cp(ml); X.dif(a, X.cp(R)); b = X.cp(R); X.dif(b, X.cp(ml))
        st['mirror']['mirL-R'] = X.lumps(a)[:8]; st['mirror']['R-mirL'] = X.lumps(b)[:8]
        status('f2c0', st)
        # C rays
        skip = ('REF_', 'TOOL_', 'INNER', 'KO_', 'AUD_')

        def ray(x, y, z, d, lim=60.0):
            hp = adsk.core.ObjectCollection.create()
            dv = V3(0, C * d, -S * d)
            ents = X.root.findBRepUsingRay(Wp(x, y, z), dv, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
            out = []
            for i in range(ents.count):
                nm = ents.item(i).body.name
                if nm.startswith(skip) or nm.endswith('_v42'):
                    continue
                yy = W(hp.item(i))[1]
                if abs(yy - y) <= lim:
                    out.append([round(yy, 2), nm.replace('HOUSING_F_', 'H_')])
            return sorted(out, key=lambda t: t[0] * d)
        rays = {}
        for sx in (1, -1):
            for (cx, cz) in ((52.8, 10.2), (52.8, 45.7), (88.2, 10.2), (88.2, 45.7)):
                for (dx, dz) in ((0, 0), (2.4, 0), (0, 2.4), (-2.4, 0), (0, -2.4)):
                    if sx < 0 and (dx, dz) != (2.4, 0):
                        continue
                    rays['%+.1f,%.1f%s' % (sx * cx, cz, '' if (dx, dz) == (0, 0) else ' d%+.1f,%+.1f' % (dx, dz))] = ray(sx * (cx + dx), 0.2, cz + dz, 1, 12)
            for dx in (-5.0, 0.0, 5.0):
                for zz in (77.0, 79.5, 83.0):
                    rays['tab %+.1f,%.1f' % (sx * (57.5 + dx), zz)] = ray(sx * (57.5 + dx), -6.0, zz, 1, 16)
            rays['key %+.1f' % (sx * 57.5)] = ray(sx * 57.5, -6.5, 79.5, -1, 100)
            rays['key %+.1f z82.5' % (sx * 57.5)] = ray(sx * 57.5, -6.5, 82.5, -1, 100)
        st['rays'] = rays
        status('f2c0', st)
        # D pads against plate features
        cen = json.load(open(os.path.join(FP, 'f2a_intake.json')))
        feat = {'foot': [(80.0, -11.5), (-80.0, -11.5), (30.0, -69.0), (-30.0, -69.0)], 'door': [(19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0)],
                'intake': cen}
        cand = [(51, -11.2), (51, -14.2), (51, -17.2), (64, -44.2), (72, -37.2), (82, -30), (85, -15), (60, -30), (-51, -11.2), (-51, -14.2), (-51, -17.2),
                (-64, -44.2), (-72, -37.2), (-82, -30), (-85, -15), (-60, -30)]
        dd = {}
        for (x, y) in cand:
            dd['%g,%g' % (x, y)] = {k: round(min(min(math.hypot(x - a, y + t - b) for t in (-1.2, 0.0, 1.2)) for (a, b) in v), 1) for k, v in feat.items()}
        st['pad_dist'] = dd
        xs = [c[0] for c in cen]; ys = [c[1] for c in cen]
        st['intake_bbox'] = [min(xs), max(xs), min(ys), max(ys)]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2c0', st)


run(None)
