# rev F d8a (2026-11-06), read-only: inputs for the VEML6030 pocket (Daniel's caliper: board 15.26 x 15.20, two Ø2.1 holes
#   11.0 apart at the top corners). Writes ~/Documents/HA_panel_renders/d_data/data/d8a_probe.json: every body near the
#   pocket (world box, visibility), the cap's small cylinders there, the lead's end at the board, rays up and down from the
#   board, and sections through the pocket.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d8a_probe.json')
CAP = 'HOUSING_F_cap'
WIN = [-16.0, 16.0, -48.0, -18.0, 168.0, 181.0]          # x_rel, y, z region round the pocket
NAMES = [CAP, 'HOUSING_F_front', 'VEML_env', 'LEAD_VEML', 'MIC_strip_L_env', 'MIC_strip_R_env']


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        cb = X.body(CAP)
        out['cap_cm3'] = round(cb.volume, 4)
        near = {}
        for b in X.comp.bRepBodies:
            try:
                bb = wbb(X, b)
            except Exception:
                continue
            if bb[0] < WIN[1] and bb[1] > WIN[0] and bb[2] < WIN[3] and bb[3] > WIN[2] and bb[4] < WIN[5] and bb[5] > WIN[4]:
                near[b.name] = {'bb': [round(v, 2) for v in bb], 'vis': b.isLightBulbOn, 'cm3': round(b.volume, 4)}
        out['near'] = near
        rows = []
        for f in cb.faces:
            g = f.geometry
            if g.objectType != adsk.core.Cylinder.classType() or g.radius * 10 > 2.5:
                continue
            ax = g.axis; ax.normalize(); o = g.origin
            ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices] or [0.0]
            tm = (min(ts) + max(ts)) / 2; c = P3(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
            xr = c.x * 10 - XC
            if not (WIN[0] < xr < WIN[1] and WIN[2] < wy(c) < WIN[3]):
                continue
            zs = [wz(v.geometry) for v in f.vertices]
            p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
            k = (p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z
            q = P3(o.x + ax.x * k, o.y + ax.y * k, o.z + ax.z * k)
            hole = V3(p.x - q.x, p.y - q.y, p.z - q.z).dotProduct(n) < 0
            rows.append([round(2 * g.radius * 10, 3), 'hole' if hole else 'pin', [round(xr, 2), round(wy(c), 2), round(wz(c), 2)],
                         [round(min(zs), 2), round(max(zs), 2)] if zs else None])
        out['cap_small_cyl'] = rows
        # the lead's piece within 3 mm of the board envelope
        ve = X.body('VEML_env'); ld = X.body('LEAD_VEML')
        if ve is not None and ld is not None:
            vb = wbb(X, ve)
            q = X.tbm.copy(ld); inter(X, q, wbox_rel(X, vb, 3.0))
            out['lead_at_board'] = {'mm3': round(q.volume * 1000, 2), 'bb': [round(v, 2) for v in wbb(X, q)] if q.volume > 0 else None}
            out['lead_faces'] = len(list(ld.faces))
            ends = []
            for f in ld.faces:
                if f.geometry.objectType == adsk.core.Plane.classType() or f.geometry.objectType == adsk.core.Sphere.classType():
                    c = f.centroid
                    ends.append([f.geometry.objectType.split('::')[-1], [round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2)], round(f.area * 100, 2)])
            out['lead_end_faces'] = ends
        # rays up (through the plate) and down (what the board hangs over) on a grid over the pocket
        names = [b.name for b in X.comp.bRepBodies if b.isLightBulbOn or b.name in ('VEML_env', 'LEAD_VEML')]
        up = {}; dn = {}
        for xr in (-9.0, -5.5, 0.0, 5.5, 9.0):
            for y in (-43.0, -39.3, -33.7, -28.0, -24.5):
                up['%g,%g' % (xr, y)] = solid_runs(X, (XC + xr, y, 176.0), (0, 0, 1), CAP, 6.0)
                hs = ray_hits(X, (XC + xr, y, 177.45), (0, 0, -1), names)
                dn['%g,%g' % (xr, y)] = [[round(h[0], 2), h[1]] for h in hs[:4]]
        out['rays_up_cap'] = up; out['rays_down'] = dn
        PL = {
            'V_z177.9': ('z', 177.9, (-16.0, 16.0, -46.0, -20.0), NAMES),
            'V_z177.2': ('z', 177.2, (-16.0, 16.0, -46.0, -20.0), NAMES),
            'V_x0': ('x', 0.0, (-48.0, -18.0, 170.0, 181.0), NAMES),
            'V_x5.5': ('x', 5.5, (-48.0, -18.0, 170.0, 181.0), NAMES),
            'V_y-33.7': ('y', -33.7, (-16.0, 16.0, 170.0, 181.0), NAMES),
            'V_y-39.3': ('y', -39.3, (-16.0, 16.0, 170.0, 181.0), NAMES),
        }
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: v for k, v in out.items() if k not in ('sec', 'rays_up_cap', 'rays_down', 'near')}
    log('v5f_d8a_veml_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
