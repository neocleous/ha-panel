# HA panel print audit, block 0/1: mesh export, read-only on the design. For each of the 14 prints (the bracket's halves split
#   by x_rel sign of each triangle's centroid, as d19a), a body mesh from the mesh calculator at PA1_TOL mm chordal tolerance
#   and <= 10 deg normal deviation, written as binary STL in WORLD mm with x_rel (no export manager, no temporary document).
#   Orientation for printing is applied in the cloud workspace. Writes print_audit/exports/<tag>.stl and
#   print_audit/data/pa1_export.json; logs each part as it is written (long run: poll pa_log.json).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
PA1_OUT = os.path.join(PA_DIR, 'data', 'pa1_export.json')
PA1_TOL = 0.01
PA1_ONLY = globals().get('PA1_ONLY')          # optional list of tags (set by the loader)


def run(_context):
    X = Ctx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'tol_mm': PA1_TOL}; t0 = time.time()
    try:
        out['guard'] = pa_guard(X)[0]
        os.makedirs(os.path.join(PA_DIR, 'exports'), exist_ok=True)
        cache = {}
        for (tag, bn, side) in PA_PRINTS:
            if PA1_ONLY and tag not in PA1_ONLY:
                continue
            t1 = time.time()
            if bn not in cache:
                cache[bn] = pa_world_mesh(X.body(bn), PA1_TOL)
            P, T = cache[bn]
            if side is not None:
                T = [t for t in T if (P[t[0]][0] + P[t[1]][0] + P[t[2]][0]) * side > 0]
            path = os.path.join(PA_DIR, 'exports', tag + '.stl')
            n = pa_write_stl(path, P, T, tag)
            out[tag] = {'body': bn, 'tris': n, 'bytes': os.path.getsize(path), 's': round(time.time() - t1, 1)}
            log('pa1_export', 'part', {tag: out[tag]})
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    pa_out(PA1_OUT, out)
    log('pa1_export', 'run', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({k: v for k, v in out.items() if k != 'guard'}, separators=(',', ':')))
