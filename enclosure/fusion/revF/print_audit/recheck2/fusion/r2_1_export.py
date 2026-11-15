# r2_1_export (block 1): guard, then a mesh of each printed body (mesh calculator 0.01 mm chordal, <= 10 deg normal deviation)
#   as binary STL in world mm (x_rel). No temporary document, no export manager. READ-ONLY on the design.
#   Parts: __PARTS__ (tags of R2_PRINTS, comma separated, or ALL). Writes print_audit_recheck2/exports/<tag>.stl and
#   data/r2_1_export_<first tag>.json. Stops before 70 s and reports what is left.
def run(_context):
    X = R2Ctx(); t0 = time.time(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'tol_mm': 0.01}
    out['guard'] = r2_guard(X)[1]
    want = '__PARTS__'
    todo = [(t, b) for t, b in R2_PRINTS if want == 'ALL' or t in want.split(',')]
    os.makedirs(os.path.join(R2_DIR, 'exports'), exist_ok=True)
    done = []
    for tag, bn in todo:
        if time.time() - t0 > 70:
            break
        t1 = time.time(); b = X.body(bn)
        P, T = r2_world_mesh(b, 0.01)
        path = os.path.join(R2_DIR, 'exports', tag + '.stl')
        n = r2_write_stl(path, P, T, tag)
        xs = [p[0] for p in P]; ys = [p[1] for p in P]; zs = [p[2] for p in P]
        pp = b.physicalProperties
        cg = r2_wpt(pp.centerOfMass)
        out[tag] = {'body': bn, 'vol_mm3': round(b.volume * 1000.0, 3), 'area_mm2': round(pp.area * 100.0, 2), 'lumps': b.lumps.count,
                    'faces': b.faces.count, 'tris': n, 'bytes': os.path.getsize(path), 'com': [round(v, 3) for v in cg],
                    'bbox': [round(min(xs), 3), round(max(xs), 3), round(min(ys), 3), round(max(ys), 3), round(min(zs), 3), round(max(zs), 3)],
                    's': round(time.time() - t1, 1)}
        done.append(tag)
    out['left'] = [t for t, b in todo if t not in done]
    out['t_s'] = round(time.time() - t0, 1)
    r2_out(os.path.join(R2_DIR, 'data', 'r2_1_export_%s.json' % (done[0] if done else 'none')), out)
    r2_log('r2_1_export', 'run', {'done': done, 'left': out['left']})
    print(json.dumps({k: (v if k in ('t_s', 'guard', 'left') else [v.get('tris'), v.get('vol_mm3'), v.get('com'), v.get('bbox'), v.get('s')])
                      for k, v in out.items() if k not in ('t', 'tol_mm')}, separators=(',', ':')))
