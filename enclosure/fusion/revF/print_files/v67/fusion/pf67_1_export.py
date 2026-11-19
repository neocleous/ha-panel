# pf67_1_export (block 1). READ-ONLY on the design (connector readOnly: true). Writes only under print_files_v67/_work/.
#   The 14 printed parts of version 67, meshed at 0.01 mm chordal and 10 deg normal deviation (PR33), as the print files of
#   2026-11-16 and the re-check's print-file-grade meshes:
#   1. exports/<tag>.stl: binary STL in world mm (pflib67.r2_write_stl, as pf_1_export), with each body's B-rep volume, area
#      and centre of mass;
#   2. orient/<tag>_plan.stl: the same triangles put on the bed with the world->bed matrices of 2026-11-16
#      (print_files/_work/data/pf_2_orient.json; the re-check of version 67 used the same), by pf_2_orient's own code, so
#      every part keeps its decided orientation and place;
#   3. compared with the re-check's bed mesh (print_audit_recheck3/orient_hr/<tag>_plan.stl): triangle count, the bytes after
#      the 80-byte header, bounds.
#   Guard first (strict). Stops after about 35 s; the next call continues where it stopped (the record keeps the done parts).


def r2_read(p):
    b = open(p, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
    return b, n


def r2_apply(src, dst, M, label):                       # pf_2_orient's code (2026-11-16), header text changed
    b, n = r2_read(src); o = bytearray(84 + 50 * n)
    o[0:80] = ('HA panel print files v67 %s bed mm' % label).encode().ljust(80, b' ')[:80]
    struct.pack_into('<I', o, 80, n)
    lo = [1e9] * 3; hi = [-1e9] * 3; vol = 0.0
    a = M
    for t in range(n):
        f = struct.unpack_from('<12f', b, 84 + 50 * t)
        v = []
        for k0 in (3, 6, 9):
            x, y, z = f[k0], f[k0 + 1], f[k0 + 2]
            X_ = a[0][0] * x + a[0][1] * y + a[0][2] * z + a[0][3]
            Y_ = a[1][0] * x + a[1][1] * y + a[1][2] * z + a[1][3]
            Z_ = a[2][0] * x + a[2][1] * y + a[2][2] * z + a[2][3]
            v += [X_, Y_, Z_]
            if X_ < lo[0]: lo[0] = X_
            if X_ > hi[0]: hi[0] = X_
            if Y_ < lo[1]: lo[1] = Y_
            if Y_ > hi[1]: hi[1] = Y_
            if Z_ < lo[2]: lo[2] = Z_
            if Z_ > hi[2]: hi[2] = Z_
        vol += (v[0] * (v[4] * v[8] - v[5] * v[7]) - v[1] * (v[3] * v[8] - v[5] * v[6]) + v[2] * (v[3] * v[7] - v[4] * v[6])) / 6.0
        nx, ny, nz = f[0], f[1], f[2]
        N = (a[0][0] * nx + a[0][1] * ny + a[0][2] * nz, a[1][0] * nx + a[1][1] * ny + a[1][2] * nz,
             a[2][0] * nx + a[2][1] * ny + a[2][2] * nz)
        struct.pack_into('<12fH', o, 84 + 50 * t, N[0], N[1], N[2], *v, 0)
    open(dst, 'wb').write(o)
    return n, [round(c, 4) for c in lo], [round(c, 4) for c in hi], round(vol, 3)


def run(_context):
    t0 = time.time(); X = R2Ctx(); r2_guard(X, strict=True)
    ORI = json.load(open(os.path.join(R2_PF65W, 'data', 'pf_2_orient.json')))
    recp = os.path.join(R2_DIR, 'data', 'pf67_1_export.json')
    out = json.load(open(recp)) if os.path.exists(recp) else {}
    done_now = []
    for tag, bn in R2_PRINTS:
        if tag in out and out[tag].get('done'):
            continue
        if time.time() - t0 > 35:
            break
        b = X.body(bn)
        if b is None:
            out[tag] = {'error': 'body missing: ' + bn}; continue
        P, T = r2_world_mesh(b, 0.01, 10.0)
        pw = os.path.join(R2_DIR, 'exports', tag + '.stl')
        n = r2_write_stl(pw, P, T, tag)
        pr = b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy)
        com = r2_wpt(pr.centerOfMass)
        pb = os.path.join(R2_DIR, 'orient', tag + '_plan.stl')
        n2, lo, hi, vol = r2_apply(pw, pb, ORI[tag]['M'], tag)
        ref = os.path.join(R2_RC3, 'orient_hr', tag + '_plan.stl')
        same = None; ref_tris = None
        if os.path.exists(ref):
            rb = open(ref, 'rb').read(); mb = open(pb, 'rb').read()
            ref_tris = struct.unpack_from('<I', rb, 80)[0]
            same = (rb[80:] == mb[80:])
        out[tag] = {'done': True, 'body': bn, 'tris': n, 'vol_mm3': round(b.volume * 1000.0, 3), 'area_mm2': round(b.area * 100.0, 2),
                    'com_world': [round(c, 3) for c in com], 'bed_lo': lo, 'bed_hi': hi, 'mesh_vol_mm3': vol,
                    'v65_lo': ORI[tag]['lo'], 'v65_hi': ORI[tag]['hi'], 'rc3_tris': ref_tris, 'same_as_rc3': same,
                    'sha_bed': r2_sha(pb)[:16], 'bytes_bed': os.path.getsize(pb)}
        done_now.append(tag)
        r2_out(recp, out)
    out['_t'] = time.strftime('%Y-%m-%d %H:%M:%S')
    r2_out(recp, out)
    r2_log('pf67_1_export', 'run', {'done_now': done_now})
    left = [t for t, _ in R2_PRINTS if not (t in out and out[t].get('done'))]
    print(json.dumps({'done_now': done_now, 'left': left, 's': round(time.time() - t0, 1),
                      'parts': {t: {k: out[t][k] for k in ('tris', 'vol_mm3', 'mesh_vol_mm3', 'bed_lo', 'bed_hi', 'same_as_rc3', 'rc3_tris')}
                                for t in done_now}}, separators=(',', ':')))
