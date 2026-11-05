# rev F cap block c1a (2026-11-05), read-only: the top region before the cap split (Daniel 13:31 / 13:51: top piece = a cap
#   screwed on from the top, clamping the fabric; 1 A spline groove in the ledge, 2 A countersunk M3 from the top,
#   3 a joint across the top ≈ 3 mm behind the display's top-back edge).
#   A. REF_F_outer top profile: rays down at x_rel 0 / ±40 / ±80 / ±90, y −14…−56 (first hit z).
#   B. HOUSING_F_front / SLAB_frame / LCD_glass hits from above at x 0, y −10…−30 (front strip behind the display).
#   C. Back wall: rays −y from y −30 at x_rel 0 / 30 / 45 / 60 / 75, z 150…178 (front / door hits: inner, outer, slots).
#   D. Side walls: rays ±x from x_rel 0 at y −25 / −35 / −45, z 165…180.
#   E. Bodies reaching above z 160 (tight world boxes), slab / glass / door / front boxes, exhaust tool box.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FD = ('HOUSING_F_front', 'HOUSING_F_door')


def zdown(X, xr, y, names):
    hs = ray_hits(X, (XC + xr, y, 250.0), (0, 0, -1), names)
    return [round(hs[0][4], 2), hs[0][1][:12]] if hs else None


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        A = {}
        for xr in (0.0, 40.0, -40.0, 80.0, -80.0, 90.0, -90.0):
            A['x%g' % xr] = [[y, (zdown(X, xr, float(y), ('REF_F_outer',)) or [None])[0]] for y in range(-14, -57, -2)]
        out['A_ref_top_z'] = A
        B = []
        for y10 in range(-100, -305, -5):
            y = y10 / 10.0
            hs = ray_hits(X, (XC, y, 250.0), (0, 0, -1), ('HOUSING_F_front', 'SLAB_frame', 'LCD_glass'))
            B.append([y] + [[h[1][:9], round(h[4], 2)] for h in hs[:3]])
        out['B_front_strip_x0'] = B
        C = {}
        for xr in (0.0, 30.0, 45.0, 60.0, 75.0):
            rows = []
            for z in range(150, 179):
                hs = [h for h in ray_hits(X, (XC + xr, -30.0, float(z)), (0, -1, 0), FD) if h[3] > -100]
                rows.append([z] + [[h[1][10:11], round(h[3], 2)] for h in hs[:6]])
            C['x%g' % xr] = rows
        out['C_back'] = C
        D = {}
        for y in (-25.0, -35.0, -45.0):
            for sx in (1, -1):
                rows = []
                for z in range(165, 181):
                    hs = ray_hits(X, (XC, y, float(z)), (sx, 0, 0), ('HOUSING_F_front', 'REF_F_outer'))
                    rows.append([z] + [[h[1][:9], round(h[2], 2)] for h in hs[:4]])
                D['y%g_%s' % (y, '+x' if sx > 0 else '-x')] = rows
        out['D_sides'] = D
        E = {}
        for b in X.comp.bRepBodies:
            try:
                bb = wbb(X, b)
            except Exception:
                continue
            if bb[5] > 160.0 and not b.name.startswith(('TOOL_', 'REF_', 'INNER_', 'HOUSING_E', 'sk_')) and not b.name.endswith(('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_revE', '_revD', '_r2', '_r3')):
                E[b.name] = [round(v, 1) for v in bb] + [b.isLightBulbOn]
        out['E_bodies_above_z160'] = E
        out['boxes'] = {n: [round(v, 1) for v in wbb(X, X.body(n))] for n in ('SLAB_frame', 'LCD_glass', 'HOUSING_F_door', 'HOUSING_F_front', 'TOOL_exhaust_slots')}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1a_probe_top', 'probe', out)
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
