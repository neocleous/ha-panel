# HA panel model audit (2026-11-05) block 1b: triangle meshes -> binary STL in world mm (x_rel, y, z), read-only.
#   SEL = list of body names (default the ten printed parts), TOL = surface tolerance in mm (default 0.01), set by the
#   loader. Files ~/Documents/audit/mesh/<name>.stl; the log row per body has nodes, triangles, the body's volume (mm³)
#   and area (mm²) for the offline watertight / volume check. Time-boxed: stops before a body when 45 s have passed.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    names = globals().get('SEL') or PRINTED
    tol = globals().get('TOL') or 0.01
    sub = globals().get('SUBDIR') or 'mesh'
    os.makedirs(os.path.join(AUD, sub), exist_ok=True)
    try:
        for name in names:
            if time.time() - t0 > 45:
                out['stopped_before'] = name; break
            b = X.body(name)
            if b is None:
                out[name] = 'missing'; continue
            t1 = time.time()
            P, T = world_mesh(b, tol_mm=tol)
            n = write_stl(os.path.join(AUD, sub, name + '.stl'), P, T, name)
            out[name] = {'nodes': len(P), 'tris': n, 'vol_mm3': round(b.volume * 1000, 3), 'area_mm2': round(b.area * 100, 3),
                         'tol': tol, 't': round(time.time() - t1, 1)}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a1b_meshes', 'meshes', out)
    print(json.dumps(out))
