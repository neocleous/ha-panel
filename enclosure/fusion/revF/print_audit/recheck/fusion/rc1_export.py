# rc1_export (block 1): guard, then a mesh of each of the 13 printed bodies (mesh calculator 0.01 mm chordal, <= 10 deg
#   normal deviation) as binary STL in world mm (x_rel). No temporary document, no export manager. READ-ONLY on the design.
#   Writes print_audit_recheck/exports/<tag>.stl and data/rc1_export.json.


def run(_context):
    X = RcCtx(); t0 = time.time(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'tol_mm': 0.01}
    out['guard'] = rc_guard(X)[0]
    os.makedirs(os.path.join(RC_DIR, 'exports'), exist_ok=True)
    for tag, bn in RC_PRINTS:
        t1 = time.time(); b = X.body(bn)
        P, T = rc_world_mesh(b, 0.01)
        path = os.path.join(RC_DIR, 'exports', tag + '.stl')
        n = rc_write_stl(path, P, T, tag)
        xs = [p[0] for p in P]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
        out[tag] = {'body': bn, 'vol_mm3': round(b.volume * 1000.0, 3), 'lumps': b.lumps.count, 'faces': b.faces.count,
                    'tris': n, 'bytes': os.path.getsize(path),
                    'bbox': [round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3), round(min(zs), 3), round(max(zs), 3)],
                    's': round(time.time() - t1, 1)}
        rc_log('rc1_export', 'part', {tag: out[tag]['s']})
    out['t_s'] = round(time.time() - t0, 1)
    rc_out(os.path.join(RC_DIR, 'data', 'rc1_export.json'), out)
    print(json.dumps({k: (v if k in ('t_s', 'guard') else [v.get('tris'), v.get('bbox'), v.get('s')]) for k, v in out.items()
                      if k not in ('t', 'tol_mm')}, separators=(',', ':')))
