# pf_1b_cmp (block 1). Touches no Fusion object. Compares each fresh export (print_files/_work/exports) with the re-check's
#   (recheck2/exports): triangle counts, header text, largest coordinate difference when the counts agree, mesh volume and
#   bounding box either way. Pure Python (struct).


def r2_stl_stats(p):
    b = open(p, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
    vol = 0.0; lo = [1e9] * 3; hi = [-1e9] * 3
    for t in range(n):
        f = struct.unpack_from('<12f', b, 84 + 50 * t)
        a = f[3:6]; c = f[6:9]; d = f[9:12]
        vol += (a[0] * (c[1] * d[2] - c[2] * d[1]) - a[1] * (c[0] * d[2] - c[2] * d[0]) + a[2] * (c[0] * d[1] - c[1] * d[0])) / 6.0
        for v in (a, c, d):
            for k in range(3):
                if v[k] < lo[k]: lo[k] = v[k]
                if v[k] > hi[k]: hi[k] = v[k]
    return b, n, vol, lo, hi


def run(_context):
    t0 = time.time(); out = {}
    for tag, bn in R2_PRINTS:
        if time.time() - t0 > 70:
            out[tag] = 'not done (time)'; continue
        p = os.path.join(R2_DIR, 'exports', tag + '.stl'); q = os.path.join(R2_RC2, 'exports', tag + '.stl')
        b1, n1, v1, lo1, hi1 = r2_stl_stats(p); b2, n2, v2, lo2, hi2 = r2_stl_stats(q)
        r = {'tris': [n1, n2], 'vol': [round(v1, 3), round(v2, 3)], 'hdr2': b2[:60].decode('latin-1').strip(),
             'bbox_dmax': round(max(max(abs(lo1[k] - lo2[k]), abs(hi1[k] - hi2[k])) for k in range(3)), 5)}
        if n1 == n2:
            dm = 0.0; nd = 0
            for t in range(n1):
                f1 = struct.unpack_from('<12f', b1, 84 + 50 * t); f2 = struct.unpack_from('<12f', b2, 84 + 50 * t)
                d = max(abs(f1[k] - f2[k]) for k in range(3, 12))
                if d > dm: dm = d
                if d > 0: nd += 1
            r['coord_dmax'] = dm; r['tris_differing'] = nd
        out[tag] = r
    r2_out(os.path.join(R2_DIR, 'data', 'pf_1b_cmp.json'), out)
    print(json.dumps(out, separators=(',', ':')))
