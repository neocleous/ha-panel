# pf_1_export (block 1). READ-ONLY on the design (connector readOnly: true). Writes only under print_files/_work/exports/.
#   The 14 printed parts of version 65 as binary STL in world mm (0.01 mm chordal, as the re-checks), with each body's volume,
#   area and centre of mass from the B-rep; each STL compared byte for byte (after its 80-byte header) with the re-check's
#   export of 2026-11-15 (recheck2/exports).
#   Guard first (strict). Stops before 70 s; a second call finishes the rest.


def run(_context):
    t0 = time.time(); X = R2Ctx(); r2_guard(X, strict=True)
    os.makedirs(os.path.join(R2_DIR, 'exports'), exist_ok=True)
    recp = os.path.join(R2_DIR, 'data', 'pf_1_export.json')
    out = json.load(open(recp)) if os.path.exists(recp) else {}
    for tag, bn in R2_PRINTS:
        if tag in out and out[tag].get('tris'):
            continue
        if time.time() - t0 > 70:
            break
        b = X.body(bn)
        if b is None:
            out[tag] = {'error': 'body missing: ' + bn}; continue
        P, T = r2_world_mesh(b, 0.01)
        p = os.path.join(R2_DIR, 'exports', tag + '.stl')
        n = r2_write_stl(p, P, T, tag)
        pr = b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy)
        com = r2_wpt(pr.centerOfMass)
        sh = r2_sha(p)
        out[tag] = {'body': bn, 'tris': n, 'vol_mm3': round(b.volume * 1000.0, 3), 'area_mm2': round(b.area * 100.0, 2),
                    'com_world': [round(c, 3) for c in com], 'sha': sh[:16], 'bytes': os.path.getsize(p)}
    for tag, bn in R2_PRINTS:                     # compare with the re-check's export after the 80-byte header (only the text differs)
        p = os.path.join(R2_DIR, 'exports', tag + '.stl'); old = os.path.join(R2_RC2, 'exports', tag + '.stl')
        if tag in out and out[tag].get('tris') and os.path.exists(p) and os.path.exists(old):
            out[tag]['same_as_recheck2'] = open(p, 'rb').read()[80:] == open(old, 'rb').read()[80:]
    out['_t'] = time.strftime('%Y-%m-%d %H:%M:%S')
    r2_out(recp, out)
    r2_log('pf_1_export', 'run', {k: (v.get('same_as_recheck2') if isinstance(v, dict) else v) for k, v in out.items()})
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in ('tris', 'vol_mm3', 'same_as_recheck2') if kk in v})
                      for k, v in out.items()}, separators=(',', ':')))
