# pf_2_orient (block 1). Touches no Fusion object. Puts this session's world exports (print_files/_work/exports) on the bed
#   with the re-checks' own world->bed matrices, so every part keeps its decided orientation and place:
#   - scope A (screen, shell, boxes, base): the matrix is recovered from the re-check of 2026-11-15, whose oriented meshes keep
#     the export's triangle order (recheck2/exports/<tag>.stl -> recheck2/slicer/orient/<tag>_plan.stl): solved from four
#     vertices, then checked on every 50th triangle;
#   - scope B (carrier, cradle, clips, hood, cap, grommet, slab, door): the matrix stored by the re-check of 2026-11-14
#     (recheck/slicer/orient/<name>.json, "M_world_to_bed").
#   Writes _work/orient/<tag>_plan.stl, copies the shell's blocker mesh (bed frame) and records the matrices, bounds and mesh
#   volumes against the re-check's oriented meshes. Pure Python (struct). Stops before 70 s; the next call continues.
import shutil

R2_A = ('screen', 'shell', 'spkbox_L', 'spkbox_R', 'base')
R2_B = {'carrier': 'carrier_plan', 'cradle': 'cradle_plan', 'clip_L': 'clip_L_plan', 'clip_R': 'clip_R_plan',
        'bme_hood': 'bme_hood_plan', 'cap': 'cap_plan', 'grommet': 'grommet_side+z', 'slab': 'slab_plan', 'door': 'door_plan'}


def r2_read(p):
    b = open(p, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
    return b, n


def r2_solve4(A, y):
    # 4x4 linear system, Gauss-Jordan with partial pivoting
    M = [list(A[i]) + [y[i]] for i in range(4)]
    for c in range(4):
        p = max(range(c, 4), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12:
            raise RuntimeError('singular')
        for r in range(4):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [M[r][k] - f * M[c][k] for k in range(5)]
    return [M[i][4] / M[i][i] for i in range(4)]


def r2_matrix_from_pair(wp, op):
    bw, n = r2_read(wp); bo, n2 = r2_read(op)
    if n != n2:
        raise RuntimeError('triangle counts differ %s %s' % (n, n2))
    # four well-spread vertices: extreme x, extreme y, extreme z, and the vertex farthest from the plane of those three
    vs = []
    for t in range(0, n, max(1, n // 4000)):
        f = struct.unpack_from('<12f', bw, 84 + 50 * t); g = struct.unpack_from('<12f', bo, 84 + 50 * t)
        vs.append((f[3:6], g[3:6]))
    i1 = min(range(len(vs)), key=lambda i: vs[i][0][0]); i2 = max(range(len(vs)), key=lambda i: vs[i][0][0])
    i3 = max(range(len(vs)), key=lambda i: abs(vs[i][0][1] - vs[i1][0][1]) + abs(vs[i][0][2] - vs[i1][0][2]))
    a, b, c = vs[i1][0], vs[i2][0], vs[i3][0]
    u = [b[k] - a[k] for k in range(3)]; v = [c[k] - a[k] for k in range(3)]
    nrm = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    i4 = max(range(len(vs)), key=lambda i: abs(sum(nrm[k] * (vs[i][0][k] - a[k]) for k in range(3))))
    pts = [vs[i] for i in (i1, i2, i3, i4)]
    A = [[p[0][0], p[0][1], p[0][2], 1.0] for p in pts]
    rows = [r2_solve4(A, [p[1][k] for p in pts]) for k in range(3)]
    M = [rows[0], rows[1], rows[2], [0.0, 0.0, 0.0, 1.0]]
    err = 0.0
    for t in range(0, n, 50):
        f = struct.unpack_from('<12f', bw, 84 + 50 * t); g = struct.unpack_from('<12f', bo, 84 + 50 * t)
        for k0 in (3, 6, 9):
            x, y, z = f[k0], f[k0 + 1], f[k0 + 2]
            for r in range(3):
                e = abs(M[r][0] * x + M[r][1] * y + M[r][2] * z + M[r][3] - g[k0 + r])
                if e > err: err = e
    return M, err


def r2_apply(src, dst, M, label):
    b, n = r2_read(src); o = bytearray(84 + 50 * n)
    o[0:80] = ('HA panel print files %s bed mm' % label).encode().ljust(80, b' ')[:80]
    struct.pack_into('<I', o, 80, n)
    lo = [1e9] * 3; hi = [-1e9] * 3; vol = 0.0
    a = M
    for t in range(n):
        f = struct.unpack_from('<12f', b, 84 + 50 * t)
        v = []
        for k0 in (3, 6, 9):
            x, y, z = f[k0], f[k0 + 1], f[k0 + 2]
            X = a[0][0] * x + a[0][1] * y + a[0][2] * z + a[0][3]
            Y = a[1][0] * x + a[1][1] * y + a[1][2] * z + a[1][3]
            Z = a[2][0] * x + a[2][1] * y + a[2][2] * z + a[2][3]
            v += [X, Y, Z]
            if X < lo[0]: lo[0] = X
            if X > hi[0]: hi[0] = X
            if Y < lo[1]: lo[1] = Y
            if Y > hi[1]: hi[1] = Y
            if Z < lo[2]: lo[2] = Z
            if Z > hi[2]: hi[2] = Z
        vol += (v[0] * (v[4] * v[8] - v[5] * v[7]) - v[1] * (v[3] * v[8] - v[5] * v[6]) + v[2] * (v[3] * v[7] - v[4] * v[6])) / 6.0
        nx, ny, nz = f[0], f[1], f[2]
        N = (a[0][0] * nx + a[0][1] * ny + a[0][2] * nz, a[1][0] * nx + a[1][1] * ny + a[1][2] * nz,
             a[2][0] * nx + a[2][1] * ny + a[2][2] * nz)
        struct.pack_into('<12fH', o, 84 + 50 * t, N[0], N[1], N[2], *v, 0)
    open(dst, 'wb').write(o)
    return n, [round(c, 4) for c in lo], [round(c, 4) for c in hi], round(vol, 3)


def r2_bounds(p):
    b, n = r2_read(p); lo = [1e9] * 3; hi = [-1e9] * 3
    for t in range(n):
        f = struct.unpack_from('<12f', b, 84 + 50 * t)
        for k0 in (3, 6, 9):
            for k in range(3):
                c = f[k0 + k]
                if c < lo[k]: lo[k] = c
                if c > hi[k]: hi[k] = c
    return [round(c, 4) for c in lo], [round(c, 4) for c in hi]


def run(_context):
    t0 = time.time(); od = os.path.join(R2_DIR, 'orient'); os.makedirs(od, exist_ok=True)
    recp = os.path.join(R2_DIR, 'data', 'pf_2_orient.json')
    out = json.load(open(recp)) if os.path.exists(recp) else {}
    for tag in list(R2_A) + list(R2_B):
        if tag in out and out[tag].get('done'):
            continue
        if time.time() - t0 > 45:
            break
        src = os.path.join(R2_DIR, 'exports', tag + '.stl'); dst = os.path.join(od, tag + '_plan.stl')
        if tag in R2_A:
            M, err = r2_matrix_from_pair(os.path.join(R2_RC2, 'exports', tag + '.stl'),
                                         os.path.join(R2_RC2, 'slicer', 'orient', tag + '_plan.stl'))
            ref = os.path.join(R2_RC2, 'slicer', 'orient', tag + '_plan.stl'); src_m = 'recheck2 pair'
        else:
            j = json.load(open(os.path.join(R2_RC1, 'slicer', 'orient', R2_B[tag] + '.json')))
            M = j['M_world_to_bed']; err = None
            ref = os.path.join(R2_RC1, 'slicer', 'orient', R2_B[tag] + '.stl'); src_m = 'recheck M_world_to_bed'
        n, lo, hi, vol = r2_apply(src, dst, M, tag)
        rlo, rhi = r2_bounds(ref)
        out[tag] = {'done': True, 'matrix_from': src_m, 'M': [[round(c, 9) for c in r] for r in M], 'fit_err_mm': err,
                    'tris': n, 'lo': lo, 'hi': hi, 'vol_mm3': vol,
                    'bounds_dmax_vs_ref': round(max(max(abs(lo[k] - rlo[k]), abs(hi[k] - rhi[k])) for k in range(3)), 5)}
    blk = os.path.join(R2_RC2, 'slicer', 'orient', 'shell_plan_blk_v2.stl')
    shutil.copy2(blk, os.path.join(od, 'shell_plan_blk_v2.stl'))
    out['_blocker_copied'] = r2_sha(blk)[:16]
    out['_t'] = time.strftime('%Y-%m-%d %H:%M:%S')
    r2_out(recp, out)
    r2_log('pf_2_orient', 'run', {k: (v.get('bounds_dmax_vs_ref') if isinstance(v, dict) else v) for k, v in out.items()})
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: v[kk] for kk in ('fit_err_mm', 'tris', 'lo', 'hi', 'vol_mm3', 'bounds_dmax_vs_ref')})
                      for k, v in out.items()}, separators=(',', ':')))
